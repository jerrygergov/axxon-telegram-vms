"""Cross-surface request and audit envelopes for future extension passes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any
import uuid


REQUEST_ACTIONS = (
    "admin",
    "analysis",
    "control",
    "read",
    "session",
)
REQUEST_SURFACES = (
    "telegram_bot",
    "future_web_app",
    "future_api_service",
)


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


def _payload_copy(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _payload_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_payload_copy(item) for item in value]
    return value


@dataclass(frozen=True)
class RequestActor:
    actor_id: str | None = None
    username: str | None = None
    role: str | None = None
    display_name: str | None = None

    def __post_init__(self) -> None:
        actor_id = _text(self.actor_id) or None
        username = _text(self.username) or None
        role = _text(self.role) or None
        display_name = _text(self.display_name) or username or actor_id or None
        object.__setattr__(self, "actor_id", actor_id)
        object.__setattr__(self, "username", username)
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "display_name", display_name)

    def as_log_fields(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "username": self.username,
            "role": self.role,
            "display_name": self.display_name,
        }


@dataclass(frozen=True)
class RequestAuditPolicy:
    audit_required: bool = True
    dry_run: bool = False
    retention_hint: str | None = None
    redact_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "retention_hint", _text(self.retention_hint) or None)
        object.__setattr__(self, "redact_fields", _split_csv_values(self.redact_fields))


@dataclass(frozen=True)
class RequestEnvelope:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    surface: str = "telegram_bot"
    action: str = "read"
    actor: RequestActor = field(default_factory=RequestActor)
    session_id: str | None = None
    correlation_id: str | None = None
    audit: RequestAuditPolicy = field(default_factory=RequestAuditPolicy)
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        request_id = _text(self.request_id) or uuid.uuid4().hex[:16]
        surface = _text(self.surface) or "telegram_bot"
        action = _text(self.action) or "read"
        if surface not in REQUEST_SURFACES:
            raise ValueError(f"Unsupported request surface: {self.surface}")
        if action not in REQUEST_ACTIONS:
            raise ValueError(f"Unsupported request action: {self.action}")
        if not isinstance(self.actor, RequestActor):
            raise ValueError("actor must be a RequestActor")
        if not isinstance(self.audit, RequestAuditPolicy):
            raise ValueError("audit must be a RequestAuditPolicy")
        metadata = _payload_copy(self.metadata) if isinstance(self.metadata, Mapping) else {}
        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "surface", surface)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "session_id", _text(self.session_id) or None)
        object.__setattr__(self, "correlation_id", _text(self.correlation_id) or None)
        object.__setattr__(self, "tags", _split_csv_values(self.tags))
        object.__setattr__(self, "metadata", metadata)

    def as_log_context(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "surface": self.surface,
            "action": self.action,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "tags": list(self.tags),
            "actor": self.actor.as_log_fields(),
            "audit": {
                "audit_required": self.audit.audit_required,
                "dry_run": self.audit.dry_run,
                "retention_hint": self.audit.retention_hint,
                "redact_fields": list(self.audit.redact_fields),
            },
            "metadata": _payload_copy(self.metadata),
        }


def build_request_actor(
    *,
    actor_id: object = None,
    username: object = None,
    role: object = None,
    display_name: object = None,
) -> RequestActor:
    return RequestActor(
        actor_id=_text(actor_id) or None,
        username=_text(username) or None,
        role=_text(role) or None,
        display_name=_text(display_name) or None,
    )


def build_request_audit_policy(
    *,
    audit_required: bool = True,
    dry_run: bool = False,
    retention_hint: object = None,
    redact_fields: Iterable[object] = (),
) -> RequestAuditPolicy:
    return RequestAuditPolicy(
        audit_required=bool(audit_required),
        dry_run=bool(dry_run),
        retention_hint=_text(retention_hint) or None,
        redact_fields=_split_csv_values(redact_fields),
    )


def build_request_envelope(
    *,
    request_id: object = None,
    surface: object = "telegram_bot",
    action: object = "read",
    actor: RequestActor | None = None,
    actor_id: object = None,
    username: object = None,
    role: object = None,
    display_name: object = None,
    session_id: object = None,
    correlation_id: object = None,
    audit: RequestAuditPolicy | None = None,
    audit_required: bool = True,
    dry_run: bool = False,
    retention_hint: object = None,
    redact_fields: Iterable[object] = (),
    tags: Iterable[object] = (),
    metadata: Mapping[str, Any] | None = None,
) -> RequestEnvelope:
    return RequestEnvelope(
        request_id=_text(request_id) or uuid.uuid4().hex[:16],
        surface=_text(surface) or "telegram_bot",
        action=_text(action) or "read",
        actor=actor or build_request_actor(
            actor_id=actor_id,
            username=username,
            role=role,
            display_name=display_name,
        ),
        session_id=_text(session_id) or None,
        correlation_id=_text(correlation_id) or None,
        audit=audit or build_request_audit_policy(
            audit_required=audit_required,
            dry_run=dry_run,
            retention_hint=retention_hint,
            redact_fields=redact_fields,
        ),
        tags=_split_csv_values(tags),
        metadata=metadata or {},
    )


__all__ = [
    "REQUEST_ACTIONS",
    "REQUEST_SURFACES",
    "RequestActor",
    "RequestAuditPolicy",
    "RequestEnvelope",
    "build_request_actor",
    "build_request_audit_policy",
    "build_request_envelope",
]
