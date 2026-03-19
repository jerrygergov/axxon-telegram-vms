#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from axxon_telegram_vms.services import (
    ArchiveJumpSyntaxError,
    EventSearchSyntaxError,
    FaceSearchSyntaxError,
    LicensePlateSearchSyntaxError,
    MacroExecutionSyntaxError,
    PtzControlSyntaxError,
    SingleCameraExportSyntaxError,
    archive_jump_request_to_api_args,
    build_macro_execution_policy,
    build_ptz_control_policy,
    event_search_request_to_api_args,
    face_search_request_to_api_args,
    license_plate_search_request_to_api_args,
    macro_execution_policy_to_api_args,
    macro_execution_request_to_api_args,
    parse_archive_jump_terms,
    parse_event_search_terms,
    parse_face_search_terms,
    parse_license_plate_search_terms,
    parse_macro_execution_terms,
    parse_ptz_control_terms,
    parse_single_camera_export_terms,
    ptz_control_policy_to_api_args,
    ptz_control_request_to_api_args,
    single_camera_export_request_to_api_args,
)
from config_loader import load_axxon_config
import tg_admin_ui
import tg_server_ui
from tg_camera_ui import (
    camera_incidents_payload,
    camera_list_payload,
    camera_live_snapshot_payload,
    camera_open_payload,
    camera_rows,
    camera_snapshot_payload,
    camera_stream_links_payload,
    compact_text,
    event_compact_label,
    event_button_label,
    event_primary_label,
    short_event_line,
)
from tg_ui_common import DISPLAY_TZ_LABEL, btn, common_conn, compact_value, configure_display_timezone, fmt_ts_short, fmt_ts_utc, parse_offset, run_api

ALERTS_WINDOW_SECONDS = 3600
EVENTS_WINDOW_SECONDS = 1800
HOME_ALERT_BUTTON_LIMIT = 3
EVENTS_PAGE_SIZE = 8
ALERTS_PAGE_SIZE = 5
EVENT_CARD_LIMIT = 200
EVENT_TOKEN_DIGEST_BYTES = 6


