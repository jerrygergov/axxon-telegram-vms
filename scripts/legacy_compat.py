#!/usr/bin/env python3
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def _trim_button(text: str, limit: int = 48) -> str:
    value = str(text or "").replace("\n", " ").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"

class UserManager:
    def __init__(self, authorized_users: list[int] | None = None, admin_users: list[int] | None = None):
        self.authorized_users = set(authorized_users or [])
        self.admin_users = set(admin_users or [])

    def is_authorized(self, user_id: int) -> bool:
        # Keep existing security behavior: empty AUTHORIZED_USERS allows all.
        if not self.authorized_users:
            return True
        return user_id in self.authorized_users or user_id in self.admin_users

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_users


def get_detector_keyboard(
    page: int = 0,
    detectors: list[dict] | None = None,
    selected_detectors: list[str] | None = None,
) -> InlineKeyboardMarkup:
    rows = detectors or []
    selected = selected_detectors or []
    per_page = 5
    total_pages = (len(rows) + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    page_rows = rows[start:start + per_page]

    keyboard: list[list[InlineKeyboardButton]] = []
    for detector in page_rows:
        detector_id = detector["access_point"]
        is_selected = detector_id in selected
        label = str(detector.get("selection_label") or "").strip() or f"{detector['name']} · {detector['camera_name']}"
        text = _trim_button(f"{'✅ ' if is_selected else '❌ '}{label}")
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"detector:{detector_id}")])

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{page + 1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🔔 Subscribe to All Alerts", callback_data="all_alerts")])

    if selected:
        keyboard.append([InlineKeyboardButton("✅ Confirm Selection", callback_data="confirm_detectors")])

    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)
