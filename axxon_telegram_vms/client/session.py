"""Future-facing session/auth contracts grounded on checked-in web references."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote


SESSION_STORAGE_KEYS = (
    "authData",
    "cloudToken",
    "nextToken",
    "accessToken",
    "refreshToken",
    "expiredDate",
    "host",
    "port",
)
SESSION_CONTEXT_SURFACES = (
    "telegram_bot",
    "future_web_app",
    "future_api_service",
)
SESSION_STORAGE_SCOPES = (
    "memory",
    "secure_profile",
    "browser_storage",
)


def _text(value: object) -> str:
    return str(value or "").strip()


def _coerce_port(value: object) -> int:
    try:
        port = int(str(value).strip())
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("port must be a positive integer") from exc
    if port <= 0:
        raise ValueError("port must be a positive integer")
    return port


@dataclass(frozen=True)
class SessionTokenBundle:
    access_token: str | None = None
    refresh_token: str | None = None
    next_token: str | None = None
    cloud_token: str | None = None
    vms_token: str | None = None
    expires_at: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "access_token", _text(self.access_token) or None)
        object.__setattr__(self, "refresh_token", _text(self.refresh_token) or None)
        object.__setattr__(self, "next_token", _text(self.next_token) or None)
        object.__setattr__(self, "cloud_token", _text(self.cloud_token) or None)
        object.__setattr__(self, "vms_token", _text(self.vms_token) or None)
        object.__setattr__(self, "expires_at", _text(self.expires_at) or None)

    @property
    def preferred_bearer(self) -> str | None:
        return self.access_token or self.vms_token or self.cloud_token or None

    @property
    def renewable(self) -> bool:
        return bool(self.refresh_token or self.next_token or self.vms_token)

    @property
    def present_keys(self) -> tuple[str, ...]:
        out: list[str] = []
        if self.cloud_token:
            out.append("cloudToken")
        if self.next_token:
            out.append("nextToken")
        if self.access_token:
            out.append("accessToken")
        if self.refresh_token:
            out.append("refreshToken")
        if self.expires_at:
            out.append("expiredDate")
        return tuple(out)


@dataclass(frozen=True)
class WebSessionContract:
    host: str
    port: int = 80
    scheme: str = "http"
    authenticate_path: str = "/v1/authentication/authenticate_ex2"
    close_session_path: str = "/v1/authentication/close_session"
    renew_path: str = "/v1/authentication/renew"
    approve_path: str = "/v1/authentication:approve"
    decline_path: str = "/v1/authentication:decline"
    token_exchange_path: str = "/api/v1/auth/tokens"
    grpc_path: str = "/grpc"
    hosts_path: str = "/hosts"
    host_detail_path: str = "/hosts/{host}"
    languages_path: str = "/languages"
    vms_token_exchange_template: str = "/vmsToken?authToken={authToken}"
    vms_token_renew_template: str = "/renewVMSToken?vmsToken={vmsToken}"
    websocket_path_template: str = "/ws?authToken={token}"
    storage_keys: tuple[str, ...] = SESSION_STORAGE_KEYS
    supports_second_factor: bool = True
    supports_token_exchange: bool = True
    supports_vms_token_bridge: bool = True
    supports_multidomain_hosts: bool = True

    def __post_init__(self) -> None:
        scheme = _text(self.scheme).lower() or "http"
        if scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported scheme: {self.scheme}")
        host = _text(self.host)
        if not host:
            raise ValueError("host is required")
        object.__setattr__(self, "scheme", scheme)
        object.__setattr__(self, "host", host)
        object.__setattr__(self, "port", _coerce_port(self.port))
        object.__setattr__(self, "storage_keys", tuple(SESSION_STORAGE_KEYS))

    @property
    def base_url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"

    def endpoint_url(self, name: str, **params: object) -> str:
        path_map = {
            "authenticate": self.authenticate_path,
            "close_session": self.close_session_path,
            "renew": self.renew_path,
            "approve": self.approve_path,
            "decline": self.decline_path,
            "token_exchange": self.token_exchange_path,
            "grpc": self.grpc_path,
            "hosts": self.hosts_path,
            "host_detail": self.host_detail_path.format(host=quote(_text(params.get("host")), safe="")),
            "languages": self.languages_path,
            "vms_token_exchange": self.vms_token_exchange_template.format(
                authToken=quote(_text(params.get("authToken")), safe="")
            ),
            "vms_token_renew": self.vms_token_renew_template.format(
                vmsToken=quote(_text(params.get("vmsToken")), safe="")
            ),
            "websocket": self.websocket_path_template.format(token=quote(_text(params.get("token")), safe="")),
        }
        path = path_map.get(_text(name))
        if not path:
            raise KeyError(f"Unknown session endpoint: {name}")
        return f"{self.base_url}{path}"


@dataclass(frozen=True)
class WebSessionContext:
    contract: WebSessionContract
    surface: str = "telegram_bot"
    tokens: SessionTokenBundle = field(default_factory=SessionTokenBundle)
    current_user: str | None = None
    domain_id: str | None = None
    storage_scope: str = "memory"

    def __post_init__(self) -> None:
        if not isinstance(self.contract, WebSessionContract):
            raise ValueError("contract must be a WebSessionContract")
        surface = _text(self.surface) or "telegram_bot"
        if surface not in SESSION_CONTEXT_SURFACES:
            raise ValueError(f"Unsupported session surface: {self.surface}")
        storage_scope = _text(self.storage_scope) or "memory"
        if storage_scope not in SESSION_STORAGE_SCOPES:
            raise ValueError(f"Unsupported session storage scope: {self.storage_scope}")
        object.__setattr__(self, "surface", surface)
        object.__setattr__(self, "current_user", _text(self.current_user) or None)
        object.__setattr__(self, "domain_id", _text(self.domain_id) or None)
        object.__setattr__(self, "storage_scope", storage_scope)

    @property
    def has_bearer_auth(self) -> bool:
        return bool(self.tokens.preferred_bearer)


def build_web_session_contract(
    *,
    host: object,
    port: object = 80,
    scheme: object = "http",
) -> WebSessionContract:
    return WebSessionContract(
        host=_text(host),
        port=port,
        scheme=_text(scheme) or "http",
    )


def session_token_bundle_from_payload(payload: Mapping[str, Any] | None = None) -> SessionTokenBundle:
    data = payload if isinstance(payload, Mapping) else {}
    return SessionTokenBundle(
        access_token=_text(data.get("accessToken") or data.get("access_token") or data.get("token")) or None,
        refresh_token=_text(data.get("refreshToken") or data.get("refresh_token")) or None,
        next_token=_text(data.get("nextToken") or data.get("next_token")) or None,
        cloud_token=_text(data.get("cloudToken") or data.get("cloud_token")) or None,
        vms_token=_text(data.get("vmsToken") or data.get("vms_token")) or None,
        expires_at=_text(data.get("expiredDate") or data.get("expiresAt") or data.get("expires_at")) or None,
    )


def build_web_session_context(
    *,
    host: object,
    port: object = 80,
    scheme: object = "http",
    surface: object = "telegram_bot",
    token_payload: Mapping[str, Any] | None = None,
    current_user: object = None,
    domain_id: object = None,
    storage_scope: object = "memory",
) -> WebSessionContext:
    return WebSessionContext(
        contract=build_web_session_contract(host=host, port=port, scheme=scheme),
        surface=_text(surface) or "telegram_bot",
        tokens=session_token_bundle_from_payload(token_payload),
        current_user=_text(current_user) or None,
        domain_id=_text(domain_id) or None,
        storage_scope=_text(storage_scope) or "memory",
    )


def session_bearer_headers(tokens: SessionTokenBundle | WebSessionContext) -> dict[str, str]:
    bundle = tokens.tokens if isinstance(tokens, WebSessionContext) else tokens
    bearer = bundle.preferred_bearer if isinstance(bundle, SessionTokenBundle) else None
    if not bearer:
        return {}
    return {"Authorization": f"Bearer {bearer}"}


def session_storage_snapshot(context: WebSessionContext) -> dict[str, Any]:
    return {
        "accessToken": context.tokens.access_token,
        "refreshToken": context.tokens.refresh_token,
        "nextToken": context.tokens.next_token,
        "cloudToken": context.tokens.cloud_token,
        "expiredDate": context.tokens.expires_at,
        "host": context.contract.host,
        "port": context.contract.port,
    }


def shape_web_session_summary(context: WebSessionContext) -> dict[str, Any]:
    return {
        "surface": context.surface,
        "base_url": context.contract.base_url,
        "current_user": context.current_user,
        "domain_id": context.domain_id,
        "storage_scope": context.storage_scope,
        "has_bearer_auth": context.has_bearer_auth,
        "renewable": context.tokens.renewable,
        "token_keys_present": list(context.tokens.present_keys),
        "supports": {
            "second_factor": context.contract.supports_second_factor,
            "token_exchange": context.contract.supports_token_exchange,
            "vms_token_bridge": context.contract.supports_vms_token_bridge,
            "multidomain_hosts": context.contract.supports_multidomain_hosts,
        },
        "paths": {
            "authenticate": context.contract.endpoint_url("authenticate"),
            "renew": context.contract.endpoint_url("renew"),
            "close_session": context.contract.endpoint_url("close_session"),
            "token_exchange": context.contract.endpoint_url("token_exchange"),
            "grpc": context.contract.endpoint_url("grpc"),
            "hosts": context.contract.endpoint_url("hosts"),
            "languages": context.contract.endpoint_url("languages"),
        },
    }


__all__ = [
    "SESSION_CONTEXT_SURFACES",
    "SESSION_STORAGE_KEYS",
    "SESSION_STORAGE_SCOPES",
    "SessionTokenBundle",
    "WebSessionContext",
    "WebSessionContract",
    "build_web_session_context",
    "build_web_session_contract",
    "session_bearer_headers",
    "session_storage_snapshot",
    "session_token_bundle_from_payload",
    "shape_web_session_summary",
]
