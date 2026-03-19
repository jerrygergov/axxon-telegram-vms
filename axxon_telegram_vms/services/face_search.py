"""Pure face-search helpers for the Step 26 MVP."""

from __future__ import annotations

import base64
import hashlib
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import ceil
from pathlib import Path
from typing import Any

from axxon_telegram_vms.models import (
    EventQuery,
    EventScopeFilter,
    EventTimeRange,
    format_query_datetime,
    normalize_event_card,
    parse_query_datetime,
)


DEFAULT_FACE_SEARCH_WINDOW_SEC = 3600
DEFAULT_FACE_SEARCH_PAGE_SIZE = 10
MAX_FACE_SEARCH_PAGE_SIZE = 10
DEFAULT_FACE_SEARCH_SCAN_LIMIT = 10
DEFAULT_FACE_SEARCH_ACCURACY = 0.9
DEFAULT_FACE_SEARCH_MAX_CAMERAS = 24
DEFAULT_FACE_SEARCH_EXPORT_PADDING_SEC = 15
DEFAULT_FACE_SEARCH_MAX_IMAGE_BYTES = 5 * 1024 * 1024
DEFAULT_FACE_SEARCH_MAX_EDGE_PX = 640
DEFAULT_FACE_SEARCH_JPEG_QSCALE = 6
FACE_SEARCH_TRANSPORT = "grpc:axxonsoft.bl.events.EventHistoryService.FindSimilarObjects"
_FACE_LABEL_RE = re.compile(r"\bface\b", flags=re.IGNORECASE)


class FaceSearchSyntaxError(ValueError):
    """Raised when a command-style face-search request is malformed."""


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


def _coerce_accuracy(value: object) -> float:
    try:
        out = float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("accuracy must be a number in the [0, 1] range") from exc
    if out < 0.0 or out > 1.0:
        raise ValueError("accuracy must be a number in the [0, 1] range")
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


def _string_events(raw: object) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    values = raw if isinstance(raw, Iterable) and not isinstance(raw, (str, bytes, bytearray)) else (raw,)
    for value in values:
        if isinstance(value, Mapping):
            text = _text(value.get("id") or value.get("name"))
        else:
            text = _text(value)
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return tuple(out)


def _looks_like_face_detector(
    *,
    detector_name: object = "",
    detector_type_name: object = "",
    detector_type: object = "",
    events: Iterable[object] = (),
) -> bool:
    if any(_normalized(event) == "faceappeared" for event in events):
        return True
    text = " ".join(
        part for part in (_text(detector_name), _text(detector_type_name), _text(detector_type)) if part
    )
    return bool(text and _FACE_LABEL_RE.search(text))


def _card_sort_key(card: Mapping[str, Any]) -> tuple[float, str, str]:
    similarity = card.get("similarity")
    try:
        score = float(similarity)
    except (TypeError, ValueError):
        score = -1.0
    return (score, str(card.get("timestamp") or ""), str(card.get("id") or ""))


def _coerce_similarity(value: object) -> float | None:
    try:
        similarity = float(value)
    except (TypeError, ValueError):
        return None
    if similarity < 0.0:
        return None
    if similarity > 1.0 and similarity <= 100.0:
        similarity = similarity / 100.0
    if similarity > 1.0:
        return None
    return similarity


