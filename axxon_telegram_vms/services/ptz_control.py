"""Guardrail-first PTZ preset control helpers for the Step 28 MVP."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


DEFAULT_PTZ_CONTROL_SPEED = 5
MIN_PTZ_CONTROL_SPEED = 1
MAX_PTZ_CONTROL_SPEED = 15


class PtzControlSyntaxError(ValueError):
    """Raised when a command-style PTZ request is malformed."""


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


def _payload_copy(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _payload_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_payload_copy(item) for item in value]
    return value


def _coerce_int(value: object, field_name: str) -> int:
    try:
        return int(str(value).strip())
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def _coerce_speed(value: object) -> int:
    speed = _coerce_int(value, "speed")
    if speed < MIN_PTZ_CONTROL_SPEED or speed > MAX_PTZ_CONTROL_SPEED:
        raise ValueError(f"speed must be between {MIN_PTZ_CONTROL_SPEED} and {MAX_PTZ_CONTROL_SPEED}")
    return speed


def _friendly_label(name: object = "", display_id: object = "", fallback: object = "") -> str:
    text = _text(name)
    ident = _text(display_id)
    fb = _text(fallback)
    if ident and text and not text.startswith(f"{ident}."):
        return f"{ident}.{text}"
    return text or fb or ident or "—"


def _boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _normalized(value)
    return text in {"1", "true", "yes", "on", "y"}


@dataclass(frozen=True)
class PtzControlRequest:
    camera_name: str | None = None
    camera_access_point: str | None = None
    preset_label: str | None = None
    preset_position: int | None = None
    speed: int = DEFAULT_PTZ_CONTROL_SPEED

    def __post_init__(self) -> None:
        camera_name = _text(self.camera_name) or None
        camera_access_point = _text(self.camera_access_point) or None
        preset_label = _text(self.preset_label) or None
        preset_position = self.preset_position
        if bool(camera_name) == bool(camera_access_point):
            raise ValueError("Use exactly one camera selector: camera=... or camera_ap=...")
        if preset_position is not None:
            preset_position = _coerce_int(preset_position, "position")
            if preset_position < 0:
                raise ValueError("position must be zero or a positive integer")
        if preset_label and preset_position is not None:
            raise ValueError("Use exactly one preset selector: preset=... or position=...")
        object.__setattr__(self, "camera_name", camera_name)
        object.__setattr__(self, "camera_access_point", camera_access_point)
        object.__setattr__(self, "preset_label", preset_label)
        object.__setattr__(self, "preset_position", preset_position)
        object.__setattr__(self, "speed", _coerce_speed(self.speed))

    @property
    def camera_selector_kind(self) -> str:
        return "camera_ap" if self.camera_access_point else "camera"

    @property
    def camera_selector_value(self) -> str:
        return self.camera_access_point or self.camera_name or ""

    @property
    def preset_selector_kind(self) -> str | None:
        if self.preset_position is not None:
            return "position"
        if self.preset_label:
            return "preset"
        return None

    @property
    def preset_selector_value(self) -> str | None:
        if self.preset_position is not None:
            return str(self.preset_position)
        if self.preset_label:
            return self.preset_label
        return None

    @property
    def action(self) -> str:
        return "goto_preset" if self.has_action else "inspect"

    @property
    def has_action(self) -> bool:
        return self.preset_label is not None or self.preset_position is not None


@dataclass(frozen=True)
class PtzControlPolicy:
    control_enabled: bool = False
    admin: bool = False
    require_admin: bool = True
    allowed_camera_access_points: tuple[str, ...] = ()
    allowed_camera_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_camera_access_points", _split_csv_values(self.allowed_camera_access_points))
        object.__setattr__(self, "allowed_camera_names", _split_csv_values(self.allowed_camera_names))

    @property
    def allowlist_configured(self) -> bool:
        return bool(self.allowed_camera_access_points or self.allowed_camera_names)


@dataclass(frozen=True)
class PtzCameraRecord:
    camera_name: str
    camera_access_point: str
    display_id: str | None
    camera_access: str | None
    ptz_count: int
    ptz_active_count: int
    point_move: bool
    area_zoom: bool


@dataclass(frozen=True)
class PtzPresetRecord:
    position: int
    label: str


@dataclass(frozen=True)
class PtzGuardrailDecision:
    allowed: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


def build_ptz_control_request(
    *,
    camera_name: object = None,
    camera_access_point: object = None,
    preset_label: object = None,
    preset_position: object = None,
    speed: object = DEFAULT_PTZ_CONTROL_SPEED,
) -> PtzControlRequest:
    return PtzControlRequest(
        camera_name=_text(camera_name) or None,
        camera_access_point=_text(camera_access_point) or None,
        preset_label=_text(preset_label) or None,
        preset_position=preset_position,
        speed=speed,
    )


def build_ptz_control_policy(
    *,
    control_enabled: bool = False,
    admin: bool = False,
    require_admin: bool = True,
    allowed_camera_access_points: Iterable[object] = (),
    allowed_camera_names: Iterable[object] = (),
) -> PtzControlPolicy:
    return PtzControlPolicy(
        control_enabled=bool(control_enabled),
        admin=bool(admin),
        require_admin=bool(require_admin),
        allowed_camera_access_points=tuple(_split_csv_values(allowed_camera_access_points)),
        allowed_camera_names=tuple(_split_csv_values(allowed_camera_names)),
    )


_TERM_ALIASES = {
    "camera": "camera_name",
    "cam": "camera_name",
    "camera_name": "camera_name",
    "camera_ap": "camera_access_point",
    "camera_access_point": "camera_access_point",
    "camera_access_points": "camera_access_point",
    "preset": "preset_label",
    "preset_name": "preset_label",
    "position": "preset_position",
    "preset_position": "preset_position",
    "speed": "speed",
}


def parse_ptz_control_terms(terms: Iterable[object]) -> PtzControlRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise PtzControlSyntaxError("Use camera=... with an optional preset=... or position=....")

    values: dict[str, Any] = {"speed": DEFAULT_PTZ_CONTROL_SPEED}
    last_key = ""
    for term in raw_terms:
        if "=" not in term:
            if last_key in {"camera_name", "preset_label"}:
                values[last_key] = f"{values[last_key]} {term}".strip()
                continue
            raise PtzControlSyntaxError(f"Unsupported PTZ term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise PtzControlSyntaxError(f"Unsupported PTZ key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise PtzControlSyntaxError(f"PTZ value is required for: {raw_key}")
        values[key] = value
        last_key = key

    if not values.get("camera_name") and not values.get("camera_access_point"):
        raise PtzControlSyntaxError("Add camera=... or camera_ap=... to select one PTZ camera.")

    try:
        return build_ptz_control_request(
            camera_name=values.get("camera_name"),
            camera_access_point=values.get("camera_access_point"),
            preset_label=values.get("preset_label"),
            preset_position=values.get("preset_position"),
            speed=values.get("speed"),
        )
    except ValueError as exc:
        raise PtzControlSyntaxError(str(exc)) from exc


def ptz_control_request_to_api_args(request: PtzControlRequest) -> list[str]:
    args: list[str] = []
    if request.camera_access_point:
        args.extend(["--camera-ap", request.camera_access_point])
    elif request.camera_name:
        args.extend(["--camera", request.camera_name])
    if request.preset_label:
        args.extend(["--preset", request.preset_label])
    if request.preset_position is not None:
        args.extend(["--position", str(request.preset_position)])
    args.extend(["--speed", str(request.speed)])
    return args


def ptz_control_policy_to_api_args(policy: PtzControlPolicy) -> list[str]:
    args: list[str] = []
    if policy.control_enabled:
        args.append("--control-enabled")
    if policy.admin:
        args.append("--admin")
    if not policy.require_admin:
        args.append("--no-require-admin")
    for value in policy.allowed_camera_access_points:
        args.extend(["--allow-camera-ap", value])
    for value in policy.allowed_camera_names:
        args.extend(["--allow-camera-name", value])
    return args


def summarize_ptz_camera_row(row: Mapping[str, Any]) -> PtzCameraRecord:
    if not isinstance(row, Mapping):
        raise ValueError("PTZ camera row must be a mapping")
    camera_access_point = _text(row.get("access_point") or row.get("camera_access_point"))
    if not camera_access_point:
        raise ValueError("PTZ camera row is missing access_point")
    ptzs = row.get("ptzs") if isinstance(row.get("ptzs"), list) else []
    display_id = _text(row.get("display_id") or row.get("camera_display_id")) or None
    camera_name = _friendly_label(
        row.get("display_name") or row.get("camera_name") or row.get("name"),
        display_id,
        camera_access_point,
    )
    point_move = any(_boolish(item.get("pointMove") or item.get("point_move")) for item in ptzs if isinstance(item, Mapping))
    area_zoom = any(_boolish(item.get("areaZoom") or item.get("area_zoom")) for item in ptzs if isinstance(item, Mapping))
    ptz_active_count = sum(
        1
        for item in ptzs
        if isinstance(item, Mapping)
        and _boolish(item.get("is_active") or item.get("isActivated") or item.get("enabled"))
    )
    return PtzCameraRecord(
        camera_name=camera_name,
        camera_access_point=camera_access_point,
        display_id=display_id,
        camera_access=_text(row.get("camera_access")) or None,
        ptz_count=len(ptzs),
        ptz_active_count=ptz_active_count,
        point_move=point_move,
        area_zoom=area_zoom,
    )


def _camera_aliases(row: Mapping[str, Any], record: PtzCameraRecord) -> set[str]:
    aliases = {
        _normalized(record.camera_name),
        _normalized(record.camera_access_point),
        _normalized(row.get("display_name")),
        _normalized(row.get("camera_name")),
        _normalized(row.get("name")),
        _normalized(record.display_id),
    }
    aliases.discard("")
    return aliases


def select_ptz_camera_record(
    request: PtzControlRequest,
    camera_rows: Iterable[Mapping[str, Any]],
) -> PtzCameraRecord:
    matches: list[PtzCameraRecord] = []
    for row in camera_rows:
        if not isinstance(row, Mapping):
            continue
        try:
            record = summarize_ptz_camera_row(row)
        except ValueError:
            continue
        if request.camera_access_point:
            if _normalized(record.camera_access_point) == _normalized(request.camera_access_point):
                matches.append(record)
        elif _normalized(request.camera_name) in _camera_aliases(row, record):
            matches.append(record)

    if not matches:
        label = request.camera_access_point or request.camera_name or "camera"
        raise ValueError(f"PTZ camera not found: {label}")
    if len(matches) > 1:
        names = ", ".join(record.camera_name for record in matches[:3])
        raise ValueError(f"PTZ camera selector is ambiguous; use camera_ap=... instead ({names})")
    return matches[0]


def summarize_ptz_preset_row(row: Mapping[str, Any]) -> PtzPresetRecord:
    if not isinstance(row, Mapping):
        raise ValueError("PTZ preset row must be a mapping")
    raw_position = row.get("position")
    if raw_position is None:
        raw_position = row.get("preset_position")
    if raw_position is None:
        raise ValueError("PTZ preset row is missing position")
    position = _coerce_int(raw_position, "position")
    label = _text(row.get("label") or row.get("name") or row.get("preset_name")) or f"Preset {position}"
    return PtzPresetRecord(position=position, label=label)


def select_ptz_preset_record(
    request: PtzControlRequest,
    preset_rows: Iterable[Mapping[str, Any]],
) -> PtzPresetRecord:
    if not request.has_action:
        raise ValueError("A PTZ preset selector is required.")

    matches: list[PtzPresetRecord] = []
    for row in preset_rows:
        if not isinstance(row, Mapping):
            continue
        try:
            record = summarize_ptz_preset_row(row)
        except ValueError:
            continue
        if request.preset_position is not None:
            if record.position == request.preset_position:
                matches.append(record)
        elif request.preset_label and _normalized(record.label) == _normalized(request.preset_label):
            matches.append(record)

    if not matches:
        label = request.preset_label if request.preset_label else str(request.preset_position)
        raise ValueError(f"PTZ preset not found: {label}")
    if len(matches) > 1:
        names = ", ".join(f"{record.label} ({record.position})" for record in matches[:3])
        raise ValueError(f"PTZ preset selector is ambiguous; use position=... instead ({names})")
    return matches[0]


def build_ptz_goto_preset_backend_request(
    request: PtzControlRequest,
    camera: PtzCameraRecord,
    preset: PtzPresetRecord,
    *,
    session_id: object,
) -> dict[str, Any]:
    return {
        "access_point": camera.camera_access_point,
        "session_id": session_id,
        "position": preset.position,
        "speed": request.speed,
    }


def evaluate_ptz_control_guardrails(
    request: PtzControlRequest,
    camera: PtzCameraRecord,
    preset: PtzPresetRecord | None,
    policy: PtzControlPolicy,
    *,
    position_info: Mapping[str, Any] | None = None,
    preview_error: str | None = None,
) -> PtzGuardrailDecision:
    reasons: list[str] = []
    warnings: list[str] = ["Guardrails are re-checked immediately before execution."]

    if not policy.control_enabled:
        reasons.append("PTZ control is disabled by configuration.")
    if policy.require_admin and not policy.admin:
        reasons.append("PTZ control is restricted to Telegram admins.")
    if camera.ptz_count <= 0:
        reasons.append("Camera has no PTZ inventory in the current camera list.")
    elif camera.ptz_active_count <= 0:
        reasons.append("Camera PTZ inventory is present but not active.")

    if not policy.allowlist_configured:
        reasons.append("No PTZ camera allowlist is configured.")
    else:
        allow_aps = {_normalized(value) for value in policy.allowed_camera_access_points}
        allow_names = {_normalized(value) for value in policy.allowed_camera_names}
        if (
            _normalized(camera.camera_access_point) not in allow_aps
            and _normalized(camera.camera_name) not in allow_names
        ):
            reasons.append("Camera is not present in the configured PTZ allowlist.")

    if not request.has_action:
        reasons.append("Select one preset to enable PTZ movement.")
    if request.has_action and preset is None:
        reasons.append("Requested PTZ preset could not be resolved safely.")
    if request.has_action and preview_error:
        reasons.append("PTZ capability readback failed; refusing control without a truthful preview.")

    capabilities = position_info.get("capabilities") if isinstance(position_info, Mapping) else {}
    if request.has_action and isinstance(capabilities, Mapping) and not capabilities.get("move_supported"):
        reasons.append("PTZ move capability is not reported for this camera.")

    if camera.ptz_count > 1:
        warnings.append(f"Camera advertises {camera.ptz_count} PTZ devices; MVP uses the camera-level preset path only.")
    if camera.point_move or camera.area_zoom:
        warnings.append("Point/area PTZ capabilities exist but remain intentionally out of scope for this MVP.")

    return PtzGuardrailDecision(
        allowed=not reasons,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
    )


def _policy_payload(policy: PtzControlPolicy) -> dict[str, Any]:
    return {
        "control_enabled": policy.control_enabled,
        "admin": policy.admin,
        "require_admin": policy.require_admin,
        "allowlist_configured": policy.allowlist_configured,
        "allowed_camera_access_points": list(policy.allowed_camera_access_points),
        "allowed_camera_names": list(policy.allowed_camera_names),
    }


def _camera_payload(camera: PtzCameraRecord) -> dict[str, Any]:
    return {
        "name": camera.camera_name,
        "access_point": camera.camera_access_point,
        "display_id": camera.display_id,
        "camera_access": camera.camera_access,
        "ptz_count": camera.ptz_count,
        "ptz_active_count": camera.ptz_active_count,
        "point_move": camera.point_move,
        "area_zoom": camera.area_zoom,
    }


def _preset_payload(preset: PtzPresetRecord | None) -> dict[str, Any] | None:
    if preset is None:
        return None
    return {
        "label": preset.label,
        "position": preset.position,
    }


def shape_ptz_control_preview(
    request: PtzControlRequest,
    camera: PtzCameraRecord,
    decision: PtzGuardrailDecision,
    *,
    policy: PtzControlPolicy,
    position_info: Mapping[str, Any] | None = None,
    presets: Iterable[PtzPresetRecord] = (),
    preset: PtzPresetRecord | None = None,
    preview_error: str | None = None,
) -> dict[str, Any]:
    capability_payload = position_info if isinstance(position_info, Mapping) else {}
    preset_list = [_preset_payload(item) for item in presets]
    return {
        "request": {
            "camera_selector": {
                "kind": request.camera_selector_kind,
                "value": request.camera_selector_value,
            },
            "preset_selector": (
                {
                    "kind": request.preset_selector_kind,
                    "value": request.preset_selector_value,
                }
                if request.preset_selector_kind and request.preset_selector_value is not None
                else None
            ),
            "action": request.action,
            "speed": request.speed,
        },
        "camera": _camera_payload(camera),
        "ptz": {
            "capabilities": _payload_copy(capability_payload.get("capabilities")) if capability_payload else None,
            "absolute_position": _payload_copy(capability_payload.get("absolute_position")) if capability_payload else None,
            "preview_error": _text(preview_error) or None,
            "preset_count": len(preset_list),
            "presets": [item for item in preset_list if item],
            "selected_preset": _preset_payload(preset),
        },
        "guardrails": {
            "allowed": decision.allowed,
            "reasons": list(decision.reasons),
            "warnings": list(decision.warnings),
            "policy": _policy_payload(policy),
        },
    }


def shape_ptz_control_result(
    request: PtzControlRequest,
    camera: PtzCameraRecord,
    decision: PtzGuardrailDecision,
    *,
    policy: PtzControlPolicy,
    position_info: Mapping[str, Any] | None = None,
    presets: Iterable[PtzPresetRecord] = (),
    preset: PtzPresetRecord | None = None,
    preview_error: str | None = None,
    attempted: bool,
    ok: bool,
    transport: str | None = None,
    response: object = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload = shape_ptz_control_preview(
        request,
        camera,
        decision,
        policy=policy,
        position_info=position_info,
        presets=presets,
        preset=preset,
        preview_error=preview_error,
    )
    payload["execution"] = {
        "attempted": bool(attempted),
        "ok": bool(ok),
        "blocked": not decision.allowed,
        "transport": _text(transport) or None,
        "response": _payload_copy(response),
        "error": _text(error) or None,
    }
    return payload


__all__ = [
    "DEFAULT_PTZ_CONTROL_SPEED",
    "MAX_PTZ_CONTROL_SPEED",
    "MIN_PTZ_CONTROL_SPEED",
    "PtzCameraRecord",
    "PtzControlPolicy",
    "PtzControlRequest",
    "PtzControlSyntaxError",
    "PtzGuardrailDecision",
    "PtzPresetRecord",
    "build_ptz_control_policy",
    "build_ptz_control_request",
    "build_ptz_goto_preset_backend_request",
    "evaluate_ptz_control_guardrails",
    "parse_ptz_control_terms",
    "ptz_control_policy_to_api_args",
    "ptz_control_request_to_api_args",
    "select_ptz_camera_record",
    "select_ptz_preset_record",
    "shape_ptz_control_preview",
    "shape_ptz_control_result",
    "summarize_ptz_camera_row",
    "summarize_ptz_preset_row",
]
