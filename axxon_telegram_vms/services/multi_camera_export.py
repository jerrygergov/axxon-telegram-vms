"""Pure multi-camera export planning helpers for the Step 24 MVP."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from axxon_telegram_vms.models import EventQuery, EventScopeFilter, EventTimeRange, format_query_datetime

from .single_camera_export import (
    DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
    SINGLE_CAMERA_EXPORT_FORMAT,
    build_single_camera_export_request,
    resolve_single_camera_export_selection,
)


DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS = DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS
DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS = 4
MULTI_CAMERA_EXPORT_IMAGE_FORMAT = "jpg"
MULTI_CAMERA_EXPORT_STRATEGY = "per_camera_exports"


class MultiCameraExportSyntaxError(ValueError):
    """Raised when a command-style multi-camera export request is malformed."""


def _coerce_positive_int(value: object, field_name: str) -> int:
    try:
        out = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if out <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return out


def _text(value: object) -> str:
    return str(value or "").strip()


def _normalized(value: object) -> str:
    return _text(value).casefold()


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


def _status_file_name(status: Mapping[str, Any] | None) -> str | None:
    if not isinstance(status, Mapping):
        return None
    files = status.get("filesFriendly")
    if isinstance(files, list):
        for value in files:
            text = _text(value)
            if text:
                return text
    files = status.get("files")
    if isinstance(files, list):
        for value in files:
            text = _text(value)
            if text:
                return text
    return None


def _export_state(
    *,
    artifact_path: str | None,
    error: str | None,
    export_status: Mapping[str, Any] | None,
) -> str:
    if artifact_path:
        return "ready"
    if error:
        return "failed"
    try:
        status_state = int((export_status or {}).get("state"))
    except (TypeError, ValueError):
        status_state = None
    if status_state in {3, 4, 5, 6}:
        return "failed"
    if status_state == 2:
        return "server_ready"
    if status_state == 1:
        return "in_progress"
    return "planned"


@dataclass(frozen=True)
class MultiCameraExportRequest:
    query: EventQuery
    waittimeout_ms: int = DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS
    archive_name: str | None = None
    max_cameras: int = DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS

    def __post_init__(self) -> None:
        time_range = self.query.time_range
        waittimeout_ms = _coerce_positive_int(self.waittimeout_ms, "waittimeout_ms")
        max_cameras = _coerce_positive_int(self.max_cameras, "max_cameras")
        archive_name = _text(self.archive_name) or None
        scope = self.query.scope
        camera_count = len(scope.camera_names) + len(scope.camera_access_points)
        if camera_count < 2:
            raise ValueError("Multi-camera export MVP requires at least two camera selectors.")
        if max_cameras < 2:
            raise ValueError("max_cameras must be at least 2 for multi-camera export.")
        if not time_range or not time_range.is_bounded():
            raise ValueError("Multi-camera export requires a bounded time range.")
        if scope.detector_names or scope.detector_access_points:
            raise ValueError("Multi-camera export MVP only accepts explicit camera selectors.")
        if not self.query.taxonomy.is_empty():
            raise ValueError("Multi-camera export MVP does not yet support taxonomy filters.")
        if not self.query.text.is_empty():
            raise ValueError("Multi-camera export MVP does not yet support text filters.")
        object.__setattr__(self, "waittimeout_ms", waittimeout_ms)
        object.__setattr__(self, "archive_name", archive_name)
        object.__setattr__(self, "max_cameras", max_cameras)

    @property
    def mode(self) -> str:
        time_range = self.query.time_range
        if time_range and time_range.begin == time_range.end:
            return "frame_set"
        return "clip_batch"

    @property
    def export_format(self) -> str:
        if self.mode == "frame_set":
            return MULTI_CAMERA_EXPORT_IMAGE_FORMAT
        return SINGLE_CAMERA_EXPORT_FORMAT

    @property
    def camera_selector_count(self) -> int:
        scope = self.query.scope
        return len(scope.camera_names) + len(scope.camera_access_points)

    @property
    def duration_seconds(self) -> int:
        time_range = self.query.time_range
        if not time_range or not time_range.begin or not time_range.end:
            return 0
        return int((time_range.end - time_range.begin).total_seconds())

    @property
    def request_begin(self) -> str:
        return format_query_datetime(self.query.time_range.begin if self.query.time_range else None) or ""

    @property
    def request_end(self) -> str:
        return format_query_datetime(self.query.time_range.end if self.query.time_range else None) or ""


@dataclass(frozen=True)
class MultiCameraExportPlan:
    index: int
    camera: str
    camera_access_point: str
    request_begin: str
    request_end: str
    target_timestamp: str
    timestamp_source: str
    export_format: str
    waittimeout_ms: int
    archive_name: str | None = None

    @property
    def video_id(self) -> str:
        return self.camera_access_point.removeprefix("hosts/")


@dataclass(frozen=True)
class MultiCameraExportSelection:
    mode: str
    export_format: str
    request_begin: str
    request_end: str
    plans: tuple[MultiCameraExportPlan, ...]

    @property
    def camera_count(self) -> int:
        return len(self.plans)


def build_multi_camera_export_request(
    *,
    begin: object = None,
    end: object = None,
    at: object = None,
    camera_names: Iterable[object] = (),
    camera_access_points: Iterable[object] = (),
    waittimeout_ms: int = DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
    archive_name: object = "",
    max_cameras: int = DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS,
) -> MultiCameraExportRequest:
    if at is not None:
        if begin is None:
            begin = at
        if end is None:
            end = at
    return MultiCameraExportRequest(
        query=EventQuery(
            time_range=EventTimeRange(begin=begin, end=end),
            scope=EventScopeFilter(
                camera_names=_split_csv_values(camera_names),
                camera_access_points=_split_csv_values(camera_access_points),
            ),
        ),
        waittimeout_ms=waittimeout_ms,
        archive_name=_text(archive_name) or None,
        max_cameras=max_cameras,
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
    "camera": "camera_names",
    "cam": "camera_names",
    "camera_name": "camera_names",
    "camera_names": "camera_names",
    "camera_ap": "camera_access_points",
    "camera_access_point": "camera_access_points",
    "camera_access_points": "camera_access_points",
    "archive": "archive_name",
    "waittimeout": "waittimeout_ms",
    "waittimeout_ms": "waittimeout_ms",
    "max_cameras": "max_cameras",
}
_MULTI_VALUE_TERMS = {"camera_names", "camera_access_points"}


def parse_multi_camera_export_terms(
    terms: Iterable[object],
    *,
    default_waittimeout_ms: int = DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
    default_max_cameras: int = DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS,
) -> MultiCameraExportRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise MultiCameraExportSyntaxError("Multi-camera export requires key=value terms.")

    values: dict[str, Any] = {
        "waittimeout_ms": default_waittimeout_ms,
        "max_cameras": default_max_cameras,
    }
    for term in raw_terms:
        if "=" not in term:
            raise MultiCameraExportSyntaxError(f"Unsupported multi-camera export term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise MultiCameraExportSyntaxError(f"Unsupported multi-camera export key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise MultiCameraExportSyntaxError(f"Multi-camera export value is required for: {raw_key}")
        if key in _MULTI_VALUE_TERMS:
            existing = list(values.get(key) or [])
            existing.extend(_split_csv_values(value))
            values[key] = existing
        else:
            values[key] = value

    if not values.get("at") and not (values.get("begin") and values.get("end")):
        raise MultiCameraExportSyntaxError("Use at=... or both from=... and to=... for the export window.")
    if not values.get("camera_names") and not values.get("camera_access_points"):
        raise MultiCameraExportSyntaxError("Add at least two camera=... or camera_ap=... selectors.")

    try:
        return build_multi_camera_export_request(
            begin=values.get("begin"),
            end=values.get("end"),
            at=values.get("at"),
            camera_names=values.get("camera_names") or (),
            camera_access_points=values.get("camera_access_points") or (),
            waittimeout_ms=_coerce_positive_int(values.get("waittimeout_ms"), "waittimeout_ms"),
            archive_name=values.get("archive_name") or "",
            max_cameras=_coerce_positive_int(values.get("max_cameras"), "max_cameras"),
        )
    except ValueError as exc:
        raise MultiCameraExportSyntaxError(str(exc)) from exc


def resolve_multi_camera_export_selection(
    request: MultiCameraExportRequest,
    camera_rows: Iterable[Mapping[str, Any]],
) -> MultiCameraExportSelection:
    scope = request.query.scope
    selectors = (
        tuple(("camera_access_point", value) for value in scope.camera_access_points)
        if scope.camera_access_points
        else tuple(("camera_name", value) for value in scope.camera_names)
    )

    plans: list[MultiCameraExportPlan] = []
    seen_camera_access_points: set[str] = set()
    for selector_kind, selector_value in selectors:
        single_request = build_single_camera_export_request(
            begin=request.request_begin,
            end=request.request_end,
            camera_names=(selector_value,) if selector_kind == "camera_name" else (),
            camera_access_points=(selector_value,) if selector_kind == "camera_access_point" else (),
            waittimeout_ms=request.waittimeout_ms,
            archive_name=request.archive_name or "",
        )
        selection = resolve_single_camera_export_selection(single_request, camera_rows)
        camera_key = _normalized(selection.camera_access_point)
        if camera_key in seen_camera_access_points:
            continue
        seen_camera_access_points.add(camera_key)
        plans.append(
            MultiCameraExportPlan(
                index=len(plans) + 1,
                camera=selection.camera,
                camera_access_point=selection.camera_access_point,
                request_begin=selection.request_begin,
                request_end=selection.request_end,
                target_timestamp=selection.target_timestamp,
                timestamp_source=selection.timestamp_source,
                export_format=request.export_format,
                waittimeout_ms=request.waittimeout_ms,
                archive_name=request.archive_name,
            )
        )

    if len(plans) < 2:
        raise ValueError("Multi-camera export needs at least two unique cameras after selection.")
    if len(plans) > request.max_cameras:
        raise ValueError(
            f"Multi-camera export requested {len(plans)} cameras, above the safe MVP cap of {request.max_cameras}."
        )

    return MultiCameraExportSelection(
        mode=request.mode,
        export_format=request.export_format,
        request_begin=request.request_begin,
        request_end=request.request_end,
        plans=tuple(plans),
    )


def multi_camera_export_plan_to_backend_request(plan: MultiCameraExportPlan) -> dict[str, Any]:
    return {
        "video_id": plan.video_id,
        "camera_access_point": plan.camera_access_point,
        "begin": plan.request_begin,
        "end": plan.request_end,
        "waittimeout_ms": plan.waittimeout_ms,
        "archive": plan.archive_name,
        "format": plan.export_format,
    }


def shape_multi_camera_export_result(
    request: MultiCameraExportRequest,
    selection: MultiCameraExportSelection,
    *,
    export_results: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    result_by_camera: dict[str, dict[str, Any]] = {}
    for row in export_results:
        if not isinstance(row, Mapping):
            continue
        camera_access_point = _normalized(row.get("camera_access_point"))
        if not camera_access_point:
            continue
        result_by_camera[camera_access_point] = dict(row)

    exports: list[dict[str, Any]] = []
    ready_count = 0
    failed_count = 0
    pending_count = 0
    total_size_bytes = 0

    for plan in selection.plans:
        raw = result_by_camera.get(_normalized(plan.camera_access_point), {})
        artifact_path = _text(raw.get("artifact_path")) or None
        artifact_size_bytes = raw.get("artifact_size_bytes")
        export_status = raw.get("export_status") if isinstance(raw.get("export_status"), Mapping) else None
        error = _text(raw.get("error")) or None

        size_value = None
        if artifact_size_bytes is not None:
            size_value = int(artifact_size_bytes)

        state = _export_state(
            artifact_path=artifact_path,
            error=error,
            export_status=export_status,
        )
        if state == "ready":
            ready_count += 1
        elif state == "failed":
            failed_count += 1
        else:
            pending_count += 1

        if size_value is not None:
            total_size_bytes += size_value

        exports.append(
            {
                "index": plan.index,
                "camera": plan.camera,
                "camera_access_point": plan.camera_access_point,
                "video_id": plan.video_id,
                "target_timestamp": plan.target_timestamp,
                "timestamp_source": plan.timestamp_source,
                "request": multi_camera_export_plan_to_backend_request(plan),
                "export": {
                    "state": state,
                    "ok": bool(artifact_path),
                    "path": artifact_path,
                    "file_name": Path(artifact_path).name if artifact_path else _status_file_name(export_status),
                    "size_bytes": size_value,
                    "format": plan.export_format,
                    "archive": plan.archive_name,
                    "status": dict(export_status) if export_status is not None else None,
                    "error": error,
                },
            }
        )

    summary_state = "planned"
    if ready_count == len(selection.plans):
        summary_state = "ready"
    elif failed_count == len(selection.plans):
        summary_state = "failed"
    elif ready_count or failed_count:
        summary_state = "partial"

    return {
        "request": {
            "filters": request.query.to_legacy_filters(),
            "waittimeout_ms": request.waittimeout_ms,
            "archive": request.archive_name,
            "format": request.export_format,
            "mode": request.mode,
            "max_cameras": request.max_cameras,
            "range_seconds": request.duration_seconds,
        },
        "selection": {
            "camera_count": selection.camera_count,
            "mode": selection.mode,
            "format": selection.export_format,
            "request_begin": selection.request_begin,
            "request_end": selection.request_end,
            "strategy": MULTI_CAMERA_EXPORT_STRATEGY,
            "cameras": [
                {
                    "index": plan.index,
                    "camera": plan.camera,
                    "camera_access_point": plan.camera_access_point,
                    "video_id": plan.video_id,
                    "target_timestamp": plan.target_timestamp,
                    "timestamp_source": plan.timestamp_source,
                    "request": multi_camera_export_plan_to_backend_request(plan),
                }
                for plan in selection.plans
            ],
        },
        "batch": {
            "strategy": MULTI_CAMERA_EXPORT_STRATEGY,
            "packaged_output": False,
            "summary": {
                "state": summary_state,
                "planned": len(selection.plans),
                "ready": ready_count,
                "failed": failed_count,
                "pending": pending_count,
                "total_size_bytes": total_size_bytes,
            },
            "exports": exports,
        },
    }


__all__ = [
    "DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS",
    "DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS",
    "MULTI_CAMERA_EXPORT_IMAGE_FORMAT",
    "MULTI_CAMERA_EXPORT_STRATEGY",
    "MultiCameraExportPlan",
    "MultiCameraExportRequest",
    "MultiCameraExportSelection",
    "MultiCameraExportSyntaxError",
    "build_multi_camera_export_request",
    "multi_camera_export_plan_to_backend_request",
    "parse_multi_camera_export_terms",
    "resolve_multi_camera_export_selection",
    "shape_multi_camera_export_result",
]