@dataclass(frozen=True)
class FaceSearchRequest:
    query: EventQuery
    accuracy: float = DEFAULT_FACE_SEARCH_ACCURACY
    page: int = 1
    page_size: int = DEFAULT_FACE_SEARCH_PAGE_SIZE
    scan_limit: int = DEFAULT_FACE_SEARCH_SCAN_LIMIT
    time_source: str = "explicit"
    window_seconds: int = DEFAULT_FACE_SEARCH_WINDOW_SEC

    def __post_init__(self) -> None:
        accuracy = _coerce_accuracy(self.accuracy)
        page = _coerce_positive_int(self.page, "page")
        page_size = min(MAX_FACE_SEARCH_PAGE_SIZE, _coerce_positive_int(self.page_size, "page_size"))
        scan_limit = max(page_size, _coerce_positive_int(self.scan_limit, "scan_limit"))
        time_source = _text(self.time_source).lower() or "explicit"
        if time_source not in {"explicit", "window"}:
            raise ValueError(f"Unsupported face search time_source: {self.time_source}")
        window_seconds = _coerce_positive_int(self.window_seconds, "window_seconds")
        if not self.query.time_range or not self.query.time_range.is_bounded():
            raise ValueError("Face search requires a bounded time range")
        object.__setattr__(self, "accuracy", accuracy)
        object.__setattr__(self, "page", page)
        object.__setattr__(self, "page_size", page_size)
        object.__setattr__(self, "scan_limit", scan_limit)
        object.__setattr__(self, "time_source", time_source)
        object.__setattr__(self, "window_seconds", window_seconds)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True)
class FaceSearchReferenceImage:
    file_name: str
    size_bytes: int
    sha256: str
    jpeg_base64: str

    def as_legacy_dict(self) -> dict[str, Any]:
        return {
            "file_name": self.file_name,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "media_type": "image/jpeg",
        }


@dataclass(frozen=True)
class FaceSearchTarget:
    camera_name: str
    camera_access_point: str
    detector_name: str
    detector_access_point: str
    detector_type_name: str = ""
    events: tuple[str, ...] = ()

    @classmethod
    def from_detector_row(cls, row: Mapping[str, Any]) -> "FaceSearchTarget | None":
        detector_access_point = _text(row.get("detector_access_point") or row.get("access_point"))
        camera_access_point = _text(row.get("camera_access_point"))
        if not detector_access_point or not camera_access_point:
            return None
        detector_name = _text(row.get("detector_name") or row.get("name")) or "Detector"
        detector_type_name = _text(row.get("detector_type_name") or row.get("detector_type"))
        events = _string_events(row.get("events"))
        if not _looks_like_face_detector(
            detector_name=detector_name,
            detector_type_name=detector_type_name,
            detector_type=row.get("detector_type"),
            events=events,
        ):
            return None
        return cls(
            camera_name=_text(row.get("camera_name")) or "Camera",
            camera_access_point=camera_access_point,
            detector_name=detector_name,
            detector_access_point=detector_access_point,
            detector_type_name=detector_type_name,
            events=events,
        )

    def as_scope_card(self) -> dict[str, Any]:
        return {
            "camera": self.camera_name,
            "camera_access_point": self.camera_access_point,
            "detector": self.detector_name,
            "detector_access_point": self.detector_access_point,
            "subject": self.detector_access_point,
        }

    def as_legacy_dict(self) -> dict[str, Any]:
        return {
            "camera": self.camera_name,
            "camera_access_point": self.camera_access_point,
            "detector": self.detector_name,
            "detector_access_point": self.detector_access_point,
            "detector_type_name": self.detector_type_name,
            "events": list(self.events),
        }


@dataclass(frozen=True)
class FaceSearchCapability:
    available: bool
    detector_count: int
    camera_count: int
    transport: str = FACE_SEARCH_TRANSPORT

    def as_legacy_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "detector_count": self.detector_count,
            "camera_count": self.camera_count,
            "transport": self.transport,
        }


