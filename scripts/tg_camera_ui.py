#!/usr/bin/env python3
import json
from pathlib import Path

from camera_catalog import normalize_camera_rows, normalize_video_id
from tg_ui_common import DISPLAY_TZ_LABEL, btn, camera_stream_links, fmt_ts_short, fmt_ts_utc, run_api


def compact_text(value: object, limit: int = 44) -> str:
    text = str(value or "").replace("\n", " ").strip()
    if not text:
        return "—"
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _legacy_event_primary_label(card: dict) -> str:
    camera = compact_text(card.get("camera") or "—", 16)
    detector = compact_text(card.get("detector") or card.get("event_type") or "—", 20)
    return compact_text(f"{camera} - {detector}", 40)


def event_compact_label(
    card: dict,
    *,
    include_status: bool = True,
    include_secondary: bool = True,
    limit: int = 44,
) -> str:
    primary = str(card.get("label_primary") or "").strip() or _legacy_event_primary_label(card)
    secondary = str(card.get("label_secondary") or "").strip()
    status = str(card.get("label_status") or "").strip()

    parts = []
    if include_status and status:
        parts.append(status)
    parts.append(primary)
    if include_secondary and secondary:
        parts.append(secondary)
    return compact_text(" · ".join(part for part in parts if part), limit)


def event_primary_label(card: dict) -> str:
    return event_compact_label(card, include_status=False, include_secondary=True, limit=40)


def event_button_label(row_idx: int, card: dict) -> str:
    when = fmt_ts_short(card.get("timestamp"))
    title = event_compact_label(card, include_status=True, include_secondary=True, limit=52)
    return compact_text(f"{row_idx}) {when} - {title}", 64)


def camera_rows(common: list[str]) -> list[dict]:
    return normalize_camera_rows(run_api(common + ["list-cameras", "--view", "VIEW_MODE_FULL"]))


def short_event_line(card: dict) -> str:
    title = event_primary_label(card)
    state = card.get("state") or ""
    suffix = f" [{state}]" if state else ""
    return f"{fmt_ts_short(card.get('timestamp'))} - {title}{suffix}"


def camera_action_rows(idx: int, include_back: bool = True) -> list[list[dict]]:
    rows = [
        [btn("▶ Live monitor", f"cam:live:start:{idx}"), btn("⏹ Stop", "cam:live:stop")],
        [btn("📸 Live snapshot", f"cam:lsnap:{idx}"), btn("🖼 Latest event frame", f"cam:snap:{idx}")],
        [btn("🚨 Incidents", f"cam:inc:{idx}:0"), btn("🔗 Stream links", f"cam:stream:{idx}")],
    ]
    if include_back:
        rows.append([btn("⬅️ Back", f"cam:open:{idx}"), btn("🏠 Main", "home")])
    return rows


