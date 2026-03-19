"""Pure archive jump helpers for the Step 22 MVP."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from axxon_telegram_vms.models import (
    EventQuery,
    EventScopeFilter,
    EventTaxonomyFilter,
    EventTextFilter,
    EventTimeRange,
    format_query_datetime,
    normalize_event_card,
    parse_query_datetime,
)


DEFAULT_ARCHIVE_PREVIEW_WIDTH = 1280
DEFAULT_ARCHIVE_PREVIEW_HEIGHT = 720
DEFAULT_ARCHIVE_PREVIEW_THRESHOLD_MS = 250
DEFAULT_ARCHIVE_CONTEXT_WINDOW_SEC = 300
DEFAULT_ARCHIVE_SCAN_LIMIT = 400


class ArchiveJumpSyntaxError(ValueError):
    """Raised when a command-style archive jump request is malformed."""


def _coerce_positive_int(value: object, field_name: str) -> int:
    try:
        out = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if out <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return out


def _coerce_non_negative_int(value: object, field_name: str) -> int:
    try:
        out = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be zero or a positive integer") from exc
    if out < 0:
        raise ValueError(f"{field_name} must be zero or a positive integer")
    return out


def _split_csv_values(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    values = raw.split(",") if isinstance(raw, str) else raw
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


def _text(value: object) -> str:
    return str(value or "").strip()


def _normalized(value: object) -> str:
    return _text(value).casefold()


def _camera_name_variants(value: object) -> set[str]:
    text = _text(value)
    if not text:
        return set()
    variants = {_normalized(text)}
    if "." in text:
        variants.add(_normalized(text.split(".", 1)[1]))
    return {value for value in variants if value}


def _coerce_card(row: Mapping[str, Any]) -> dict[str, Any]:
    if "timestamp" in row and "camera" in row and "event_type" in row:
        return dict(row)
    return normalize_event_card(dict(row))


def _card_sort_key(card: Mapping[str, Any]) -> tuple[str, str]:
    return (str(card.get("timestamp") or ""), str(card.get("id") or ""))


def _camera_row_matches_name(row: Mapping[str, Any], camera_name: str) -> bool:
    expected = _camera_name_variants(camera_name)
    if not expected:
        return False
    actual = set()
    actual.update(_camera_name_variants(row.get("name")))
    actual.update(_camera_name_variants(row.get("display_name")))
    return bool(actual & expected)


def _resolve_explicit_camera_row(
    request: "ArchiveJumpRequest",
    camera_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any] | None:
    rows = [dict(row) for row in camera_rows if isinstance(row, Mapping)]
    access_points = request.query.scope.camera_access_points
    camera_names = request.query.scope.camera_names

    if len(access_points) > 1 or len(camera_names) > 1:
        raise ValueError("Archive jump MVP supports one camera at a time.")

    if access_points:
        camera_ap = access_points[0]
        for row in rows:
            if _normalized(row.get("access_point")) == _normalized(camera_ap):
                return row
        return {"name": camera_ap, "access_point": camera_ap}

    if camera_names:
        matches = [row for row in rows if _camera_row_matches_name(row, camera_names[0])]
        if len(matches) > 1:
            raise ValueError(f"Archive jump camera is ambiguous: {camera_names[0]}")
        if matches:
            return matches[0]
        raise ValueError(f"Archive jump camera not found: {camera_names[0]}")

    return None


def _matching_cards(
    request: "ArchiveJumpRequest",
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    cards = [_coerce_card(row) for row in rows if isinstance(row, Mapping)]
    cards = [card for card in cards if request.query.matches_card(card)]
    cards.sort(key=_card_sort_key, reverse=request.query.descending)
    return cards


@dataclass(frozen=True)
class ArchiveJumpRequest:
    query: EventQuery
    requested_timestamp: object | None = None
    scan_limit: int = DEFAULT_ARCHIVE_SCAN_LIMIT
    preview_width: int = DEFAULT_ARCHIVE_PREVIEW_WIDTH
    preview_height: int = DEFAULT_ARCHIVE_PREVIEW_HEIGHT
    preview_threshold_ms: int = DEFAULT_ARCHIVE_PREVIEW_THRESHOLD_MS
    context_window_sec: int = DEFAULT_ARCHIVE_CONTEXT_WINDOW_SEC

    def __post_init__(self) -> None:
        requested_timestamp = parse_query_datetime(self.requested_timestamp)
        scan_limit = _coerce_positive_int(self.scan_limit, "scan_limit")
        preview_width = _coerce_positive_int(self.preview_width, "preview_width")
        preview_height = _coerce_positive_int(self.preview_height, "preview_height")
        preview_threshold_ms = _coerce_non_negative_int(self.preview_threshold_ms, "preview_threshold_ms")
        context_window_sec = _coerce_positive_int(self.context_window_sec, "context_window_sec")
        time_range = self.query.time_range
        if not time_range or not time_range.is_bounded():
            raise ValueError("Archive jump requires a bounded time range")
        if requested_timestamp is not None and not time_range.contains(requested_timestamp):
            raise ValueError("requested_timestamp must fall inside the bounded archive range")
        object.__setattr__(self, "requested_timestamp", requested_timestamp)
        object.__setattr__(self, "scan_limit", scan_limit)
        object.__setattr__(self, "preview_width", preview_width)
        object.__setattr__(self, "preview_height", preview_height)
        object.__setattr__(self, "preview_threshold_ms", preview_threshold_ms)
        object.__setattr__(self, "context_window_sec", context_window_sec)

    @property
    def uses_exact_timestamp(self) -> bool:
        return self.requested_timestamp is not None


@dataclass(frozen=True)
class ArchiveJumpSelection:
    camera: str
    camera_access_point: str
    target_timestamp: str
    timestamp_source: str
    request_begin: str
    request_end: str
    context_begin: str
    context_end: str
    matched_count: int = 0
    matched_card: dict[str, Any] | None = None


def build_archive_jump_request(
    *,
    begin: object = None,
    end: object = None,
    at: object = None,
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
    scan_limit: int = DEFAULT_ARCHIVE_SCAN_LIMIT,
    preview_width: int = DEFAULT_ARCHIVE_PREVIEW_WIDTH,
    preview_height: int = DEFAULT_ARCHIVE_PREVIEW_HEIGHT,
    preview_threshold_ms: int = DEFAULT_ARCHIVE_PREVIEW_THRESHOLD_MS,
    context_window_sec: int = DEFAULT_ARCHIVE_CONTEXT_WINDOW_SEC,
    descending: bool = True,
) -> ArchiveJumpRequest:
    requested_timestamp = parse_query_datetime(at)
    if requested_timestamp is not None:
        if begin is None:
            begin = requested_timestamp
        if end is None:
            end = requested_timestamp
    time_range = EventTimeRange(begin=begin, end=end)
    if not time_range.is_bounded():
        raise ValueError("Archive jump requires at=... or both from=... and to=...")

    return ArchiveJumpRequest(
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
            taxonomy=EventTaxonomyFilter(
                categories=_split_csv_values(categories),
                event_types=_split_csv_values(event_types),
                states=_split_csv_values(states),
                severities=_split_csv_values(severities),
                priorities=_split_csv_values(priorities),
            ),
            text=EventTextFilter(
                contains=_text(contains),
                mask=_text(mask),
            ),
            descending=descending,
        ),
        requested_timestamp=requested_timestamp,
        scan_limit=scan_limit,
        preview_width=preview_width,
        preview_height=preview_height,
        preview_threshold_ms=preview_threshold_ms,
        context_window_sec=context_window_sec,
    )


_TERM_ALIASES = {
    "from": "begin",
    "begin": "begin",
    "start": "begin",
    "to": "end",
    "end": "end",
    "at": "at",
    "time": "at",
    "timestamp": "at",
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
    "category": "categories",
    "categories": "categories",
    "type": "event_types",
    "event_type": "event_types",
    "event_types": "event_types",
    "state": "states",
    "states": "states",
    "severity": "severities",
    "priority": "priorities",
    "contains": "contains",
    "text": "contains",
    "mask": "mask",
    "scan_limit": "scan_limit",
    "sort": "sort",
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


def parse_archive_jump_terms(
    terms: Iterable[object],
    *,
    default_scan_limit: int = DEFAULT_ARCHIVE_SCAN_LIMIT,
) -> ArchiveJumpRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise ArchiveJumpSyntaxError("Archive jump requires key=value terms.")

    values: dict[str, Any] = {"scan_limit": default_scan_limit}
    if all("=" not in term for term in raw_terms):
        if len(raw_terms) >= 3:
            candidate_time = f"{raw_terms[-2]} {raw_terms[-1]}"
            try:
                parse_query_datetime(candidate_time)
            except ValueError as exc:
                raise ArchiveJumpSyntaxError(
                    "Use at=... or both from=... and to=..., or shorthand like: /archive Gate 12:00:00 12-03-2026"
                ) from exc
            camera_name = " ".join(raw_terms[:-2]).strip()
            if not camera_name:
                raise ArchiveJumpSyntaxError("Archive camera name is required before the date/time shorthand")
            values["camera_names"] = [camera_name]
            values["at"] = candidate_time
        else:
            raise ArchiveJumpSyntaxError(
                "Use at=... or both from=... and to=..., or shorthand like: /archive Gate 12:00:00 12-03-2026"
            )
    else:
        for term in raw_terms:
            if "=" not in term:
                raise ArchiveJumpSyntaxError(f"Unsupported archive term: {term}")
            raw_key, raw_value = term.split("=", 1)
            key = _TERM_ALIASES.get(raw_key.strip().lower())
            if not key:
                raise ArchiveJumpSyntaxError(f"Unsupported archive key: {raw_key}")
            value = raw_value.strip()
            if not value:
                raise ArchiveJumpSyntaxError(f"Archive value is required for: {raw_key}")
            if key in _MULTI_VALUE_TERMS:
                existing = list(values.get(key) or [])
                existing.extend(_split_csv_values(value))
                values[key] = existing
            else:
                values[key] = value

    if not values.get("at") and not (values.get("begin") and values.get("end")):
        raise ArchiveJumpSyntaxError("Use at=... or both from=... and to=...")

    descending = _coerce_descending(sort=values.get("sort"))
    try:
        return build_archive_jump_request(
            begin=values.get("begin"),
            end=values.get("end"),
            at=values.get("at"),
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
            scan_limit=_coerce_positive_int(values.get("scan_limit"), "scan_limit"),
            descending=descending,
        )
    except ValueError as exc:
        raise ArchiveJumpSyntaxError(str(exc)) from exc


def archive_jump_request_to_api_args(request: ArchiveJumpRequest) -> list[str]:
    time_range = request.query.time_range
    begin = format_query_datetime(time_range.begin if time_range else None)
    end = format_query_datetime(time_range.end if time_range else None)
    if not (begin and end):
        raise ValueError("Archive jump request must include begin and end timestamps")

    args = [
        "--begin", begin,
        "--end", end,
        "--scan-limit", str(request.scan_limit),
        "--preview-width", str(request.preview_width),
        "--preview-height", str(request.preview_height),
        "--preview-threshold-ms", str(request.preview_threshold_ms),
        "--context-window-sec", str(request.context_window_sec),
    ]
    if request.requested_timestamp is not None:
        args.extend(["--at", format_query_datetime(request.requested_timestamp)])
    if not request.query.descending:
        args.append("--ascending")
    for value in request.query.scope.hosts:
        args.extend(["--scope-host", value])
    for value in request.query.scope.domains:
        args.extend(["--domain", value])
    if request.query.scope.camera_access_points:
        for value in request.query.scope.camera_access_points:
            args.extend(["--camera-ap", value])
    else:
        for value in request.query.scope.camera_names:
            args.extend(["--camera", value])
    if request.query.scope.detector_access_points:
        for value in request.query.scope.detector_access_points:
            args.extend(["--detector-ap", value])
    else:
        for value in request.query.scope.detector_names:
            args.extend(["--detector", value])
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


def derive_archive_jump_selection(
    request: ArchiveJumpRequest,
    rows: Iterable[Mapping[str, Any]],
    camera_rows: Iterable[Mapping[str, Any]],
) -> ArchiveJumpSelection:
    explicit_camera = _resolve_explicit_camera_row(request, camera_rows)
    cards = _matching_cards(request, rows)
    matched_card = dict(cards[0]) if cards else None
    matched_count = len(cards)

    camera: dict[str, Any] | None = explicit_camera
    if camera is None and matched_card is not None:
        camera_ap = _text(matched_card.get("camera_access_point"))
        if camera_ap:
            camera = {
                "name": _text(matched_card.get("camera")) or camera_ap,
                "access_point": camera_ap,
            }
        else:
            unique_camera_rows = {
                _text(card.get("camera")): card
                for card in cards
                if _text(card.get("camera"))
            }
            if len(unique_camera_rows) == 1:
                only = next(iter(unique_camera_rows.values()))
                camera = {
                    "name": _text(only.get("camera")),
                    "access_point": _text(only.get("camera_access_point")),
                }

    if camera is None:
        raise ValueError("Archive jump needs a single camera context; add camera=... or narrow the search.")

    camera_name = _text(camera.get("name") or camera.get("camera") or camera.get("access_point"))
    camera_access_point = _text(camera.get("access_point") or camera.get("camera_access_point"))
    if not camera_access_point:
        raise ValueError("Archive jump camera context is missing camera_access_point.")

    if request.requested_timestamp is not None:
        target_dt = request.requested_timestamp
        timestamp_source = "explicit"
    elif matched_card is not None and matched_card.get("timestamp"):
        target_dt = parse_query_datetime(matched_card.get("timestamp"))
        timestamp_source = "matching_event"
    else:
        time_range = request.query.time_range
        if not time_range or not (time_range.begin and time_range.end):
            raise ValueError("Archive jump could not derive a timestamp from the request range.")
        midpoint = time_range.begin + ((time_range.end - time_range.begin) / 2)
        target_dt = midpoint
        timestamp_source = "range_midpoint"

    if target_dt is None:
        raise ValueError("Archive jump could not resolve a target timestamp.")

    context_delta = timedelta(seconds=request.context_window_sec)
    context_begin = format_query_datetime(target_dt - context_delta) or ""
    context_end = format_query_datetime(target_dt + context_delta) or ""
    request_begin = format_query_datetime(request.query.time_range.begin if request.query.time_range else None) or ""
    request_end = format_query_datetime(request.query.time_range.end if request.query.time_range else None) or ""

    return ArchiveJumpSelection(
        camera=camera_name or camera_access_point,
        camera_access_point=camera_access_point,
        target_timestamp=format_query_datetime(target_dt) or "",
        timestamp_source=timestamp_source,
        request_begin=request_begin,
        request_end=request_end,
        context_begin=context_begin,
        context_end=context_end,
        matched_count=matched_count,
        matched_card=matched_card,
    )


def _interval_contains(interval: Mapping[str, Any], timestamp: str) -> bool:
    begin = parse_query_datetime(interval.get("begin"))
    end = parse_query_datetime(interval.get("end"))
    point = parse_query_datetime(timestamp)
    if point is None or begin is None or end is None:
        return False
    return begin <= point <= end


def shape_archive_jump_result(
    request: ArchiveJumpRequest,
    selection: ArchiveJumpSelection,
    *,
    preview_path: str | None = None,
    preview_error: str | None = None,
    preview_mode: str = "",
    archives: Iterable[Mapping[str, Any]] = (),
    depth: Mapping[str, Any] | None = None,
    intervals: Iterable[Mapping[str, Any]] = (),
    intervals_more: bool = False,
    errors: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    archive_rows = [dict(row) for row in archives if isinstance(row, Mapping)]
    interval_rows = [dict(row) for row in intervals if isinstance(row, Mapping)]
    containing_interval = next(
        (interval for interval in interval_rows if _interval_contains(interval, selection.target_timestamp)),
        None,
    )
    default_archive = next(
        (_text(row.get("name")) for row in archive_rows if row.get("default")),
        "",
    )

    return {
        "request": {
            "filters": request.query.to_legacy_filters(),
            "requested_timestamp": format_query_datetime(request.requested_timestamp),
            "scan_limit": request.scan_limit,
            "preview_width": request.preview_width,
            "preview_height": request.preview_height,
            "preview_threshold_ms": request.preview_threshold_ms,
            "context_window_sec": request.context_window_sec,
        },
        "selection": {
            "camera": selection.camera,
            "camera_access_point": selection.camera_access_point,
            "video_id": selection.camera_access_point.removeprefix("hosts/"),
            "timestamp": selection.target_timestamp,
            "timestamp_source": selection.timestamp_source,
            "request_begin": selection.request_begin,
            "request_end": selection.request_end,
            "context_begin": selection.context_begin,
            "context_end": selection.context_end,
            "matched_count": selection.matched_count,
            "matched_event": selection.matched_card,
        },
        "archive": {
            "archives": archive_rows,
            "default_archive": default_archive or None,
            "depth": dict(depth) if isinstance(depth, Mapping) else None,
            "intervals": interval_rows,
            "intervals_more": bool(intervals_more),
            "in_archive": containing_interval is not None,
            "context_handle": {
                "camera_access_point": selection.camera_access_point,
                "video_id": selection.camera_access_point.removeprefix("hosts/"),
                "timestamp": selection.target_timestamp,
                "request_begin": selection.request_begin,
                "request_end": selection.request_end,
                "interval_begin": _text((containing_interval or {}).get("begin")) or None,
                "interval_end": _text((containing_interval or {}).get("end")) or None,
                "archive": default_archive or None,
            },
            "errors": [dict(error) for error in errors if isinstance(error, Mapping)],
        },
        "preview": {
            "ok": bool(preview_path),
            "path": _text(preview_path) or None,
            "error": _text(preview_error) or None,
            "mode": _text(preview_mode) or None,
            "width": request.preview_width,
            "height": request.preview_height,
            "threshold_ms": request.preview_threshold_ms,
        },
    }


__all__ = [
    "ArchiveJumpRequest",
    "ArchiveJumpSelection",
    "ArchiveJumpSyntaxError",
    "DEFAULT_ARCHIVE_CONTEXT_WINDOW_SEC",
    "DEFAULT_ARCHIVE_PREVIEW_HEIGHT",
    "DEFAULT_ARCHIVE_PREVIEW_THRESHOLD_MS",
    "DEFAULT_ARCHIVE_PREVIEW_WIDTH",
    "DEFAULT_ARCHIVE_SCAN_LIMIT",
    "archive_jump_request_to_api_args",
    "build_archive_jump_request",
    "derive_archive_jump_selection",
    "parse_archive_jump_terms",
    "shape_archive_jump_result",
]
