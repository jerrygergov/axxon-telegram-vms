#!/usr/bin/env python3
from tg_ui_common import btn, compact_value, run_api


def _text(value: object) -> str:
    return str(value or "").strip()


def _bool_label(value: object) -> str:
    if value is None:
        return "unknown"
    return "yes" if bool(value) else "no"


def _admin_menu_buttons() -> list[list[dict]]:
    return [
        [btn("🔄 Refresh", "adm:menu"), btn("🖥 Hosts", "adm:hosts")],
        [btn("🔐 Access", "adm:access"), btn("🧭 Capability", "adm:caps")],
        [btn("🖥 Server", "srv:menu"), btn("🏠 Main", "home")],
    ]


def _admin_data(common: list[str]) -> dict:
    try:
        data = run_api(common + ["admin-view", "--admin"])
    except Exception as ex:
        data = {"errors": [{"section": "admin-view", "message": str(ex)}]}
    if not isinstance(data, dict):
        return {"errors": [{"section": "admin-view", "message": "unexpected payload type"}]}
    return data


def _note_lines(data: dict) -> list[str]:
    errors = data.get("errors") if isinstance(data.get("errors"), list) else []
    sections: list[str] = []
    seen: set[str] = set()
    for item in errors[:6]:
        if not isinstance(item, dict):
            continue
        section = _text(item.get("section"))
        if not section or section in seen:
            continue
        seen.add(section)
        sections.append(section)
    if not sections:
        return []
    return ["", f"Notes: unavailable {', '.join(sections)}"]


def _admin_overview_payload(data: dict) -> dict:
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    viewer = data.get("viewer") if isinstance(data.get("viewer"), dict) else {}
    capabilities = data.get("capabilities") if isinstance(data.get("capabilities"), dict) else {}
    future = capabilities.get("future_write_plane") if isinstance(capabilities.get("future_write_plane"), dict) else {}

    lines = [
        "🛠 *Admin foundation*",
        "Read-only host, access, and capability visibility. No broad admin writes are enabled.",
        "",
        f"Viewer: Telegram admin {_bool_label(viewer.get('telegram_admin'))} · Axxon user {compact_value(viewer.get('axxon_user'))}",
        (
            f"Inventory: {compact_value(summary.get('node_count'))} nodes · "
            f"{compact_value(summary.get('domain_count'))} domains · "
            f"{compact_value(summary.get('role_count'))} roles · "
            f"{compact_value(summary.get('user_count'))} users"
        ),
        (
            f"Users: {compact_value(summary.get('enabled_user_count'))} enabled · "
            f"assignments {compact_value(summary.get('assignment_count'))} · "
            f"LDAP {compact_value(summary.get('ldap_server_count'))}"
        ),
        (
            f"Write plane: {'enabled' if future.get('enabled') else 'disabled'} · "
            f"dry-run {_bool_label(future.get('dry_run_required'))} · "
            f"audit {_bool_label(future.get('audit_required'))}"
        ),
    ]

    role_names = viewer.get("role_names") if isinstance(viewer.get("role_names"), list) else []
    if role_names:
        lines.append(f"Viewer roles: {', '.join(str(value) for value in role_names[:4])}")

    lines.extend(_note_lines(data))
    return {"text": "\n".join(lines), "buttons": _admin_menu_buttons(), "raw": data}


def _admin_hosts_payload(data: dict) -> dict:
    hosts = data.get("hosts") if isinstance(data.get("hosts"), dict) else {}
    summary = hosts.get("summary") if isinstance(hosts.get("summary"), dict) else {}
    domains = hosts.get("domains") if isinstance(hosts.get("domains"), list) else []
    items = hosts.get("items") if isinstance(hosts.get("items"), list) else []
    license_counts = summary.get("license_status_counts") if isinstance(summary.get("license_status_counts"), dict) else {}
    license_line = ", ".join(f"{key} {value}" for key, value in sorted(license_counts.items())[:4])

    lines = [
        "🖥 *Host / domain inventory*",
        "",
        (
            f"Nodes: {compact_value(summary.get('node_count'))} · "
            f"physical hosts {compact_value(summary.get('host_count'))} · "
            f"domains {compact_value(summary.get('domain_count'))}"
        ),
    ]
    if license_line:
        lines.append(f"Licenses: {license_line}")
    if domains:
        lines.append("Domains: " + ", ".join(f"{compact_value(item.get('name'))} ({compact_value(item.get('nodes'))})" for item in domains[:4] if isinstance(item, dict)))

    if not items:
        lines.extend(["", "No host inventory returned."])
    else:
        lines.extend(["", "Top nodes"])
        for item in items[:8]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"• {compact_value(item.get('node_name'))} -> {compact_value(item.get('host_name'))} · "
                f"{compact_value(item.get('domain_friendly_name') or item.get('domain_name'))} · "
                f"license {compact_value(item.get('license_status'))}"
            )
            extras = [
                _text(item.get("os")),
                _text(item.get("machine")),
                _text(item.get("time_zone_label")),
            ]
            extras = [value for value in extras if value]
            extras.append(f"cluster {compact_value(item.get('cluster_node_count'))}")
            lines.append("  " + " · ".join(extras[:4]))

    lines.extend(_note_lines(data))
    return {"text": "\n".join(lines), "buttons": _admin_menu_buttons(), "raw": data}