def camera_list_payload(common: list[str], offset: int = 0):
    cams = camera_rows(common)
    page = cams[offset: offset + 8]
    lines = [
        "📷 *Cameras*",
        "Open a camera to monitor it, grab a frame, or follow recent incidents.",
        "",
    ]
    if not page:
        lines.append("No cameras found.")
    else:
        for idx, cam in enumerate(page, start=offset + 1):
            detector_count = len(cam.get("detectors") or [])
            lines.append(f"{idx}. {cam.get('name')} · detectors: {detector_count}")

    buttons = [[btn(cam.get("name"), f"cam:open:{idx}")] for idx, cam in enumerate(page, start=offset)]
    nav: list[dict] = []
    if offset > 0:
        nav.append(btn("⬅️ Previous", f"cam:list:{max(0, offset - 8)}"))
    if offset + 8 < len(cams):
        nav.append(btn("Next ➡️", f"cam:list:{offset + 8}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def camera_open_payload(common: list[str], idx: int):
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "cam:list:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    lines = [
        "🎥 *Camera*",
        f"Name: {cam.get('name')}",
        "Choose an action for this camera.",
        f"Connected detectors: {len(cam.get('detectors') or [])}",
        f"Source: `{cam.get('access_point')}`",
        "",
        "Use Live monitor for a refresh feed, Snapshot for the current view, or Incidents for recent activity.",
    ]
    return {"text": "\n".join(lines), "buttons": camera_action_rows(idx)}


def camera_incidents_payload(common: list[str], idx: int, offset: int = 0, seconds: int = 3600):
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "cam:list:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    cards = run_api(common + [
        "telegram-cards",
        "--seconds", str(seconds),
        "--event-type", "ET_DetectorEvent",
        "--subject", cam.get("access_point"),
        "--limit", "100",
    ])
    cards = [card for card in (cards or []) if not (card.get("event_type") == "moveInZone" and card.get("state") == "ENDED")]
    page = cards[offset: offset + 5]

    lines = [
        f"🚨 *Incidents: {cam.get('name')}*",
        f"Window: last 60 minutes ({DISPLAY_TZ_LABEL})",
        "",
    ]
    if not page:
        lines.append("No incidents found.")
    else:
        for row_idx, card in enumerate(page, start=1):
            lines.append(f"{row_idx}. {short_event_line(card)}")

    buttons = []
    for row_idx, card in enumerate(page, start=1):
        card_id = card.get("id") or ""
        buttons.append([btn(event_button_label(row_idx, card), f"ev:open:{card_id}")])
    nav: list[dict] = []
    if offset > 0:
        nav.append(btn("⬅️ Previous", f"cam:inc:{idx}:{max(0, offset - 5)}"))
    if offset + 5 < len(cards):
        nav.append(btn("Next ➡️", f"cam:inc:{idx}:{offset + 5}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("🔔 Subscribe to this camera", f"sub:new:cam:{idx}")])
    buttons.append([btn("⬅️ Back", f"cam:open:{idx}"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def camera_snapshot_payload(common: list[str], idx: int, seconds: int = 3600):
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "cam:list:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    events = run_api(common + [
        "events",
        "--seconds", str(seconds),
        "--event-type", "ET_DetectorEvent",
        "--subject", cam.get("access_point"),
        "--limit", "50",
    ])
    if not events:
        return {"text": f"No detector events found for {cam.get('name')} in the last hour.", "buttons": [[btn("⬅️ Back", f"cam:open:{idx}"), btn("🏠 Main", "home")]]}
    event = events[0]
    event_id = (event.get("body", {}) or {}).get("guid") or "latest"
    event_json = Path(f"/tmp/axxon_tg_cam_event_{event_id}.json")
    event_json.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    out = Path(f"/tmp/axxon_tg_cam_frame_{event_id}.jpg")
    path = run_api(common + ["frame-from-event", "--event-json", str(event_json), "--out", str(out), "--mode", "media"])
    text = "\n".join([
        "🖼 *Latest event frame*",
        f"Camera: {cam.get('name')}",
        f"Event time: {fmt_ts_utc((event.get('body', {}) or {}).get('timestamp'))}",
    ])
    return {"text": text, "media_path": path, "buttons": camera_action_rows(idx)}


def camera_live_snapshot_payload(common: list[str], idx: int):
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "cam:list:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    video_id = normalize_video_id(cam.get("access_point"))
    out = Path(f"/tmp/axxon_tg_cam_live_snapshot_{idx}.jpg")
    path = run_api(common + ["live-snapshot", "--video-id", video_id, "--out", str(out), "--w", "1280", "--h", "720"])
    text = "\n".join([
        "📸 *Live snapshot*",
        f"Camera: {cam.get('name')}",
        f"Source: `{cam.get('access_point')}`",
    ])
    return {"text": text, "media_path": path, "buttons": camera_action_rows(idx)}


def camera_stream_links_payload(common: list[str], idx: int):
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "cam:list:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    links = camera_stream_links(common, str(cam.get("access_point") or ""))
    lines = [
        "🔗 *Camera stream links*",
        f"Camera: {cam.get('name')}",
        f"Access point: `{cam.get('access_point')}`",
        "",
        "Use `Live monitor` in Telegram for low-fps operator refresh. Use the links below when you need a browser or VLC.",
        "",
        "Live snapshot:",
        f"`{links['live_snapshot']}`",
        "",
        "Live MJPEG:",
        f"`{links['live_mjpeg']}`",
        "",
        "HLS init URL:",
        f"`{links['live_hls_init']}`",
        "",
        "RTSP:",
        f"`{links['live_rtsp']}`",
        "",
        "RTSP over HTTP tunnel:",
        f"`{links['live_rtsp_http_tunnel']}`",
    ]
    return {"text": "\n".join(lines), "buttons": camera_action_rows(idx)}
