"""Resolve high-level scope selectors into exact camera or detector subjects."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from axxon_telegram_vms.models import EventScopeFilter


def _text(value: object) -> str:
    return str(value or "").strip()


def _friendly_label(name: object = "", display_id: object = "", fallback: object = "") -> str:
    text = _text(name)
    ident = _text(display_id)
    fb = _text(fallback)
    if ident and text and not text.startswith(f"{ident}."):
        return f"{ident}.{text}"
    return text or fb or ident or "Camera"


@dataclass(frozen=True)
class ResolvedScopeSubjects:
    camera_access_points: tuple[str, ...] = ()
    detector_access_points: tuple[str, ...] = ()

    @property
    def preferred_subjects(self) -> tuple[str, ...]:
        if self.detector_access_points:
            return self.detector_access_points
        return self.camera_access_points


def _dedupe(values: Iterable[object]) -> tuple[str, ...]:
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


def _camera_scope_card(row: Mapping[str, Any]) -> dict[str, Any] | None:
    access_point = _text(row.get("access_point"))
    if not access_point:
        return None
    return {
        "camera": _friendly_label(row.get("display_name"), row.get("display_id"), access_point),
        "camera_access_point": access_point,
        "subject": access_point,
    }


def _detector_scope_cards(row: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    camera_access_point = _text(row.get("access_point"))
    if not camera_access_point:
        return ()
    camera_name = _friendly_label(row.get("display_name"), row.get("display_id"), camera_access_point)
    out: list[dict[str, Any]] = []
    for detector in row.get("detectors", ()) or ():
        if not isinstance(detector, Mapping):
            continue
        detector_access_point = _text(detector.get("access_point"))
        if not detector_access_point:
            continue
        out.append(
            {
                "camera": camera_name,
                "camera_access_point": camera_access_point,
                "detector": _friendly_label(
                    detector.get("display_name"),
                    detector.get("display_id"),
                    detector_access_point,
                ),
                "detector_access_point": detector_access_point,
                "subject": detector_access_point,
            }
        )
    return tuple(out)


def resolve_scope_subjects(
    scope: EventScopeFilter,
    camera_rows: Iterable[Mapping[str, Any]],
    *,
    include_detectors: bool = False,
) -> ResolvedScopeSubjects:
    rows = tuple(row for row in camera_rows if isinstance(row, Mapping))
    detector_scope_requested = bool(scope.detector_access_points or (scope.detector_names and not scope.camera_access_points))

    matched_cameras: list[str] = list(scope.camera_access_points) if not detector_scope_requested else []
    if not detector_scope_requested:
        for row in rows:
            card = _camera_scope_card(row)
            if card and scope.matches_card(card):
                matched_cameras.append(card["camera_access_point"])

    matched_detectors: list[str] = list(scope.detector_access_points) if include_detectors and detector_scope_requested else []
    if include_detectors and detector_scope_requested:
        for row in rows:
            for card in _detector_scope_cards(row):
                if scope.matches_card(card):
                    matched_detectors.append(card["detector_access_point"])

    return ResolvedScopeSubjects(
        camera_access_points=_dedupe(matched_cameras),
        detector_access_points=_dedupe(matched_detectors),
    )


__all__ = ["ResolvedScopeSubjects", "resolve_scope_subjects"]