@dataclass(frozen=True)
class FaceSearchSelection:
    capability: FaceSearchCapability
    targets: tuple[FaceSearchTarget, ...] = ()
    error: str | None = None
    max_cameras: int = DEFAULT_FACE_SEARCH_MAX_CAMERAS

    @property
    def searchable(self) -> bool:
        return self.capability.available and not _text(self.error) and bool(self.camera_access_points)

    @property
    def camera_access_points(self) -> tuple[str, ...]:
        out: list[str] = []
        seen: set[str] = set()
        for target in self.targets:
            key = target.camera_access_point.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(target.camera_access_point)
        return tuple(out)

    @property
    def camera_count(self) -> int:
        return len(self.camera_access_points)

    @property
    def detector_count(self) -> int:
        return len(self.targets)

    def as_legacy_dict(self) -> dict[str, Any]:
        return {
            "searchable": self.searchable,
            "error": self.error,
            "camera_count": self.camera_count,
            "detector_count": self.detector_count,
            "max_cameras": self.max_cameras,
            "cameras": [
                {"name": target.camera_name, "access_point": target.camera_access_point}
                for target in self.targets[: self.max_cameras]
            ],
            "detectors": [target.as_legacy_dict() for target in self.targets[: self.max_cameras]],
        }


def build_face_search_request(
    *,
    begin: object = None,
    end: object = None,
    last_sec: int = DEFAULT_FACE_SEARCH_WINDOW_SEC,
    accuracy: float = DEFAULT_FACE_SEARCH_ACCURACY,
    now_provider: Callable[[], datetime] = _utc_now,
    hosts: Iterable[object] = (),
    domains: Iterable[object] = (),
    camera_names: Iterable[object] = (),
    camera_access_points: Iterable[object] = (),
    detector_names: Iterable[object] = (),
    detector_access_points: Iterable[object] = (),
    page: int = 1,
    page_size: int = DEFAULT_FACE_SEARCH_PAGE_SIZE,
    scan_limit: int = DEFAULT_FACE_SEARCH_SCAN_LIMIT,
) -> FaceSearchRequest:
    explicit_begin = begin is not None and _text(begin)
    explicit_end = end is not None and _text(end)
    if explicit_begin or explicit_end:
        if not (explicit_begin and explicit_end):
            raise ValueError("Use both from=... and to=... for an explicit face-search range.")
        if last_sec != DEFAULT_FACE_SEARCH_WINDOW_SEC:
            raise ValueError("Use either from/to or last=..., not both.")
        time_range = EventTimeRange(begin=begin, end=end)
        time_source = "explicit"
        window_seconds = DEFAULT_FACE_SEARCH_WINDOW_SEC
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

    return FaceSearchRequest(
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
        ),
        accuracy=accuracy,
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
    "accuracy": "accuracy",
    "score": "accuracy",
    "similarity": "accuracy",
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
}
_MULTI_VALUE_TERMS = {
    "hosts",
    "domains",
    "camera_names",
    "camera_access_points",
    "detector_names",
    "detector_access_points",
}