def _format_size_bytes(value: object) -> str:
    try:
        size = int(value)
    except (TypeError, ValueError):
        return compact_value(value)
    if size < 1024:
        return f"{size} B"
    if size < (1024 * 1024):
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def _event_search_help_payload(error_text: str | None = None, *, buttons: list[list[dict]] | None = None):
    lines = ["🔎 *Event search*"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Start with a time window, then add filters only when you need them.",
        "Advanced typed search:",
        "",
        "Examples:",
        "/search from=2026-03-10T08:00:00Z to=2026-03-10T09:00:00Z mode=summary",
        "/search from=20260310T080000 to=20260310T090000 camera=2.Gate category=lpr mode=list page=1",
        "",
        "Supported filters:",
        "camera, camera_ap, detector, detector_ap, host, domain, category, type, state, severity, priority, contains, mask, sort=asc|desc",
    ])
    return {
        "text": "\n".join(lines),
        "buttons": buttons or [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
    }


def _event_search_filter_line(filters: dict[str, object]) -> str:
    parts = []
    for key, label in (
        ("hosts", "host"),
        ("domains", "domain"),
        ("camera_names", "camera"),
        ("camera_access_points", "camera AP"),
        ("detector_names", "detector"),
        ("detector_access_points", "detector AP"),
        ("categories", "category"),
        ("event_types", "type"),
        ("states", "state"),
        ("severities", "severity"),
        ("priorities", "priority"),
    ):
        values = filters.get(key)
        if isinstance(values, list) and values:
            parts.append(f"{label}: {', '.join(str(value) for value in values[:3])}")
    if filters.get("contains"):
        parts.append(f"contains: {filters['contains']}")
    if filters.get("mask"):
        parts.append(f"mask: {filters['mask']}")
    return " · ".join(parts[:5]) if parts else "all events"


def _event_search_result_payload(result: dict[str, object]) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    filters = request.get("filters") if isinstance(request.get("filters"), dict) else {}
    range_payload = filters.get("range") if isinstance(filters.get("range"), dict) else {}
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    pagination = result.get("pagination") if isinstance(result.get("pagination"), dict) else {}
    items = result.get("items") if isinstance(result.get("items"), list) else []

    begin = range_payload.get("begin_time")
    end = range_payload.get("end_time")
    mode = str(request.get("mode") or "summary")
    complete = bool(summary.get("complete"))
    matched = int(summary.get("matched") or 0)
    scanned = int(summary.get("scanned") or 0)
    page = int(pagination.get("page") or 1)
    page_count = int(pagination.get("page_count") or 0)

    lines = [
        "🔎 *Event search*",
        f"Window: {fmt_ts_utc(begin)} -> {fmt_ts_utc(end)}",
        f"Filters: {_event_search_filter_line(filters)}",
        f"Matched: {matched} · scanned: {scanned} · {'complete' if complete else 'scan cap reached'}",
    ]

    category_counts = summary.get("by_category") if isinstance(summary.get("by_category"), dict) else {}
    if category_counts:
        mix = " · ".join(f"{str(name).upper()} {count}" for name, count in sorted(category_counts.items()))
        lines.append(f"Mix: {mix}")

    top_cameras = summary.get("top_cameras") if isinstance(summary.get("top_cameras"), list) else []
    if top_cameras:
        lines.append(
            "Top cameras: "
            + " · ".join(f"{row.get('name')} ({row.get('count')})" for row in top_cameras[:3] if isinstance(row, dict))
        )
    top_detectors = summary.get("top_detectors") if isinstance(summary.get("top_detectors"), list) else []
    if top_detectors:
        lines.append(
            "Top detectors: "
            + " · ".join(f"{row.get('name')} ({row.get('count')})" for row in top_detectors[:3] if isinstance(row, dict))
        )

    if mode == "list":
        lines.extend(["", f"Page: {page}/{page_count or 1}"])
        if not items:
            lines.append("No events on this page.")
        else:
            start_idx = ((page - 1) * int(request.get("page_size") or 1)) + 1
            for idx, card in enumerate(items, start=start_idx):
                lines.append(f"{idx}. {short_event_line(card)}")
        if matched:
            lines.extend([
                "",
                f"Next page: /search ... mode=list page={page + 1}" if bool(pagination.get("has_next")) else "No further pages in the current result set.",
            ])
    elif matched:
        lines.extend([
            "",
            "Use mode=list page=1 with the same filters to inspect individual events.",
        ])
    else:
        lines.extend(["", "No events matched the current filter set."])

    if not complete:
        lines.append("Narrow the range or scope for exhaustive results before archive/export passes.")

    return {
        "text": "\n".join(lines),
        "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        "meta": {"kind": "event_search", "page_size": len(items)},
        "result": result,
    }


def event_search_payload(common: list[str], terms: list[str]):
    try:
        request = parse_event_search_terms(terms)
    except EventSearchSyntaxError as exc:
        return _event_search_help_payload(str(exc))

    try:
        result = run_api(common + ["search-events", *event_search_request_to_api_args(request)])
    except Exception as exc:
        return {
            "text": f"⚠️ Event search failed.\n{exc}",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ Event search returned an unexpected payload.",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    return _event_search_result_payload(result)


def _face_search_help_payload(error_text: str | None = None, *, buttons: list[list[dict]] | None = None):
    lines = ["🙂 *Face search*"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Upload a Telegram photo to start the guided similarity/time flow.",
        "Need exact filters? Reply /face to a photo and add key=value terms.",
        "Accepted image format: JPEG.",
        "",
        "Examples:",
        "(upload photo) send a Telegram photo",
        "(reply to photo) /face",
        "(reply to photo) /face camera=1.Lobby last=7200",
        "(reply to photo) /face from=20260310T080000 to=20260310T090000 detector=Face accuracy=0.82",
        "",
        "Supported filters:",
        "camera, camera_ap, detector, detector_ap, host, domain, last, from, to, accuracy, page, page_size, scan_limit",
    ])
    return {
        "text": "\n".join(lines),
        "buttons": buttons or [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
    }


def _format_similarity(value: object) -> str | None:
    try:
        similarity = float(value)
    except (TypeError, ValueError):
        return None
    if similarity < 0.0:
        return None
    if similarity > 1.0 and similarity <= 100.0:
        similarity = similarity / 100.0
    if similarity > 1.0:
        return None
    return f"{similarity:.0%}"


def _face_search_result_payload(result: dict[str, object]) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    filters = request.get("filters") if isinstance(request.get("filters"), dict) else {}
    range_payload = filters.get("range") if isinstance(filters.get("range"), dict) else {}
    capability = result.get("capability") if isinstance(result.get("capability"), dict) else {}
    selection = result.get("selection") if isinstance(result.get("selection"), dict) else {}
    reference = result.get("reference_image") if isinstance(result.get("reference_image"), dict) else {}
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    pagination = result.get("pagination") if isinstance(result.get("pagination"), dict) else {}
    items = result.get("items") if isinstance(result.get("items"), list) else []
    error = compact_value(result.get("error"))

    begin = range_payload.get("begin_time")
    end = range_payload.get("end_time")
    matched = int(summary.get("matched") or 0)
    scanned = int(summary.get("scanned") or 0)
    page = int(pagination.get("page") or 1)
    page_count = int(pagination.get("page_count") or 0)
    complete = bool(summary.get("complete"))
    window_seconds = int(request.get("window_seconds") or 0)
    time_source = str(request.get("time_source") or "explicit")
    available_cameras = int(capability.get("camera_count") or 0)
    available_detectors = int(capability.get("detector_count") or 0)
    selected_cameras = int(selection.get("camera_count") or 0)
    selected_detectors = int(selection.get("detector_count") or 0)

    window_line = f"Window: {fmt_ts_utc(begin)} → {fmt_ts_utc(end)}"
    accuracy = _format_similarity(request.get("accuracy"))
    scope_line = _plate_search_scope_line(filters)
    capability_line = None
    if selected_detectors:
        capability_line = f"Face detectors: {selected_detectors} VaFaceDetector instance(s) across {selected_cameras or available_cameras} camera(s)"

    lines = [
        "🙂 *Face search*",
        window_line,
        f"Threshold: {accuracy or compact_value(request.get('accuracy'))} · Scope: {scope_line}",
    ]
    if selection.get("searchable"):
        lines.append(f"Results: {matched} match(es) · scanned {scanned} · {'complete' if complete else 'scan cap reached'}")
        if capability_line:
            lines.append(capability_line)
        if items:
            best_similarity = _format_similarity(items[0].get("similarity")) if isinstance(items[0], dict) else None
            best_camera = compact_value(items[0].get("camera") or "Camera") if isinstance(items[0], dict) else "Camera"
            best_ts = fmt_ts_utc(items[0].get("timestamp")) if isinstance(items[0], dict) else "—"
            lines.append(f"Top hit: {best_camera} · {best_ts} · {best_similarity or '—'}")
        else:
            lines.append("No matching faces in this range.")
    else:
        if capability_line:
            lines.append(capability_line)
        if error not in {"—", "(none)"}:
            lines.append(f"⚠️ {error}")
        else:
            lines.append("Backend search not started.")

    return {
        "text": "\n".join(lines),
        "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        "meta": {"kind": "face_search", "page_size": len(items)},
        "result": result,
    }


def face_search_payload(common: list[str], image_path: str, terms: list[str]):
    if not str(image_path or "").strip():
        return _face_search_help_payload("Upload a Telegram photo or reply /face to a photo to start.")

    try:
        request = parse_face_search_terms(terms)
    except FaceSearchSyntaxError as exc:
        return _face_search_help_payload(str(exc))

    try:
        result = run_api(common + ["face-search", *face_search_request_to_api_args(request, image_path=image_path)])
    except Exception as exc:
        return {
            "text": f"⚠️ Face search failed.\n{exc}",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ Face search returned an unexpected payload.",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    return _face_search_result_payload(result)


def _plate_search_help_payload(error_text: str | None = None, *, buttons: list[list[dict]] | None = None):
    lines = ["🔎 *License plate search*"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Use plate=..., contains=..., or mask=... with either from/to or a bounded default window.",
        "",
        "Examples:",
        "/plate plate=BE59922",
        "/plate contains=5992 camera=2.Gate last=7200",
        "/plate mask=*9922 from=20260308T220000 to=20260308T230000 camera_ap=hosts/AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
        "",
        "Supported filters:",
        "camera, camera_ap, detector, detector_ap, host, domain, last, sort=asc|desc, page, page_size, scan_limit",
    ])
    return {
        "text": "\n".join(lines),
        "buttons": buttons or [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
    }


def _plate_search_scope_line(filters: dict[str, object]) -> str:
    line = _event_search_filter_line(filters)
    return "all cameras" if line == "all events" else line


def _plate_search_match_line(match: dict[str, object]) -> str:
    mode = str(match.get("mode") or "exact").strip().lower()
    value = compact_value(match.get("value"))
    label = {
        "exact": "exact",
        "contains": "contains",
        "mask": "mask",
    }.get(mode, mode)
    return f"{label}: {value}"


def _format_plate_confidence(value: object) -> str | None:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return None
    if confidence < 0:
        return None
    return f"{confidence:.0f}%"


def _plate_search_result_payload(result: dict[str, object]) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    filters = request.get("filters") if isinstance(request.get("filters"), dict) else {}
    range_payload = filters.get("range") if isinstance(filters.get("range"), dict) else {}
    match = request.get("match") if isinstance(request.get("match"), dict) else {}
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    pagination = result.get("pagination") if isinstance(result.get("pagination"), dict) else {}
    items = result.get("items") if isinstance(result.get("items"), list) else []

    begin = range_payload.get("begin_time")
    end = range_payload.get("end_time")
    matched = int(summary.get("matched") or 0)
    scanned = int(summary.get("scanned") or 0)
    page = int(pagination.get("page") or 1)
    page_count = int(pagination.get("page_count") or 0)
    complete = bool(summary.get("complete"))
    time_source = str(request.get("time_source") or "explicit")
    window_seconds = int(request.get("window_seconds") or 0)

    window_line = f"Window: {fmt_ts_utc(begin)} -> {fmt_ts_utc(end)}"
    if time_source == "window" and window_seconds > 0:
        window_line += f" · default last {max(1, window_seconds // 60)} min"

    lines = [
        "🔎 *License plate search*",
        window_line,
        f"Match: {_plate_search_match_line(match)}",
        f"Scope: {_plate_search_scope_line(filters)}",
        f"Matched: {matched} · scanned: {scanned} · {'complete' if complete else 'scan cap reached'}",
    ]

    top_cameras = summary.get("top_cameras") if isinstance(summary.get("top_cameras"), list) else []
    if top_cameras:
        lines.append(
            "Top cameras: "
            + " · ".join(f"{row.get('name')} ({row.get('count')})" for row in top_cameras[:3] if isinstance(row, dict))
        )
    top_plates = summary.get("top_plates") if isinstance(summary.get("top_plates"), list) else []
    if top_plates and str(match.get("mode") or "").lower() != "exact":
        lines.append(
            "Top plates: "
            + " · ".join(f"{row.get('name')} ({row.get('count')})" for row in top_plates[:3] if isinstance(row, dict))
        )

    lines.extend(["", f"Page: {page}/{page_count or 1}"])
    if not items:
        lines.append("No matching plates on this page.")
    else:
        start_idx = ((page - 1) * int(request.get("page_size") or 1)) + 1
        for idx, card in enumerate(items, start=start_idx):
            if not isinstance(card, dict):
                continue
            plate = compact_value(card.get("plate") or "(no plate)")
            camera = compact_value(card.get("camera") or "Camera")
            line = f"{idx}. {fmt_ts_utc(card.get('timestamp'))} · {plate} · {camera}"
            confidence = _format_plate_confidence(card.get("confidence"))
            if confidence:
                line += f" · {confidence}"
            lines.append(line)
            extra = []
            detector = compact_value(card.get("detector"))
            if detector not in {"—", "(none)"}:
                extra.append(detector)
            vehicle = card.get("vehicle") if isinstance(card.get("vehicle"), dict) else {}
            vehicle_bits = [str(vehicle.get(key) or "").strip() for key in ("brand", "model", "color")]
            vehicle_line = " / ".join(bit for bit in vehicle_bits if bit)
            if vehicle_line:
                extra.append(vehicle_line)
            if extra:
                lines.append(f"   {' · '.join(extra)}")

    if bool(pagination.get("has_next")):
        lines.extend(["", f"Next page: /plate ... page={page + 1}"])
    if not complete:
        lines.append("Narrow the window or add camera scope for exhaustive investigative passes.")

    payload = {
        "text": "\n".join(lines),
        "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        "meta": {"kind": "license_plate_search", "page_size": len(items)},
        "result": result,
    }
    media_path = ""
    if items and isinstance(items[0], dict):
        media_path = str(items[0].get("full_frame") or "").strip()
    if media_path:
        payload["media_path"] = media_path
    return payload


def plate_search_payload(common: list[str], terms: list[str]):
    try:
        request = parse_license_plate_search_terms(terms)
    except LicensePlateSearchSyntaxError as exc:
        return _plate_search_help_payload(str(exc))

    try:
        result = run_api(common + ["plate-search", *license_plate_search_request_to_api_args(request)])
    except Exception as exc:
        return {
            "text": f"⚠️ License plate search failed.\n{exc}",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ License plate search returned an unexpected payload.",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    return _plate_search_result_payload(result)


def _archive_jump_help_payload(error_text: str | None = None, *, buttons: list[list[dict]] | None = None):
    lines = ["🎬 *Archive jump*"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Start with one camera and one moment in time.",
        "Easiest way: open *Archive wizard* and pick a camera with buttons.",
        "Power-user mode still accepts one camera and one moment in time.",
        "You can also use a bounded range if it still resolves to one camera.",
        "",
        "Quick examples:",
        "/archive",
        "/archive Gate 10:55",
        "/archive camera=2.Gate at=2026-03-10T10:55:00Z",
        "/archive from=20260310T100000 to=20260310T110000 camera=2.Gate category=lpr",
        "",
        "Open any event or alert card and press Archive to jump from its camera and timestamp directly.",
    ])
    return {
        "text": "\n".join(lines),
        "buttons": buttons or [[btn("⬅️ Archive", "arch:menu"), btn("✨ Wizard", "arch:wiz:0")], [btn("🏠 Main", "home")]],
    }


def _archive_wizard_payload(common: list[str], offset: int = 0) -> dict[str, object]:
    cams = camera_rows(common)
    page = cams[offset: offset + 8]
    lines = [
        "🎬 *Archive wizard*",
        "Choose one camera first. Then pick a recent moment with buttons.",
        "",
    ]
    if not page:
        lines.append("No cameras found.")
    else:
        for idx, cam in enumerate(page, start=offset + 1):
            lines.append(f"{idx}. {compact_value(cam.get('name'))}")
        lines.extend([
            "",
            "After that you can jump around with -15s / +15s buttons.",
        ])
    buttons = [[btn(compact_text(cam.get("name"), 32), f"arch:cam:{idx}")] for idx, cam in enumerate(page, start=offset)]
    nav = []
    if offset > 0:
        nav.append(btn("⬅️ Previous", f"arch:wiz:{max(0, offset - 8)}"))
    if offset + 8 < len(cams):
        nav.append(btn("Next ➡️", f"arch:wiz:{offset + 8}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("🎬 Jump help", "arch:jump"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def _archive_depth_payload(common: list[str], camera_ap: str) -> dict[str, object]:
    try:
        result = run_api(common + ["archive-depth", "--camera-ap", camera_ap])
    except Exception:
        return {}
    return result if isinstance(result, dict) else {}


def _archive_camera_wizard_payload(common: list[str], idx: int) -> dict[str, object]:
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "arch:wiz:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    depth = _archive_depth_payload(common, str(cam.get('camera_access_point') or cam.get('access_point') or ''))
    lines = [
        "🎬 *Archive wizard*",
        f"Camera: {compact_value(cam.get('name'))}",
    ]
    if depth:
        lines.extend([
            f"Archive range: {fmt_ts_utc(depth.get('start'))} → {fmt_ts_utc(depth.get('end'))}",
        ])
    lines.extend([
        "",
        "Pick a recent moment or open the calendar for any date and time.",
        "",
        "Quick presets:",
        "- now - 1 min",
        "- now - 5 min",
        "- now - 15 min",
        "- now - 1 hour",
        "",
        "Exact time also works in text form:",
        f"`/archive {compact_value(cam.get('name'))} 10:55`",
    ])
    return {
        "text": "\n".join(lines),
        "buttons": [
            [btn("Now - 1 min", f"arch:go:{idx}:60"), btn("Now - 5 min", f"arch:go:{idx}:300")],
            [btn("Now - 15 min", f"arch:go:{idx}:900"), btn("Now - 1 hour", f"arch:go:{idx}:3600")],
            [btn("📅 Pick date & time", f"arch:date:{idx}:{_archive_now_utc().strftime('%Y%m')}:0")],
            [btn("⬅️ Cameras", "arch:wiz:0"), btn("🏠 Main", "home")],
        ],
    }


def _archive_month_parse(value: str | None = None) -> datetime:
    raw = str(value or "").strip()
    if raw and re.fullmatch(r"\d{6}", raw):
        return datetime.strptime(raw, "%Y%m").replace(tzinfo=timezone.utc)
    now = _archive_now_utc()
    return now.replace(day=1, hour=0, minute=0, second=0)


def _archive_month_shift(month_dt: datetime, delta_months: int) -> datetime:
    year = month_dt.year + ((month_dt.month - 1 + delta_months) // 12)
    month = ((month_dt.month - 1 + delta_months) % 12) + 1
    return month_dt.replace(year=year, month=month, day=1)


def _archive_calendar_payload(common: list[str], idx: int, month_key: str | None = None) -> dict[str, object]:
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "arch:wiz:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    depth = _archive_depth_payload(common, str(cam.get('camera_access_point') or cam.get('access_point') or ''))
    month_dt = _archive_month_parse(month_key)
    next_month = _archive_month_shift(month_dt, 1)
    days_in_month = (next_month - timedelta(days=1)).day
    first_weekday = month_dt.weekday()  # Mon=0
    now_utc = _archive_now_utc()
    lines = [
        "📅 *Archive date picker*",
        f"Camera: {compact_value(cam.get('name'))}",
        f"Month: {month_dt.strftime('%B %Y')} (UTC)",
    ]
    if depth:
        lines.append(f"Archive range: {fmt_ts_utc(depth.get('start'))} → {fmt_ts_utc(depth.get('end'))}")
    lines.append("Pick any day, then choose hour and minute.")
    buttons: list[list[dict]] = []
    buttons.append([
        btn("⬅️", f"arch:date:{idx}:{_archive_month_shift(month_dt, -1).strftime('%Y%m')}:0"),
        btn(month_dt.strftime("%b %Y"), f"arch:noop"),
        btn("➡️", f"arch:date:{idx}:{_archive_month_shift(month_dt, 1).strftime('%Y%m')}:0"),
    ])
    weekday_labels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    buttons.append([btn(label, "arch:noop") for label in weekday_labels])
    row: list[dict] = []
    for _ in range(first_weekday):
        row.append(btn("·", "arch:noop"))
    for day in range(1, days_in_month + 1):
        day_dt = month_dt.replace(day=day)
        label = f"[{day}]" if day_dt.date() == now_utc.date() else str(day)
        row.append(btn(label, f"arch:day:{idx}:{day_dt.strftime('%Y%m%d')}"))
        if len(row) == 7:
            buttons.append(row)
            row = []
    if row:
        while len(row) < 7:
            row.append(btn("·", "arch:noop"))
        buttons.append(row)
    buttons.append([btn("⬅️ Time presets", f"arch:cam:{idx}"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def _archive_hour_payload(common: list[str], idx: int, day_key: str, page: int = 0) -> dict[str, object]:
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "arch:wiz:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    day_dt = datetime.strptime(day_key, "%Y%m%d").replace(tzinfo=timezone.utc)
    page = max(0, min(3, page))
    hours = list(range(page * 6, min(24, page * 6 + 6)))
    lines = [
        "🕒 *Choose hour*",
        f"Camera: {compact_value(cam.get('name'))}",
        f"Date: {day_dt.strftime('%Y-%m-%d')} UTC",
        "Pick the hour.",
    ]
    buttons: list[list[dict]] = []
    for start in range(0, len(hours), 3):
        chunk = hours[start:start + 3]
        buttons.append([btn(f"{hour:02d}:xx", f"arch:h:{idx}:{day_key}:{hour:02d}") for hour in chunk])
    nav = []
    if page > 0:
        nav.append(btn("⬅️ Earlier", f"arch:hr:{idx}:{day_key}:{page - 1}"))
    if page < 3:
        nav.append(btn("Later ➡️", f"arch:hr:{idx}:{day_key}:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("📅 Change date", f"arch:date:{idx}:{day_dt.strftime('%Y%m')}:0"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def _archive_minute_payload(common: list[str], idx: int, day_key: str, hour_key: str, page: int = 0) -> dict[str, object]:
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "arch:wiz:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    page = max(0, min(5, page))
    hour = int(hour_key)
    minute_start = page * 10
    minute_values = list(range(minute_start, min(60, minute_start + 10)))
    day_dt = datetime.strptime(day_key, "%Y%m%d").replace(tzinfo=timezone.utc)
    lines = [
        "⏱ *Choose minute*",
        f"Camera: {compact_value(cam.get('name'))}",
        f"Date: {day_dt.strftime('%Y-%m-%d')} UTC",
        f"Hour: {hour:02d}:xx",
        "Pick the exact minute.",
    ]
    buttons: list[list[dict]] = []
    for start in range(0, len(minute_values), 5):
        chunk = minute_values[start:start + 5]
        buttons.append([btn(f"{minute:02d}", f"arch:m:{idx}:{day_key}:{hour:02d}:{minute:02d}") for minute in chunk])
    nav = []
    if page > 0:
        nav.append(btn("⬅️ Earlier", f"arch:min:{idx}:{day_key}:{hour:02d}:{page - 1}"))
    if page < 5:
        nav.append(btn("Later ➡️", f"arch:min:{idx}:{day_key}:{hour:02d}:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("🕒 Change hour", f"arch:hr:{idx}:{day_key}:0"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def _archive_jump_for_camera(common: list[str], idx: int, target_dt: datetime) -> dict[str, object]:
    cams = camera_rows(common)
    if idx < 0 or idx >= len(cams):
        return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "arch:wiz:0"), btn("🏠 Main", "home")]]}
    cam = cams[idx]
    target_iso = _archive_ts_iso(target_dt)
    result = run_api(common + [
        "archive-jump",
        "--begin", target_iso,
        "--end", target_iso,
        "--at", target_iso,
        "--camera-ap", str(cam.get("access_point") or ""),
    ])
    if not isinstance(result, dict):
        return {"text": "⚠️ Archive jump returned an unexpected payload.", "buttons": [[btn("⬅️ Back", f"arch:cam:{idx}"), btn("🏠 Main", "home")]]}
    payload = _archive_jump_result_payload(result, common=common, back_cb=f"arch:cam:{idx}", back_txt="⬅️ Time presets")
    buttons = payload.get("buttons") if isinstance(payload.get("buttons"), list) else []
    nav_buttons = _archive_result_nav_buttons(idx, target_dt)
    fallback_buttons = _archive_unavailable_buttons(idx, result)
    payload["buttons"] = nav_buttons + fallback_buttons + buttons
    return payload


def _archive_relay_mjpeg_url(handle: dict[str, object], camera_name: object = "", *, width: int = 1280, height: int = 720, speed: int = 1, fr: int = 3, ttl_sec: int = 900) -> str:
    relay_script = ROOT / "scripts" / "archive_stream_relay.py"
    if not relay_script.exists():
        return ""
    video_id = str(handle.get("video_id") or "").strip()
    timestamp = str(handle.get("timestamp") or "").strip()
    if not video_id or not timestamp:
        return ""
    cmd = [
        sys.executable,
        str(relay_script),
        "--video-id", video_id,
        "--ts", timestamp,
        "--camera-name", str(camera_name or ""),
        "--ttl-sec", str(ttl_sec),
        "--w", str(width),
        "--h", str(height),
        "--speed", str(speed),
        "--fr", str(fr),
        "--mode", "mjpeg",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, timeout=10).strip()
    except Exception:
        return ""
    return out


def _archive_native_mjpeg_url(common: list[str], handle: dict[str, object], *, width: int = 1280, height: int = 720, speed: int = 1, fr: int = 3) -> str:
    conn = common_conn(common)
    host = conn.get("host") or ""
    port = conn.get("port") or "80"
    user = quote(conn.get("user") or "", safe="")
    password = quote(conn.get("password") or "", safe="")
    video_id = quote(str(handle.get("video_id") or ""), safe="/:")
    timestamp = str(handle.get("timestamp") or "")
    auth = f"{user}:{password}@" if user or password else ""
    return f"http://{auth}{host}:{port}/archive/media/{video_id}/{timestamp}?format=mjpeg&speed={speed}&fr={fr}&w={width}&h={height}"


def _archive_timestamp_source_label(value: object) -> str:
    mapping = {
        "explicit": "requested point",
        "matching_event": "matching event",
        "range_midpoint": "range midpoint",
    }
    return mapping.get(str(value or "").strip(), compact_value(value))


def _archive_jump_result_payload(
    result: dict[str, object],
    *,
    common: list[str] | None = None,
    back_cb: str = "arch:menu",
    back_txt: str = "⬅️ Back",
) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    selection = result.get("selection") if isinstance(result.get("selection"), dict) else {}
    archive = result.get("archive") if isinstance(result.get("archive"), dict) else {}
    preview = result.get("preview") if isinstance(result.get("preview"), dict) else {}
    depth = archive.get("depth") if isinstance(archive.get("depth"), dict) else {}
    handle = archive.get("context_handle") if isinstance(archive.get("context_handle"), dict) else {}

    requested_ts = request.get("requested_timestamp")
    resolved_ts = selection.get("timestamp")
    effective_ts = selection.get("effective_timestamp") or resolved_ts
    in_archive = bool(archive.get("in_archive"))
    nearest_available = _archive_best_available_point(result)

    lines = [
        "🎬 *Archive jump*",
        f"Camera: {compact_value(selection.get('camera'))}",
        f"Requested: {fmt_ts_utc(requested_ts)}",
    ]

    if in_archive or effective_ts != resolved_ts:
        lines.append(f"Using: {fmt_ts_utc(effective_ts)}")
    else:
        lines.append("Status: requested point is outside available archive.")
        if depth:
            lines.append(f"Archive available from: {fmt_ts_utc(depth.get('start'))}")
        if nearest_available is not None:
            lines.append(f"Nearest available: {nearest_available.strftime('%d-%m-%Y %H:%M:%S UTC')}")
        if effective_ts != resolved_ts:
            lines.append("The preview/link was shifted automatically to the nearest available archive point.")

    if handle:
        relay_mjpeg_url = _archive_relay_mjpeg_url(handle, selection.get("camera"))
        if relay_mjpeg_url:
            lines.extend(["", "MJPEG relay link:", relay_mjpeg_url])
        elif common:
            try:
                native_mjpeg_url = _archive_native_mjpeg_url(common, handle)
            except Exception:
                native_mjpeg_url = ""
            if native_mjpeg_url:
                lines.extend(["", "MJPEG link:", native_mjpeg_url])

    preview_path = str(preview.get("path") or "").strip()
    if preview.get("ok") and preview_path:
        lines.extend(["", f"Preview: ready ({compact_value(preview.get('mode'))})"])
    else:
        lines.append("")
        if not in_archive and depth:
            lines.append("Preview unavailable: the requested time is earlier than the available archive range.")
        else:
            lines.append("Preview unavailable: archive preview endpoint did not return a frame.")

    payload = {
        "text": "\n".join(lines),
        "buttons": [[btn(back_txt, back_cb), btn("🏠 Main", "home")]],
        "meta": {"kind": "archive_jump"},
        "result": result,
    }
    if preview.get("ok") and preview_path:
        payload["media_path"] = preview_path
    return payload


def archive_jump_payload(common: list[str], terms: list[str]):
    try:
        request = parse_archive_jump_terms(terms)
    except ArchiveJumpSyntaxError as exc:
        return _archive_jump_help_payload(str(exc))

    try:
        result = run_api(common + ["archive-jump", *archive_jump_request_to_api_args(request)])
    except Exception as exc:
        return {
            "text": f"⚠️ Archive jump failed.\n{exc}",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ Archive jump returned an unexpected payload.",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    return _archive_jump_result_payload(result, common=common)


def _single_camera_export_help_payload(error_text: str | None = None, *, buttons: list[list[dict]] | None = None):
    lines = ["📦 *Single-camera export*"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Start with one camera and a clear start/end time.",
        "",
        "Examples:",
        "/export from=2026-03-10T10:50:00Z to=2026-03-10T10:55:00Z camera=2.Gate",
        "/export from=20260310T105000 to=20260310T105500 camera_ap=hosts/AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
        "",
        "Optional terms: archive=hosts/.../MultimediaStorage waittimeout=90000",
    ])
    return {
        "text": "\n".join(lines),
        "buttons": buttons or [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
    }


def _single_camera_export_result_payload(result: dict[str, object]) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    selection = result.get("selection") if isinstance(result.get("selection"), dict) else {}
    export = result.get("export") if isinstance(result.get("export"), dict) else {}
    status = export.get("status") if isinstance(export.get("status"), dict) else {}

    lines = [
        "📦 *Single-camera export*",
        f"Camera: {compact_value(selection.get('camera'))}",
        f"Window: {fmt_ts_utc(selection.get('request_begin'))} -> {fmt_ts_utc(selection.get('request_end'))}",
    ]

    if request.get("archive"):
        lines.append(f"Archive: {compact_value(request.get('archive'))}")

    if status:
        progress = float(status.get("progress") or 0.0)
        lines.append(
            f"Server export: state {compact_value(status.get('state'))} · progress {progress:.0%}"
        )

    if export.get("file_name"):
        lines.append(f"File: `{compact_value(export.get('file_name'))}`")
    if export.get("size_bytes") is not None:
        lines.append(f"Size: {_format_size_bytes(export.get('size_bytes'))}")

    if export.get("ok"):
        lines.append("Result: clip ready.")
    else:
        lines.append(f"Result: unavailable ({compact_value(export.get('error'))})")

    payload = {
        "text": "\n".join(lines),
        "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        "meta": {"kind": "single_camera_export"},
        "result": result,
    }
    media_path = str(export.get("path") or "").strip()
    if export.get("ok") and media_path:
        payload["media_path"] = media_path
    return payload


def single_camera_export_payload(common: list[str], terms: list[str]):
    try:
        request = parse_single_camera_export_terms(terms)
    except SingleCameraExportSyntaxError as exc:
        return _single_camera_export_help_payload(str(exc))

    try:
        result = run_api(common + ["single-camera-export", *single_camera_export_request_to_api_args(request)])
    except Exception as exc:
        return {
            "text": f"⚠️ Single-camera export failed.\n{exc}",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ Single-camera export returned an unexpected payload.",
            "buttons": [[btn("🎬 Archive", "arch:menu"), btn("🏠 Main", "home")]],
        }
    return _single_camera_export_result_payload(result)


def _macro_execution_help_payload(error_text: str | None = None):
    lines = ["⚙️ Macro execution"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Admin-only. Preview is read-safe; execution still requires explicit confirmation.",
        "The runtime blocks macros unless execution is enabled, the macro is allowlisted,",
        "the macro is a manual/common menu action, and no denied action families are present.",
        "",
        "Examples:",
        "/macro id=941f88d1-b512-4189-84a6-7d274892dd95",
        "/macro name=Manual Alert Test",
    ])
    return {"text": "\n".join(lines), "buttons": [[btn("🏠 Main", "home")]]}


def _macro_execution_preview_payload(result: dict[str, object]) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    selector = request.get("selector") if isinstance(request.get("selector"), dict) else {}
    macro = result.get("macro") if isinstance(result.get("macro"), dict) else {}
    guardrails = result.get("guardrails") if isinstance(result.get("guardrails"), dict) else {}
    policy = guardrails.get("policy") if isinstance(guardrails.get("policy"), dict) else {}
    reasons = [str(item).strip() for item in (guardrails.get("reasons") or []) if str(item).strip()]
    warnings = [str(item).strip() for item in (guardrails.get("warnings") or []) if str(item).strip()]
    allowed = bool(guardrails.get("allowed"))

    lines = [
        "✅ Macro execution preview" if allowed else "⛔️ Macro execution blocked",
        f"Selector: {compact_value(selector.get('kind'))}={compact_value(selector.get('value'))}",
        f"Macro: {compact_value(macro.get('name'))}",
        f"ID: {compact_value(macro.get('id'))}",
        (
            f"Mode: {compact_value(macro.get('mode_kind'))} · "
            f"enabled {compact_value(macro.get('enabled'))} · "
            f"menu {compact_value(macro.get('is_add_to_menu'))}"
        ),
        f"Actions: {', '.join(macro.get('action_families') or []) or 'unknown'}",
        (
            f"Policy: config {compact_value(policy.get('execution_enabled'))} · "
            f"admin {compact_value(policy.get('admin'))} · "
            f"allowlist {compact_value(policy.get('allowlist_configured'))}"
        ),
    ]
    if macro.get("user_role"):
        lines.append(f"Axxon user_role: {compact_value(macro.get('user_role'))}")
    if reasons:
        lines.extend(["", "Blocked by:"])
        lines.extend([f"- {item}" for item in reasons])
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend([f"- {item}" for item in warnings])
    if allowed:
        lines.extend(["", "Confirm in Telegram to execute this one macro."])

    return {
        "text": "\n".join(lines),
        "buttons": [[btn("🏠 Main", "home")]],
        "meta": {
            "kind": "macro_execution_preview",
            "allowed": allowed,
            "macro_id": compact_value(macro.get("id")),
            "macro_name": compact_value(macro.get("name")),
        },
        "result": result,
    }


def macro_execution_payload(
    common: list[str],
    terms: list[str],
    *,
    execution_enabled: bool = False,
    admin: bool = False,
    allow_ids: list[str] | None = None,
    allow_names: list[str] | None = None,
):
    try:
        request = parse_macro_execution_terms(terms)
    except MacroExecutionSyntaxError as exc:
        return _macro_execution_help_payload(str(exc))

    policy = build_macro_execution_policy(
        execution_enabled=execution_enabled,
        admin=admin,
        allowed_macro_ids=allow_ids or (),
        allowed_macro_names=allow_names or (),
    )
    try:
        result = run_api(
            common
            + ["macro-preview", *macro_execution_request_to_api_args(request), *macro_execution_policy_to_api_args(policy)]
        )
    except Exception as exc:
        return {
            "text": f"⚠️ Macro execution preview failed.\n{exc}",
            "buttons": [[btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ Macro execution preview returned an unexpected payload.",
            "buttons": [[btn("🏠 Main", "home")]],
        }
    return _macro_execution_preview_payload(result)


def _ptz_capability_mode_label(value: object) -> str:
    if isinstance(value, dict):
        if value.get("is_absolute"):
            return "absolute"
        if value.get("is_continuous"):
            return "continuous"
    return "—"


def _ptz_control_help_payload(error_text: str | None = None):
    lines = ["🎛️ PTZ control"]
    if error_text:
        lines.extend(["", f"⚠️ {error_text}"])
    lines.extend([
        "",
        "Admin-only. This command stays out of the menu and always previews first.",
        "The runtime only allows allowlisted cameras and only exposes preset jumps in this MVP.",
        "",
        "Examples:",
        "/ptz camera=2.Gate",
        "/ptz camera=2.Gate preset=Home",
        "/ptz camera_ap=hosts/Server/DeviceIpint.200/SourceEndpoint.video:0:0 position=12 speed=5",
    ])
    return {"text": "\n".join(lines), "buttons": [[btn("🏠 Main", "home")]]}


def _ptz_control_preview_payload(result: dict[str, object]) -> dict[str, object]:
    request = result.get("request") if isinstance(result.get("request"), dict) else {}
    camera = result.get("camera") if isinstance(result.get("camera"), dict) else {}
    ptz = result.get("ptz") if isinstance(result.get("ptz"), dict) else {}
    guardrails = result.get("guardrails") if isinstance(result.get("guardrails"), dict) else {}
    policy = guardrails.get("policy") if isinstance(guardrails.get("policy"), dict) else {}
    camera_selector = request.get("camera_selector") if isinstance(request.get("camera_selector"), dict) else {}
    preset_selector = request.get("preset_selector") if isinstance(request.get("preset_selector"), dict) else {}
    capabilities = ptz.get("capabilities") if isinstance(ptz.get("capabilities"), dict) else {}
    position = ptz.get("absolute_position") if isinstance(ptz.get("absolute_position"), dict) else {}
    selected_preset = ptz.get("selected_preset") if isinstance(ptz.get("selected_preset"), dict) else {}
    reasons = [str(item).strip() for item in (guardrails.get("reasons") or []) if str(item).strip()]
    warnings = [str(item).strip() for item in (guardrails.get("warnings") or []) if str(item).strip()]
    presets = [item for item in (ptz.get("presets") or []) if isinstance(item, dict)]
    allowed = bool(guardrails.get("allowed"))

    lines = [
        "✅ PTZ preset preview" if allowed else "⛔️ PTZ control blocked",
        f"Camera selector: {compact_value(camera_selector.get('kind'))}={compact_value(camera_selector.get('value'))}",
        f"Camera: {compact_value(camera.get('name'))}",
        f"Source: {compact_value(camera.get('access_point'))}",
        (
            f"Inventory: PTZ {compact_value(camera.get('ptz_count'))} · "
            f"active {compact_value(camera.get('ptz_active_count'))} · "
            f"point {compact_value(camera.get('point_move'))} · "
            f"area {compact_value(camera.get('area_zoom'))}"
        ),
        (
            f"Capabilities: move {_ptz_capability_mode_label(capabilities.get('move_supported'))} · "
            f"zoom {_ptz_capability_mode_label(capabilities.get('zoom_supported'))} · "
            f"tours {compact_value(capabilities.get('is_tours_supported'))}"
        ),
        (
            f"Position: pan {compact_value(position.get('pan'))} · "
            f"tilt {compact_value(position.get('tilt'))} · "
            f"zoom {compact_value(position.get('zoom'))}"
        ),
        (
            f"Policy: config {compact_value(policy.get('control_enabled'))} · "
            f"admin {compact_value(policy.get('admin'))} · "
            f"allowlist {compact_value(policy.get('allowlist_configured'))}"
        ),
    ]
    if preset_selector:
        lines.append(
            f"Requested preset: {compact_value(preset_selector.get('kind'))}={compact_value(preset_selector.get('value'))}"
        )
    if selected_preset:
        lines.append(
            f"Selected preset: {compact_value(selected_preset.get('label'))} ({compact_value(selected_preset.get('position'))})"
        )
    if presets:
        preview = " · ".join(
            f"{compact_value(item.get('label'))} ({compact_value(item.get('position'))})"
            for item in presets[:6]
        )
        if len(presets) > 6:
            preview += " · …"
        lines.append(f"Presets: {preview}")
    else:
        lines.append("Presets: none discovered")
    if ptz.get("preview_error"):
        lines.append(f"Preview note: {compact_value(ptz.get('preview_error'))}")
    if reasons:
        lines.extend(["", "Blocked by:"])
        lines.extend([f"- {item}" for item in reasons])
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend([f"- {item}" for item in warnings])
    if allowed:
        lines.extend([
            "",
            f"Confirm in Telegram to move to preset {compact_value(selected_preset.get('label'))} at speed {compact_value(request.get('speed'))}.",
        ])

    return {
        "text": "\n".join(lines),
        "buttons": [[btn("🏠 Main", "home")]],
        "meta": {
            "kind": "ptz_control_preview",
            "allowed": allowed,
            "camera_access_point": compact_value(camera.get("access_point")),
            "camera_name": compact_value(camera.get("name")),
            "preset_label": compact_value(selected_preset.get("label")),
            "preset_position": compact_value(selected_preset.get("position")),
            "speed": compact_value(request.get("speed")),
        },
        "result": result,
    }


def ptz_control_payload(
    common: list[str],
    terms: list[str],
    *,
    control_enabled: bool = False,
    admin: bool = False,
    allow_camera_aps: list[str] | None = None,
    allow_camera_names: list[str] | None = None,
):
    try:
        request = parse_ptz_control_terms(terms)
    except PtzControlSyntaxError as exc:
        return _ptz_control_help_payload(str(exc))

    policy = build_ptz_control_policy(
        control_enabled=control_enabled,
        admin=admin,
        allowed_camera_access_points=allow_camera_aps or (),
        allowed_camera_names=allow_camera_names or (),
    )
    try:
        result = run_api(
            common
            + ["ptz-preview", *ptz_control_request_to_api_args(request), *ptz_control_policy_to_api_args(policy)]
        )
    except Exception as exc:
        return {
            "text": f"⚠️ PTZ preview failed.\n{exc}",
            "buttons": [[btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ PTZ preview returned an unexpected payload.",
            "buttons": [[btn("🏠 Main", "home")]],
        }
    return _ptz_control_preview_payload(result)


def alert_flag_to_severity(flag: str) -> str | None:
    mapping = {
        "confirmed": "SV_ALARM",
        "suspicious": "SV_WARNING",
        "false": "SV_FALSE",
    }
    return mapping.get((flag or "").strip().lower())


def server_info_payload(common: list[str], domain: bool = False):
    tg_server_ui.run_api = run_api
    return tg_server_ui.server_info_payload(common, domain=domain)


def server_version_payload(common: list[str]):
    tg_server_ui.run_api = run_api
    return tg_server_ui.server_version_payload(common)


def server_statistics_payload(common: list[str]):
    tg_server_ui.run_api = run_api
    return tg_server_ui.server_statistics_payload(common)


def admin_view_payload(common: list[str], section: str = "menu", *, admin: bool = False):
    tg_admin_ui.run_api = run_api
    return tg_admin_ui.admin_view_payload(common, section=section, admin=admin)


def _short_token(kind: str, value: str) -> str:
    raw = f"{kind}:{value}".encode("utf-8", errors="replace")
    return hashlib.blake2s(raw, digest_size=EVENT_TOKEN_DIGEST_BYTES).hexdigest()


def _camera_key(card: dict) -> str:
    camera_ap = str(card.get("camera_access_point") or "").strip()
    if camera_ap:
        return f"ap:{camera_ap}"
    camera_name = str(card.get("camera") or "Camera").strip() or "Camera"
    return f"name:{camera_name}"


def _detector_key(card: dict) -> str:
    detector_ap = str(card.get("detector_access_point") or "").strip()
    if detector_ap:
        return f"ap:{detector_ap}"
    detector_name = str(card.get("detector") or card.get("event_type") or "Detector").strip() or "Detector"
    return f"{_camera_key(card)}|name:{detector_name}"


def _collect_event_cameras(cards: list[dict]) -> list[dict]:
    buckets: dict[str, dict] = {}
    for card in cards:
        key = _camera_key(card)
        token = _short_token("cam", key)
        entry = buckets.get(token)
        if entry and entry["key"] != key:
            raise ValueError("camera token collision in event navigation")
        if not entry:
            entry = {
                "key": key,
                "token": token,
                "camera": str(card.get("camera") or "Camera"),
                "count": 0,
            }
            buckets[token] = entry
        entry["count"] += 1
    return sorted(buckets.values(), key=lambda item: (item["camera"].lower(), item["token"]))


def _collect_event_detectors(cards: list[dict], camera_token: str | None = None) -> tuple[dict | None, list[dict]]:
    camera_entry = None
    if camera_token:
        for item in _collect_event_cameras(cards):
            if item["token"] == camera_token:
                camera_entry = item
                break
        if not camera_entry:
            return None, []

    buckets: dict[str, dict] = {}
    for card in cards:
        if camera_entry and _camera_key(card) != camera_entry["key"]:
            continue
        key = _detector_key(card)
        token = _short_token("det", key)
        entry = buckets.get(token)
        if entry and entry["key"] != key:
            raise ValueError("detector token collision in event navigation")
        if not entry:
            primary_label = str(card.get("label_primary") or "").strip()
            entry = {
                "key": key,
                "token": token,
                "camera": str(card.get("camera") or "Camera"),
                "camera_token": _short_token("cam", _camera_key(card)),
                "detector": str(card.get("detector") or card.get("event_type") or "Detector"),
                "preview": primary_label,
                "count": 0,
            }
            buckets[token] = entry
        entry["count"] += 1
    return camera_entry, sorted(buckets.values(), key=lambda item: (item["detector"].lower(), item["token"]))


def _resolve_detector_entry(cards: list[dict], detector_token: str, camera_token: str | None = None) -> dict | None:
    _, detectors = _collect_event_detectors(cards, camera_token=camera_token)
    for entry in detectors:
        if entry["token"] == detector_token:
            return entry
    return None


def _event_list_button_label(card: dict) -> str:
    when = fmt_ts_short(card.get("timestamp"))
    title = event_compact_label(card, include_status=True, include_secondary=False, limit=34)
    suffix = ""
    plate = str(card.get("plate") or "").strip()
    if plate and plate.lower() not in title.lower():
        suffix = f" · {plate}"
    return compact_text(f"{when} · {title}{suffix}", 48)


def _event_lookup_seconds(event_type: str, seconds: int) -> int:
    if event_type == "ET_Alert":
        return max(seconds, ALERTS_WINDOW_SECONDS)
    return max(seconds, EVENTS_WINDOW_SECONDS)


def detector_list_payload(common: list[str], seconds: int, camera_token: str):
    cards = _event_cards(common, seconds, limit=EVENT_CARD_LIMIT)
    camera_entry, items = _collect_event_detectors(cards, camera_token=camera_token)
    camera_name = camera_entry["camera"] if camera_entry else "Camera"
    lines = [
        f"🎛 *{camera_name}*",
        f"Detectors with recent events: {len(items)}",
        "Choose detector:",
    ]
    if not items:
        lines.append("No detectors with recent events.")
    buttons = []
    for item in items:
        label_parts = [str(item["detector"] or "Detector")]
        preview = str(item.get("preview") or "").strip()
        if preview and preview.lower() != label_parts[0].lower():
            label_parts.append(preview)
        label_parts.append(str(item["count"]))
        buttons.append([btn(compact_text(" · ".join(label_parts), 48), f"ev:det:{camera_token}:{item['token']}")])
    buttons.append([btn("⬅️ Back", "ev:feed:0"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def detector_events_payload(common: list[str], seconds: int, camera_token: str, detector_token: str, offset: int = 0):
    cards = _event_cards(common, seconds, limit=EVENT_CARD_LIMIT)
    detector_entry = _resolve_detector_entry(cards, detector_token, camera_token=camera_token)
    filtered = [card for card in cards if detector_entry and _detector_key(card) == detector_entry["key"]]
    page = filtered[offset: offset + EVENTS_PAGE_SIZE]
    camera_name = detector_entry["camera"] if detector_entry else "Camera"
    detector_name = detector_entry["detector"] if detector_entry else "Detector"
    lines = [
        f"📋 *{detector_name}*",
        f"{camera_name} · recent events: {len(filtered)}",
        "Choose event:",
    ]
    if not page:
        lines.append("No events found in the current window.")
    buttons = []
    for card in page:
        card_id = card.get("id") or ""
        buttons.append([btn(_event_list_button_label(card), f"ev:open:{card_id}:{detector_token}:{offset}")])
    nav: list[dict] = []
    if offset > 0:
        nav.append(btn("⬅️ Previous", f"ev:list:{camera_token}:{detector_token}:{max(0, offset - EVENTS_PAGE_SIZE)}"))
    if offset + EVENTS_PAGE_SIZE < len(filtered):
        nav.append(btn("Next ➡️", f"ev:list:{camera_token}:{detector_token}:{offset + EVENTS_PAGE_SIZE}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("⬅️ Back", f"ev:cam:{camera_token}"), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons}


def alert_state_badge(state: str | None) -> str:
    value = (state or "ACTIVE").upper()
    if value in {"ST_WANT_REACTION", "ACTIVE", "RAISED", "NEW"}:
        return "🔴 ACTIVE"
    if value in {"ST_IN_PROGRESS", "ACKNOWLEDGED", "IN_PROGRESS"}:
        return "🟡 ACK"
    if value in {"ST_RESOLVED", "ST_CLOSED", "RESOLVED", "CLOSED", "ENDED"}:
        return "🟢 RESOLVED"
    return f"⚪️ {value}"


def alert_priority_badge(priority) -> str:
    value = str(priority or "").strip().upper()
    if value in {"3", "HIGH", "CRITICAL", "AP_HIGH", "AP_CRITICAL"}:
        return "🟥 P3"
    if value in {"2", "MEDIUM", "AP_MEDIUM"}:
        return "🟧 P2"
    if value in {"1", "LOW", "AP_LOW"}:
        return "🟩 P1"
    if value:
        return f"🔹 {value}"
    return "🔹 P?"


def alerts_payload(common: list[str], seconds: int, limit: int, offset: int = 0):
    cards = run_api(common + [
        "telegram-cards",
        "--seconds", str(seconds),
        "--event-type", "ET_Alert",
        "--limit", str(limit),
    ])
    cards = cards if isinstance(cards, list) else []
    page = cards[offset: offset + ALERTS_PAGE_SIZE]
    lines = [
        "🚨 *Alerts*",
        f"Last 60 minutes ({DISPLAY_TZ_LABEL}) · {len(cards)} total",
        "Tap an alert:",
    ]
    if not page:
        lines.append("No alerts found.")

    buttons = []
    for row_idx, card in enumerate(page, start=1):
        card_id = card.get("id") or ""
        buttons.append([btn(event_button_label(row_idx, card), f"al:open:{card_id}")])
    nav: list[dict] = []
    if offset > 0:
        nav.append(btn("⬅️ Previous", f"al:feed:{max(0, offset - ALERTS_PAGE_SIZE)}"))
    if offset + ALERTS_PAGE_SIZE < len(cards):
        nav.append(btn("Next ➡️", f"al:feed:{offset + ALERTS_PAGE_SIZE}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("🔔 Subscribe to alerts", "sub:new:alert")])
    buttons.append([btn("🚨 Events", "ev:feed:0"), btn("🏠 Main", "home")])
    return {
        "text": "\n".join(lines),
        "buttons": buttons,
        "cards": cards,
        "meta": {"kind": "alerts_feed", "page_size": len(page), "total_cards": len(cards)},
    }


def home_payload(common: list[str], seconds: int, limit: int, *, admin: bool = False):
    dashboard = run_api(common + ["dashboard", "--seconds", str(seconds), "--limit", str(limit)])
    try:
        version_data = run_api(common + ["server-version"]) or {}
    except Exception:
        version_data = {}
    version = "unknown"
    if isinstance(version_data, dict):
        version = (
            str(version_data.get("version") or "").strip()
            or str(version_data.get("backendVersion") or "").strip()
            or str(version_data.get("httpSdk") or "").strip()
            or "unknown"
        )

    alert_cards = run_api(common + [
        "telegram-cards",
        "--seconds", "3600",
        "--event-type", "ET_Alert",
        "--limit", "300",
    ])
    alerts_count = len(alert_cards or [])
    latest_alerts = (alert_cards or [])[:HOME_ALERT_BUTTON_LIMIT]
    by_category = (dashboard.get("by_category") or {}) if isinstance(dashboard, dict) else {}
    mix_labels = {
        "lpr": "LPR",
        "motion": "Motion",
        "traffic": "Traffic",
        "meta": "Meta",
        "other": "Other",
    }
    mix_parts = [f"{mix_labels[key]} {by_category.get(key)}" for key in mix_labels if by_category.get(key)]
    mix_line = " · ".join(mix_parts[:4]) if mix_parts else "No detector events in the dashboard window."

    lines = [
        "👋 *Axxon One Home*",
        "Choose what you want to do.",
        f"Recent alerts: {alerts_count} in the last hour",
        f"Recent mix: {mix_line}",
        f"Version: {version}",
        "Open cameras, review alerts, or start a search from the buttons below.",
    ]
    lines.append("Latest alerts are ready below." if latest_alerts else "No recent alerts to review.")

    buttons = []
    for row_idx, card in enumerate(latest_alerts, start=1):
        card_id = card.get("id") or ""
        buttons.append([btn(event_button_label(row_idx, card), f"al:open:{card_id}")])
    buttons.extend([
        [btn("📷 Cameras", "cam:list:0"), btn("🚨 Events", "ev:feed:0")],
        [btn("🚨 Alerts", "al:feed:0"), btn("🔎 Search", "sea:menu")],
        [btn("🎬 Archive", "arch:menu"), btn("🔔 Subscribe", "sub:det:list")],
        [btn("📋 Subscriptions", "sub:list"), btn("📊 My stats", "sub:stats")],
        [btn("🖥 Server", "srv:menu"), btn("🛠 Health", "sys:health")],
    ])
    if admin:
        buttons.append([btn("🛠 Admin view", "adm:menu")])
    return {"text": "\n".join(lines), "buttons": buttons, "raw": dashboard}


def _event_cards(common: list[str], seconds: int, limit: int = 200) -> list[dict]:
    cards = run_api(common + ["telegram-cards", "--seconds", str(seconds), "--limit", str(limit)])
    cards = cards if isinstance(cards, list) else []
    return [card for card in cards if not (card.get("event_type") == "moveInZone" and card.get("state") == "ENDED")]


def events_payload(common: list[str], seconds: int, limit: int, offset: int = 0, filter_page: int = 0, categories: list[str] | None = None):
    cards = _event_cards(common, seconds, limit=limit)
    camera_items = _collect_event_cameras(cards)
    page = camera_items[offset: offset + EVENTS_PAGE_SIZE]
    lines = [
        "🚨 *Events*",
        f"Last 30 minutes ({DISPLAY_TZ_LABEL}) · {len(cards)} events",
        "Choose camera:",
    ]
    if not page:
        lines.append("No detector events found.")

    buttons = []
    for meta in page:
        buttons.append([btn(compact_text(f"{meta['camera']} · {meta['count']}", 48), f"ev:cam:{meta['token']}")])

    nav: list[dict] = []
    if offset > 0:
        nav.append(btn("⬅️ Previous", f"ev:feed:{max(0, offset - EVENTS_PAGE_SIZE)}"))
    if offset + EVENTS_PAGE_SIZE < len(camera_items):
        nav.append(btn("Next ➡️", f"ev:feed:{offset + EVENTS_PAGE_SIZE}"))
    if nav:
        buttons.append(nav)
    buttons.append([btn("🏠 Main", "home")])
    return {
        "text": "\n".join(lines),
        "buttons": buttons,
        "cards": cards,
        "meta": {"kind": "events_feed", "page_size": len(page), "total_cards": len(cards)},
    }


def open_event_payload(
    common: list[str],
    seconds: int,
    event_id: str,
    event_type: str = "ET_DetectorEvent",
    back_cb: str | None = None,
    back_txt: str | None = None,
    archive_cb: str | None = None,
):
    lookup_seconds = _event_lookup_seconds(event_type, seconds)
    cards = run_api(common + [
        "telegram-cards",
        "--seconds", str(lookup_seconds),
        "--event-type", event_type,
        "--limit", str(EVENT_CARD_LIMIT),
    ])
    cards = cards if isinstance(cards, list) else []
    card = next((item for item in cards if item.get("id") == event_id), None)
    if not card:
        fallback_back_cb = "al:feed:0" if event_type == "ET_Alert" else "ev:feed:0"
        return {"text": "Event not found in the current history window.", "buttons": [[btn(back_txt or "⬅️ Back", back_cb or fallback_back_cb), btn("🏠 Main", "home")]]}

    header = "🧾 *Alert card*" if event_type == "ET_Alert" else "🧾 *Event card*"
    summary = compact_value(card.get("label_primary") or card.get("text") or card.get("event_type"))
    lines = [
        header,
        f"What happened: {summary}",
        f"When: {fmt_ts_utc(card.get('timestamp'))}",
        f"Where: {compact_value(card.get('camera'))}",
        f"Detector: {compact_value(card.get('detector'))}",
    ]
    if event_type == "ET_Alert":
        lines.append(f"Status: {alert_priority_badge(card.get('priority'))} {alert_state_badge(card.get('state'))}")
        if not (card.get("alert_id") and card.get("camera_access_point")):
            lines.append("⚠️ Alert review is unavailable via API because `alert_id` or `camera_access_point` is missing.")
    else:
        lines.append(f"Event type: {compact_value(card.get('event_type'))} / {compact_value(card.get('state'))}")
    if card.get("plate"):
        vehicle = card.get("vehicle") or {}
        lines.extend([
            f"Plate: *{card.get('plate')}*",
            f"Vehicle: {vehicle.get('brand')} / {vehicle.get('model')} / {vehicle.get('color')}",
        ])
    detail_text = str(card.get("text") or "").strip()
    if detail_text and detail_text != summary:
        lines.extend(["", detail_text])

    prefix = "al" if event_type == "ET_Alert" else "ev"
    resolved_back_cb = back_cb or ("al:feed:0" if event_type == "ET_Alert" else "ev:feed:0")
    resolved_archive_cb = archive_cb or f"{prefix}:arch:{event_id}"
    buttons = [
        [btn("🖼 Frame", f"{prefix}:frame:{event_id}"), btn("🎬 30s clip", f"{prefix}:clip30:{event_id}")],
        [btn("🎬 Archive", resolved_archive_cb)],
    ]
    if event_type == "ET_Alert":
        buttons.append([
            btn("✅ Confirmed", f"al:flag:confirmed:{event_id}"),
            btn("⚠️ Suspicious", f"al:flag:suspicious:{event_id}"),
        ])
        buttons.append([btn("❌ False alarm", f"al:flag:false:{event_id}")])
    buttons.append([btn(back_txt or "⬅️ Back", resolved_back_cb), btn("🏠 Main", "home")])
    return {"text": "\n".join(lines), "buttons": buttons, "card": card}


def find_raw_event_by_id(common: list[str], seconds: int, event_id: str, event_type: str = "ET_DetectorEvent"):
    events = run_api(common + ["events", "--seconds", str(_event_lookup_seconds(event_type, seconds)), "--event-type", event_type, "--limit", "300"])
    for item in events:
        if (item.get("body", {}) or {}).get("guid") == event_id:
            return item
    return None


def _live_status_payload(idx: int, state: str):
    if state == "start":
        if idx < 0:
            return {"text": "Camera not found.", "buttons": [[btn("⬅️ Back", "cam:list:0"), btn("🏠 Main", "home")]]}
        text = (
            "▶ Live monitor requested.\n"
            "The bot refreshes this chat every few seconds while live monitor is active.\n"
            "Stop it when you are done."
        )
        buttons = [
            [btn("▶ Live monitor", f"cam:live:start:{idx}"), btn("⏹ Stop", "cam:live:stop")],
            [btn("📸 Live snapshot", f"cam:lsnap:{idx}"), btn("🚨 Incidents", f"cam:inc:{idx}:0")],
            [btn("⬅️ Back", f"cam:open:{idx}"), btn("🏠 Main", "home")],
        ]
        return {"text": text, "buttons": buttons}
    return {
        "text": "⏹ Live monitor stop requested.",
        "buttons": [[btn("📷 Cameras", "cam:list:0"), btn("🏠 Main", "home")]],
    }


def _search_menu_payload():
    return {
        "text": (
            "🔎 *Search & lookup*\n\n"
            "Choose what you want to search.\n"
            "Use the buttons below to open the right search help.\n"
            "For face search, upload a Telegram photo. Event and plate searches also support advanced typed commands when you need exact filters."
        ),
        "buttons": [
            [btn("🔎 Events", "sea:event"), btn("🚘 Plates", "sea:plate")],
            [btn("🙂 Faces", "sea:face"), btn("🎬 Archive", "arch:menu")],
            [btn("🏠 Main", "home")],
        ],
    }


def _lpr_menu_payload(common: list[str], *, buttons: list[list[dict]] | None = None):
    cards = run_api(common + ["telegram-cards", "--seconds", "3600", "--limit", "300"])
    lpr = [card for card in (cards or []) if card.get("category") == "lpr"]
    rows = [card for card in lpr if card.get("plate")] or lpr

    lines = [
        "🔎 *License plate search*",
        f"Recent LPR activity: last 60 minutes ({DISPLAY_TZ_LABEL})",
        "",
        "Search commands:",
        "/plate plate=BE59922",
        "/plate contains=5992 camera=2.Gate last=7200",
        "/plate mask=*9922 from=20260308T220000 to=20260308T230000",
        "",
    ]
    if not rows:
        lines.append("No LPR events in the last hour.")
    else:
        lines.append("Recent matches:")
        for idx, row in enumerate(rows[:5], start=1):
            plate = row.get("plate") or "(no plate)"
            vehicle = row.get("vehicle") or {}
            brand = vehicle.get("brand") or "—"
            model = vehicle.get("model") or "—"
            lines.append(f"{idx}. {fmt_ts_utc(row.get('timestamp'))} · {plate} · {brand} {model}")
    return {
        "text": "\n".join(lines),
        "buttons": buttons or [[btn("🔎 Search", "sea:menu"), btn("🎬 Archive", "arch:menu")], [btn("🏠 Main", "home")]],
    }


def _archive_now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _archive_ts_compact(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S")


def _archive_ts_parse_compact(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)


def _archive_ts_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _archive_ts_from_api(value: object) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    for candidate in (raw, raw.replace("Z", "+00:00")):
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass
    for fmt in ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M%S.%f"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _archive_result_nav_buttons(camera_idx: int, target_dt: datetime) -> list[list[dict]]:
    compact = _archive_ts_compact(target_dt)
    return [
        [
            btn("⏪ -60s", f"arch:seek:{camera_idx}:{compact}:-60"),
            btn("◀ -15s", f"arch:seek:{camera_idx}:{compact}:-15"),
            btn("▶ +15s", f"arch:seek:{camera_idx}:{compact}:15"),
            btn("⏩ +60s", f"arch:seek:{camera_idx}:{compact}:60"),
        ]
    ]


def _archive_best_available_point(result: dict[str, object]) -> datetime | None:
    selection = result.get("selection") if isinstance(result.get("selection"), dict) else {}
    archive = result.get("archive") if isinstance(result.get("archive"), dict) else {}
    handle = archive.get("context_handle") if isinstance(archive.get("context_handle"), dict) else {}
    depth = archive.get("depth") if isinstance(archive.get("depth"), dict) else {}

    requested = _archive_ts_from_api(selection.get("timestamp"))
    interval_begin = _archive_ts_from_api(handle.get("interval_begin"))
    interval_end = _archive_ts_from_api(handle.get("interval_end"))
    depth_start = _archive_ts_from_api(depth.get("start"))
    depth_end = _archive_ts_from_api(depth.get("end"))

    if requested is None:
        return interval_begin or depth_start or interval_end or depth_end
    if interval_begin and interval_end:
        if requested < interval_begin:
            return interval_begin
        if requested > interval_end:
            return interval_end
        return requested
    if depth_start and requested < depth_start:
        return depth_start
    if depth_end and requested > depth_end:
        return depth_end
    return interval_begin or depth_start or interval_end or depth_end


def _archive_unavailable_buttons(camera_idx: int, result: dict[str, object]) -> list[list[dict]]:
    target = _archive_best_available_point(result)
    if target is None:
        return []
    compact = _archive_ts_compact(target)
    return [[btn("⏭ Nearest available", f"arch:goto:{camera_idx}:{compact}")]]


def _archive_menu_payload():
    return {
        "text": (
            "🎬 *Archive & export*\n\n"
            "Choose Jump for a quick archive preview.\n"
            "Use Wizard for the easy Telegram flow: choose camera → choose time → preview archive.\n"
            "Use Export when you need a clip file.\n"
            "Any event or alert card can also open archive context directly."
        ),
        "buttons": [
            [btn("✨ Archive wizard", "arch:wiz:0"), btn("🎬 Jump help", "arch:jump")],
            [btn("📦 Export help", "arch:export"), btn("📷 Cameras", "cam:list:0")],
            [btn("🔎 Search", "sea:menu"), btn("🏠 Main", "home")],
        ],
    }


def _status_payload(common: list[str]):
    try:
        events = run_api(common + ["events", "--seconds", "300", "--limit", "1"])
        ok = bool(events)
        text = (
            "🛠 *Status*\n\n"
            "Axxon API: ✅ reachable\n"
            f"Recent events: {'present' if ok else 'none in the last 5 minutes'}"
        )
    except Exception as ex:
        text = f"🛠 *Status*\n\nAxxon API: ❌ error\n{ex}"
    return {"text": text, "buttons": [[btn("🔄 Refresh", "sys:health"), btn("🏠 Main", "home")]]}


def _frame_payload(common: list[str], seconds: int, event_id: str, event_type: str):
    event = find_raw_event_by_id(common, seconds, event_id, event_type=event_type)
    if not event:
        back = "al:feed:0" if event_type == "ET_Alert" else "ev:feed:0"
        noun = "Alert" if event_type == "ET_Alert" else "Event"
        return {"text": f"{noun} for frame not found.", "buttons": [[btn("⬅️ Back", back), btn("🏠 Main", "home")]]}
    prefix = "alert" if event_type == "ET_Alert" else "event"
    event_json = Path(f"/tmp/axxon_tg_{prefix}_{event_id}.json")
    event_json.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    out = Path(f"/tmp/axxon_tg_{prefix}_frame_{event_id}.jpg")
    path = run_api(common + ["frame-from-event", "--event-json", str(event_json), "--out", str(out), "--mode", "media"])
    open_cb = f"al:open:{event_id}" if event_type == "ET_Alert" else f"ev:open:{event_id}"
    back_cb = "al:feed:0" if event_type == "ET_Alert" else "ev:feed:0"
    noun = "Alert" if event_type == "ET_Alert" else "Event"
    return {"text": f"🖼 {noun} frame {event_id}", "media_path": path, "buttons": [[btn("Open card", open_cb), btn("⬅️ Back", back_cb)], [btn("🏠 Main", "home")]]}


def _clip_payload(common: list[str], seconds: int, event_id: str, event_type: str):
    event = find_raw_event_by_id(common, seconds, event_id, event_type=event_type)
    if not event:
        back = "al:feed:0" if event_type == "ET_Alert" else "ev:feed:0"
        noun = "Alert" if event_type == "ET_Alert" else "Event"
        return {"text": f"{noun} for clip not found.", "buttons": [[btn("⬅️ Back", back), btn("🏠 Main", "home")]]}
    prefix = "alert" if event_type == "ET_Alert" else "event"
    event_json = Path(f"/tmp/axxon_tg_{prefix}_{event_id}.json")
    event_json.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    out = Path(f"/tmp/axxon_tg_{prefix}_clip_{event_id}.mp4")
    path = run_api(common + ["clip-from-event", "--event-json", str(event_json), "--out", str(out), "--pre", "15", "--post", "15"])
    open_cb = f"al:open:{event_id}" if event_type == "ET_Alert" else f"ev:open:{event_id}"
    back_cb = "al:feed:0" if event_type == "ET_Alert" else "ev:feed:0"
    noun = "Alert" if event_type == "ET_Alert" else "Event"
    return {"text": f"🎬 {noun} 30s clip {event_id}", "media_path": path, "buttons": [[btn("Open card", open_cb), btn("⬅️ Back", back_cb)], [btn("🏠 Main", "home")]]}


def _archive_jump_from_event_payload(
    common: list[str],
    seconds: int,
    event_id: str,
    event_type: str,
    *,
    open_cb: str | None = None,
):
    lookup_seconds = _event_lookup_seconds(event_type, seconds)
    cards = run_api(common + [
        "telegram-cards",
        "--seconds", str(lookup_seconds),
        "--event-type", event_type,
        "--limit", str(EVENT_CARD_LIMIT),
    ])
    cards = cards if isinstance(cards, list) else []
    card = next((item for item in cards if item.get("id") == event_id), None)
    if not card:
        noun = "Alert" if event_type == "ET_Alert" else "Event"
        return {
            "text": f"{noun} for archive jump not found.",
            "buttons": [[btn("⬅️ Back", "al:feed:0" if event_type == "ET_Alert" else "ev:feed:0"), btn("🏠 Main", "home")]],
        }

    camera_ap = str(card.get("camera_access_point") or "").strip()
    timestamp = str(card.get("timestamp") or "").strip()
    if not (camera_ap and timestamp):
        return {
            "text": (
                "Archive jump is unavailable for this card.\n"
                "Reason: missing `camera_access_point` or `timestamp`."
            ),
            "buttons": [[btn("Open card", f"{'al' if event_type == 'ET_Alert' else 'ev'}:open:{event_id}"), btn("🏠 Main", "home")]],
        }

    try:
        result = run_api(common + [
            "archive-jump",
            "--begin", timestamp,
            "--end", timestamp,
            "--at", timestamp,
            "--camera-ap", camera_ap,
        ])
    except Exception as exc:
        return {
            "text": f"⚠️ Archive jump failed.\n{exc}",
            "buttons": [[btn("Open card", f"{'al' if event_type == 'ET_Alert' else 'ev'}:open:{event_id}"), btn("🏠 Main", "home")]],
        }
    if not isinstance(result, dict):
        return {
            "text": "⚠️ Archive jump returned an unexpected payload.",
            "buttons": [[btn("Open card", f"{'al' if event_type == 'ET_Alert' else 'ev'}:open:{event_id}"), btn("🏠 Main", "home")]],
        }

    prefix = "al" if event_type == "ET_Alert" else "ev"
    contextual_open_cb = open_cb or f"{prefix}:open:{event_id}"
    payload = _archive_jump_result_payload(
        result,
        common=common,
        back_cb=contextual_open_cb,
        back_txt="⬅️ Back",
    )
    try:
        camera_idx = next(
            (idx for idx, cam in enumerate(camera_rows(common)) if str(cam.get("access_point") or "").strip() == camera_ap),
            -1,
        )
    except Exception:
        camera_idx = -1
    target_dt = _archive_ts_from_api(timestamp)
    if camera_idx >= 0 and target_dt is not None:
        buttons = payload.get("buttons") if isinstance(payload.get("buttons"), list) else []
        payload["buttons"] = buttons + _archive_result_nav_buttons(camera_idx, target_dt) + _archive_unavailable_buttons(camera_idx, result)
    return payload


def _alert_review_payload(common: list[str], seconds: int, callback_data: str):
    parts = callback_data.split(":")
    flag = parts[2] if len(parts) > 2 else ""
    event_id = parts[3] if len(parts) > 3 else ""
    severity = alert_flag_to_severity(flag)
    if not severity:
        return {"text": f"Unknown flag: {flag}", "buttons": [[btn("⬅️ Back", f"al:open:{event_id}"), btn("🏠 Main", "home")]]}

    cards = run_api(common + [
        "telegram-cards",
        "--seconds", str(max(seconds, ALERTS_WINDOW_SECONDS)),
        "--event-type", "ET_Alert",
        "--limit", str(EVENT_CARD_LIMIT),
    ])
    cards = cards if isinstance(cards, list) else []
    card = next((item for item in cards if item.get("id") == event_id), None)
    if not card:
        return {"text": "Alert not found in the current time window.", "buttons": [[btn("⬅️ Back", "al:feed:0"), btn("🏠 Main", "home")]]}

    camera_ap = card.get("camera_access_point")
    alert_id = card.get("alert_id")
    if not (camera_ap and alert_id):
        return {
            "text": (
                "ℹ️ Alert review is unavailable for this card.\n"
                "Reason: missing `camera_access_point` or `alert_id`.\n"
                f"Current status: {alert_priority_badge(card.get('priority'))} {alert_state_badge(card.get('state'))}"
            ),
            "buttons": [[btn("Open card", f"al:open:{event_id}"), btn("🏠 Main", "home")]],
        }

    result = run_api(common + [
        "alert-review",
        "--camera-ap", str(camera_ap),
        "--alert-id", str(alert_id),
        "--severity", severity,
    ])
    ok = isinstance(result, dict) and bool(result.get("ok"))
    flag_label = {"confirmed": "CONFIRMED", "suspicious": "SUSPICIOUS", "false": "FALSE"}[flag]
    before_state = card.get("state") or "ST_WANT_REACTION"
    after_state = flag_label if ok else (result.get("current_state") if isinstance(result, dict) else None) or before_state

    if ok:
        text = (
            f"✅ Alarm reviewed\n"
            f"Alert ID: {alert_id}\n"
            f"STATE: need reaction → {flag_label}\n"
            f"Severity: {severity}"
        )
    else:
        limitation = (result.get("limitation") if isinstance(result, dict) else None) or "Unknown API limitation."
        text = (
            f"⚠️ Review not applied\n"
            f"Alert ID: {alert_id}\n"
            f"STATE: {before_state} → {after_state}\n"
            f"Reason: {limitation}"
        )
    return {
        "text": text,
        "buttons": [[btn("Open card", f"al:open:{event_id}"), btn("⬅️ Back", "al:feed:0")], [btn("🏠 Main", "home")]],
        "raw": result,
    }


def _callback_payload_impl(common: list[str], seconds: int, callback_data: str, *, admin: bool = False):
    # Keep callback surface parity visible in this router for tests and operator flows:
    # sub:new:cam:, sub:new:ev:, sub:det:list, srv:menu.
    if callback_data == "home":
        return home_payload(common, seconds=3600, limit=100, admin=admin)

    if callback_data.startswith("cam:list"):
        return camera_list_payload(common, offset=parse_offset(callback_data.split(":")))

    if callback_data.startswith("cam:open:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        return camera_open_payload(common, idx)

    if callback_data.startswith("cam:inc:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        return camera_incidents_payload(common, idx=idx, offset=parse_offset(parts, idx=3), seconds=3600)

    if callback_data.startswith("cam:snap:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        return camera_snapshot_payload(common, idx=idx, seconds=3600)

    if callback_data.startswith("cam:lsnap:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        return camera_live_snapshot_payload(common, idx=idx)

    if callback_data.startswith("cam:live:start:"):
        parts = callback_data.split(":")
        idx = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else -1
        return _live_status_payload(idx, "start")

    if callback_data == "cam:live:stop":
        return _live_status_payload(-1, "stop")

    if callback_data.startswith("cam:stream:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        return camera_stream_links_payload(common, idx=idx)

    if callback_data.startswith("al:feed"):
        return alerts_payload(common, seconds=ALERTS_WINDOW_SECONDS, limit=50, offset=parse_offset(callback_data.split(":")))

    if callback_data == "sea:menu":
        return _search_menu_payload()

    if callback_data == "sea:event":
        return _event_search_help_payload(
            buttons=[[btn("⬅️ Search", "sea:menu"), btn("🏠 Main", "home")]],
        )

    if callback_data == "sea:plate":
        return _lpr_menu_payload(
            common,
            buttons=[
                [btn("⬅️ Search", "sea:menu"), btn("🎬 Archive", "arch:menu")],
                [btn("🏠 Main", "home")],
            ],
        )

    if callback_data == "sea:face":
        return _face_search_help_payload(
            buttons=[[btn("⬅️ Search", "sea:menu"), btn("🏠 Main", "home")]],
        )

    if callback_data == "lpr:menu":
        return _lpr_menu_payload(common)

    if callback_data == "arch:menu":
        return _archive_menu_payload()

    if callback_data.startswith("arch:wiz:"):
        return _archive_wizard_payload(common, offset=parse_offset(callback_data.split(":")))

    if callback_data.startswith("arch:cam:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        return _archive_camera_wizard_payload(common, idx)

    if callback_data.startswith("arch:date:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        month_key = parts[3] if len(parts) > 3 else None
        return _archive_calendar_payload(common, idx, month_key)

    if callback_data.startswith("arch:day:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        day_key = parts[3] if len(parts) > 3 else ""
        return _archive_hour_payload(common, idx, day_key, page=0)

    if callback_data.startswith("arch:hr:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        day_key = parts[3] if len(parts) > 3 else ""
        page = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
        return _archive_hour_payload(common, idx, day_key, page=page)

    if callback_data.startswith("arch:h:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        day_key = parts[3] if len(parts) > 3 else ""
        hour_key = parts[4] if len(parts) > 4 else "00"
        return _archive_minute_payload(common, idx, day_key, hour_key, page=0)

    if callback_data.startswith("arch:min:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        day_key = parts[3] if len(parts) > 3 else ""
        hour_key = parts[4] if len(parts) > 4 else "00"
        page = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
        return _archive_minute_payload(common, idx, day_key, hour_key, page=page)

    if callback_data.startswith("arch:m:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        day_key = parts[3] if len(parts) > 3 else ""
        hour_key = parts[4] if len(parts) > 4 else "00"
        minute_key = parts[5] if len(parts) > 5 else "00"
        target_dt = datetime.strptime(f"{day_key}{hour_key}{minute_key}", "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
        return _archive_jump_for_camera(common, idx, target_dt)

    if callback_data.startswith("arch:goto:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        target_key = parts[3] if len(parts) > 3 else ""
        return _archive_jump_for_camera(common, idx, _archive_ts_parse_compact(target_key))

    if callback_data == "arch:noop":
        return {"text": "📅 Use the active calendar buttons to pick date and time.", "buttons": [[btn("⬅️ Archive", "arch:menu"), btn("🏠 Main", "home")]]}

    if callback_data.startswith("arch:go:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        delta_seconds = int(parts[3]) if len(parts) > 3 and re.match(r"^-?\d+$", parts[3]) else 0
        return _archive_jump_for_camera(common, idx, _archive_now_utc() - timedelta(seconds=delta_seconds))

    if callback_data.startswith("arch:seek:"):
        parts = callback_data.split(":")
        idx = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        base_ts = parts[3] if len(parts) > 3 else ""
        delta_seconds = int(parts[4]) if len(parts) > 4 and re.match(r"^-?\d+$", parts[4]) else 0
        return _archive_jump_for_camera(common, idx, _archive_ts_parse_compact(base_ts) + timedelta(seconds=delta_seconds))

    if callback_data == "arch:jump":
        return _archive_jump_help_payload(
            buttons=[[btn("⬅️ Archive", "arch:menu"), btn("✨ Wizard", "arch:wiz:0")], [btn("🏠 Main", "home")]],
        )

    if callback_data == "arch:export":
        return _single_camera_export_help_payload(
            buttons=[[btn("⬅️ Archive", "arch:menu"), btn("🏠 Main", "home")]],
        )

    if callback_data == "sea:help":
        return _event_search_help_payload(
            buttons=[[btn("🔎 Search", "sea:menu"), btn("🏠 Main", "home")]],
        )

    if callback_data == "srv:menu":
        return server_info_payload(common, domain=False)
    if callback_data == "srv:domain":
        return server_info_payload(common, domain=True)
    if callback_data == "srv:version":
        return server_version_payload(common)
    if callback_data == "srv:stats":
        return server_statistics_payload(common)

    if callback_data == "adm:menu":
        return admin_view_payload(common, section="menu", admin=admin)
    if callback_data == "adm:hosts":
        return admin_view_payload(common, section="hosts", admin=admin)
    if callback_data == "adm:access":
        return admin_view_payload(common, section="access", admin=admin)
    if callback_data == "adm:caps":
        return admin_view_payload(common, section="caps", admin=admin)

    if callback_data == "sys:health":
        return _status_payload(common)

    if callback_data.startswith("ev:feed"):
        parts = callback_data.split(":")
        offset = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        return events_payload(common, seconds=max(seconds, EVENTS_WINDOW_SECONDS), limit=EVENT_CARD_LIMIT, offset=offset)

    if callback_data.startswith("ev:cam:"):
        camera_token = callback_data.split(":", 2)[2]
        return detector_list_payload(common, seconds=max(seconds, EVENTS_WINDOW_SECONDS), camera_token=camera_token)

    if callback_data.startswith("ev:det:"):
        parts = callback_data.split(":")
        camera_token = parts[2] if len(parts) > 2 else ""
        detector_token = parts[3] if len(parts) > 3 else ""
        return detector_events_payload(common, seconds=max(seconds, EVENTS_WINDOW_SECONDS), camera_token=camera_token, detector_token=detector_token, offset=0)

    if callback_data.startswith("ev:list:"):
        parts = callback_data.split(":")
        camera_token = parts[2] if len(parts) > 2 else ""
        detector_token = parts[3] if len(parts) > 3 else ""
        offset = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
        return detector_events_payload(common, seconds=max(seconds, EVENTS_WINDOW_SECONDS), camera_token=camera_token, detector_token=detector_token, offset=offset)

    if callback_data.startswith("ev:open:"):
        parts = callback_data.split(":")
        event_id = parts[2] if len(parts) > 2 else ""
        detector_token = parts[3] if len(parts) > 3 else ""
        offset = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
        back_cb = None
        back_txt = None
        if detector_token:
            detector_entry = _resolve_detector_entry(_event_cards(common, max(seconds, EVENTS_WINDOW_SECONDS), limit=EVENT_CARD_LIMIT), detector_token)
            if detector_entry:
                back_cb = f"ev:list:{detector_entry['camera_token']}:{detector_token}:{offset}"
                back_txt = "⬅️ Back to events"
        archive_cb = f"ev:arch:{event_id}:{detector_token}:{offset}" if detector_token else f"ev:arch:{event_id}"
        return open_event_payload(
            common,
            seconds=max(seconds, EVENTS_WINDOW_SECONDS),
            event_id=event_id,
            event_type="ET_DetectorEvent",
            back_cb=back_cb,
            back_txt=back_txt,
            archive_cb=archive_cb,
        )

    if callback_data.startswith("al:open:"):
        event_id = callback_data.split(":", 2)[2]
        return open_event_payload(
            common,
            seconds=max(seconds, ALERTS_WINDOW_SECONDS),
            event_id=event_id,
            event_type="ET_Alert",
            archive_cb=f"al:arch:{event_id}",
        )

    if callback_data.startswith("al:flag:"):
        return _alert_review_payload(common, seconds, callback_data)

    if callback_data.startswith("ev:frame:"):
        return _frame_payload(common, seconds, callback_data.split(":", 2)[2], "ET_DetectorEvent")

    if callback_data.startswith("al:frame:"):
        return _frame_payload(common, max(seconds, ALERTS_WINDOW_SECONDS), callback_data.split(":", 2)[2], "ET_Alert")

    if callback_data.startswith("ev:clip30:"):
        return _clip_payload(common, seconds, callback_data.split(":", 2)[2], "ET_DetectorEvent")

    if callback_data.startswith("al:clip30:"):
        return _clip_payload(common, max(seconds, ALERTS_WINDOW_SECONDS), callback_data.split(":", 2)[2], "ET_Alert")

    if callback_data.startswith("ev:arch:"):
        remainder = callback_data[len("ev:arch:"):]
        event_id, _, tail = remainder.partition(":")
        open_cb = f"ev:open:{event_id}:{tail}" if tail else f"ev:open:{event_id}"
        return _archive_jump_from_event_payload(
            common,
            seconds,
            event_id,
            "ET_DetectorEvent",
            open_cb=open_cb,
        )

    if callback_data.startswith("al:arch:"):
        return _archive_jump_from_event_payload(
            common,
            max(seconds, ALERTS_WINDOW_SECONDS),
            callback_data.split(":", 2)[2],
            "ET_Alert",
            open_cb=f"al:open:{callback_data.split(':', 2)[2]}",
        )

    return {"text": f"Unknown callback: {callback_data}", "buttons": [[btn("🏠 Main", "home")]]}


def callback_payload(common: list[str], seconds: int, callback_data: str, *, admin: bool = False):
    try:
        payload = _callback_payload_impl(common, seconds, callback_data, admin=admin)
    except Exception as ex:
        payload = {
            "text": (
                "⚠️ Callback processing failed.\n"
                "The requested data may not be available on this server version."
            ),
            "buttons": [[btn("🔄 Retry", callback_data)], [btn("🏠 Main", "home")]],
            "error": str(ex),
        }
    if not isinstance(payload, dict):
        return {"text": "⚠️ Callback returned unexpected payload type.", "buttons": [[btn("🔄 Retry", callback_data)], [btn("🏠 Main", "home")]]}
    if not payload.get("text"):
        payload["text"] = "⚠️ Callback returned no text."
    if not isinstance(payload.get("buttons"), list) or not payload.get("buttons"):
        payload["buttons"] = [[btn("🏠 Main", "home")]]
    return payload


def main():
    cfg = load_axxon_config()
    parser = argparse.ArgumentParser(description="Telegram UI payload builder for Axxon")
    parser.add_argument("--host", default=cfg.host)
    parser.add_argument("--user", default=cfg.user)
    parser.add_argument("--password", default=cfg.password)
    parser.add_argument("--port", default=str(cfg.port))
    parser.add_argument("--tz", default="UTC")

    sub = parser.add_subparsers(dest="cmd", required=True)

    home = sub.add_parser("home")
    home.add_argument("--seconds", type=int, default=3600)
    home.add_argument("--limit", type=int, default=100)
    home.add_argument("--admin", action="store_true")

    events = sub.add_parser("events")
    events.add_argument("--seconds", type=int, default=1800)
    events.add_argument("--limit", type=int, default=200)
    events.add_argument("--offset", type=int, default=0)

    open_event = sub.add_parser("open-event")
    open_event.add_argument("--seconds", type=int, default=1800)
    open_event.add_argument("--event-id", required=True)

    callback = sub.add_parser("callback")
    callback.add_argument("--seconds", type=int, default=1800)
    callback.add_argument("--data", required=True)
    callback.add_argument("--admin", action="store_true")

    event_search = sub.add_parser("event-search")
    event_search.add_argument("terms", nargs="*")

    face_search = sub.add_parser("face-search")
    face_search.add_argument("--image", required=True)
    face_search.add_argument("terms", nargs="*")

    plate_search = sub.add_parser("plate-search")
    plate_search.add_argument("terms", nargs="*")

    archive_jump = sub.add_parser("archive-jump")
    archive_jump.add_argument("terms", nargs="*")

    single_camera_export = sub.add_parser("single-camera-export")
    single_camera_export.add_argument("terms", nargs="*")

    macro_execution = sub.add_parser("macro-execution")
    macro_execution.add_argument("--execution-enabled", action="store_true")
    macro_execution.add_argument("--admin", action="store_true")
    macro_execution.add_argument("--allow-id", action="append", default=[])
    macro_execution.add_argument("--allow-name", action="append", default=[])
    macro_execution.add_argument("terms", nargs="*")

    ptz_control = sub.add_parser("ptz-control")
    ptz_control.add_argument("--control-enabled", action="store_true")
    ptz_control.add_argument("--admin", action="store_true")
    ptz_control.add_argument("--allow-camera-ap", action="append", default=[])
    ptz_control.add_argument("--allow-camera-name", action="append", default=[])
    ptz_control.add_argument("terms", nargs="*")

    args = parser.parse_args()
    if not (args.host and args.password):
        raise SystemExit("Set --host/--password or env AXXON_HOST/AXXON_PASS")
    configure_display_timezone(args.tz)

    common = [
        "--host", args.host,
        "--user", args.user,
        "--password", args.password,
        "--port", str(args.port),
    ]

    if args.cmd == "home":
        print(json.dumps(home_payload(common, args.seconds, args.limit, admin=args.admin), ensure_ascii=False, indent=2))
        return
    if args.cmd == "events":
        print(json.dumps(events_payload(common, args.seconds, args.limit, args.offset), ensure_ascii=False, indent=2))
        return
    if args.cmd == "open-event":
        print(json.dumps(open_event_payload(common, args.seconds, args.event_id), ensure_ascii=False, indent=2))
        return
    if args.cmd == "callback":
        print(json.dumps(callback_payload(common, args.seconds, args.data, admin=args.admin), ensure_ascii=False, indent=2))
        return
    if args.cmd == "event-search":
        print(json.dumps(event_search_payload(common, args.terms), ensure_ascii=False, indent=2))
        return
    if args.cmd == "face-search":
        print(json.dumps(face_search_payload(common, args.image, args.terms), ensure_ascii=False, indent=2))
        return
    if args.cmd == "plate-search":
        print(json.dumps(plate_search_payload(common, args.terms), ensure_ascii=False, indent=2))
        return
    if args.cmd == "archive-jump":
        print(json.dumps(archive_jump_payload(common, args.terms), ensure_ascii=False, indent=2))
        return
    if args.cmd == "single-camera-export":
        print(json.dumps(single_camera_export_payload(common, args.terms), ensure_ascii=False, indent=2))
        return
    if args.cmd == "macro-execution":
        print(
            json.dumps(
                macro_execution_payload(
                    common,
                    args.terms,
                    execution_enabled=args.execution_enabled,
                    admin=args.admin,
                    allow_ids=args.allow_id,
                    allow_names=args.allow_name,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.cmd == "ptz-control":
        print(
            json.dumps(
                ptz_control_payload(
                    common,
                    args.terms,
                    control_enabled=args.control_enabled,
                    admin=args.admin,
                    allow_camera_aps=args.allow_camera_ap,
                    allow_camera_names=args.allow_camera_name,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return


if __name__ == "__main__":
    main()
