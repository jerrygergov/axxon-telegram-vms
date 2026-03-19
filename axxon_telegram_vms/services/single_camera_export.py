"""Pure single-camera export helpers for the Step 23 MVP."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .archive_jump import (
    ArchiveJumpRequest,
    ArchiveJumpSelection,
    build_archive_jump_request,
    derive_archive_jump_selection,
)
from axxon_telegram_vms.models import format_query_datetime


DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS = 90000
SINGLE_CAMERA_EXPORT_FORMAT = "mp4"


class SingleCameraExportSyntaxError(ValueError):
    """Raised when a command-style single-camera export request is malformed."""


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


@dataclass(frozen=True)
class SingleCameraExportRequest:
    archive_request: ArchiveJumpRequest
    waittimeout_ms: int = DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS
    archive_name: str | None = None
    export_format: str = SINGLE_CAMERA_EXPORT_FORMAT

    def __post_init__(self) -> None:
        waittimeout_ms = _coerce_positive_int(self.waittimeout_ms, "waittimeout_ms")
        archive_name = _text(self.archive_name) or None
        export_format = _text(self.export_format).lower() or SINGLE_CAMERA_EXPORT_FORMAT
        if export_format != SINGLE_CAMERA_EXPORT_FORMAT:
            raise ValueError(f"Unsupported export format: {self.export_format}")
        scope = self.archive_request.query.scope
        camera_count = len(scope.camera_names) + len(scope.camera_access_points)
        if camera_count != 1:
            raise ValueError("Single-camera export MVP requires exactly one camera selector.")
        time_range = self.archive_request.query.time_range
        if not time_range or not time_range.is_bounded():
            raise ValueError("Single-camera export requires a bounded time range.")
        object.__setattr__(self, "waittimeout_ms", waittimeout_ms)
        object.__setattr__(self, "archive_name", archive_name)
        object.__setattr__(self, "export_format", export_format)

    @property
    def query(self):
        return self.archive_request.query


def build_single_camera_export_request(
    *,
    begin: object,
    end: object,
    camera_names: Iterable[object] = (),
    camera_access_points: Iterable[object] = (),
    waittimeout_ms: int = DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
    archive_name: object = "",
) -> SingleCameraExportRequest:
    archive_request = build_archive_jump_request(
        begin=begin,
        end=end,
        camera_names=_split_csv_values(camera_names),
        camera_access_points=_split_csv_values(camera_access_points),
    )
    return SingleCameraExportRequest(
        archive_request=archive_request,
        waittimeout_ms=waittimeout_ms,
        archive_name=_text(archive_name) or None,
    )


_TERM_ALIASES = {
    "from": "begin",
    "begin": "begin",
    "start": "begin",
    "to": "end",
    "end": "end",
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
}
_MULTI_VALUE_TERMS = {"camera_names", "camera_access_points"}


def parse_single_camera_export_terms(
    terms: Iterable[object],
    *,
    default_waittimeout_ms: int = DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
) -> SingleCameraExportRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise SingleCameraExportSyntaxError("Single-camera export requires key=value terms.")

    values: dict[str, Any] = {"waittimeout_ms": default_waittimeout_ms}
    for term in raw_terms:
        if "=" not in term:
            raise SingleCameraExportSyntaxError(f"Unsupported export term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise SingleCameraExportSyntaxError(f"Unsupported export key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise SingleCameraExportSyntaxError(f"Export value is required for: {raw_key}")
        if key in _MULTI_VALUE_TERMS:
            existing = list(values.get(key) or [])
            existing.extend(_split_csv_values(value))
            values[key] = existing
        else:
            values[key] = value

    if not values.get("begin") or not values.get("end"):
        raise SingleCameraExportSyntaxError("Use from=... and to=... for the export window.")
    if not values.get("camera_names") and not values.get("camera_access_points"):
        raise SingleCameraExportSyntaxError("Add camera=... or camera_ap=... for the export camera.")

    try:
        return build_single_camera_export_request(
            begin=values.get("begin"),
            end=values.get("end"),
            camera_names=values.get("camera_names") or (),
            camera_access_points=values.get("camera_access_points") or (),
            waittimeout_ms=_coerce_positive_int(values.get("waittimeout_ms"), "waittimeout_ms"),
            archive_name=values.get("archive_name") or "",
        )
    except ValueError as exc:
        raise SingleCameraExportSyntaxError(str(exc)) from exc


def single_camera_export_request_to_api_args(request: SingleCameraExportRequest) -> list[str]:
    time_range = request.query.time_range
    begin = format_query_datetime(time_range.begin if time_range else None)
    end = format_query_datetime(time_range.end if time_range else None)
    if not (begin and end):
        raise ValueError("Single-camera export request must include begin and end timestamps")

    args = [
        "--begin", begin,
        "--end", end,
        "--waittimeout-ms", str(request.waittimeout_ms),
    ]
    if request.archive_name:
        args.extend(["--archive", request.archive_name])
    for value in request.query.scope.camera_names:
        args.extend(["--camera", value])
    for value in request.query.scope.camera_access_points:
        args.extend(["--camera-ap", value])
    return args


def resolve_single_camera_export_selection(
    request: SingleCameraExportRequest,
    camera_rows: Iterable[Mapping[str, Any]],
) -> ArchiveJumpSelection:
    return derive_archive_jump_selection(request.archive_request, [], camera_rows)


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


def shape_single_camera_export_result(
    request: SingleCameraExportRequest,
    selection: ArchiveJumpSelection,
    *,
    artifact_path: str | None = None,
    artifact_size_bytes: int | None = None,
    export_status: Mapping[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    artifact = Path(str(artifact_path)) if _text(artifact_path) else None
    return {
        "request": {
            "filters": request.query.to_legacy_filters(),
            "waittimeout_ms": request.waittimeout_ms,
            "archive": request.archive_name,
            "format": request.export_format,
        },
        "selection": {
            "camera": selection.camera,
            "camera_access_point": selection.camera_access_point,
            "video_id": selection.camera_access_point.removeprefix("hosts/"),
            "target_timestamp": selection.target_timestamp,
            "timestamp_source": selection.timestamp_source,
            "request_begin": selection.request_begin,
            "request_end": selection.request_end,
        },
        "export": {
            "ok": artifact is not None,
            "path": str(artifact) if artifact else None,
            "file_name": artifact.name if artifact else _status_file_name(export_status),
            "size_bytes": int(artifact_size_bytes) if artifact_size_bytes is not None else None,
            "archive": request.archive_name,
            "format": request.export_format,
            "status": dict(export_status) if isinstance(export_status, Mapping) else None,
            "error": _text(error) or None,
        },
    }


__all__ = [
    "DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS",
    "SINGLE_CAMERA_EXPORT_FORMAT",
    "SingleCameraExportRequest",
    "SingleCameraExportSyntaxError",
    "build_single_camera_export_request",
    "parse_single_camera_export_terms",
    "resolve_single_camera_export_selection",
    "shape_single_camera_export_result",
    "single_camera_export_request_to_api_args",
]
