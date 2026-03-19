#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

try:
    from scripts.process_bridge import run_command
except ImportError:  # pragma: no cover - top-level script import path
    from process_bridge import run_command

BASE = Path(__file__).resolve().parent
API = BASE / "axxon_web_api.py"
DISPLAY_TZ = timezone.utc
DISPLAY_TZ_LABEL = "UTC"


def configure_display_timezone(tz_name: str | None):
    global DISPLAY_TZ, DISPLAY_TZ_LABEL
    tz = str(tz_name or "UTC").strip() or "UTC"
    if tz.upper() == "UTC":
        DISPLAY_TZ = timezone.utc
        DISPLAY_TZ_LABEL = "UTC"
        return
    try:
        DISPLAY_TZ = ZoneInfo(tz)
        DISPLAY_TZ_LABEL = tz
    except Exception:
        DISPLAY_TZ = timezone.utc
        DISPLAY_TZ_LABEL = "UTC"


def run_api(args: list[str]) -> object:
    cmd = ["python3", str(API)] + args
    subcmd = str(args[0]) if args else ""
    timeout_sec = 90 if subcmd in {"search-events", "face-search", "plate-search", "single-camera-export", "archive-jump"} else 25
    return run_command(cmd, timeout_sec=timeout_sec).parsed


def btn(text: str, cb: str, style: str | None = None):
    payload = {"text": text, "callback_data": cb}
    if style:
        payload["style"] = style
    return payload


def fmt_ts_utc(ts: str | None) -> str:
    if not ts:
        return f"— {DISPLAY_TZ_LABEL}"
    for fmt in ("%Y%m%dT%H%M%S.%f", "%Y%m%dT%H%M%S"):
        try:
            dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc).astimezone(DISPLAY_TZ)
            return dt.strftime(f"%d-%m-%Y %H:%M:%S {DISPLAY_TZ_LABEL}")
        except Exception:
            continue
    return f"{ts} {DISPLAY_TZ_LABEL}"


def fmt_ts_short(ts: str | None) -> str:
    if not ts:
        return "—"
    for fmt in ("%Y%m%dT%H%M%S.%f", "%Y%m%dT%H%M%S"):
        try:
            dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc).astimezone(DISPLAY_TZ)
            return dt.strftime("%d-%m-%y %H:%M")
        except Exception:
            continue
    return str(ts)


def fmt_iso_utc(ts: str | None) -> str:
    if not ts:
        return "—"
    text = str(ts).strip()
    if not text:
        return "—"
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(DISPLAY_TZ)
        return dt.strftime(f"%d-%m-%Y %H:%M:%S {DISPLAY_TZ_LABEL}")
    except Exception:
        return str(ts)


def compact_value(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).strip()
    return text if text else "—"


def to_float(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        text = str(value).strip()
        return float(text) if text else None
    except Exception:
        return None


def fmt_float(value: object, decimals: int = 2) -> str:
    n = to_float(value)
    if n is None:
        return "—"
    text = f"{n:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if text else "0"


def fmt_mb(value: object, decimals: int = 2) -> str:
    n = to_float(value)
    if n is None:
        return "—"
    return f"{fmt_float(n / (1024.0 * 1024.0), decimals)} MB"


def fmt_mb_s(value: object, decimals: int = 2) -> str:
    n = to_float(value)
    if n is None:
        return "—"
    return f"{fmt_float(n / (1024.0 * 1024.0), decimals)} MB/s"


def fmt_gb(value: object, decimals: int = 2) -> str:
    n = to_float(value)
    if n is None:
        return "—"
    return f"{fmt_float(n / (1024.0 * 1024.0 * 1024.0), decimals)} GB"


def find_numeric_by_keys(obj: object, keys: set[str], depth: int = 0):
    if depth > 3:
        return None
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, str) and key.lower() in keys:
                n = to_float(value)
                if n is not None:
                    return n
        for value in obj.values():
            found = find_numeric_by_keys(value, keys, depth + 1)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj[:10]:
            found = find_numeric_by_keys(value, keys, depth + 1)
            if found is not None:
                return found
    return None


def collect_numeric_fields(obj: object, prefix: str = "", depth: int = 0) -> list[tuple[str, float]]:
    if depth > 2:
        return []
    out: list[tuple[str, float]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                out.append((full_key, float(value)))
            elif isinstance(value, (dict, list)):
                out.extend(collect_numeric_fields(value, full_key, depth + 1))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj[:8]):
            full_key = f"{prefix}[{idx}]" if prefix else f"[{idx}]"
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                out.append((full_key, float(value)))
            elif isinstance(value, (dict, list)):
                out.extend(collect_numeric_fields(value, full_key, depth + 1))
    return out[:80]


def parse_offset(parts: list[str], idx: int = 2) -> int:
    if len(parts) > idx and parts[idx].isdigit():
        return max(0, int(parts[idx]))
    return 0


def common_conn(common: list[str]) -> dict[str, str]:
    out = {"host": "", "user": "", "password": "", "port": "80"}
    idx = 0
    while idx < len(common):
        key = common[idx]
        value = common[idx + 1] if idx + 1 < len(common) else ""
        if key == "--host":
            out["host"] = str(value)
        elif key == "--user":
            out["user"] = str(value)
        elif key == "--password":
            out["password"] = str(value)
        elif key == "--port":
            out["port"] = str(value)
        idx += 2
    return out


def camera_stream_links(common: list[str], access_point: str) -> dict[str, str]:
    from camera_catalog import normalize_video_id

    conn = common_conn(common)
    host = conn["host"]
    user = quote(conn["user"], safe="")
    password = quote(conn["password"], safe="")
    http_port = conn["port"] or "80"
    video_id = normalize_video_id(access_point)
    video_id_q = quote(video_id, safe="/:")
    host_video_q = quote(f"hosts/{video_id}", safe="/:")
    auth = f"{user}:{password}@"
    return {
        "live_snapshot": f"http://{auth}{host}:{http_port}/live/media/snapshot/{video_id_q}?w=1280&h=720",
        "live_mjpeg": f"http://{auth}{host}:{http_port}/live/media/{video_id_q}?w=1280&h=720",
        "live_hls_init": f"http://{auth}{host}:{http_port}/live/media/{video_id_q}?format=hls&keep_alive=60",
        "live_rtsp": f"rtsp://{auth}{host}:554/{host_video_q}",
        "live_rtsp_http_tunnel": f"rtsp://{auth}{host}:{http_port}/rtspproxy/{host_video_q}",
    }