def parse_face_search_terms(
    terms: Iterable[object],
    *,
    now_provider: Callable[[], datetime] = _utc_now,
    default_window_sec: int = DEFAULT_FACE_SEARCH_WINDOW_SEC,
    default_page_size: int = DEFAULT_FACE_SEARCH_PAGE_SIZE,
    default_scan_limit: int = DEFAULT_FACE_SEARCH_SCAN_LIMIT,
    default_accuracy: float = DEFAULT_FACE_SEARCH_ACCURACY,
) -> FaceSearchRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    values: dict[str, Any] = {
        "last_sec": default_window_sec,
        "page": 1,
        "page_size": default_page_size,
        "scan_limit": default_scan_limit,
        "accuracy": default_accuracy,
    }
    explicit_range_keys: set[str] = set()
    for term in raw_terms:
        if "=" not in term:
            raise FaceSearchSyntaxError(f"Unsupported face-search term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise FaceSearchSyntaxError(f"Unsupported face-search key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise FaceSearchSyntaxError(f"Face-search value is required for: {raw_key}")
        if key in {"begin", "end"}:
            explicit_range_keys.add(key)
        if key == "last_sec" and explicit_range_keys:
            raise FaceSearchSyntaxError("Use either from/to or last=..., not both.")
        if key in _MULTI_VALUE_TERMS:
            existing = list(values.get(key) or [])
            existing.extend(_split_csv_values(value))
            values[key] = existing
        else:
            values[key] = value

    try:
        return build_face_search_request(
            begin=values.get("begin"),
            end=values.get("end"),
            last_sec=_coerce_positive_int(values.get("last_sec"), "last_sec"),
            accuracy=_coerce_accuracy(values.get("accuracy")),
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
        )
    except ValueError as exc:
        raise FaceSearchSyntaxError(str(exc)) from exc


def face_search_request_to_api_args(request: FaceSearchRequest, *, image_path: object) -> list[str]:
    time_range = request.query.time_range
    begin = format_query_datetime(time_range.begin if time_range else None)
    end = format_query_datetime(time_range.end if time_range else None)
    if not (begin and end):
        raise ValueError("Face-search request must include begin and end timestamps")

    image = _text(image_path)
    if not image:
        raise ValueError("Face-search request requires a reference image path")

    args = [
        "--image", image,
        "--begin", begin,
        "--end", end,
        "--page", str(request.page),
        "--page-size", str(request.page_size),
        "--scan-limit", str(request.scan_limit),
        "--accuracy", f"{request.accuracy:.6f}",
    ]
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
    return args


def _prepare_face_search_jpeg(path: Path) -> bytes:
    raw = path.read_bytes()
    if not raw:
        raise ValueError("Face search reference image is empty.")
    if not raw.startswith(b"\xff\xd8\xff"):
        raise ValueError("Face search currently requires a JPEG reference image. Send a Telegram photo or a .jpg file.")
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        return raw
    with tempfile.TemporaryDirectory(prefix="face-search-") as tmpdir:
        out_path = Path(tmpdir) / "prepared.jpg"
        try:
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    str(path),
                    "-vf",
                    f"scale='min({DEFAULT_FACE_SEARCH_MAX_EDGE_PX},iw)':-2",
                    "-q:v",
                    str(DEFAULT_FACE_SEARCH_JPEG_QSCALE),
                    str(out_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            prepared = out_path.read_bytes()
            if prepared.startswith(b"\xff\xd8\xff") and prepared:
                return prepared
        except Exception:
            pass
    return raw


def load_face_search_reference_image(
    image_path: object,
    *,
    max_bytes: int = DEFAULT_FACE_SEARCH_MAX_IMAGE_BYTES,
) -> FaceSearchReferenceImage:
    path = Path(_text(image_path))
    if not path.exists() or not path.is_file():
        raise ValueError("Face search requires a readable JPEG reference image.")
    raw = _prepare_face_search_jpeg(path)
    if len(raw) > max_bytes:
        raise ValueError(f"Face search reference image exceeds the {max_bytes} byte safety cap.")
    return FaceSearchReferenceImage(
        file_name=path.name or "reference.jpg",
        size_bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        jpeg_base64=base64.b64encode(raw).decode("ascii"),
    )


def _face_targets_from_rows(detector_rows: Iterable[Mapping[str, Any]]) -> tuple[FaceSearchTarget, ...]:
    out: list[FaceSearchTarget] = []
    seen: set[str] = set()
    for row in detector_rows or ():
        if not isinstance(row, Mapping):
            continue
        target = FaceSearchTarget.from_detector_row(row)
        if target is None:
            continue
        key = target.detector_access_point.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(target)
    out.sort(key=lambda item: (item.camera_name.casefold(), item.detector_name.casefold(), item.detector_access_point.casefold()))
    return tuple(out)


def detect_face_search_capability(detector_rows: Iterable[Mapping[str, Any]]) -> FaceSearchCapability:
    targets = _face_targets_from_rows(detector_rows)
    cameras = {target.camera_access_point.casefold() for target in targets}
    return FaceSearchCapability(
        available=bool(targets),
        detector_count=len(targets),
        camera_count=len(cameras),
    )


def resolve_face_search_selection(
    request: FaceSearchRequest,
    detector_rows: Iterable[Mapping[str, Any]],
    *,
    max_cameras: int = DEFAULT_FACE_SEARCH_MAX_CAMERAS,
) -> FaceSearchSelection:
    all_targets = _face_targets_from_rows(detector_rows)
    capability = FaceSearchCapability(
        available=bool(all_targets),
        detector_count=len(all_targets),
        camera_count=len({target.camera_access_point.casefold() for target in all_targets}),
    )
    matched_targets = tuple(target for target in all_targets if request.query.scope.matches_card(target.as_scope_card()))
    error = None
    if not capability.available:
        error = "Face search is unavailable: no face-capable detectors are exposed by the current inventory."
    elif not matched_targets:
        error = "No face-capable detectors match the requested scope."
    else:
        camera_count = len({target.camera_access_point.casefold() for target in matched_targets})
        if camera_count > max_cameras:
            error = (
                f"Face search would scan {camera_count} cameras, above the safe MVP cap of {max_cameras}. "
                "Narrow the scope before running a broad forensic search."
            )
    return FaceSearchSelection(
        capability=capability,
        targets=matched_targets,
        error=error,
        max_cameras=max_cameras,
    )


def build_face_search_backend_request(
    request: FaceSearchRequest,
    selection: FaceSearchSelection,
    reference_image: FaceSearchReferenceImage,
) -> dict[str, Any]:
    if not selection.searchable:
        raise ValueError(selection.error or "Face-search selection is not searchable.")
    range_payload = request.query.time_range.as_axxon_range() if request.query.time_range else {}
    begin = range_payload.get("begin_time")
    end = range_payload.get("end_time")
    if not (begin and end):
        raise ValueError("Face-search request requires a bounded time range")
    return {
        "session": 0,
        "is_face": True,
        "minimal_score": request.accuracy,
        "jpeg_image": reference_image.jpeg_base64,
        "range": {
            "begin_time": begin,
            "end_time": end,
        },
        "origin_ids": list(selection.camera_access_points),
        "limit": request.scan_limit,
        "offset": 0,
    }


def _build_face_action_commands(card: Mapping[str, Any]) -> tuple[str | None, str | None]:
    camera_access_point = _text(card.get("camera_access_point"))
    timestamp = parse_query_datetime(card.get("timestamp"))
    if not camera_access_point or timestamp is None:
        return None, None
    at = format_query_datetime(timestamp)
    begin = format_query_datetime(timestamp - timedelta(seconds=DEFAULT_FACE_SEARCH_EXPORT_PADDING_SEC))
    end = format_query_datetime(timestamp + timedelta(seconds=DEFAULT_FACE_SEARCH_EXPORT_PADDING_SEC))
    archive_command = f"/archive camera_ap={camera_access_point} at={at}" if at else None
    export_command = (
        f"/export from={begin} to={end} camera_ap={camera_access_point}"
        if begin and end
        else None
    )
    return archive_command, export_command


def _coerce_face_search_card(row: Mapping[str, Any]) -> dict[str, Any] | None:
    event: Mapping[str, Any] | None = None
    if "timestamp" in row and "camera" in row and "event_type" in row:
        card = dict(row)
    else:
        event = row.get("event") if isinstance(row.get("event"), Mapping) else None
        if not isinstance(event, Mapping):
            return None
        body = event.get("body") if isinstance(event.get("body"), Mapping) else event
        origin_ext = body.get("origin_ext") if isinstance(body.get("origin_ext"), Mapping) else {}
        detector_ext = body.get("detector_ext") if isinstance(body.get("detector_ext"), Mapping) else {}
        card = {
            "id": _text(body.get("guid")),
            "timestamp": _text(body.get("timestamp")),
            "event_type": _text(body.get("event_type") or event.get("event_type")) or "faceAppeared",
            "state": _text(body.get("state")) or "SPECIFIED",
            "camera": _text(origin_ext.get("friendly_name")) or "Camera",
            "camera_access_point": _text(origin_ext.get("access_point") or body.get("origin_deprecated") or event.get("origin_deprecated")),
            "detector": _text(detector_ext.get("friendly_name")) or "Detector",
            "detector_access_point": _text(detector_ext.get("access_point") or body.get("detector_deprecated") or event.get("detector_deprecated")),
            "text": _text(body.get("event_type") or event.get("event_type")) or "faceAppeared",
            "raw_event": dict(body),
        }
    raw_event = card.get("raw_event")
    card.pop("raw_event", None)
    if isinstance(event, Mapping):
        card["event_guid"] = _text(event.get("guid") or card.get("id"))
        card["event_timestamp"] = _text(event.get("timestamp") or card.get("timestamp"))
        card["raw_event"] = dict(event)
    elif raw_event is not None:
        card["raw_event"] = raw_event
    similarity = _coerce_similarity(row.get("score"))
    if similarity is None:
        similarity = _coerce_similarity(row.get("accuracy"))
    if similarity is not None:
        card["similarity"] = similarity
    archive_command, export_command = _build_face_action_commands(card)
    if archive_command:
        card["archive_command"] = archive_command
    if export_command:
        card["export_command"] = export_command
    return card


def shape_face_search_results(
    rows: Iterable[Mapping[str, Any]],
    request: FaceSearchRequest,
    selection: FaceSearchSelection,
    reference_image: FaceSearchReferenceImage | None,
    *,
    scanned_count: int,
    complete: bool,
    error: str | None = None,
) -> dict[str, Any]:
    cards: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        card = _coerce_face_search_card(row)
        if card is None:
            continue
        if not request.query.matches_card(card):
            continue
        cards.append(card)

    cards.sort(key=_card_sort_key, reverse=True)
    matched = len(cards)
    start = request.offset
    end = start + request.page_size
    page_items = cards[start:end]
    page_count = ceil(matched / request.page_size) if matched else 0

    by_camera = Counter(str(card.get("camera") or "Camera") for card in cards)
    by_detector = Counter(str(card.get("detector") or "Detector") for card in cards)
    best_similarity = max((_coerce_similarity(card.get("similarity")) or 0.0 for card in cards), default=0.0)

    return {
        "request": {
            "page": request.page,
            "page_size": request.page_size,
            "scan_limit": request.scan_limit,
            "accuracy": request.accuracy,
            "filters": request.query.to_legacy_filters(),
            "time_source": request.time_source,
            "window_seconds": request.window_seconds,
        },
        "capability": selection.capability.as_legacy_dict(),
        "selection": selection.as_legacy_dict(),
        "reference_image": reference_image.as_legacy_dict() if reference_image is not None else None,
        "summary": {
            "matched": matched,
            "scanned": scanned_count,
            "complete": bool(complete),
            "truncated": not bool(complete),
            "best_similarity": best_similarity,
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
        "error": _text(error) or selection.error,
    }


__all__ = [
    "DEFAULT_FACE_SEARCH_ACCURACY",
    "DEFAULT_FACE_SEARCH_EXPORT_PADDING_SEC",
    "DEFAULT_FACE_SEARCH_MAX_CAMERAS",
    "DEFAULT_FACE_SEARCH_MAX_IMAGE_BYTES",
    "DEFAULT_FACE_SEARCH_PAGE_SIZE",
    "DEFAULT_FACE_SEARCH_SCAN_LIMIT",
    "DEFAULT_FACE_SEARCH_WINDOW_SEC",
    "FACE_SEARCH_TRANSPORT",
    "FaceSearchCapability",
    "FaceSearchReferenceImage",
    "FaceSearchRequest",
    "FaceSearchSelection",
    "FaceSearchSyntaxError",
    "FaceSearchTarget",
    "build_face_search_backend_request",
    "build_face_search_request",
    "detect_face_search_capability",
    "face_search_request_to_api_args",
    "load_face_search_reference_image",
    "parse_face_search_terms",
    "resolve_face_search_selection",
    "shape_face_search_results",
]
