"""Guardrail-first macro execution helpers for the Step 27 MVP."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


DEFAULT_ALLOWED_MACRO_MODE_KINDS = ("common",)
DEFAULT_DENIED_MACRO_ACTION_FAMILIES = (
    "acfa",
    "arm_state",
    "disarm_state",
    "export",
    "goto_ptz",
    "gui",
    "macro",
    "replication",
    "service_state",
    "switch_relay",
    "web_query",
    "write_archive",
)
KNOWN_MACRO_ACTION_FAMILIES = (
    "acfa",
    "arm_state",
    "audio_notification",
    "close_alert",
    "disarm_state",
    "email_notification",
    "export",
    "goto_ptz",
    "gui",
    "macro",
    "push_event",
    "raise_alert",
    "replication",
    "service_state",
    "switch_relay",
    "web_query",
    "write_archive",
)


class MacroExecutionSyntaxError(ValueError):
    """Raised when a command-style macro execution request is malformed."""


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


def _mapping_count(value: object) -> int:
    if isinstance(value, Mapping):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 0


def _mode_kind(mode: Mapping[str, Any] | None) -> str:
    if not isinstance(mode, Mapping):
        return "unknown"
    for key in ("common", "autorule", "continuous", "timezone"):
        if key in mode and isinstance(mode.get(key), Mapping):
            return key
    if "enabled" in mode or "is_add_to_menu" in mode:
        return "common"
    return "unknown"


def _collect_action_families(node: object, out: set[str]) -> None:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if isinstance(key, str) and key in KNOWN_MACRO_ACTION_FAMILIES:
                out.add(key)
            _collect_action_families(value, out)
        return
    if isinstance(node, list):
        for value in node:
            _collect_action_families(value, out)


def _payload_copy(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _payload_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_payload_copy(item) for item in value]
    return value


@dataclass(frozen=True)
class MacroExecutionRequest:
    macro_id: str | None = None
    macro_name: str | None = None

    def __post_init__(self) -> None:
        macro_id = _text(self.macro_id) or None
        macro_name = _text(self.macro_name) or None
        if bool(macro_id) == bool(macro_name):
            raise ValueError("Use exactly one selector: id=... or name=...")
        object.__setattr__(self, "macro_id", macro_id)
        object.__setattr__(self, "macro_name", macro_name)

    @property
    def selector_kind(self) -> str:
        return "id" if self.macro_id else "name"

    @property
    def selector_value(self) -> str:
        return self.macro_id or self.macro_name or ""


@dataclass(frozen=True)
class MacroExecutionPolicy:
    execution_enabled: bool = False
    admin: bool = False
    require_admin: bool = True
    allowed_macro_ids: tuple[str, ...] = ()
    allowed_macro_names: tuple[str, ...] = ()
    allowed_mode_kinds: tuple[str, ...] = DEFAULT_ALLOWED_MACRO_MODE_KINDS
    denied_action_families: tuple[str, ...] = DEFAULT_DENIED_MACRO_ACTION_FAMILIES
    require_enabled: bool = True
    require_add_to_menu: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_macro_ids", _split_csv_values(self.allowed_macro_ids))
        object.__setattr__(self, "allowed_macro_names", _split_csv_values(self.allowed_macro_names))
        object.__setattr__(self, "allowed_mode_kinds", _split_csv_values(self.allowed_mode_kinds))
        object.__setattr__(self, "denied_action_families", _split_csv_values(self.denied_action_families))

    @property
    def allowlist_configured(self) -> bool:
        return bool(self.allowed_macro_ids or self.allowed_macro_names)


@dataclass(frozen=True)
class MacroInventoryRecord:
    macro_id: str
    name: str
    enabled: bool
    user_role: str | None
    is_add_to_menu: bool
    mode_kind: str
    action_families: tuple[str, ...]
    conditions_count: int
    rules_count: int


@dataclass(frozen=True)
class MacroGuardrailDecision:
    allowed: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


def build_macro_execution_request(
    *,
    macro_id: object = None,
    macro_name: object = None,
) -> MacroExecutionRequest:
    return MacroExecutionRequest(
        macro_id=_text(macro_id) or None,
        macro_name=_text(macro_name) or None,
    )


def build_macro_execution_policy(
    *,
    execution_enabled: bool = False,
    admin: bool = False,
    require_admin: bool = True,
    allowed_macro_ids: Iterable[object] = (),
    allowed_macro_names: Iterable[object] = (),
    allowed_mode_kinds: Iterable[object] = DEFAULT_ALLOWED_MACRO_MODE_KINDS,
    denied_action_families: Iterable[object] = DEFAULT_DENIED_MACRO_ACTION_FAMILIES,
    require_enabled: bool = True,
    require_add_to_menu: bool = True,
) -> MacroExecutionPolicy:
    return MacroExecutionPolicy(
        execution_enabled=bool(execution_enabled),
        admin=bool(admin),
        require_admin=bool(require_admin),
        allowed_macro_ids=tuple(_split_csv_values(allowed_macro_ids)),
        allowed_macro_names=tuple(_split_csv_values(allowed_macro_names)),
        allowed_mode_kinds=tuple(_split_csv_values(allowed_mode_kinds)),
        denied_action_families=tuple(_split_csv_values(denied_action_families)),
        require_enabled=bool(require_enabled),
        require_add_to_menu=bool(require_add_to_menu),
    )


_TERM_ALIASES = {
    "id": "macro_id",
    "guid": "macro_id",
    "macro_id": "macro_id",
    "name": "macro_name",
    "macro": "macro_name",
    "macro_name": "macro_name",
}


def parse_macro_execution_terms(terms: Iterable[object]) -> MacroExecutionRequest:
    raw_terms = [str(term or "").strip() for term in (terms or []) if str(term or "").strip()]
    if not raw_terms:
        raise MacroExecutionSyntaxError("Use id=... or name=... to select one macro.")

    values: dict[str, str] = {}
    last_key = ""
    for term in raw_terms:
        if "=" not in term:
            if last_key == "macro_name":
                values[last_key] = f"{values[last_key]} {term}".strip()
                continue
            raise MacroExecutionSyntaxError(f"Unsupported macro term: {term}")
        raw_key, raw_value = term.split("=", 1)
        key = _TERM_ALIASES.get(raw_key.strip().lower())
        if not key:
            raise MacroExecutionSyntaxError(f"Unsupported macro key: {raw_key}")
        value = raw_value.strip()
        if not value:
            raise MacroExecutionSyntaxError(f"Macro value is required for: {raw_key}")
        values[key] = value
        last_key = key

    try:
        return build_macro_execution_request(
            macro_id=values.get("macro_id"),
            macro_name=values.get("macro_name"),
        )
    except ValueError as exc:
        raise MacroExecutionSyntaxError(str(exc)) from exc


def macro_execution_request_to_api_args(request: MacroExecutionRequest) -> list[str]:
    if request.macro_id:
        return ["--macro-id", request.macro_id]
    if request.macro_name:
        return ["--macro-name", request.macro_name]
    raise ValueError("Macro execution request must include a selector")


def macro_execution_policy_to_api_args(policy: MacroExecutionPolicy) -> list[str]:
    args: list[str] = []
    if policy.execution_enabled:
        args.append("--execution-enabled")
    if policy.admin:
        args.append("--admin")
    if not policy.require_admin:
        args.append("--no-require-admin")
    if not policy.require_enabled:
        args.append("--allow-disabled")
    if not policy.require_add_to_menu:
        args.append("--allow-hidden")
    for value in policy.allowed_macro_ids:
        args.extend(["--allow-id", value])
    for value in policy.allowed_macro_names:
        args.extend(["--allow-name", value])
    return args


def summarize_macro_inventory_row(row: Mapping[str, Any]) -> MacroInventoryRecord:
    if not isinstance(row, Mapping):
        raise ValueError("Macro inventory row must be a mapping")
    mode = row.get("mode") if isinstance(row.get("mode"), Mapping) else {}
    action_families: set[str] = set()
    _collect_action_families(row.get("rules"), action_families)
    macro_id = _text(row.get("guid") or row.get("id"))
    if not macro_id:
        raise ValueError("Macro inventory row is missing guid/id")
    return MacroInventoryRecord(
        macro_id=macro_id,
        name=_text(row.get("name")) or macro_id,
        enabled=bool(mode.get("enabled")),
        user_role=_text(mode.get("user_role")) or None,
        is_add_to_menu=bool(mode.get("is_add_to_menu")),
        mode_kind=_mode_kind(mode),
        action_families=tuple(sorted(action_families)),
        conditions_count=_mapping_count(row.get("conditions")),
        rules_count=_mapping_count(row.get("rules")),
    )


def select_macro_inventory_record(
    request: MacroExecutionRequest,
    macro_rows: Iterable[Mapping[str, Any]],
) -> MacroInventoryRecord:
    matches: list[MacroInventoryRecord] = []
    for row in macro_rows:
        if not isinstance(row, Mapping):
            continue
        try:
            record = summarize_macro_inventory_row(row)
        except ValueError:
            continue
        if request.macro_id and _normalized(record.macro_id) == _normalized(request.macro_id):
            matches.append(record)
        elif request.macro_name and _normalized(record.name) == _normalized(request.macro_name):
            matches.append(record)

    if not matches:
        label = request.macro_id or request.macro_name or "macro"
        raise ValueError(f"Macro not found: {label}")
    if len(matches) > 1:
        ids = ", ".join(record.macro_id for record in matches[:3])
        raise ValueError(f"Macro selector is ambiguous; use id=... instead ({ids})")
    return matches[0]


def evaluate_macro_execution_guardrails(
    record: MacroInventoryRecord,
    policy: MacroExecutionPolicy,
) -> MacroGuardrailDecision:
    reasons: list[str] = []
    warnings: list[str] = [
        "Guardrails are re-checked immediately before execution.",
    ]

    if not policy.execution_enabled:
        reasons.append("Macro execution is disabled by configuration.")
    if policy.require_admin and not policy.admin:
        reasons.append("Macro execution is restricted to Telegram admins.")
    if policy.require_enabled and not record.enabled:
        reasons.append("Macro is disabled in the Axxon inventory.")
    if policy.require_add_to_menu and not record.is_add_to_menu:
        reasons.append("Macro is not marked as a manual menu action.")
    if record.mode_kind not in set(policy.allowed_mode_kinds):
        allowed = ", ".join(policy.allowed_mode_kinds) or "manual"
        reasons.append(f"Macro mode `{record.mode_kind}` is blocked; allowed modes: {allowed}.")
    if record.rules_count <= 0:
        reasons.append("Macro has no executable rules.")
    if not record.action_families:
        reasons.append("Macro action families could not be identified safely from inventory.")

    if not policy.allowlist_configured:
        reasons.append("No macro allowlist is configured.")
    else:
        allow_ids = {_normalized(value) for value in policy.allowed_macro_ids}
        allow_names = {_normalized(value) for value in policy.allowed_macro_names}
        if _normalized(record.macro_id) not in allow_ids and _normalized(record.name) not in allow_names:
            reasons.append("Macro is not present in the configured allowlist.")

    denied = sorted(
        family for family in record.action_families if _normalized(family) in {_normalized(x) for x in policy.denied_action_families}
    )
    if denied:
        reasons.append(f"Action families blocked by policy: {', '.join(denied)}.")

    if record.user_role:
        warnings.append(f"Axxon user_role hint: {record.user_role}.")

    return MacroGuardrailDecision(
        allowed=not reasons,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
    )


def _macro_payload(record: MacroInventoryRecord) -> dict[str, Any]:
    return {
        "id": record.macro_id,
        "name": record.name,
        "enabled": record.enabled,
        "user_role": record.user_role,
        "is_add_to_menu": record.is_add_to_menu,
        "mode_kind": record.mode_kind,
        "action_families": list(record.action_families),
        "conditions_count": record.conditions_count,
        "rules_count": record.rules_count,
    }


def _policy_payload(policy: MacroExecutionPolicy) -> dict[str, Any]:
    return {
        "execution_enabled": policy.execution_enabled,
        "admin": policy.admin,
        "require_admin": policy.require_admin,
        "require_enabled": policy.require_enabled,
        "require_add_to_menu": policy.require_add_to_menu,
        "allowlist_configured": policy.allowlist_configured,
        "allowed_mode_kinds": list(policy.allowed_mode_kinds),
        "denied_action_families": list(policy.denied_action_families),
    }


def shape_macro_execution_preview(
    request: MacroExecutionRequest,
    record: MacroInventoryRecord,
    decision: MacroGuardrailDecision,
    *,
    policy: MacroExecutionPolicy,
) -> dict[str, Any]:
    return {
        "request": {
            "selector": {
                "kind": request.selector_kind,
                "value": request.selector_value,
            }
        },
        "macro": _macro_payload(record),
        "guardrails": {
            "allowed": decision.allowed,
            "reasons": list(decision.reasons),
            "warnings": list(decision.warnings),
            "policy": _policy_payload(policy),
        },
    }


def shape_macro_execution_result(
    request: MacroExecutionRequest,
    record: MacroInventoryRecord,
    decision: MacroGuardrailDecision,
    *,
    policy: MacroExecutionPolicy,
    attempted: bool,
    ok: bool,
    transport: str | None = None,
    response: object = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload = shape_macro_execution_preview(request, record, decision, policy=policy)
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
    "DEFAULT_ALLOWED_MACRO_MODE_KINDS",
    "DEFAULT_DENIED_MACRO_ACTION_FAMILIES",
    "KNOWN_MACRO_ACTION_FAMILIES",
    "MacroExecutionPolicy",
    "MacroExecutionRequest",
    "MacroExecutionSyntaxError",
    "MacroGuardrailDecision",
    "MacroInventoryRecord",
    "build_macro_execution_policy",
    "build_macro_execution_request",
    "evaluate_macro_execution_guardrails",
    "macro_execution_policy_to_api_args",
    "macro_execution_request_to_api_args",
    "parse_macro_execution_terms",
    "select_macro_inventory_record",
    "shape_macro_execution_preview",
    "shape_macro_execution_result",
    "summarize_macro_inventory_row",
]