def _admin_access_payload(data: dict) -> dict:
    access = data.get("access") if isinstance(data.get("access"), dict) else {}
    summary = access.get("summary") if isinstance(access.get("summary"), dict) else {}
    current_user = access.get("current_user") if isinstance(access.get("current_user"), dict) else {}
    roles = access.get("roles") if isinstance(access.get("roles"), list) else []

    lines = [
        "🔐 *Role / access summary*",
        "",
        (
            f"Users: {compact_value(summary.get('user_count'))} total · "
            f"{compact_value(summary.get('enabled_user_count'))} enabled · "
            f"{compact_value(summary.get('disabled_user_count'))} disabled"
        ),
        (
            f"Roles: {compact_value(summary.get('role_count'))} · "
            f"assignments {compact_value(summary.get('assignment_count'))} · "
            f"LDAP {compact_value(summary.get('ldap_server_count'))}"
        ),
        (
            f"Password policy: min {compact_value(summary.get('password_min_length'))} · "
            f"complexity {_bool_label(summary.get('password_complexity_required'))}"
        ),
        (
            f"Capability coverage: domain ops {compact_value(summary.get('roles_with_domain_ops'))} · "
            f"user rights {compact_value(summary.get('roles_with_user_rights_setup'))} · "
            f"search {compact_value(summary.get('roles_with_search'))} · "
            f"export {compact_value(summary.get('roles_with_export'))}"
        ),
    ]

    role_names = current_user.get("role_names") if isinstance(current_user.get("role_names"), list) else []
    if role_names:
        lines.append(f"Viewer roles: {', '.join(str(value) for value in role_names[:4])}")

    if not roles:
        lines.extend(["", "No role inventory returned."])
    else:
        lines.extend(["", "Top roles"])
        for role in roles[:6]:
            if not isinstance(role, dict):
                continue
            lines.append(
                f"• {compact_value(role.get('name'))} · users {compact_value(role.get('user_count'))} · "
                f"features {compact_value(role.get('feature_access_count'))} · "
                f"setup {compact_value(role.get('admin_feature_count'))}"
            )
            privileges = role.get("privileges") if isinstance(role.get("privileges"), dict) else {}
            flags = []
            for key, label in (
                ("domain_ops", "domain ops"),
                ("users_rights_setup", "user rights"),
                ("search", "search"),
                ("export", "export"),
            ):
                if privileges.get(key):
                    flags.append(label)
            if flags:
                lines.append("  " + ", ".join(flags[:4]))

    lines.extend(_note_lines(data))
    return {"text": "\n".join(lines), "buttons": _admin_menu_buttons(), "raw": data}


def _admin_capabilities_payload(data: dict) -> dict:
    capabilities = data.get("capabilities") if isinstance(data.get("capabilities"), dict) else {}
    server = capabilities.get("server") if isinstance(capabilities.get("server"), dict) else {}
    read_surfaces = capabilities.get("read_surfaces") if isinstance(capabilities.get("read_surfaces"), list) else []
    guarded_actions = capabilities.get("guarded_actions") if isinstance(capabilities.get("guarded_actions"), list) else []
    future = capabilities.get("future_write_plane") if isinstance(capabilities.get("future_write_plane"), dict) else {}

    lines = [
        "🧭 *Admin capability surface*",
        "",
        (
            f"Server: backend {compact_value(server.get('backend_version'))} · "
            f"API {compact_value(server.get('api_version'))}"
        ),
        f"Telegram admins configured: {compact_value(capabilities.get('telegram_admin_user_count'))}",
        "",
        "Read surfaces",
    ]
    if not read_surfaces:
        lines.append("No read surface data returned.")
    else:
        for item in read_surfaces:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"• {compact_value(item.get('label'))}: "
                f"{'available' if item.get('available') else 'unavailable'}"
            )

    lines.extend(["", "Guarded action surfaces"])
    if not guarded_actions:
        lines.append("No guarded action data returned.")
    else:
        for item in guarded_actions:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"• {compact_value(item.get('label'))}: "
                f"{'enabled' if item.get('enabled') else 'disabled'} · "
                f"allowlist {_bool_label(item.get('allowlist_configured'))} · "
                f"audit {_bool_label(item.get('audited'))}"
            )

    lines.extend(["", "Future config writes"])
    lines.append(f"Status: {'enabled' if future.get('enabled') else 'disabled'}")
    lines.append(
        f"Required: admin gate {_bool_label(future.get('require_admin'))} · "
        f"dry-run {_bool_label(future.get('dry_run_required'))} · "
        f"audit {_bool_label(future.get('audit_required'))}"
    )
    boundaries = future.get("planned_boundaries") if isinstance(future.get("planned_boundaries"), list) else []
    if boundaries:
        lines.append("Boundaries: " + ", ".join(str(value) for value in boundaries[:4]))

    lines.extend(_note_lines(data))
    return {"text": "\n".join(lines), "buttons": _admin_menu_buttons(), "raw": data}


def _admin_restricted_payload() -> dict:
    return {
        "text": (
            "⛔️ Admin view is restricted to configured Telegram admins.\n"
            "Use the operator menu for non-admin actions."
        ),
        "buttons": [[btn("🏠 Main", "home")]],
    }


def admin_view_payload(common: list[str], section: str = "menu", *, admin: bool = False) -> dict:
    if not admin:
        return _admin_restricted_payload()
    data = _admin_data(common)
    if section == "hosts":
        return _admin_hosts_payload(data)
    if section == "access":
        return _admin_access_payload(data)
    if section in {"caps", "capabilities"}:
        return _admin_capabilities_payload(data)
    return _admin_overview_payload(data)
