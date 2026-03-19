"""Pure detector normalization helpers for the staged models lane."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


def friendly_label(name: object = "", display_id: object = "", fallback: object = "") -> str:
    text = str(name or "").strip()
    ident = str(display_id or "").strip()
    fb = str(fallback or "").strip()
    if ident and text and not text.startswith(f"{ident}."):
        return f"{ident}.{text}"
    return text or fb or ident or "—"


def _label_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def _contains_label(haystack: object, needle: object) -> bool:
    hay = _label_key(haystack)
    target = _label_key(needle)
    return bool(hay and target and target in hay)


def detector_selection_label(
    name: object = "",
    camera_name: object = "",
    detector_type_name: object = "",
) -> str:
    detector = str(name or "").strip() or "Detector"
    camera = str(camera_name or "").strip()
    detector_type = str(detector_type_name or "").strip()

    parts = [detector]
    if camera and not _contains_label(detector, camera):
        parts.append(camera)
    if detector_type and not any(_contains_label(part, detector_type) or _contains_label(detector_type, part) for part in parts):
        parts.append(detector_type)
    return " · ".join(parts)


@dataclass(frozen=True)
class NormalizedDetectorRow:
    access_point: str
    name: str
    camera_name: str
    camera_access_point: str = ""
    detector_type: str = ""
    detector_type_name: str = ""
    is_activated: bool | None = None

    @classmethod
    def from_raw_row(cls, row: dict[str, Any]) -> "NormalizedDetectorRow | None":
        det_ap = str((row or {}).get("detector_access_point") or "").strip()
        if not det_ap:
            return None
        is_activated = row.get("is_activated")
        return cls(
            access_point=det_ap,
            name=friendly_label(
                row.get("detector_name"),
                row.get("detector_display_id"),
                "Detector",
            ),
            camera_name=friendly_label(
                row.get("camera_name"),
                row.get("camera_display_id"),
                "Camera",
            ),
            camera_access_point=str(row.get("camera_access_point") or "").strip(),
            detector_type=str(row.get("detector_type") or "").strip(),
            detector_type_name=str(row.get("detector_type_name") or "").strip(),
            is_activated=is_activated if isinstance(is_activated, bool) else None,
        )

    def as_legacy_dict(self) -> dict[str, Any]:
        return {
            "access_point": self.access_point,
            "name": self.name,
            "camera_name": self.camera_name,
            "camera_access_point": self.camera_access_point,
            "detector_type": self.detector_type,
            "detector_type_name": self.detector_type_name,
            "is_activated": self.is_activated,
            "selection_label": self.selection_label(),
        }

    def selection_label(self) -> str:
        return detector_selection_label(
            self.name,
            self.camera_name,
            self.detector_type_name,
        )


def normalize_detector_rows(rows: list[dict[str, Any]] | None) -> list[NormalizedDetectorRow]:
    out: list[NormalizedDetectorRow] = []
    for row in rows or []:
        normalized = NormalizedDetectorRow.from_raw_row(row)
        if normalized:
            out.append(normalized)
    return out


def normalize_detector_rows_legacy(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [row.as_legacy_dict() for row in normalize_detector_rows(rows)]


__all__ = [
    "NormalizedDetectorRow",
    "detector_selection_label",
    "friendly_label",
    "normalize_detector_rows",
    "normalize_detector_rows_legacy",
]
