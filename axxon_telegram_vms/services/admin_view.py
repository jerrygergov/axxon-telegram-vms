"""Read-only admin inspection helpers for the Step 29 foundation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


DEFAULT_ADMIN_FUTURE_WRITE_BOUNDARIES = (
    "host_inventory",
    "role_access_summary",
    "future_config_dry_run",
)
DEFAULT_ADMIN_AUDITED_ACTION_SURFACES = (
    "macro_execution",
    "ptz_control",
)
ADMIN_FEATURE_ACCESS = {
    "FEATURE_ACCESS_ARCHIVES_SETUP",
    "FEATURE_ACCESS_DETECTORS_SETUP",
    "FEATURE_ACCESS_DEVICES_SETUP",
    "FEATURE_ACCESS_DOMAIN_MANAGING_OPS",
    "FEATURE_ACCESS_PROGRAMMING_SETUP",
    "FEATURE_ACCESS_SETTINGS_SETUP",
    "FEATURE_ACCESS_USERS_RIGHTS_SETUP",
}


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


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _first_mapping(value: object) -> Mapping[str, Any]:
    items = _mapping_list(value)
    return items[0] if items else {}


def _to_int(value: object) -> int | None:
    text = _text(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _boolish(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = _normalized(value)
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return None


def _timezone_label(minutes: object) -> str | None:
    value = _to_int(minutes)
    if value is None:
        return None
    sign = "+" if value >= 0 else "-"
    total = abs(value)
    hours, mins = divmod(total, 60)
    return f"UTC{sign}{hours:02d}:{mins:02d}"


def _feature_flags(feature_access: Iterable[object]) -> dict[str, bool]:
    features = {_text(item) for item in feature_access if _text(item)}
    return {
        "domain_ops": "FEATURE_ACCESS_DOMAIN_MANAGING_OPS" in features,
        "export": "FEATURE_ACCESS_EXPORT" in features,
        "search": "FEATURE_ACCESS_SEARCH" in features,
        "users_rights_setup": "FEATURE_ACCESS_USERS_RIGHTS_SETUP" in features,
        "devices_setup": "FEATURE_ACCESS_DEVICES_SETUP" in features,
        "archives_setup": "FEATURE_ACCESS_ARCHIVES_SETUP" in features,
        "detectors_setup": "FEATURE_ACCESS_DETECTORS_SETUP" in features,
        "programming_setup": "FEATURE_ACCESS_PROGRAMMING_SETUP" in features,
        "settings_setup": "FEATURE_ACCESS_SETTINGS_SETUP" in features,
        "web_ui_login": "FEATURE_ACCESS_WEB_UI_LOGIN" in features,
    }


def _user_login(user: Mapping[str, Any]) -> str:
    return _text(
        user.get("login")
        or user.get("loginname")
        or user.get("name")
    )


@dataclass(frozen=True)
class AdminViewPolicy:
    admin: bool = False
    require_admin: bool = True
    read_only: bool = True
    config_write_enabled: bool = False
    dry_run_required: bool = True
    audit_required: bool = True
    future_write_boundaries: tuple[str, ...] = DEFAULT_ADMIN_FUTURE_WRITE_BOUNDARIES
    audited_action_surfaces: tuple[str, ...] = DEFAULT_ADMIN_AUDITED_ACTION_SURFACES

    def __post_init__(self) -> None:
        object.__setattr__(self, "future_write_boundaries", _split_csv_values(self.future_write_boundaries))
        object.__setattr__(self, "audited_action_surfaces", _split_csv_values(self.audited_action_surfaces))


def build_admin_view_policy(
    *,
    admin: bool = False,
    require_admin: bool = True,
    read_only: bool = True,
    config_write_enabled: bool = False,
    dry_run_required: bool = True,
    audit_required: bool = True,
    future_write_boundaries: Iterable[object] = DEFAULT_ADMIN_FUTURE_WRITE_BOUNDARIES,
    audited_action_surfaces: Iterable[object] = DEFAULT_ADMIN_AUDITED_ACTION_SURFACES,
) -> AdminViewPolicy:
    return AdminViewPolicy(
        admin=bool(admin),
        require_admin=bool(require_admin),
        read_only=bool(read_only),
        config_write_enabled=bool(config_write_enabled),
        dry_run_required=bool(dry_run_required),
        audit_required=bool(audit_required),
        future_write_boundaries=tuple(_split_csv_values(future_write_boundaries)),
        audited_action_surfaces=tuple(_split_csv_values(audited_action_surfaces)),
    )


def admin_view_policy_to_api_args(policy: AdminViewPolicy) -> list[str]:
    return ["--admin"] if policy.admin else []


def shape_host_inventory(
    hosts: Iterable[object] = (),
    host_details: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    detail_map = {
        _text(key): value
        for key, value in (host_details or {}).items()
        if _text(key)
    }
    ordered_names: list[str] = []
    seen_names: set[str] = set()
    for raw in tuple(hosts or ()) + tuple(detail_map.keys()):
        name = _text(raw)
        if not name or name.casefold() in seen_names:
            continue
        seen_names.add(name.casefold())
        ordered_names.append(name)

    items: list[dict[str, Any]] = []
    domain_counts: Counter[str] = Counter()
    license_counts: Counter[str] = Counter()
    host_name_keys: set[str] = set()
    for name in sorted(ordered_names, key=str.casefold):
        detail = _mapping(detail_map.get(name))
        domain_info = _mapping(detail.get("domainInfo"))
        platform_info = _mapping(detail.get("platformInfo"))
        cluster_nodes = [
            _text(value)
            for value in (detail.get("nodes") or [])
            if _text(value)
        ]
        item = {
            "node_name": _text(detail.get("nodeName")) or name,
            "host_name": _text(platform_info.get("hostName")) or name,
            "domain_name": _text(domain_info.get("domainName")) or None,
            "domain_friendly_name": _text(domain_info.get("domainFriendlyName")) or None,
            "license_status": _text(detail.get("licenseStatus")) or None,
            "time_zone_minutes": detail.get("timeZone"),
            "time_zone_label": _timezone_label(detail.get("timeZone")),
            "os": _text(platform_info.get("os")) or None,
            "machine": _text(platform_info.get("machine")) or None,
            "cluster_nodes": cluster_nodes,
            "cluster_node_count": len(cluster_nodes),
        }
        items.append(item)
        domain_key = _text(item.get("domain_friendly_name") or item.get("domain_name")) or "unknown"
        domain_counts[domain_key] += 1
        license_key = _text(item.get("license_status")) or "unknown"
        license_counts[license_key] += 1
        host_name = _text(item.get("host_name"))
        if host_name:
            host_name_keys.add(host_name.casefold())

    top_domains = [
        {"name": name, "nodes": count}
        for name, count in sorted(domain_counts.items(), key=lambda item: (-item[1], item[0].casefold()))
    ]
    return {
        "summary": {
            "node_count": len(items),
            "host_count": len(host_name_keys),
            "domain_count": len(domain_counts),
            "license_status_counts": dict(sorted(license_counts.items())),
        },
        "domains": top_domains,
        "items": items,
    }


def shape_access_summary(
    security_config: Mapping[str, Any] | None = None,
    global_permissions: Mapping[str, Any] | None = None,
    current_user: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    config = _mapping(security_config)
    permissions_root = _mapping(
        _mapping(global_permissions).get("permissions")
        if isinstance(_mapping(global_permissions).get("permissions"), Mapping)
        else global_permissions
    )
    roles = _mapping_list(config.get("roles"))
    users = _mapping_list(config.get("users"))
    assignments = _mapping_list(config.get("user_assignments"))
    ldap_servers = _mapping_list(config.get("ldap_servers"))
    pwd_policy = _first_mapping(config.get("pwd_policy"))
    ip_filters = _mapping_list(config.get("ip_filters"))
    trusted_ip_list = [_text(item) for item in (config.get("trusted_ip_list") or []) if _text(item)]

    role_map = {
        _text(role.get("index")): role
        for role in roles
        if _text(role.get("index"))
    }
    user_by_login = {
        _normalized(_user_login(user)): user
        for user in users
        if _user_login(user)
    }

    user_role_ids: dict[str, list[str]] = {}
    role_user_counts: Counter[str] = Counter()
    for assignment in assignments:
        user_id = _text(assignment.get("user_id"))
        role_id = _text(assignment.get("role_id"))
        if not user_id or not role_id:
            continue
        user_role_ids.setdefault(user_id, []).append(role_id)
        role_user_counts[role_id] += 1

    current_user_name = _text(
        _mapping(current_user).get("currentuser")
        or _mapping(current_user).get("current_user")
        or _mapping(current_user).get("name")
    )
    matched_user = user_by_login.get(_normalized(current_user_name)) if current_user_name else None
    matched_user_id = _text((matched_user or {}).get("index"))
    current_role_ids = user_role_ids.get(matched_user_id, [])
    current_role_names = [
        _text(_mapping(role_map.get(role_id)).get("name")) or role_id
        for role_id in current_role_ids
        if role_id
    ]

    role_items: list[dict[str, Any]] = []
    for role in roles:
        role_id = _text(role.get("index"))
        if not role_id:
            continue
        permissions = _mapping(permissions_root.get(role_id))
        feature_access = [
            _text(item)
            for item in (permissions.get("feature_access") or [])
            if _text(item)
        ]
        flags = _feature_flags(feature_access)
        item = {
            "role_id": role_id,
            "name": _text(role.get("name")) or role_id,
            "comment": _text(role.get("comment")) or None,
            "user_count": role_user_counts.get(role_id, 0),
            "feature_access_count": len(feature_access),
            "admin_feature_count": len(set(feature_access) & ADMIN_FEATURE_ACCESS),
            "maps_access": _text(permissions.get("maps_access")) or None,
            "alert_access": _text(permissions.get("alert_access")) or None,
            "unrestricted_access": _text(permissions.get("unrestricted_access")) or None,
            "default_camera_access": _text(permissions.get("default_camera_access")) or None,
            "default_archive_access": _text(permissions.get("default_archive_access")) or None,
            "default_macros_access": _text(permissions.get("default_macros_access")) or None,
            "default_telemetry_priority": _text(permissions.get("default_telemetry_priority")) or None,
            "feature_access": feature_access,
            "privileges": flags,
        }
        role_items.append(item)

    role_items.sort(
        key=lambda item: (
            -int(item.get("admin_feature_count") or 0),
            -int(item.get("user_count") or 0),
            _text(item.get("name")).casefold(),
        )
    )

    enabled_user_count = 0
    for user in users:
        enabled = _boolish(user.get("enabled"))
        if enabled:
            enabled_user_count += 1

    summary = {
        "role_count": len(role_items),
        "permissions_role_count": len([item for item in role_items if item.get("feature_access_count") or item.get("maps_access")]),
        "user_count": len(users),
        "enabled_user_count": enabled_user_count,
        "disabled_user_count": max(0, len(users) - enabled_user_count),
        "assignment_count": len(assignments),
        "ldap_server_count": len(ldap_servers),
        "ip_filter_count": len(ip_filters),
        "trusted_ip_count": len(trusted_ip_list),
        "password_min_length": _to_int(
            pwd_policy.get("minimum_password_length")
            or pwd_policy.get("min_length")
        ),
        "password_complexity_required": _boolish(
            pwd_policy.get("password_must_meet_complexity_requirements")
            or pwd_policy.get("must_meet_complexity_requirements")
        ),
        "roles_with_domain_ops": len([item for item in role_items if _mapping(item.get("privileges")).get("domain_ops")]),
        "roles_with_user_rights_setup": len([item for item in role_items if _mapping(item.get("privileges")).get("users_rights_setup")]),
        "roles_with_export": len([item for item in role_items if _mapping(item.get("privileges")).get("export")]),
        "roles_with_search": len([item for item in role_items if _mapping(item.get("privileges")).get("search")]),
    }

    current_user_payload = {
        "axxon_user": current_user_name or None,
        "matched_user_id": matched_user_id or None,
        "matched_login": _user_login(_mapping(matched_user)) or None,
        "matched_name": _text((matched_user or {}).get("name")) or None,
        "matched_enabled": _boolish((matched_user or {}).get("enabled")),
        "role_ids": [role_id for role_id in current_role_ids if role_id],
        "role_names": [role_name for role_name in current_role_names if role_name],
        "restrictions": _payload_copy(_mapping((matched_user or {}).get("restrictions"))),
    }

    return {
        "summary": summary,
        "roles": role_items,
        "current_user": current_user_payload,
    }


def shape_admin_capability_surface(
    hosts: Mapping[str, Any],
    access: Mapping[str, Any],
    server_info: Mapping[str, Any] | None,
    policy: AdminViewPolicy,
    runtime_capabilities: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    host_summary = _mapping(hosts.get("summary"))
    access_summary = _mapping(access.get("summary"))
    server = _mapping(server_info)
    version = _mapping(server.get("version"))
    runtime = _mapping(runtime_capabilities)

    read_surfaces = [
        {
            "id": "server_overview",
            "label": "Server overview",
            "available": bool(server.get("usage") or version or server.get("statistics")),
            "detail": "HTTP usage/version/statistics",
        },
        {
            "id": "host_inventory",
            "label": "Host/domain inventory",
            "available": bool(host_summary.get("node_count")),
            "detail": "GET /hosts and GET /hosts/{host}",
        },
        {
            "id": "current_user",
            "label": "Current web user",
            "available": bool(_mapping(access.get("current_user")).get("axxon_user")),
            "detail": "GET /currentuser",
        },
        {
            "id": "security_config",
            "label": "Roles and users inventory",
            "available": bool(access_summary.get("role_count") or access_summary.get("user_count")),
            "detail": "SecurityService.ListConfig",
        },
        {
            "id": "global_permissions",
            "label": "Role access summary",
            "available": bool(access_summary.get("permissions_role_count")),
            "detail": "SecurityService.ListGlobalPermissions",
        },
    ]

    guarded_actions = []
    for action_id, label in (
        ("macro_execution", "Macro execution"),
        ("ptz_control", "PTZ preset control"),
    ):
        payload = _mapping(runtime.get(action_id))
        guarded_actions.append(
            {
                "id": action_id,
                "label": label,
                "enabled": bool(payload.get("enabled")),
                "admin_only": bool(payload.get("admin_only", True)),
                "allowlist_configured": bool(payload.get("allowlist_configured")),
                "audited": bool(payload.get("audited")),
                "confirm_ttl_sec": _to_int(payload.get("confirm_ttl_sec")),
            }
        )

    return {
        "server": {
            "backend_version": _text(version.get("version") or version.get("backendVersion")) or None,
            "api_version": _text(version.get("httpSdk") or version.get("apiVersion")) or None,
            "errors": _payload_copy(server.get("errors") or []),
        },
        "read_surfaces": read_surfaces,
        "guarded_actions": guarded_actions,
        "future_write_plane": {
            "enabled": policy.config_write_enabled,
            "require_admin": policy.require_admin,
            "read_only": policy.read_only,
            "dry_run_required": policy.dry_run_required,
            "audit_required": policy.audit_required,
            "planned_boundaries": list(policy.future_write_boundaries),
            "audited_action_surfaces": list(policy.audited_action_surfaces),
        },
        "telegram_admin_user_count": _to_int(runtime.get("telegram_admin_user_count")) or 0,
    }


def shape_admin_view_result(
    *,
    hosts: Iterable[object] = (),
    host_details: Mapping[str, object] | None = None,
    current_user: Mapping[str, Any] | None = None,
    security_config: Mapping[str, Any] | None = None,
    global_permissions: Mapping[str, Any] | None = None,
    server_info: Mapping[str, Any] | None = None,
    policy: AdminViewPolicy | None = None,
    runtime_capabilities: Mapping[str, Any] | None = None,
    errors: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    active_policy = policy or build_admin_view_policy()
    host_payload = shape_host_inventory(hosts, host_details)
    access_payload = shape_access_summary(
        security_config=security_config,
        global_permissions=global_permissions,
        current_user=current_user,
    )
    capability_payload = shape_admin_capability_surface(
        host_payload,
        access_payload,
        server_info=server_info,
        policy=active_policy,
        runtime_capabilities=runtime_capabilities,
    )
    viewer = {
        **_mapping(access_payload.get("current_user")),
        "telegram_admin": active_policy.admin,
    }
    host_summary = _mapping(host_payload.get("summary"))
    access_summary = _mapping(access_payload.get("summary"))
    return {
        "policy": {
            "admin": active_policy.admin,
            "require_admin": active_policy.require_admin,
            "read_only": active_policy.read_only,
            "config_write_enabled": active_policy.config_write_enabled,
            "dry_run_required": active_policy.dry_run_required,
            "audit_required": active_policy.audit_required,
            "future_write_boundaries": list(active_policy.future_write_boundaries),
            "audited_action_surfaces": list(active_policy.audited_action_surfaces),
        },
        "summary": {
            "node_count": host_summary.get("node_count") or 0,
            "domain_count": host_summary.get("domain_count") or 0,
            "role_count": access_summary.get("role_count") or 0,
            "user_count": access_summary.get("user_count") or 0,
            "enabled_user_count": access_summary.get("enabled_user_count") or 0,
            "assignment_count": access_summary.get("assignment_count") or 0,
            "ldap_server_count": access_summary.get("ldap_server_count") or 0,
        },
        "viewer": viewer,
        "hosts": host_payload,
        "access": access_payload,
        "capabilities": capability_payload,
        "errors": [
            _payload_copy(item)
            for item in errors
            if isinstance(item, Mapping)
        ],
    }


__all__ = [
    "ADMIN_FEATURE_ACCESS",
    "AdminViewPolicy",
    "DEFAULT_ADMIN_AUDITED_ACTION_SURFACES",
    "DEFAULT_ADMIN_FUTURE_WRITE_BOUNDARIES",
    "admin_view_policy_to_api_args",
    "build_admin_view_policy",
    "shape_access_summary",
    "shape_admin_capability_surface",
    "shape_admin_view_result",
    "shape_host_inventory",
]
