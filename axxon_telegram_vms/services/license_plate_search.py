"""Pure license-plate search helpers for the Step 25 MVP."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Any

from axxon_telegram_vms.models import (
    EventQuery,
    EventScopeFilter,
    EventTaxonomyFilter,
    EventTimeRange,
    format_query_datetime,
    normalize_event_card,
)


DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC = 3600
DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE = 5
MAX_LICENSE_PLATE_SEARCH_PAGE_SIZE = 10
DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT = 400
LICENSE_PLATE_SEARCH_MATCH_MODES = frozenset({"exact", "contains", "mask"})


class LicensePlateSearchSyntaxError(ValueError):
    """Raised when a command-style license-plate search request is malformed."""


def _text(value: object) -> str:
    return str(value or "").strip()


def _normalized(value: object) -> str:
    return _text(value).casefold()


def _coerce_positive_int(value: object, field_name: str) -> int:
    try:
        out = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if out <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return out


def _split_csv_values(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    values = raw.split(",") if isinstance(raw, str) else raw
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _text(value)
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return tuple(out)


def _coerce_descending(*, sort: str | None = None, ascending: bool = False) -> bool:
    if ascending:
        return False
    value = _text(sort or "desc").lower()
    if value in {"asc", "ascending", "oldest"}:
        return False
    if value in {"desc", "descending", "newest", ""}:
        return True
    raise ValueError("sort must be asc or desc")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _top_counter_rows(counter: Counter[str], limit: int = 3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for value, count in counter.most_common():
        if not _text(value):
            continue
        rows.append({"name": value, "count": count})
        if len(rows) >= limit:
            break
    return rows


def _card_sort_key(card: Mapping[str, Any]) -> tuple[str, str]:
    return (str(card.get("timestamp") or ""), str(card.get("id") or ""))


def _coerce_plate_search_card(row: Mapping[str, Any]) -> dict[str, Any]:
    if "timestamp" in row and "camera" in row and "event_type" in row:
        card = dict(row)
    else:
        card = normalize_event_card(dict(row))
    card.pop("raw_event", None)
    return card


def _plate_matches(value: object, *, mode: str, expected: str) -> bool:
    candidate = _text(value)
    if not candidate:
        return False
    if mode == "exact":
        return _normalized(candidate) == _normalized(expected)
    if mode == "contains":
        return _normalized(expected) in _normalized(candidate)
    if mode == "mask":
        import re

        pattern = "^" + re.escape(expected).replace("\\*", ".*") + "$"
        return re.match(pattern, candidate, flags=re.IGNORECASE) is not None
    return False


@dataclass(frozen=True)
class LicensePlateSearchRequest:
    query: EventQuery
    match_mode: str
    match_value: str
    page: int = 1
    page_size: int = DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE
    scan_limit: int = DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT
    time_source: str = "explicit"
    window_seconds: int = DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC

    def __post_init__(self) -> None:
        match_mode = _text(self.match_mode).lower()
        match_value = _text(self.match_value)
        if match_mode not in LICENSE_PLATE_SEARCH_MATCH_MODES:
            raise ValueError(f"Unsupported plate search mode: {self.match_mode}")
        if not match_value:
            raise ValueError("License-plate search requires plate=..., contains=..., or mask=...")
        page = _coerce_positive_int(self.page, "page")
        page_size = min(
            MAX_LICENSE_PLATE_SEARCH_PAGE_SIZE,
            _coerce_positive_int(self.page_size, "page_size"),
        )
        scan_limit = max(page_size, _coerce_positive_int(self.scan_limit, "scan_limit"))
        time_source = _text(self.time_source).lower() or "explicit"
        if time_source not in {"explicit", "window"}:
            raise ValueError(f"Unsupported plate search time_source: {self.time_source}")
        window_seconds = _coerce_positive_int(self.window_seconds, "window_seconds")
        if not self.query.time_range or not self.query.time_range.is_bounded():
            raise ValueError("License-plate search requires a bounded time range")
        object.__setattr__(self, "match_mode", match_mode)
        object.__setattr__(self, "match_value", match_value)
        object.__setattr__(self, "page", page)
        object.__setattr__(self, "page_size", page_size)
        object.__setattr__(self, "scan_limit", scan_limit)
        object.__setattr__(self, "time_source", time_source)
        object.__setattr__(self, "window_seconds", window_seconds)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def build_license_plate_search_request(
    *,
    plate: object = "",
    contains: object = "",
    mask: object = "",
    begin: object = None,
    end: object = None,
    last_sec: int = DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC,
    now_provider: Callable[[], datetime] = _utc_now,
    hosts: Iterable[object] = (),
    domains: Iterable[object] = (),
    camera_names: Iterable[object] = (),
    camera_access_points: Iterable[object] = (),
    detector_names: Iterable[object] = (),
    detector_access_points: Iterable[object] = (),
    page: int = 1,
    page_size: int = DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE,
    scan_limit: int = DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT,
    descending: bool = True,
) -> LicensePlateSearchRequest:
    matchers = [
        ("exact", _text(plate)),
        ("contains", _text(contains)),
        ("mask", _text(mask)),
    ]
    selected = [(mode, value) for mode, value in matchers if value]
    if not selected:
        raise ValueError("License-plate search requires plate=..., contains=..., or mask=...")
    if len(selected) > 1:
        raise ValueError("Use only one of plate=..., contains=..., or mask=...")
    match_mode, match_value = selected[0]

    explicit_begin = begin is not None and _text(begin)
    explicit_end = end is not None and _text(end)
    if explicit_begin or explicit_end:
        if not (explicit_begin and explicit_end):
            raise ValueError("Use both from=... and to=... for an explicit plate-search range.")
        if last_sec != DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC:
            raise ValueError("Use either from/to or last=..., not both.")
        time_range = EventTimeRange(begin=begin, end=end)
        time_source = "explicit"
        window_seconds = DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC
    else:
        window_seconds = _coerce_positive_int(last_sec, "last_sec")
        end_dt = now_provider()
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        else:
            end_dt = end_dt.astimezone(timezone.utc)
        begin_dt = end_dt - timedelta(seconds=window_seconds)
        time_range = EventTimeRange(begin=begin_dt, end=end_dt)
        time_source = "window"

    return LicensePlateSearchRequest(
        query=EventQuery(
            time_range=time_range,
            scope=EventScopeFilter(
                hosts=_split_csv_values(hosts),
                domains=_split_csv_values(domains),
                camera_names=_split_csv_values(camera_names),
                camera_access_points=_split_csv_values(camera_access_points),
                detector_names=_split_csv_values(detector_names),
                detector_access_points=_split_csv_values(detector_access_points),
            ),
            taxonomy=EventTaxonomyFilter(categories=("lpr",)),
            descending=descending,
        ),
        match_mode=match_mode,
        match_value=match_value,
        page=page,
        page_size=page_size,
        scan_limit=scan_limit,
        time_source=time_source,
        window_seconds=window_seconds,
    )


_TERM_ALIASES = {
    "from": "begin",
    "begin": "begin",
    "start": "begin",
    "to": "end",
    "end": "end",
    "last": "last_sec",
    "seconds": "last_sec",
    "window": "last_sec",
    "plate": "plate",
    "exact": "plate",
    "contains": "contains",
    "mask": "mask",
    "host": "hosts",
    "hosts": "hosts",
    "domain": "domains",
    "domains": "domains",
    "camera": "camera_names",
    "cam": "camera_names",
    "camera_name": "camera_names",
    "camera_names": "camera_names",
    "camera_ap": "camera_access_points",
    "camera_access_point": "camera_access_points",
    "camera_access_points": "camera_access_points",
    "detector": "detector_names",
    "det": "detector_names",
    "detector_name": "detector_names",
    "detector_names": "detector_names",
    "detector_ap": "detector_access_points",
    "detector_access_point": "detector_access_points",
    "detector_access_points": "detector_access_points",
    "page": "page",
    "page_size": "page_size",
    "scan_limit": "scan_limit",
    "sort": "sort",
    "order": "sort",
}
_MULTI_VALUE_TERMS = {
    "hosts",
    "domains",
    "camera_names",
    "camera_access_points",
    "detector_names",
    "detector_access_points",
}


def parse_license_plate_search_terms(
    terms: Iterable[object],
    *,
    now_provider: Callable[[], datetime] = _utc_now,
    default_window_sec: int = DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC,
    default_page_size: int = DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE,
    default_scan_limit: int = DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT,
) -> LicensePlateSearchRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise LicensePlateSearchSyntaxError("Use plate=..., contains=..., or mask=... to search license plates.")

    values: dict[str, Any] = {
        "last_sec": default_window_sec,
        "page": 1,
        "page_size": default_page_size,
        "scan_limit": default_scan_limit,
    }
    explicit_range_keys: set[str] = set()
    for term in raw_terms:
        if "=" not in term:
            raise LicensePlateSearchSyntaxError(f"Unsupported plate-search term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise LicensePlateSearchSyntaxError(f"Unsupported plate-search key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise LicensePlateSearchSyntaxError(f"Plate-search value is required for: {raw_key}")
        if key in {"begin", "end"}:
            explicit_range_keys.add(key)
        if key == "last_sec" and explicit_range_keys:
            raise LicensePlateSearchSyntaxError("Use either from/to or last=..., not both.")
        if key in _MULTI_VALUE_TERMS:
            existing = list(values.get(key) or [])
            existing.extend(_split_csv_values(value))
            values[key] = existing
        else:
            values[key] = value

    descending = _coerce_descending(sort=values.get("sort"))
    try:
        return build_license_plate_search_request(
            plate=values.get("plate") or "",
            contains=values.get("contains") or "",
            mask=values.get("mask") or "",
            begin=values.get("begin"),
            end=values.get("end"),
            last_sec=_coerce_positive_int(values.get("last_sec"), "last_sec"),
            now_provider=now_provider,
            hosts=values.get("hosts") or (),
            domains=values.get("domains") or (),
            camera_names=values.get("camera_names") or (),
            camera_access_points=values.get("camera_access_points") or (),
            detector_names=values.get("detector_names") or (),
            detector_access_points=values.get("detector_access_points") or (),
            page=_coerce_positive_int(values.get("page"), "page"),
            page_size=_coerce_positive_int(values.get("page_size"), "page_size"),
            scan_limit=_coerce_positive_int(values.get("scan_limit"), "scan_limit"),
            descending=descending,
        )
    except ValueError as exc:
        raise LicensePlateSearchSyntaxError(str(exc)) from exc


def license_plate_search_request_to_api_args(request: LicensePlateSearchRequest) -> list[str]:
    time_range = request.query.time_range
    begin = format_query_datetime(time_range.begin if time_range else None)
    end = format_query_datetime(time_range.end if time_range else None)
    if not (begin and end):
        raise ValueError("License-plate search request must include begin and end timestamps")

    args = [
        "--begin", begin,
        "--end", end,
        "--page", str(request.page),
        "--page-size", str(request.page_size),
        "--scan-limit", str(request.scan_limit),
    ]
    if not request.query.descending:
        args.append("--ascending")
    if request.match_mode == "exact":
        args.extend(["--plate", request.match_value])
    elif request.match_mode == "contains":
        args.extend(["--contains", request.match_value])
    elif request.match_mode == "mask":
        args.extend(["--mask", request.match_value])
    for value in request.query.scope.hosts:
        args.extend(["--scope-host", value])
    for value in request.query.scope.domains:
        args.extend(["--domain", value])
    for value in request.query.scope.camera_names:
        args.extend(["--camera", value])
    for value in request.query.scope.camera_access_points:
        args.extend(["--camera-ap", value])
    for value in request.query.scope.detector_names:
        args.extend(["--detector", value])
    for value in request.query.scope.detector_access_points:
        args.extend(["--detector-ap", value])
    return args


def build_license_plate_search_backend_request(
    request: LicensePlateSearchRequest,
    *,
    batch_size: int,
    offset: int = 0,
    subject: str | None = None,
) -> dict[str, Any]:
    range_payload = request.query.time_range.as_axxon_range() if request.query.time_range else {}
    begin = range_payload.get("begin_time")
    end = range_payload.get("end_time")
    if not (begin and end):
        raise ValueError("License-plate search requires a bounded time range")

    if subject is None:
        if len(request.query.scope.camera_access_points) == 1:
            subject = request.query.scope.camera_access_points[0]
        elif len(request.query.scope.detector_access_points) == 1:
            subject = request.query.scope.detector_access_points[0]
        elif len(request.query.scope.subjects) == 1:
            subject = request.query.scope.subjects[0]

    search_predicate = None
    plate = None
    if request.match_mode == "exact":
        plate = request.match_value
    elif request.match_mode == "contains":
        search_predicate = f"*{request.match_value}*"
    else:
        search_predicate = request.match_value

    limit = max(request.page_size, min(int(batch_size), request.scan_limit))
    return {
        "begin": begin,
        "end": end,
        "subject": subject,
        "plate": plate,
        "search_predicate": search_predicate,
        "limit": limit,
        "offset": max(0, int(offset)),
        "descending": request.query.descending,
    }


def shape_license_plate_search_results(
    rows: Iterable[Mapping[str, Any]],
    request: LicensePlateSearchRequest,
    *,
    scanned_count: int,
    complete: bool,
) -> dict[str, Any]:
    cards = [_coerce_plate_search_card(row) for row in rows if isinstance(row, Mapping)]
    cards = [
        card
        for card in cards
        if request.query.matches_card(card)
        and _plate_matches(card.get("plate"), mode=request.match_mode, expected=request.match_value)
    ]
    cards.sort(key=_card_sort_key, reverse=request.query.descending)

    matched = len(cards)
    start = request.offset
    end = start + request.page_size
    page_items = cards[start:end]
    page_count = ceil(matched / request.page_size) if matched else 0

    by_camera = Counter(str(card.get("camera") or "Camera") for card in cards)
    by_plate = Counter(str(card.get("plate") or "") for card in cards)

    return {
        "request": {
            "page": request.page,
            "page_size": request.page_size,
            "scan_limit": request.scan_limit,
            "descending": request.query.descending,
            "filters": request.query.to_legacy_filters(),
            "match": {
                "mode": request.match_mode,
                "value": request.match_value,
            },
            "time_source": request.time_source,
            "window_seconds": request.window_seconds,
        },
        "summary": {
            "matched": matched,
            "scanned": scanned_count,
            "complete": bool(complete),
            "truncated": not bool(complete),
            "top_cameras": _top_counter_rows(by_camera),
            "top_plates": _top_counter_rows(by_plate),
        },
        "pagination": {
            "page": request.page,
            "page_size": request.page_size,
            "page_count": page_count,
            "has_previous": request.page > 1,
            "has_next": end < matched or not bool(complete),
        },
        "items": page_items,
    }


__all__ = [
    "DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE",
    "DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT",
    "DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC",
    "LICENSE_PLATE_SEARCH_MATCH_MODES",
    "LicensePlateSearchRequest",
    "LicensePlateSearchSyntaxError",
    "build_license_plate_search_backend_request",
    "build_license_plate_search_request",
    "license_plate_search_request_to_api_args",
    "parse_license_plate_search_terms",
    "shape_license_plate_search_results",
]
