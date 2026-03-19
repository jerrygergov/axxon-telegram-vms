"""Pure time-range event search helpers for the Step 21 MVP."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from math import ceil
from typing import Any

from axxon_telegram_vms.models import (
    EventQuery,
    EventScopeFilter,
    EventTaxonomyFilter,
    EventTextFilter,
    EventTimeRange,
    format_query_datetime,
    normalize_event_card,
)


DEFAULT_EVENT_SEARCH_PAGE_SIZE = 5
MAX_EVENT_SEARCH_PAGE_SIZE = 10
DEFAULT_EVENT_SEARCH_SCAN_LIMIT = 1200
EVENT_SEARCH_MODES = frozenset({"summary", "list"})


class EventSearchSyntaxError(ValueError):
    """Raised when a command-style event search request is malformed."""


@dataclass(frozen=True)
class EventSearchRequest:
    query: EventQuery
    mode: str = "summary"
    page: int = 1
    page_size: int = DEFAULT_EVENT_SEARCH_PAGE_SIZE
    scan_limit: int = DEFAULT_EVENT_SEARCH_SCAN_LIMIT

    def __post_init__(self) -> None:
        mode = str(self.mode or "summary").strip().lower() or "summary"
        if mode not in EVENT_SEARCH_MODES:
            raise ValueError(f"Unsupported event search mode: {self.mode}")
        page = _coerce_positive_int(self.page, "page")
        page_size = min(MAX_EVENT_SEARCH_PAGE_SIZE, _coerce_positive_int(self.page_size, "page_size"))
        scan_limit = max(page_size, _coerce_positive_int(self.scan_limit, "scan_limit"))
        if not self.query.time_range or not self.query.time_range.is_bounded():
            raise ValueError("Event search requires a bounded time range")
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "page", page)
        object.__setattr__(self, "page_size", page_size)
        object.__setattr__(self, "scan_limit", scan_limit)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


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
    if isinstance(raw, str):
        values = raw.split(",")
    else:
        values = raw
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
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
    value = str(sort or "desc").strip().lower()
    if value in {"asc", "ascending", "oldest"}:
        return False
    if value in {"desc", "descending", "newest", ""}:
        return True
    raise ValueError("sort must be asc or desc")


def build_event_search_request(
    *,
    begin: object,
    end: object,
    hosts: Iterable[object] = (),
    domains: Iterable[object] = (),
    camera_names: Iterable[object] = (),
    camera_access_points: Iterable[object] = (),
    detector_names: Iterable[object] = (),
    detector_access_points: Iterable[object] = (),
    categories: Iterable[object] = (),
    event_types: Iterable[object] = (),
    states: Iterable[object] = (),
    severities: Iterable[object] = (),
    priorities: Iterable[object] = (),
    contains: object = "",
    mask: object = "",
    mode: str = "summary",
    page: int = 1,
    page_size: int = DEFAULT_EVENT_SEARCH_PAGE_SIZE,
    scan_limit: int = DEFAULT_EVENT_SEARCH_SCAN_LIMIT,
    descending: bool = True,
) -> EventSearchRequest:
    return EventSearchRequest(
        query=EventQuery(
            time_range=EventTimeRange(begin=begin, end=end),
            scope=EventScopeFilter(
                hosts=_split_csv_values(hosts),
                domains=_split_csv_values(domains),
                camera_names=_split_csv_values(camera_names),
                camera_access_points=_split_csv_values(camera_access_points),
                detector_names=_split_csv_values(detector_names),
                detector_access_points=_split_csv_values(detector_access_points),
            ),
            taxonomy=EventTaxonomyFilter(
                categories=_split_csv_values(categories),
                event_types=_split_csv_values(event_types),
                states=_split_csv_values(states),
                severities=_split_csv_values(severities),
                priorities=_split_csv_values(priorities),
            ),
            text=EventTextFilter(
                contains=str(contains or "").strip(),
                mask=str(mask or "").strip(),
            ),
            descending=descending,
        ),
        mode=mode,
        page=page,
        page_size=page_size,
        scan_limit=scan_limit,
    )


_TERM_ALIASES = {
    "from": "begin",
    "begin": "begin",
    "start": "begin",
    "to": "end",
    "end": "end",
    "host": "hosts",
    "hosts": "hosts",
    "domain": "domains",
    "domains": "domains",
    "camera": "camera_names",
    "cam": "camera_names",
    "camera_name": "camera_names",
    "camera_names": "camera_names",
    "camera_ap": "camera_access_points",
    "camera-app": "camera_access_points",
    "camera_access_point": "camera_access_points",
    "camera_access_points": "camera_access_points",
    "detector": "detector_names",
    "det": "detector_names",
    "detector_name": "detector_names",
    "detector_names": "detector_names",
    "detector_ap": "detector_access_points",
    "detector_access_point": "detector_access_points",
    "detector_access_points": "detector_access_points",
    "category": "categories",
    "categories": "categories",
    "cat": "categories",
    "type": "event_types",
    "types": "event_types",
    "event_type": "event_types",
    "event_types": "event_types",
    "state": "states",
    "states": "states",
    "severity": "severities",
    "severities": "severities",
    "priority": "priorities",
    "priorities": "priorities",
    "contains": "contains",
    "text": "contains",
    "mask": "mask",
    "mode": "mode",
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
    "categories",
    "event_types",
    "states",
    "severities",
    "priorities",
}


def parse_event_search_terms(
    terms: Iterable[object],
    *,
    default_mode: str = "summary",
    default_page_size: int = DEFAULT_EVENT_SEARCH_PAGE_SIZE,
    default_scan_limit: int = DEFAULT_EVENT_SEARCH_SCAN_LIMIT,
) -> EventSearchRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise EventSearchSyntaxError("Search requires key=value terms.")

    values: dict[str, Any] = {
        "mode": default_mode,
        "page": 1,
        "page_size": default_page_size,
        "scan_limit": default_scan_limit,
    }
    for term in raw_terms:
        if "=" not in term:
            raise EventSearchSyntaxError(f"Unsupported search term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise EventSearchSyntaxError(f"Unsupported search key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise EventSearchSyntaxError(f"Search value is required for: {raw_key}")
        if key in _MULTI_VALUE_TERMS:
            existing = list(values.get(key) or [])
            existing.extend(_split_csv_values(value))
            values[key] = existing
        else:
            values[key] = value

    if not values.get("begin") or not values.get("end"):
        raise EventSearchSyntaxError("Use from=... and to=... for the time range.")

    descending = _coerce_descending(sort=values.get("sort"))
    try:
        return build_event_search_request(
            begin=values.get("begin"),
            end=values.get("end"),
            hosts=values.get("hosts") or (),
            domains=values.get("domains") or (),
            camera_names=values.get("camera_names") or (),
            camera_access_points=values.get("camera_access_points") or (),
            detector_names=values.get("detector_names") or (),
            detector_access_points=values.get("detector_access_points") or (),
            categories=values.get("categories") or (),
            event_types=values.get("event_types") or (),
            states=values.get("states") or (),
            severities=values.get("severities") or (),
            priorities=values.get("priorities") or (),
            contains=values.get("contains") or "",
            mask=values.get("mask") or "",
            mode=str(values.get("mode") or default_mode),
            page=_coerce_positive_int(values.get("page"), "page"),
            page_size=_coerce_positive_int(values.get("page_size"), "page_size"),
            scan_limit=_coerce_positive_int(values.get("scan_limit"), "scan_limit"),
            descending=descending,
        )
    except ValueError as exc:
        raise EventSearchSyntaxError(str(exc)) from exc


def event_search_request_to_api_args(request: EventSearchRequest) -> list[str]:
    time_range = request.query.time_range
    if not time_range:
        raise ValueError("Event search request is missing a time range")
    begin = format_query_datetime(time_range.begin)
    end = format_query_datetime(time_range.end)
    if not (begin and end):
        raise ValueError("Event search request must include begin and end timestamps")

    args = [
        "--begin", begin,
        "--end", end,
        "--mode", request.mode,
        "--page", str(request.page),
        "--page-size", str(request.page_size),
        "--scan-limit", str(request.scan_limit),
    ]
    if not request.query.descending:
        args.append("--ascending")
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
    for value in request.query.taxonomy.categories:
        args.extend(["--category", value])
    for value in request.query.taxonomy.event_types:
        args.extend(["--event-type", value])
    for value in request.query.taxonomy.states:
        args.extend(["--state", value])
    for value in request.query.taxonomy.severities:
        args.extend(["--severity", value])
    for value in request.query.taxonomy.priorities:
        args.extend(["--priority", value])
    if request.query.text.contains:
        args.extend(["--contains", request.query.text.contains])
    if request.query.text.mask:
        args.extend(["--mask", request.query.text.mask])
    return args


def build_event_search_backend_request(
    request: EventSearchRequest,
    *,
    batch_size: int,
    offset: int,
    subject: str | None = None,
) -> dict[str, Any]:
    range_payload = request.query.time_range.as_axxon_range() if request.query.time_range else {}
    begin = range_payload.get("begin_time")
    end = range_payload.get("end_time")
    if not (begin and end):
        raise ValueError("Event search requires a bounded time range")

    if subject is None:
        if len(request.query.scope.camera_access_points) == 1:
            subject = request.query.scope.camera_access_points[0]
        elif len(request.query.scope.detector_access_points) == 1:
            subject = request.query.scope.detector_access_points[0]
        elif len(request.query.scope.subjects) == 1:
            subject = request.query.scope.subjects[0]

    event_type = None
    if len(request.query.taxonomy.event_types) == 1:
        event_type = request.query.taxonomy.event_types[0]
    elif not request.query.taxonomy.event_types and request.query.taxonomy.categories:
        categories = {value.casefold() for value in request.query.taxonomy.categories}
        if categories == {"alert"}:
            event_type = "ET_Alert"
        elif "alert" not in categories:
            event_type = "ET_DetectorEvent"

    limit = max(request.page_size, min(int(batch_size), request.scan_limit))
    return {
        "begin": begin,
        "end": end,
        "subject": subject,
        "event_type": event_type,
        "limit": limit,
        "offset": max(0, int(offset)),
        "descending": request.query.descending,
    }


def _coerce_search_card(row: Mapping[str, Any]) -> dict[str, Any]:
    if "timestamp" in row and "camera" in row and "event_type" in row:
        return dict(row)
    return normalize_event_card(dict(row))


def _card_sort_key(card: Mapping[str, Any]) -> tuple[str, str]:
    return (str(card.get("timestamp") or ""), str(card.get("id") or ""))


def _top_counter_rows(counter: Counter[str], limit: int = 3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for value, count in counter.most_common():
        if not str(value).strip():
            continue
        rows.append({"name": value, "count": count})
        if len(rows) >= limit:
            break
    return rows


def shape_event_search_results(
    rows: Iterable[Mapping[str, Any]],
    request: EventSearchRequest,
    *,
    scanned_count: int,
    complete: bool,
) -> dict[str, Any]:
    cards = [_coerce_search_card(row) for row in rows if isinstance(row, Mapping)]
    cards = [card for card in cards if request.query.matches_card(card)]
    cards.sort(key=_card_sort_key, reverse=request.query.descending)

    matched = len(cards)
    start = request.offset
    end = start + request.page_size
    page_items = cards[start:end]
    page_count = ceil(matched / request.page_size) if matched else 0

    by_category = Counter(str(card.get("category") or "other") for card in cards)
    by_camera = Counter(str(card.get("camera") or "Camera") for card in cards)
    by_detector = Counter(
        str(card.get("detector") or card.get("event_type") or "Detector")
        for card in cards
    )

    return {
        "request": {
            "mode": request.mode,
            "page": request.page,
            "page_size": request.page_size,
            "scan_limit": request.scan_limit,
            "descending": request.query.descending,
            "filters": request.query.to_legacy_filters(),
        },
        "summary": {
            "matched": matched,
            "scanned": scanned_count,
            "complete": bool(complete),
            "truncated": not bool(complete),
            "by_category": dict(sorted(by_category.items())),
            "top_cameras": _top_counter_rows(by_camera),
            "top_detectors": _top_counter_rows(by_detector),
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
    "DEFAULT_EVENT_SEARCH_PAGE_SIZE",
    "DEFAULT_EVENT_SEARCH_SCAN_LIMIT",
    "EVENT_SEARCH_MODES",
    "EventSearchRequest",
    "EventSearchSyntaxError",
    "build_event_search_backend_request",
    "build_event_search_request",
    "event_search_request_to_api_args",
    "parse_event_search_terms",
    "shape_event_search_results",
]
