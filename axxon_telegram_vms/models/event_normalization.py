"""Pure event normalization seam extracted from the script runtime."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


ONE_PHASE_DETECTOR_GROUPS = frozenset({
    "DG_AI_DETECTOR",
    "DG_FACE_DETECTOR",
    "DG_LPR_DETECTOR",
    "DG_VEHICLE_DETECTOR",
})
ONE_PHASE_EVENT_MARKERS = (
    "descriptor",
    "face",
    "listed_lpr",
    "meta",
    "neurotracker",
    "plate",
    "querydetected",
    "recognized",
    "vehicletransit",
)
EVENT_NAME_RE = re.compile(r'event name\s+"([^"]+)"', flags=re.IGNORECASE)
LABEL_SPACE_RE = re.compile(r"\s+")
LOCALIZATION_SOURCE_PREFIX_RE = re.compile(r'^(?:camera|source)\s+"[^"]+"\s*[:.]\s*', flags=re.IGNORECASE)
LOCALIZATION_TRIGGER_RE = re.compile(
    r'^(?:beginning|end) of detector ".+" triggering$|^detector ".+" triggering(?:,.*)?$',
    flags=re.IGNORECASE,
)
PLATE_TOKEN_RE = re.compile(r'\.\s*LP\s+"?([A-Z0-9-]{3,12})"?', flags=re.IGNORECASE)


def _first_text(*values: object, fallback: str = "") -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return fallback


def _clean_label_text(value: object) -> str:
    text = LABEL_SPACE_RE.sub(" ", str(value or "").replace("\n", " ")).strip()
    return text.strip(" .;,:-")


def _label_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", _clean_label_text(value).casefold())


def _contains_label(haystack: object, needle: object) -> bool:
    hay = _label_key(haystack)
    target = _label_key(needle)
    return bool(hay and target and target in hay)


def _normalize_localization_candidate(text: object) -> str:
    value = _clean_label_text(text)
    if not value:
        return ""
    return PLATE_TOKEN_RE.sub(r" · \1", value)


def _meaningful_localization_text(localization_text: object, event_type: object = "") -> str:
    text = _clean_label_text(localization_text)
    if not text:
        return ""

    stripped = _clean_label_text(LOCALIZATION_SOURCE_PREFIX_RE.sub("", text))
    before_extended = _normalize_localization_candidate(stripped.split("Extended info:", 1)[0])
    event_name_match = EVENT_NAME_RE.search(stripped)
    event_name = _normalize_localization_candidate(event_name_match.group(1) if event_name_match else "")
    fallback = _normalize_localization_candidate(stripped)
    raw_event_type = _clean_label_text(event_type).casefold()

    for candidate in (before_extended, event_name, fallback):
        if not candidate:
            continue
        lowered = candidate.casefold()
        if lowered == raw_event_type:
            continue
        if "extended info" in lowered:
            continue
        if LOCALIZATION_TRIGGER_RE.match(candidate):
            continue
        return candidate
    return ""


def _alert_priority_short(priority: object) -> str:
    value = _clean_label_text(priority).upper()
    return {
        "1": "P1",
        "LOW": "P1",
        "AP_LOW": "P1",
        "2": "P2",
        "MEDIUM": "P2",
        "AP_MEDIUM": "P2",
        "3": "P3",
        "HIGH": "P3",
        "CRITICAL": "P3",
        "AP_HIGH": "P3",
        "AP_CRITICAL": "P3",
    }.get(value, "")


def _event_status_label(event: "NormalizedEvent") -> str:
    if event.source_kind == "alert":
        parts = []
        priority = _alert_priority_short(event.priority)
        if priority:
            parts.append(priority)
        phase_label = event.phase.label
        if phase_label == "acknowledged":
            phase_label = "ack"
        if phase_label:
            parts.append(phase_label)
        return " ".join(parts)
    if event.phase.family == "paired" and event.phase.label in {"began", "ended"}:
        return event.phase.label
    return ""


def _detector_label_candidate(event: "NormalizedEvent", primary: str) -> str:
    detector = _clean_label_text(event.detector)
    if not detector or detector in {"Detector", "ET_Alert"}:
        return ""
    if detector.casefold() == _clean_label_text(event.event_type).casefold():
        return ""
    if _contains_label(primary, detector):
        return ""
    if event.category == "lpr":
        lowered = detector.casefold()
        if any(token in lowered for token in ("license plate", "recognizer", "lpr")) and any(
            token in primary.casefold() for token in ("lp", "plate", "license")
        ):
            return ""
    return detector


def event_operator_label_parts(event: "NormalizedEvent") -> tuple[str, str, str]:
    localization = _meaningful_localization_text(event.localization_text, event_type=event.event_type)
    detector = _clean_label_text(event.detector)
    camera = _clean_label_text(event.camera)
    plate = _clean_label_text(event.plate)
    detector_primary = detector if detector not in {"", "Detector", "ET_Alert"} else ""
    if detector_primary.casefold() == _clean_label_text(event.event_type).casefold():
        detector_primary = ""
    camera_primary = camera if camera not in {"", "Camera"} else ""
    fallback = _clean_label_text(event.event_type)
    if fallback in {"", "ET_Alert", "ET_DetectorEvent"}:
        fallback = "Alert" if event.source_kind == "alert" else "Event"
    primary = _first_text(localization, detector_primary, camera_primary, plate, fallback=fallback)

    secondary_parts: list[str] = []
    detector_label = _detector_label_candidate(event, primary)
    if detector_label:
        secondary_parts.append(detector_label)
    if camera and not _contains_label(primary, camera):
        secondary_parts.append(camera)
    if plate and not _contains_label(primary, plate):
        secondary_parts.append(plate)
    return primary, " · ".join(secondary_parts[:2]), _event_status_label(event)


def _category_from_raw_event(event: dict[str, Any]) -> str:
    if str(event.get("event_type") or "").strip() == "ET_Alert":
        return "alert"
    body = event.get("body", {}) or {}
    event_type = str(body.get("event_type") or event.get("event_type") or "").lower()
    detector_groups = {str(item) for item in (body.get("detectors_group") or [])}
    text = str(((event.get("localization") or {}).get("text")) or "").lower()
    if "DG_LPR_DETECTOR" in detector_groups or "plate" in event_type or "license plate" in text:
        return "lpr"
    if "DG_SITUATION_DETECTOR" in detector_groups or "moveinzone" in event_type:
        return "motion"
    if "traffic" in event_type or "overspeed" in event_type or "accident" in event_type:
        return "traffic"
    if "meta" in event_type or "querydetected" in event_type:
        return "meta"
    return "other"


def _event_camera_name(body: dict[str, Any]) -> str:
    origin_ext = body.get("origin_ext") or {}
    return _first_text(
        origin_ext.get("friendly_name"),
        origin_ext.get("display_name"),
        origin_ext.get("name"),
        body.get("origin_deprecated"),
        fallback="Camera",
    )


def _event_detector_name(body: dict[str, Any]) -> str:
    detector_ext = body.get("detector_ext") or {}
    return _first_text(
        detector_ext.get("friendly_name"),
        detector_ext.get("display_name"),
        detector_ext.get("name"),
        body.get("detector_deprecated"),
        body.get("event_type"),
        fallback="Detector",
    )


def _extract_plate(body: dict[str, Any], localization_text: str) -> str | None:
    data = body.get("data", {}) or {}
    hypotheses = data.get("Hypotheses") or []
    plate = data.get("plate")
    if not plate and hypotheses and isinstance(hypotheses[0], dict):
        plate = hypotheses[0].get("PlateFull")
    if not plate:
        for detail in body.get("details") or []:
            auto = detail.get("auto_recognition_result") or {}
            auto_hypotheses = auto.get("hypotheses") or []
            if auto_hypotheses and isinstance(auto_hypotheses[0], dict):
                plate = auto_hypotheses[0].get("plate_full")
                if plate:
                    break
            listed_item = detail.get("listed_item_detected_result") or {}
            listed_plate = (listed_item.get("listed_plate_info") or {}).get("plate")
            if listed_plate:
                plate = listed_plate
                break
    if not plate and localization_text:
        match = re.search(r"\bLP\s+([A-Z0-9-]{3,12})\b", localization_text, flags=re.IGNORECASE)
        if match:
            plate = match.group(1).upper()
    return str(plate).strip() or None if plate else None


def _vehicle_from_body(body: dict[str, Any]) -> "NormalizedVehicle | None":
    data = body.get("data", {}) or {}
    brand = data.get("VehicleBrand")
    model = data.get("VehicleModel")
    color = data.get("VehicleColor")
    if not any((brand, model, color)):
        return None
    return NormalizedVehicle(
        brand=str(brand).strip() or None if brand else None,
        model=str(model).strip() or None if model else None,
        color=str(color).strip() or None if color else None,
    )


def _extract_lots_object_count(body: dict[str, Any]) -> int | None:
    for detail in body.get("details") or []:
        lots = (detail or {}).get("lots_objects") or {}
        if "object_count" not in lots:
            continue
        try:
            return int(lots.get("object_count"))
        except (TypeError, ValueError):
            return None
    return None


def _coerce_phase(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _looks_like_one_phase_event(event_type: str, detector_groups: set[str], phase: int | None, state: str) -> bool:
    if state == "HAPPENED":
        return True
    if phase == 0:
        return True
    if detector_groups.intersection(ONE_PHASE_DETECTOR_GROUPS):
        return True
    event_type_lower = event_type.lower()
    return any(marker in event_type_lower for marker in ONE_PHASE_EVENT_MARKERS)


@dataclass(frozen=True)
class NormalizedEventPhase:
    family: str
    label: str
    is_terminal: bool
    raw_state: str = ""
    raw_phase: int | None = None


def normalize_detector_event_phase(
    event_type: str,
    state: object,
    phase: object = None,
    detector_groups: list[object] | tuple[object, ...] | None = None,
) -> NormalizedEventPhase:
    state_text = str(state or "").strip().upper()
    phase_value = _coerce_phase(phase)
    groups = {str(item) for item in (detector_groups or []) if str(item)}
    if state_text == "BEGAN" or phase_value == 1:
        return NormalizedEventPhase(
            family="paired",
            label="began",
            is_terminal=False,
            raw_state=state_text,
            raw_phase=phase_value,
        )
    if state_text == "ENDED" or phase_value == 2:
        return NormalizedEventPhase(
            family="paired",
            label="ended",
            is_terminal=True,
            raw_state=state_text,
            raw_phase=phase_value,
        )
    if _looks_like_one_phase_event(str(event_type or ""), groups, phase_value, state_text):
        return NormalizedEventPhase(
            family="instant",
            label="happened",
            is_terminal=True,
            raw_state=state_text,
            raw_phase=phase_value,
        )
    return NormalizedEventPhase(
        family="unknown",
        label=(state_text.lower() or "event"),
        is_terminal=state_text in {"ENDED", "HAPPENED"},
        raw_state=state_text,
        raw_phase=phase_value,
    )


def normalize_alert_phase(state: object) -> NormalizedEventPhase:
    state_text = str(state or "ACTIVE").strip().upper() or "ACTIVE"
    if state_text in {"ST_WANT_REACTION", "ACTIVE", "RAISED", "NEW"}:
        label = "active"
        is_terminal = False
    elif state_text in {"ST_IN_PROGRESS", "ACKNOWLEDGED", "IN_PROGRESS"}:
        label = "acknowledged"
        is_terminal = False
    elif state_text in {"ST_RESOLVED", "ST_CLOSED", "RESOLVED", "CLOSED", "ENDED"}:
        label = "resolved"
        is_terminal = True
    else:
        label = state_text.lower()
        is_terminal = False
    return NormalizedEventPhase(
        family="alert",
        label=label,
        is_terminal=is_terminal,
        raw_state=state_text,
        raw_phase=None,
    )


@dataclass(frozen=True)
class NormalizedVehicle:
    brand: str | None = None
    model: str | None = None
    color: str | None = None

    def as_legacy_dict(self) -> dict[str, str | None]:
        return {
            "brand": self.brand,
            "model": self.model,
            "color": self.color,
        }


@dataclass(frozen=True)
class NormalizedEvent:
    id: str | None
    timestamp: str | None
    category: str
    source_kind: str
    event_type: str
    state: str | None
    phase: NormalizedEventPhase
    camera: str
    camera_access_point: str = ""
    detector: str = ""
    detector_access_point: str = ""
    text: str = ""
    localization_text: str = ""
    server: str = ""
    priority: str | None = None
    alert_id: str | None = None
    plate: str | None = None
    vehicle: NormalizedVehicle | None = None
    review_available: bool = False
    actions: tuple[str, ...] = ()
    trigger_event_type: str | None = None
    trigger_state: str | None = None
    trigger_phase_family: str | None = None
    trigger_phase_label: str | None = None
    object_count: int | None = None

    def operator_label_parts(self) -> tuple[str, str, str]:
        return event_operator_label_parts(self)

    def to_telegram_card(self) -> dict[str, Any]:
        label_primary, label_secondary, label_status = self.operator_label_parts()
        card: dict[str, Any] = {
            "id": self.id,
            "timestamp": self.timestamp,
            "category": self.category,
            "event_type": self.event_type,
            "state": self.state,
            "server": self.server,
            "camera": self.camera,
            "camera_access_point": self.camera_access_point,
            "detector": self.detector,
            "detector_access_point": self.detector_access_point,
            "text": self.text,
            "localization_text": self.localization_text,
            "phase_family": self.phase.family,
            "phase_label": self.phase.label,
            "is_terminal": self.phase.is_terminal,
            "actions": list(self.actions),
            "label_primary": label_primary,
        }
        if label_secondary:
            card["label_secondary"] = label_secondary
        if label_status:
            card["label_status"] = label_status
        if self.priority:
            card["priority"] = self.priority
        if self.alert_id:
            card["alert_id"] = self.alert_id
        if self.plate:
            card["plate"] = self.plate
            card["vehicle"] = self.vehicle.as_legacy_dict() if self.vehicle else {
                "brand": None,
                "model": None,
                "color": None,
            }
        if self.review_available or self.source_kind == "alert":
            card["review_available"] = self.review_available
        if self.trigger_event_type:
            card["trigger_event_type"] = self.trigger_event_type
        if self.trigger_state:
            card["trigger_state"] = self.trigger_state
        if self.trigger_phase_family:
            card["trigger_phase_family"] = self.trigger_phase_family
        if self.trigger_phase_label:
            card["trigger_phase_label"] = self.trigger_phase_label
        if self.object_count is not None:
            card["object_count"] = self.object_count
        return card


def _normalize_alert_event(event: dict[str, Any]) -> NormalizedEvent:
    body = event.get("body", {}) or {}
    alert_body = ((event.get("data", {}) or {}).get("items", [{}])[0] or {}).get("body", {})
    if not alert_body:
        alert_body = body

    states = alert_body.get("states") or []
    first_state = states[0] if states and isinstance(states[0], dict) else {}
    camera = alert_body.get("camera") or {}
    detector = alert_body.get("detector") or {}
    macro = alert_body.get("macro") or {}
    localization_text = str(((event.get("localization") or {}).get("text")) or "").strip()

    reasons = first_state.get("reasons") or []
    reasons_text = ", ".join(str(reason).strip() for reason in reasons if str(reason).strip())
    detector_ext = (alert_body.get("detector") or {}).get("detector_ext") or {}
    detector_name = _first_text(
        detector_ext.get("friendly_name"),
        detector.get("friendly_name"),
        detector.get("name"),
    )
    macro_name = _first_text(
        ((alert_body.get("macro") or {}).get("macro") or {}).get("friendly_name"),
        macro.get("friendly_name"),
        macro.get("name"),
    )
    if not reasons_text and (macro_name or detector_name):
        reasons_text = " / ".join(value for value in (macro_name, detector_name) if value)

    alert_id = first_state.get("alert_id") or body.get("guid")
    detector_value = _first_text(
        detector_name,
        (body.get("detector_ext") or {}).get("friendly_name"),
        macro_name,
        body.get("event_type"),
        fallback="ET_Alert",
    )
    camera_access_point = str(
        camera.get("access_point")
        or camera.get("id")
        or ((body.get("origin_ext") or {}).get("access_point"))
        or ""
    ).strip()
    camera_name = _first_text(
        camera.get("friendly_name"),
        camera.get("display_name"),
        (body.get("origin_ext") or {}).get("friendly_name"),
        camera_access_point,
        fallback="Camera",
    )

    trigger_body = alert_body.get("detector") or {}
    trigger_data = trigger_body.get("data", {}) or {}
    trigger_phase = normalize_detector_event_phase(
        event_type=str(trigger_body.get("event_type") or ""),
        state=trigger_body.get("state"),
        phase=trigger_data.get("phase"),
        detector_groups=trigger_body.get("detectors_group") or [],
    ) if trigger_body else None
    phase = normalize_alert_phase(first_state.get("state") or body.get("state") or "ACTIVE")

    trigger_hypotheses = trigger_data.get("Hypotheses") or []
    trigger_time_best = (
        trigger_hypotheses[0].get("TimeBest")
        if trigger_hypotheses and isinstance(trigger_hypotheses[0], dict)
        else None
    )

    return NormalizedEvent(
        id=body.get("guid") or alert_id,
        timestamp=(
            trigger_time_best
            or trigger_data.get("plate_appeared_time")
            or alert_body.get("timestamp")
            or first_state.get("timestamp")
            or body.get("timestamp")
        ),
        category="alert",
        source_kind="alert",
        event_type="ET_Alert",
        state=first_state.get("state") or body.get("state") or "ACTIVE",
        phase=phase,
        camera=camera_name,
        camera_access_point=camera_access_point,
        detector=detector_value,
        detector_access_point=str(detector_ext.get("access_point") or "").strip(),
        text=reasons_text or localization_text or "Alert",
        localization_text=localization_text,
        server=str((body.get("node_info") or {}).get("friendly_name") or "").strip(),
        priority=first_state.get("priority"),
        alert_id=alert_id,
        review_available=bool(alert_id and camera_access_point),
        actions=("frame", "clip_30s", "flag_confirmed", "flag_suspicious", "flag_false"),
        trigger_event_type=str(trigger_body.get("event_type") or "").strip() or None,
        trigger_state=str(trigger_body.get("state") or "").strip() or None,
        trigger_phase_family=trigger_phase.family if trigger_phase else None,
        trigger_phase_label=trigger_phase.label if trigger_phase else None,
    )


def _normalize_detector_event(event: dict[str, Any]) -> NormalizedEvent:
    body = event.get("body", {}) or {}
    event_type = str(body.get("event_type") or event.get("event_type") or "").strip()
    localization_text = str(((event.get("localization") or {}).get("text")) or "").strip()
    data = body.get("data", {}) or {}
    category = _category_from_raw_event(event)
    phase = normalize_detector_event_phase(
        event_type=event_type,
        state=body.get("state"),
        phase=data.get("phase"),
        detector_groups=body.get("detectors_group") or [],
    )
    plate = _extract_plate(body, localization_text)
    actions: tuple[str, ...] = ("frame", "clip_30s")
    if plate:
        actions = ("frame", "plate_crop", "clip_30s", "similar_plate")
    if category == "motion":
        actions = (*actions, "timeline_before_after")
    hypotheses = data.get("Hypotheses") or []
    time_best = hypotheses[0].get("TimeBest") if hypotheses and isinstance(hypotheses[0], dict) else None

    return NormalizedEvent(
        id=body.get("guid"),
        timestamp=(
            time_best
            or data.get("plate_appeared_time")
            or ((body.get("detector") or {}).get("timestamp"))
            or ((body.get("states") or [{}])[0].get("timestamp"))
            or body.get("timestamp")
        ),
        category=category,
        source_kind="detector_event",
        event_type=event_type,
        state=body.get("state"),
        phase=phase,
        camera=_event_camera_name(body),
        camera_access_point=str((body.get("origin_ext") or {}).get("access_point") or "").strip(),
        detector=_event_detector_name(body),
        detector_access_point=str((body.get("detector_ext") or {}).get("access_point") or "").strip(),
        text=localization_text,
        localization_text=localization_text,
        server=str((body.get("node_info") or {}).get("friendly_name") or "").strip(),
        plate=plate,
        vehicle=_vehicle_from_body(body),
        actions=actions,
        object_count=_extract_lots_object_count(body),
    )


def normalize_event(event: dict[str, Any]) -> NormalizedEvent:
    if str(event.get("event_type") or "").strip() == "ET_Alert":
        return _normalize_alert_event(event)
    return _normalize_detector_event(event)


def normalize_event_card(event: dict[str, Any]) -> dict[str, Any]:
    return normalize_event(event).to_telegram_card()


def classify_raw_event_category(event: dict[str, Any]) -> str:
    return _category_from_raw_event(event)


__all__ = [
    "NormalizedEvent",
    "NormalizedEventPhase",
    "NormalizedVehicle",
    "classify_raw_event_category",
    "event_operator_label_parts",
    "normalize_alert_phase",
    "normalize_detector_event_phase",
    "normalize_event",
    "normalize_event_card",
]
