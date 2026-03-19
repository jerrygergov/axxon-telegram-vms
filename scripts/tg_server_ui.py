#!/usr/bin/env python3
from tg_ui_common import (
    btn,
    collect_numeric_fields,
    compact_value,
    find_numeric_by_keys,
    fmt_float,
    fmt_gb,
    fmt_mb,
    fmt_mb_s,
    run_api,
)


def _server_menu_buttons() -> list[list[dict]]:
    return [
        [btn("🔄 Refresh", "srv:menu"), btn("🌐 Domain", "srv:domain")],
        [btn("📦 Version", "srv:version"), btn("📈 Stats", "srv:stats")],
        [btn("🏠 Main", "home")],
    ]


def server_info_payload(common: list[str], domain: bool = False):
    try:
        data = run_api(common + ["server-info"] + (["--domain"] if domain else []))
    except Exception as ex:
        data = {"usage": None, "version": None, "statistics": None, "errors": [{"section": "server-info", "message": str(ex)}]}
    usage = (data or {}).get("usage") if isinstance(data, dict) else None
    version = (data or {}).get("version") if isinstance(data, dict) else None
    statistics = (data or {}).get("statistics") if isinstance(data, dict) else None
    errors = (data or {}).get("errors") if isinstance(data, dict) else []

    if isinstance(usage, list):
        server = usage[0] if usage else {}
    elif isinstance(usage, dict):
        servers = (usage or {}).get("servers") if isinstance(usage, dict) else []
        server = servers[0] if isinstance(servers, list) and servers else usage
    else:
        server = {}

    adapters = server.get("networkAdapters") if isinstance(server, dict) else []
    adapter_ips = [str((item or {}).get("ipAddress")) for item in adapters or [] if (item or {}).get("ipAddress")]
    numeric = collect_numeric_fields(statistics)
    bytes_out = find_numeric_by_keys(statistics, {"bytesout"})
    bytes_out_ps = find_numeric_by_keys(statistics, {"bytesoutpersecond"})
    backend_version = compact_value((version or {}).get("version") or (version or {}).get("backendVersion"))
    server_name = compact_value(server.get("name") or server.get("vmsId")) if isinstance(server, dict) else "—"
    summary_parts = []
    if backend_version != "—":
        summary_parts.append(f"Version {backend_version}")
    if server_name != "—":
        summary_parts.append(f"Server {server_name}")
    if isinstance(errors, list) and errors:
        summary_parts.append("Some sections unavailable")
    elif summary_parts:
        summary_parts.append("API reachable")

    lines = [
        "🖥 *Server overview*",
        "",
        f"Summary: {' · '.join(summary_parts) if summary_parts else 'Server details available below.'}",
        "",
        "Version",
    ]

    if isinstance(version, dict) and version:
        lines.append(f"Backend: {compact_value((version or {}).get('version') or (version or {}).get('backendVersion'))}")
        lines.append(f"API: {compact_value((version or {}).get('httpSdk') or (version or {}).get('apiVersion'))}")
        lines.append(f"Driver Pack: {compact_value((version or {}).get('DriverPackVersion'))}")
        lines.append(f"Detector Pack: {compact_value((version or {}).get('DetectorPackVersion'))}")
    else:
        lines.append("Not available on this server version.")

    lines.extend(["", "Usage"])
    if isinstance(server, dict) and server:
        lines.append(f"Server: {compact_value(server.get('name') or server.get('vmsId'))}")
        lines.append(f"CPU total: {fmt_float(server.get('totalCPU'), 2)}")
        lines.append(f"Network max usage: {fmt_float(server.get('netMaxUsage'), 3)}")
        drives = server.get("drives") if isinstance(server.get("drives"), list) else []
        if drives:
            drive = drives[0] if isinstance(drives[0], dict) else {}
            lines.append(
                "Primary drive: {0} (free {1} / capacity {2})".format(
                    compact_value(drive.get("name")),
                    fmt_gb(drive.get("freeSpace"), 2),
                    fmt_gb(drive.get("capacity"), 2),
                )
            )
        if adapter_ips:
            lines.append(f"IPs: {', '.join(adapter_ips[:3])}")
    else:
        lines.append("Not available on this server version.")

    lines.extend(["", "Web server"])
    if numeric:
        lines.append(f"Bytes out: {fmt_mb(bytes_out, 2)}")
        lines.append(f"Bytes out rate: {fmt_mb_s(bytes_out_ps, 3)}")
        shown = 0
        for key, value in numeric:
            if "bytesout" in key.lower():
                continue
            lines.append(f"{key}: {fmt_float(value, 3)}")
            shown += 1
            if shown >= 3:
                break
    else:
        lines.append("Not available on this server version.")

    lines.extend(["", "Domain"])
    if isinstance(usage, list):
        lines.append(f"Servers: {len(usage)}")
        for item in usage[:3]:
            if not isinstance(item, dict):
                continue
            lines.append(
                "{0}: CPU {1}, NET {2}".format(
                    compact_value(item.get("name")),
                    fmt_float(item.get("totalCPU"), 2),
                    fmt_float(item.get("netMaxUsage"), 3),
                )
            )
    elif isinstance(usage, dict) and usage.get("domainUsageData"):
        domain_usage = usage.get("domainUsageData") or {}
        lines.append(f"Active users: {compact_value(domain_usage.get('activeUsersNow'))}")
        lines.append(f"User sessions: {compact_value(domain_usage.get('userSessions'))}")
        lines.append(f"Total sessions: {compact_value(domain_usage.get('totalSessions'))}")
    else:
        lines.append("Not available on this server version.")

    if isinstance(errors, list) and errors:
        sections = [compact_value((item or {}).get("section")) for item in errors[:4]]
        lines.extend(["", f"Notes: unavailable {', '.join(sections)}"])

    return {"text": "\n".join(lines), "buttons": _server_menu_buttons(), "raw": data}


def server_version_payload(common: list[str]):
    try:
        version = run_api(common + ["server-version"]) or {}
    except Exception:
        version = {}
    lines = [
        "📦 *Server version*",
        "",
    ]
    if isinstance(version, dict) and version:
        lines.append(f"Backend version: `{compact_value((version or {}).get('version') or (version or {}).get('backendVersion'))}`")
        lines.append(f"API version: `{compact_value((version or {}).get('httpSdk') or (version or {}).get('apiVersion'))}`")
    else:
        lines.append("Not available on this server version.")
    extras = {key: value for key, value in (version or {}).items() if key not in {"backendVersion", "apiVersion", "version", "httpSdk"}}
    if extras:
        lines.extend(["", "Extra fields:"])
        for key in sorted(extras.keys())[:8]:
            lines.append(f"• {key}: {compact_value(extras[key])}")
    return {"text": "\n".join(lines), "buttons": _server_menu_buttons(), "raw": version}


def server_statistics_payload(common: list[str]):
    try:
        stats = run_api(common + ["server-statistics"]) or {}
    except Exception:
        stats = None
    numeric = collect_numeric_fields(stats)
    lines = [
        "📈 *Server statistics*",
        "Top numeric counters returned by the web statistics endpoint.",
        "",
    ]
    if stats is None:
        lines.append("Not available on this server version.")
    elif not numeric:
        lines.append("No numeric counters found.")
    else:
        for key, value in numeric[:12]:
            lines.append(f"• {key}: {value:g}")
    return {"text": "\n".join(lines), "buttons": _server_menu_buttons(), "raw": stats}
