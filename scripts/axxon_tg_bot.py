#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import logging
import os
import queue
import re
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from collections import deque
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Update,
)
try:
    from telegram import BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats, MenuButtonCommands
except ImportError:  # test doubles / older telegram stubs
    BotCommandScopeAllGroupChats = None
    BotCommandScopeAllPrivateChats = None
    MenuButtonCommands = None
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from camera_catalog import normalize_camera_rows, normalize_video_id
from axxon_web_api import AxxonClient
from axxon_telegram_vms.client import RuntimeReadCache, build_runtime_cache_key
from axxon_telegram_vms.models import normalize_event_card
from axxon_telegram_vms.ui.telegram_face_search import (
    build_face_search_wizard_period_buttons,
    build_face_search_wizard_terms,
    build_face_search_wizard_threshold_buttons,
    face_reference_attachment,
    face_search_terms_support_wizard,
    format_face_search_wizard_period_label,
    parse_face_search_wizard_callback,
    should_start_face_search_from_upload,
)
from config_loader import load_axxon_config, load_secure_profile_config, load_tg_bot_config
from legacy_compat import UserManager, get_detector_keyboard
from live_session_runtime import LiveSessionRecord, LiveSessionRuntime
from media_utils import extract_raw_rectangle_candidates, is_meaningful_rectangle_candidate, normalized_to_pixel_crop, pick_primary_rectangle, pick_primary_rectangle_candidate, rectangle_candidate_to_pixel_crop
try:
    from scripts.process_bridge import CommandExecutionError, run_command
except ImportError:  # pragma: no cover - top-level script import path
    from process_bridge import CommandExecutionError, run_command
from secure_profile_storage import SecureProfileStore
from subscription_services import (
    SubscriptionLedger,
    SubscriptionPolicy,
    SubscriptionRecord,
    build_notifier_include_filters,
    filter_cards_for_subscription,
    subscription_states_match,
)
from axxon_telegram_vms.services import (
    build_macro_execution_policy,
    macro_execution_policy_to_api_args,
    build_ptz_control_policy,
    ptz_control_policy_to_api_args,
)
from unification_helpers import normalize_detector_rows
UI = BASE / "axxon_tg_ui.py"
API = BASE / "axxon_web_api.py"

AXXON_CFG = load_axxon_config()
BOT_CFG = load_tg_bot_config()
SECURE_CFG = load_secure_profile_config()

USER_MANAGER = UserManager(
    authorized_users=BOT_CFG.authorized_users,
    admin_users=BOT_CFG.admin_users,
)

SECURE_STORE = SecureProfileStore(
    enabled=SECURE_CFG.enabled,
    storage_dir=SECURE_CFG.storage_dir,
    master_key=SECURE_CFG.master_key,
)

LOG_LEVEL = os.getenv("TG_BOT_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("TG_BOT_LOG_FILE", str((Path(__file__).resolve().parent.parent / "tmp" / "bot.log")))
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
log = logging.getLogger("axxon_tg_bot")
_LIVE_OVERLAY_FFMPEG_READY: bool | None = None
_LIVE_OVERLAY_WARNED: bool = False


class SendThrottle:
    def __init__(self, max_count: int, period_sec: int, duplicate_window_sec: int):
        self.max_count = max(1, max_count)
        self.period_sec = max(1, period_sec)
        self.duplicate_window_sec = max(0, duplicate_window_sec)
        self._per_user_send_ts: dict[int, deque[float]] = {}
        self._dedupe_seen_at: dict[tuple[int, str], float] = {}

    def allow(self, user_id: int, fingerprint: str) -> bool:
        now = time.monotonic()
        history = self._per_user_send_ts.setdefault(user_id, deque())
        while history and (now - history[0]) > self.period_sec:
            history.popleft()
        if len(history) >= self.max_count:
            return False

        if self.duplicate_window_sec > 0:
            key = (user_id, fingerprint)
            last = self._dedupe_seen_at.get(key)
            if last is not None and (now - last) < self.duplicate_window_sec:
                return False
            self._dedupe_seen_at[key] = now

        history.append(now)
        return True


SEND_THROTTLE = SendThrottle(
    max_count=BOT_CFG.send_rate_limit_count,
    period_sec=BOT_CFG.send_rate_limit_period_sec,
    duplicate_window_sec=BOT_CFG.duplicate_window_sec,
)


class RuntimeCounters:
    def __init__(self, enabled: bool):
        self.enabled = bool(enabled)
        self.day = datetime.now(timezone.utc).date().isoformat()
        self.values: dict[str, int] = {}

    def _rollover(self):
        day_now = datetime.now(timezone.utc).date().isoformat()
        if day_now != self.day:
            self.day = day_now
            self.values = {}

    def incr(self, key: str, value: int = 1):
        if not self.enabled:
            return
        self._rollover()
        self.values[key] = self.values.get(key, 0) + max(0, value)

    def snapshot(self) -> tuple[str, dict[str, int]]:
        self._rollover()
        return self.day, dict(self.values)


RUNTIME_COUNTERS = RuntimeCounters(BOT_CFG.enable_daily_counters)
READ_CACHE = RuntimeReadCache()
MACRO_CONFIRM_TTL_SEC = BOT_CFG.macro_confirm_ttl_sec
PTZ_CONFIRM_TTL_SEC = BOT_CFG.ptz_confirm_ttl_sec
FACE_SEARCH_WIZARD_KEY = "face_search_wizard"
FACE_SEARCH_WIZARD_NEXT_ID_KEY = "face_search_wizard_next_id"
FACE_SEARCH_PENDING_KEY = "face_search_pending"
COUNTER_WATCH_POLL_SEC = 3


def _is_counter_detector_row(row: dict[str, Any]) -> bool:
    detector_type = str(row.get("detector_type") or "").strip()
    return detector_type in {"NeuroCounter", "VaCrowdDetector"}


def _build_notifier_include(*, event_type: str, subjects: list[str] | tuple[str, ...] | None = None) -> list[dict[str, str]]:
    normalized_event_type = str(event_type or "").strip() or "ET_DetectorEvent"
    include: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw_subject in subjects or ():
        subject = str(raw_subject or "").strip()
        if not subject:
            continue
        key = (normalized_event_type, subject)
        if key in seen:
            continue
        seen.add(key)
        include.append({"event_type": normalized_event_type, "subject": subject})
    if include:
        return include
    return [{"event_type": normalized_event_type}]


def _detector_notifier_subject(row: dict[str, Any]) -> str:
    if _is_counter_detector_row(row):
        return str(row.get("camera_access_point") or "").strip()
    return str(row.get("access_point") or row.get("detector_access_point") or "").strip()


def _build_detector_notifier_include(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    return _build_notifier_include(
        event_type="ET_DetectorEvent",
        subjects=[_detector_notifier_subject(row) for row in rows],
    )


def _card_object_count(card: dict[str, Any]) -> int | None:
    value = card.get("object_count")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _axxon_client() -> AxxonClient:
    return AxxonClient(
        host=AXXON_CFG.host,
        user=AXXON_CFG.user,
        password=AXXON_CFG.password,
        port=AXXON_CFG.port,
    )


def _packet_items(packet: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(packet.get("items"), list):
        return [item for item in (packet.get("items") or []) if isinstance(item, dict)]
    data = packet.get("data") if isinstance(packet.get("data"), dict) else {}
    if isinstance(data.get("items"), list):
        return [item for item in (data.get("items") or []) if isinstance(item, dict)]
    return []


def _cards_from_packets(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for packet in packets:
        for item in _packet_items(packet):
            try:
                cards.append(normalize_event_card(item))
            except Exception as ex:
                log.debug("notifier card normalize failed err=%s", ex)
    return cards


def _disconnect_notifier_channel(channel_id: str) -> bool:
    if not channel_id:
        return False
    try:
        packets = _axxon_client().grpc_call(
            "axxonsoft.bl.events.DomainNotifier.DisconnectEventChannel",
            {"subscription_id": channel_id},
            timeout=30,
        )
    except Exception:
        return False
    return all(not isinstance(packet, dict) or packet.get("result") is not False for packet in packets)


class _NotifierStream:
    def __init__(
        self,
        *,
        channel_id: str,
        filters: dict[str, Any],
        timeout_sec: int,
    ):
        self.channel_id = str(channel_id)
        self.filters = dict(filters)
        self.timeout_sec = max(5, int(timeout_sec))
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._stop_event = threading.Event()
        self._closed_event = threading.Event()
        self.error: str = ""
        self._thread = threading.Thread(target=self._run, name=f"notifier-{self.channel_id}", daemon=True)

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    @property
    def closed(self) -> bool:
        return self._closed_event.is_set()

    @property
    def stop_requested(self) -> bool:
        return self._stop_event.is_set()

    def drain_cards(self) -> list[dict[str, Any]]:
        packets: list[dict[str, Any]] = []
        while True:
            try:
                packets.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return _cards_from_packets(packets)

    def _run(self) -> None:
        payload = {
            "subscription_id": self.channel_id,
            "filters": {
                "include": build_notifier_include_filters(self.filters),
            },
        }
        try:
            client = _axxon_client()
            for packet in client.grpc_stream_packets(
                "axxonsoft.bl.events.DomainNotifier.PullEvents",
                payload,
                timeout=max(self.timeout_sec, BOT_CFG.subscription_notifier_timeout_sec + 5),
                stop_event=self._stop_event,
            ):
                if self._stop_event.is_set():
                    break
                if isinstance(packet, dict):
                    self._queue.put(packet)
        except Exception as ex:
            self.error = str(ex)
        finally:
            self._closed_event.set()


class CounterWatchRuntime:
    def __init__(self):
        self._tasks: dict[int, dict[str, asyncio.Task]] = {}
        self._message_ids: dict[int, dict[str, int]] = {}
        self._history: dict[int, dict[str, list[tuple[str, int | None]]]] = {}
        self._channels: dict[int, dict[str, str]] = {}
        self._streams: dict[int, dict[str, _NotifierStream]] = {}

    @staticmethod
    def _sparkline(values: list[int]) -> str:
        if not values:
            return "-"
        ticks = "▁▂▃▄▅▆▇█"
        lo = min(values)
        hi = max(values)
        if lo == hi:
            mid = len(ticks) // 2
            return ticks[mid] * len(values)
        out = []
        span = hi - lo
        for value in values:
            idx = round((value - lo) * (len(ticks) - 1) / span)
            out.append(ticks[max(0, min(len(ticks) - 1, idx))])
        return "".join(out)

    @staticmethod
    def _counter_rows() -> list[dict[str, Any]]:
        rows = fetch_detectors()
        return [row for row in rows if _is_counter_detector_row(row)]

    @staticmethod
    def _latest_counter_card(cards: list[dict[str, Any]], detector_name: str) -> dict[str, Any] | None:
        matches = [
            card for card in cards
            if str(card.get("event_type") or "") == "lotsObjects"
            and str(card.get("detector") or "") == detector_name
            and _card_object_count(card) is not None
        ]
        matches.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
        return matches[0] if matches else None

    async def _watch_loop(self, bot, rec: SubscriptionRecord, detector_row: dict[str, Any]):
        user_id = rec.user_id
        sub_id = rec.subscription_id
        camera_subject = str(detector_row.get("camera_access_point") or "")
        camera_name = str(detector_row.get("camera_name") or "Camera")
        detector_name = str(detector_row.get("name") or detector_row.get("detector_name") or "Detector")
        chat_id = user_id
        channel_id = rec.channel_id or f"counter-{user_id}-{sub_id}-{uuid.uuid4().hex[:8]}"
        self._channels.setdefault(user_id, {})[sub_id] = channel_id
        stream = _NotifierStream(
            channel_id=channel_id,
            filters={
                "event_type": "ET_DetectorEvent",
                "camera_access_points": [camera_subject],
                "include": _build_detector_notifier_include([detector_row]),
            },
            timeout_sec=max(5, BOT_CFG.subscription_notifier_timeout_sec),
        )
        self._streams.setdefault(user_id, {})[sub_id] = stream
        stream.start()
        last_text = ""
        last_event_ts = ""
        last_guid = ""
        last_count: int | None = None
        last_updated = datetime.now(timezone.utc).strftime('%H:%M:%S')
        try:
            while sub_id in (self._tasks.get(user_id) or {}):
                cards = stream.drain_cards()
                if stream.closed and not stream.stop_requested:
                    if stream.error:
                        log.debug("counter notifier stream closed detector=%s sub=%s err=%s", detector_name, sub_id, stream.error)
                    stream = _NotifierStream(
                        channel_id=channel_id,
                        filters={
                            "event_type": "ET_DetectorEvent",
                            "camera_access_points": [camera_subject],
                            "include": _build_detector_notifier_include([detector_row]),
                        },
                        timeout_sec=max(5, BOT_CFG.subscription_notifier_timeout_sec),
                    )
                    self._streams.setdefault(user_id, {})[sub_id] = stream
                    stream.start()
                    RUNTIME_COUNTERS.incr("counterwatch_notifier_reconnects")

                card = self._latest_counter_card(cards, detector_name)
                history = self._history.setdefault(user_id, {}).setdefault(sub_id, [])
                if card:
                    count = _card_object_count(card)
                    when = str(card.get("timestamp") or "")
                    guid = str(card.get("id") or "")
                    if when and when != last_event_ts:
                        history.insert(0, (when, count))
                        del history[8:]
                        last_event_ts = when
                    if guid:
                        last_guid = guid
                    if count is not None:
                        last_count = count
                    last_updated = datetime.now(timezone.utc).strftime('%H:%M:%S')

                if history or last_event_ts or last_count is not None:
                    numeric_values = [int(v) for _, v in history if isinstance(v, int)]
                    stats_line = (
                        f"min {min(numeric_values)} · max {max(numeric_values)} · avg {sum(numeric_values)/len(numeric_values):.1f} · n={len(numeric_values)}"
                        if numeric_values else "min - · max - · avg - · n=0"
                    )
                    spark = self._sparkline(numeric_values[:12][::-1]) if numeric_values else "-"
                    history_text = "\n".join(
                        f"• <code>{ts}</code> → <b>{val if val is not None else '—'}</b>" for ts, val in history[:8]
                    ) or "• <code>-</code> → <b>—</b>"
                    text = "\n".join([
                        f"📟 <b>Crowd counter · Sub #{sub_id}</b>",
                        f"📷 <b>{camera_name}</b>",
                        f"🧠 <b>{detector_name}</b>",
                        f"🔢 <b>{last_count if last_count is not None else '—'}</b>",
                        f"🕒 Last event: <code>{last_event_ts or '-'}</code>",
                        f"🆔 GUID: <code>{last_guid or '-'}</code>",
                        f"📈 <b>Trend</b>: <code>{spark}</code>",
                        f"📊 <code>{stats_line}</code>",
                        f"🔄 Updated: <code>{last_updated} UTC</code>",
                        "🧪 <b>Recent values</b>",
                        history_text,
                    ])
                else:
                    text = "\n".join([
                        f"📟 <b>Crowd counter · Sub #{sub_id}</b>",
                        f"📷 <b>{camera_name}</b>",
                        f"🧠 <b>{detector_name}</b>",
                        "🔢 <b>—</b>",
                        "🕒 Last event: <code>-</code>",
                        "🔄 Updated: <code>waiting for live events</code>",
                        "🧪 <b>Recent values</b>",
                        "• <code>-</code> → <b>—</b>",
                    ])
                if text != last_text:
                    message_id = ((self._message_ids.get(user_id) or {}).get(sub_id))
                    if message_id:
                        try:
                            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='HTML')
                        except Exception:
                            msg = await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
                            self._message_ids.setdefault(user_id, {})[sub_id] = int(msg.message_id)
                    else:
                        msg = await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
                        self._message_ids.setdefault(user_id, {})[sub_id] = int(msg.message_id)
                    last_text = text
                await asyncio.sleep(COUNTER_WATCH_POLL_SEC)
        except asyncio.CancelledError:
            raise
        finally:
            stream = (self._streams.get(user_id) or {}).pop(sub_id, None)
            if stream is not None:
                stream.stop()
            if not self._streams.get(user_id):
                self._streams.pop(user_id, None)
            (self._tasks.get(user_id) or {}).pop(sub_id, None)
            if not self._tasks.get(user_id):
                self._tasks.pop(user_id, None)
            (self._history.get(user_id) or {}).pop(sub_id, None)
            if not self._history.get(user_id):
                self._history.pop(user_id, None)
            channel_id = (self._channels.get(user_id) or {}).pop(sub_id, None)
            if not self._channels.get(user_id):
                self._channels.pop(user_id, None)
            if channel_id:
                try:
                    _disconnect_notifier_channel(channel_id)
                except Exception:
                    pass

    async def start_subscription(self, rec: SubscriptionRecord, bot, detector_row: dict[str, Any], *, message_id: int | None = None) -> None:
        await self.stop_subscription(rec.user_id, rec.subscription_id)
        self._history.setdefault(rec.user_id, {})[rec.subscription_id] = []
        if message_id is not None:
            self._message_ids.setdefault(rec.user_id, {})[rec.subscription_id] = int(message_id)
        self._tasks.setdefault(rec.user_id, {})[rec.subscription_id] = asyncio.create_task(self._watch_loop(bot, rec, detector_row))

    async def stop_subscription(self, user_id: int, subscription_id: str) -> bool:
        task = (self._tasks.get(user_id) or {}).get(subscription_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        removed = task is not None or subscription_id in (self._message_ids.get(user_id) or {})
        (self._message_ids.get(user_id) or {}).pop(subscription_id, None)
        if not self._message_ids.get(user_id):
            self._message_ids.pop(user_id, None)
        return removed

    async def stop(self, user_id: int) -> bool:
        ids = list((self._tasks.get(user_id) or {}).keys())
        removed = False
        for sub_id in ids:
            if await self.stop_subscription(user_id, sub_id):
                removed = True
        return removed


COUNTER_WATCH = CounterWatchRuntime()


class SubscriptionRuntime:
    def __init__(self):
        self._ledger = SubscriptionLedger(
            SubscriptionPolicy(
                max_subscriptions_per_user=BOT_CFG.max_subscriptions_per_user,
                max_events_per_day=BOT_CFG.max_events_per_day,
                duplicate_window_sec=BOT_CFG.duplicate_window_sec,
                min_notification_interval_sec=BOT_CFG.min_notification_interval_sec,
            )
        )
        self._tasks: dict[int, dict[str, asyncio.Task]] = {}
        self._streams: dict[int, dict[str, _NotifierStream]] = {}

    def _next_subscription_id(self, user_id: int) -> str:
        return self._ledger.next_subscription_id(user_id)

    def list_subscriptions(self, user_id: int) -> list[SubscriptionRecord]:
        return self._ledger.list_subscriptions(user_id)

    def stats(self, user_id: int) -> dict[str, int]:
        return self._ledger.stats(user_id).as_legacy_dict()

    def can_add_subscription(self, user_id: int) -> bool:
        return self._ledger.can_add_subscription(user_id)

    def allow_event_delivery(self, user_id: int, event_id: str, now: float | None = None) -> tuple[bool, str]:
        return self._ledger.allow_event_delivery(user_id, event_id, now=now)

    async def _apply_min_notification_interval(self, user_id: int):
        wait = self._ledger.notification_wait_seconds(user_id)
        if wait > 0:
            await asyncio.sleep(wait)
        self._ledger.mark_notification_sent(user_id)

    def _persist_user_meta(self, user_id: int):
        if not SECURE_STORE.enabled:
            return
        rows = [x.as_meta() for x in self.list_subscriptions(user_id)]
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "utc_day": self._ledger.utc_day,
            "events_today": self._ledger.events_today(user_id),
            "subscriptions": rows,
        }
        try:
            SECURE_STORE.save_profile("user", f"tg-subscriptions-{user_id}", payload)
        except Exception:
            RUNTIME_COUNTERS.incr("secure_profile_errors")

    def _start_notifier_stream(self, rec: SubscriptionRecord) -> _NotifierStream:
        stream = _NotifierStream(
            channel_id=rec.channel_id,
            filters=rec.filters,
            timeout_sec=max(5, BOT_CFG.subscription_notifier_timeout_sec),
        )
        self._streams.setdefault(rec.user_id, {})[rec.subscription_id] = stream
        stream.start()
        RUNTIME_COUNTERS.incr("subscription_notifier_streams_started")
        return stream

    def _states_match(self, card: dict[str, Any], states: list[str]) -> bool:
        return subscription_states_match(card, states)

    def _fmt_ts_utc(self, ts: str) -> str:
        for fmt in ("%Y%m%dT%H%M%S.%f", "%Y%m%dT%H%M%S"):
            try:
                dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
                return dt.strftime("%d-%m-%Y %H:%M:%S UTC")
            except Exception:
                continue
        return f"{ts} UTC"

    def _parse_event_ts(self, ts: str) -> datetime | None:
        if not ts:
            return None
        for fmt in ("%Y%m%dT%H%M%S.%f", "%Y%m%dT%H%M%S"):
            try:
                return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
            except Exception:
                continue
        return None

    def _event_camera_ap(self, event_obj: dict[str, Any]) -> str:
        body = event_obj.get("body") or {}
        return str(
            ((body.get("origin_ext") or {}).get("access_point"))
            or ((body.get("data") or {}).get("origin_id"))
            or ((body.get("camera") or {}).get("access_point"))
            or ""
        )

    def _event_timestamp(self, event_obj: dict[str, Any]) -> str:
        body = event_obj.get("body") or {}
        data = body.get("data") or {}
        hypotheses = data.get("Hypotheses") or []
        if hypotheses and isinstance(hypotheses[0], dict) and hypotheses[0].get("TimeBest"):
            return str(hypotheses[0].get("TimeBest"))
        if data.get("plate_appeared_time"):
            return str(data.get("plate_appeared_time"))
        detector_ts = ((body.get("detector") or {}).get("timestamp"))
        state_ts = ((body.get("states") or [{}])[0].get("timestamp"))
        return str(detector_ts or state_ts or body.get("timestamp") or "")

    def _find_raw_event(self, event_id: str, event_type: str = "ET_DetectorEvent") -> dict[str, Any] | None:
        try:
            events = run_api(
                "events",
                "--seconds", str(BOT_CFG.subscription_poll_window_sec),
                "--event-type", event_type,
                "--limit", str(max(200, BOT_CFG.subscription_poll_limit * 5)),
            )
            for e in events:
                if (e.get("body", {}) or {}).get("guid") == event_id:
                    return e
        except Exception:
            return None
        return None

    def _exact_alert_frame_from_payload(self, raw: dict[str, Any], out_path: Path) -> bool:
        try:
            body = raw.get("body") or {}
            detector_body = body.get("detector") or {}
            detector_data = detector_body.get("data") or {}
            ts = str(_event_best_timestamp(detector_body, detector_data, {}) or body.get("timestamp") or "").strip()
            ap = ((body.get("origin_ext") or {}).get("access_point")
                  or (body.get("data", {}).get("origin_id"))
                  or (body.get("camera", {}).get("access_point"))
                  or ((detector_body.get("origin_ext") or {}).get("access_point"))
                  or (detector_data.get("origin_id"))
                  or "")
            video_id = ap.replace("hosts/", "") if ap else ""
            if not ts or not video_id:
                return False
            client = AxxonClient(
                host=AXXON_CFG.host,
                user=AXXON_CFG.user,
                password=AXXON_CFG.password,
                port=AXXON_CFG.port,
            )
            client.media_frame(video_id, ts, out_path, threshold_ms=50)
            return out_path.exists() and out_path.stat().st_size > 0
        except Exception as ex:
            log.debug("exact alert frame failed id=%s err=%s", (raw.get("body") or {}).get("guid"), ex)
            return False

    def _build_combined_event_image_from_raw(self, raw: dict[str, Any], event_id: str, event_type: str = "ET_DetectorEvent") -> str | None:
        if isinstance(raw, dict) and not isinstance(raw.get("body"), dict):
            raw = {
                "event_type": event_type,
                "body": dict(raw),
                "localization": {"text": str((raw.get("event_type") if isinstance(raw, dict) else "") or "")},
            }
        safe_event_id = re.sub(r"[^A-Za-z0-9_.-]", "_", event_id or "event")
        base = Path(f"/tmp/ax_sub_{safe_event_id}")
        raw_json = base.with_suffix(".json")
        frame = Path(f"/tmp/ax_sub_{safe_event_id}_frame.jpg")
        boxed = Path(f"/tmp/ax_sub_{safe_event_id}_boxed.jpg")
        crop = Path(f"/tmp/ax_sub_{safe_event_id}_crop.jpg")
        merged = Path(f"/tmp/ax_sub_{safe_event_id}_merged.jpg")
        raw_rect_candidates = extract_raw_rectangle_candidates(raw)
        primary_rect_candidate = pick_primary_rectangle_candidate(raw)
        rect = pick_primary_rectangle(raw)
        if not rect and not raw_rect_candidates and event_type == "ET_Alert":
            log.info("combined_image: alert has no rectangle in raw payload id=%s; skip crop panel", event_id)
        raw_json.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

        try:
            frame_ok = False
            if event_type == "ET_Alert":
                frame_ok = self._exact_alert_frame_from_payload(raw, frame)
            if not frame_ok:
                try:
                    threshold = "50" if event_type == "ET_Alert" else "250"
                    run_api("frame-from-event", "--event-json", str(raw_json), "--out", str(frame), "--mode", "media", "--threshold-ms", threshold)
                except Exception:
                    # Alerts may fail on archive/media path; fallback to export mode.
                    run_api("frame-from-event", "--event-json", str(raw_json), "--out", str(frame), "--mode", "export")
        except Exception as ex:
            log.debug("combined_image: frame build failed id=%s err=%s", event_id, ex)
            return str(frame) if frame.exists() else None

        try:
            run_api("box-from-event", "--event-json", str(raw_json), "--image", str(frame), "--out", str(boxed))
        except Exception as ex:
            log.debug("combined_image: box overlay failed id=%s err=%s", event_id, ex)
        try:
            import subprocess as _sp

            probe = _sp.check_output([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(frame)
            ], text=True).strip()
            fw, fh = (int(x) for x in probe.split("x", 1)) if "x" in probe else (1920, 1080)

            crop_ready = False
            crop_candidate = primary_rect_candidate or rect
            if crop_candidate and is_meaningful_rectangle_candidate(crop_candidate):
                px = rectangle_candidate_to_pixel_crop(crop_candidate, fw, fh)
                if px:
                    x, y, w, h = px
                    # Expand crop around bbox for better visual context (less tiny/sliver crops).
                    cxp, cyp = x + w // 2, y + h // 2
                    scale = 2.2
                    w = min(fw, max(2, int(round(w * scale))))
                    h = min(fh, max(2, int(round(h * scale))))
                    x = max(0, min(fw - w, cxp - w // 2))
                    y = max(0, min(fh - h, cyp - h // 2))
                    # enforce minimum readable crop size
                    min_w, min_h = min(260, fw), min(260, fh)
                    if w < min_w or h < min_h:
                        cxp, cyp = x + w // 2, y + h // 2
                        w = max(w, min_w)
                        h = max(h, min_h)
                        x = max(0, min(fw - w, cxp - w // 2))
                        y = max(0, min(fh - h, cyp - h // 2))
                    crop.parent.mkdir(parents=True, exist_ok=True)
                    _sp.run(
                        [
                            "ffmpeg", "-y", "-loglevel", "error",
                            "-i", str(frame),
                            "-vf", f"crop={w}:{h}:{x}:{y}",
                            "-frames:v", "1",
                            str(crop),
                        ],
                        check=True,
                        stdout=_sp.DEVNULL,
                        stderr=_sp.DEVNULL,
                    )
                    crop_ready = crop.exists() and crop.stat().st_size > 0

            main_img = boxed if boxed.exists() else frame
            panel_img = crop if crop_ready else frame
            _sp.run(
                [
                    "ffmpeg", "-y", "-i", str(main_img), "-i", str(panel_img),
                    "-filter_complex", "[1:v][0:v]scale2ref=w=oh*mdar:h=ih[c][m];[m][c]hstack=inputs=2",
                    str(merged),
                ],
                check=True,
                stdout=_sp.DEVNULL,
                stderr=_sp.DEVNULL,
            )
            if merged.exists():
                return str(merged)
        except Exception as ex:
            log.debug("combined_image: merge failed id=%s err=%s", event_id, ex)

        return str(boxed) if boxed.exists() else str(frame) if frame.exists() else None

    def _build_combined_event_image(self, event_id: str, event_type: str = "ET_DetectorEvent") -> str | None:
        raw = self._find_raw_event(event_id, event_type=event_type)
        if not raw:
            time.sleep(0.8)
            raw = self._find_raw_event(event_id, event_type=event_type)
        if not raw:
            log.debug("combined_image: raw event not found id=%s type=%s", event_id, event_type)
            return None
        return self._build_combined_event_image_from_raw(raw, event_id, event_type)

    async def _send_notification(self, bot, rec: SubscriptionRecord, card: dict[str, Any]):
        event_id = str(card.get("id") or "")
        when = str(card.get("timestamp") or "")
        camera = str(card.get("camera") or "?")
        server = str(card.get("server") or "?")
        detector = str(card.get("detector") or "?")
        event_type = str(card.get("event_type") or "event")
        state = str(card.get("state") or "")
        body = str(card.get("text") or "")
        event_kind = "ET_Alert" if (rec.filters.get("event_type") == "ET_Alert" or event_type == "ET_Alert") else "ET_DetectorEvent"
        if event_id and event_kind == "ET_Alert":
            clip_kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🟢 False Alarm", callback_data=f"al:flag:false:{event_id}"),
                    InlineKeyboardButton("🟡 Suspicious", callback_data=f"al:flag:suspicious:{event_id}"),
                    InlineKeyboardButton("🔴 Confirmed", callback_data=f"al:flag:confirmed:{event_id}"),
                ],
                [InlineKeyboardButton("🎬 Clip -15/+15 sec", callback_data=f"sub:clip:{event_kind}:{event_id}")],
            ])
        else:
            clip_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Clip -15/+15 sec", callback_data=f"sub:clip:{event_kind}:{event_id}")]
            ]) if event_id else None
        if len(body) > 220:
            body = f"{body[:217]}..."

        if card.get("plate"):
            veh = card.get("vehicle") or {}
            msg = "\n".join([
                "🔎 LPR + MMR",
                f"🛰️ Server: {server}",
                f"📷 Camera: {camera}",
                f"🧠 Detector: {detector}",
                f"🕒 Time (UTC): {self._fmt_ts_utc(when)}",
                f"📒 Plate: {card.get('plate')}",
                f"🚘 Brand/Model/Color: {veh.get('brand') or '-'} / {veh.get('model') or '-'} / {veh.get('color') or '-'}",
                f"📝 Event: {body}",
            ])
        elif str(event_type) == 'lotsObjects':
            count = _card_object_count(card)
            msg = f"{camera} — {detector} — {count if count is not None else body}"
        else:
            msg = "\n".join([
                f"🔔 Sub #{rec.subscription_id}",
                f"🛰️ Server: {server}",
                f"📷 Camera: {camera}",
                f"🧠 Detector: {detector}",
                f"🕒 Time (UTC): {self._fmt_ts_utc(when)}",
                f"🧩 Type/State: {event_type}/{state or '-'}",
                f"📝 Event: {body}",
                f"🆔 ID: {event_id}",
            ])
        event_fp = f"subevent:{rec.user_id}:{rec.subscription_id}:{event_id}:{when}"
        if not SEND_THROTTLE.allow(rec.user_id, event_fp):
            RUNTIME_COUNTERS.incr("subscription_messages_suppressed")
            log.debug("subscription send suppressed by throttle user=%s sub=%s event=%s", rec.user_id, rec.subscription_id, event_id)
            return

        if BOT_CFG.subscription_attach_media:
            try:
                media_path = await asyncio.to_thread(self._build_combined_event_image, event_id, event_kind)
            except Exception:
                media_path = None
            if media_path:
                p = Path(media_path)
                if p.exists():
                    with p.open("rb") as fh:
                        await bot.send_photo(chat_id=rec.user_id, photo=fh, caption=msg, reply_markup=clip_kb)
                        RUNTIME_COUNTERS.incr("subscription_media_sent")
                        return
                else:
                    log.debug("subscription media path missing on disk event=%s path=%s", event_id, media_path)
            else:
                log.debug("subscription media merge unavailable event=%s", event_id)

        await bot.send_message(chat_id=rec.user_id, text=msg, reply_markup=clip_kb)
        RUNTIME_COUNTERS.incr("subscription_messages_sent")

    async def _subscription_loop(self, bot, rec: SubscriptionRecord):
        user_id = rec.user_id
        sub_id = rec.subscription_id
        try:
            log.info("subscription loop started user=%s sub=%s", user_id, sub_id)
            while self._ledger.get(user_id, sub_id):
                try:
                    cards = []
                    streams = self._streams.setdefault(user_id, {})
                    stream = streams.get(sub_id)
                    if stream is None:
                        stream = self._start_notifier_stream(rec)
                    cards = filter_cards_for_subscription(stream.drain_cards(), rec.filters)
                    notifier_failed = stream.closed and not stream.stop_requested and bool(stream.error)
                    if stream.closed and not stream.stop_requested:
                        if notifier_failed:
                            log.debug("subscription notifier stream closed user=%s sub=%s err=%s", user_id, sub_id, stream.error)
                            RUNTIME_COUNTERS.incr("subscription_notifier_errors")
                        stream = self._start_notifier_stream(rec)
                except Exception as ex:
                    log.exception("subscription poll error user=%s sub=%s: %s", user_id, sub_id, ex)
                    RUNTIME_COUNTERS.incr("subscription_poll_errors")
                    await asyncio.sleep(BOT_CFG.subscription_poll_interval_sec)
                    continue

                log.debug("subscription pull user=%s sub=%s cards=%d", user_id, sub_id, len(cards))
                if cards:
                    for card in reversed(cards):
                        event_id = str(card.get("id") or "")
                        if not event_id:
                            continue
                        if not self._states_match(card, rec.states):
                            log.debug("subscription state filter skip user=%s sub=%s event=%s type=%s state=%s states=%s", user_id, sub_id, event_id, card.get('event_type'), card.get('state'), rec.states)
                            continue
                        allowed, reason = self.allow_event_delivery(user_id, event_id)
                        if not allowed:
                            if reason == "daily_cap":
                                RUNTIME_COUNTERS.incr("subscription_daily_cap_hits")
                            continue
                        await self._apply_min_notification_interval(user_id)
                        await self._send_notification(bot, rec, card)
                        rec.sent_events += 1
                        rec.last_event_id = event_id
                        rec.last_event_ts = str(card.get("timestamp") or "")
                        RUNTIME_COUNTERS.incr("subscription_events_delivered")
                        self._persist_user_meta(user_id)

                await asyncio.sleep(BOT_CFG.subscription_poll_interval_sec)
        except asyncio.CancelledError:
            raise
        except Exception:
            RUNTIME_COUNTERS.incr("subscription_loop_crash")

    async def create_subscription(
        self,
        user_id: int,
        bot,
        source: str,
        filters: dict[str, Any],
        states: list[str],
        summary: str,
    ) -> tuple[bool, str, SubscriptionRecord | None]:
        log.info("create_subscription user=%s source=%s states=%s filters=%s", user_id, source, states, filters)
        if not self.can_add_subscription(user_id):
            log.warning("create_subscription denied: max subscriptions user=%s", user_id)
            return False, "max_subscriptions", None

        sub_id = self._next_subscription_id(user_id)
        rec = SubscriptionRecord(
            subscription_id=sub_id,
            channel_id=f"tg-{user_id}-{sub_id}-{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            source=source,
            filters=filters,
            states=states,
            summary=summary,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._ledger.add(rec)

        if source != "counter_detector":
            task = asyncio.create_task(self._subscription_loop(bot, rec))
            self._tasks.setdefault(user_id, {})[sub_id] = task
        self._persist_user_meta(user_id)
        log.info("subscription created user=%s sub=%s channel=%s", user_id, sub_id, rec.channel_id)
        return True, "created", rec

    async def stop_subscription(self, user_id: int, subscription_id: str) -> bool:
        rec = self._ledger.get(user_id, subscription_id)
        if not rec:
            log.warning("stop_subscription: not found user=%s sub=%s", user_id, subscription_id)
            return False

        if rec.source == "counter_detector":
            await COUNTER_WATCH.stop_subscription(user_id, subscription_id)
        else:
            task = (self._tasks.get(user_id) or {}).pop(subscription_id, None)
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

        self._ledger.remove(user_id, subscription_id)
        stream = (self._streams.get(user_id) or {}).pop(subscription_id, None)
        if stream is not None:
            stream.stop()
        if rec.channel_id:
            try:
                if _disconnect_notifier_channel(rec.channel_id):
                    RUNTIME_COUNTERS.incr("subscription_notifier_disconnects")
                else:
                    RUNTIME_COUNTERS.incr("subscription_notifier_disconnect_errors")
            except Exception:
                RUNTIME_COUNTERS.incr("subscription_notifier_disconnect_errors")

        if not self._tasks.get(user_id):
            self._tasks.pop(user_id, None)
        if not self._streams.get(user_id):
            self._streams.pop(user_id, None)
        self._persist_user_meta(user_id)
        return True

    async def stop_all(self, user_id: int) -> int:
        ids = [x.subscription_id for x in self.list_subscriptions(user_id)]
        removed = 0
        for sid in ids:
            if await self.stop_subscription(user_id, sid):
                removed += 1
        return removed


SUBSCRIPTIONS = SubscriptionRuntime()


def _live_controls(idx: int) -> list[list[dict[str, str]]]:
    return [
        [
            {"text": "▶ Live (in-chat)", "callback_data": f"cam:live:start:{idx}"},
            {"text": "⏹ Stop live", "callback_data": "cam:live:stop"},
        ],
        [
            {"text": "📸 Snapshot", "callback_data": f"cam:lsnap:{idx}"},
            {"text": "🚨 Incidents", "callback_data": f"cam:inc:{idx}:0"},
        ],
        [
            {"text": "⬅️ Back", "callback_data": f"cam:open:{idx}"},
            {"text": "🏠 Main", "callback_data": "home"},
        ],
    ]


def _live_caption(base_text: str, session_state: str, overlay_note: str = "") -> str:
    updated = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S UTC")
    lines = [x.rstrip() for x in str(base_text or "").splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    if overlay_note:
        lines.extend(["", overlay_note])
    lines.extend(["", f"Live mode: {session_state}", f"Updated: {updated}"])
    return "\n".join(lines)


def _ffmpeg_drawtext_escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _live_overlay_stamp(frame_counter: int) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    frame_num = max(1, int(frame_counter))
    return f"{ts} UTC | Frame #{frame_num}"


def _ffmpeg_live_overlay_ready() -> bool:
    global _LIVE_OVERLAY_FFMPEG_READY
    global _LIVE_OVERLAY_WARNED
    if _LIVE_OVERLAY_FFMPEG_READY is not None:
        return _LIVE_OVERLAY_FFMPEG_READY
    try:
        probe = subprocess.run(
            ["ffmpeg", "-hide_banner", "-filters"],
            capture_output=True,
            text=True,
            check=False,
        )
        ready = (probe.returncode == 0) and ("drawtext" in (probe.stdout or ""))
    except Exception:
        ready = False
    _LIVE_OVERLAY_FFMPEG_READY = ready
    if not ready and not _LIVE_OVERLAY_WARNED:
        log.warning("TG_LIVE_OVERLAY is enabled but ffmpeg drawtext is unavailable; using caption-only fallback")
        _LIVE_OVERLAY_WARNED = True
    return ready


def _prepare_live_overlay_media(media_path: str, frame_counter: int) -> tuple[str, str]:
    src = Path(str(media_path))
    if not src.exists():
        raise RuntimeError(f"snapshot file not found: {src}")
    if not BOT_CFG.live_overlay:
        return str(src), ""

    stamp = _live_overlay_stamp(frame_counter)
    out = Path("/tmp") / f"tg_live_overlay_{uuid.uuid4().hex[:12]}.jpg"

    # Preferred: text overlay (drawtext)
    if _ffmpeg_live_overlay_ready():
        safe_text = _ffmpeg_drawtext_escape(stamp)
        vf = (
            "drawbox=x=8:y=h-48:w=620:h=36:color=black@0.55:t=fill,"
            f"drawtext=text='{safe_text}':x=16:y=h-40:fontsize=20:fontcolor=white"
        )
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
            "-vf", vf, "-frames:v", "1", str(out),
        ]
        try:
            subprocess.run(cmd, check=True)
            if out.exists():
                return str(out), ""
        except Exception:
            pass

    # Fallback: drawbox-only animated marker (no drawtext dependency)
    try:
        colors = ["red", "yellow", "lime", "cyan", "magenta", "white"]
        color = colors[max(0, int(frame_counter)) % len(colors)]
        width = 40 + (max(0, int(frame_counter)) % 20) * 12
        vf = f"drawbox=x=10:y=h-26:w={width}:h=14:color={color}@0.85:t=fill"
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
            "-vf", vf, "-frames:v", "1", str(out),
        ]
        subprocess.run(cmd, check=True)
        if out.exists():
            return str(out), f"Live frame marker: {stamp}"
    except Exception:
        pass

    try:
        out.unlink(missing_ok=True)
    except Exception:
        pass
    return str(src), f"Live frame marker: {stamp}"


def _cleanup_live_overlay_media(original_media_path: str, prepared_media_path: str, remove_original: bool = False):
    if str(prepared_media_path) != str(original_media_path):
        try:
            Path(prepared_media_path).unlink(missing_ok=True)
        except Exception:
            pass
    if remove_original:
        try:
            Path(original_media_path).unlink(missing_ok=True)
        except Exception:
            pass


async def _safe_edit_live_text(bot, rec: LiveSessionRecord, text: str, idx: int):
    markup = kb(_live_controls(idx))
    try:
        await bot.edit_message_caption(chat_id=rec.chat_id, message_id=rec.message_id, caption=text, reply_markup=markup)
    except Exception:
        await bot.edit_message_text(chat_id=rec.chat_id, message_id=rec.message_id, text=text, reply_markup=markup)


async def _upsert_live_photo(bot, rec: LiveSessionRecord, text: str, media_path: str):
    p = Path(str(media_path))
    if not p.exists():
        raise RuntimeError(f"snapshot file not found: {p}")
    markup = kb(_live_controls(rec.camera_idx))
    if rec.message_id > 0:
        try:
            with p.open("rb") as fh:
                media = InputMediaPhoto(media=fh, caption=text)
                await bot.edit_message_media(chat_id=rec.chat_id, message_id=rec.message_id, media=media, reply_markup=markup)
                return
        except Exception as ex:
            log.info("live photo edit fallback user=%s session=%s err=%s", rec.user_id, rec.session_id, ex)
    with p.open("rb") as fh:
        sent = await bot.send_photo(chat_id=rec.chat_id, photo=fh, caption=text, reply_markup=markup)
    rec.chat_id = sent.chat_id
    rec.message_id = sent.message_id


def _build_live_snapshot_payload(camera_idx: int) -> dict[str, str]:
    cams = fetch_camera_rows()
    if camera_idx < 0 or camera_idx >= len(cams):
        raise RuntimeError("camera not found")
    cam = cams[camera_idx]
    out = Path("/tmp") / f"axxon_tg_live_snapshot_{camera_idx}_{uuid.uuid4().hex[:12]}.jpg"
    media_path = run_api(
        "live-snapshot",
        "--video-id", normalize_video_id(str(cam.get("access_point") or "")),
        "--out", str(out),
        "--w", "1280",
        "--h", "720",
    )
    return {
        "text": "\n".join([
            "📸 Live snapshot",
            f"Camera: {cam.get('name')}",
            f"Source: `{cam.get('access_point')}`",
        ]),
        "media_path": str(media_path),
    }


async def _live_session_loop(bot, rec: LiveSessionRecord):
    interval = BOT_CFG.live_in_chat_interval_sec
    max_duration = BOT_CFG.live_in_chat_max_duration_sec
    started = time.monotonic()
    log.info(
        "live session started user=%s camera_idx=%s chat=%s msg=%s interval=%ss max_duration=%ss",
        rec.user_id, rec.camera_idx, rec.chat_id, rec.message_id, interval, max_duration,
    )
    RUNTIME_COUNTERS.incr("live_sessions_started")
    frame_counter = 1
    while (time.monotonic() - started) < max_duration:
        cycle_started = time.monotonic()
        try:
            frame_counter += 1
            payload = await asyncio.to_thread(_build_live_snapshot_payload, rec.camera_idx)
            media_path = str(payload.get("media_path") or "")
            if not media_path:
                raise RuntimeError("empty media_path in live payload")
            prepared_media_path, overlay_note = await asyncio.to_thread(
                _prepare_live_overlay_media, media_path, frame_counter
            )
            caption = _live_caption(payload.get("text", "📸 Live snapshot"), "ON", overlay_note=overlay_note)
            try:
                await _upsert_live_photo(bot, rec, caption, prepared_media_path)
            finally:
                _cleanup_live_overlay_media(media_path, prepared_media_path, remove_original=True)
            RUNTIME_COUNTERS.incr("live_session_updates")
        except asyncio.CancelledError:
            log.info("live session cancelled user=%s session=%s", rec.user_id, rec.session_id)
            raise
        except Exception as ex:
            log.exception("live session error user=%s session=%s err=%s", rec.user_id, rec.session_id, ex)
            RUNTIME_COUNTERS.incr("live_session_errors")
            try:
                await _safe_edit_live_text(
                    bot,
                    rec,
                    _live_caption("⚠️ Live mode stopped due to an update error.", "ERROR"),
                    rec.camera_idx,
                )
            except Exception:
                pass
            return
        sleep_for = max(0.0, interval - (time.monotonic() - cycle_started))
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)
    RUNTIME_COUNTERS.incr("live_session_timeouts")
    log.info("live session timeout user=%s session=%s", rec.user_id, rec.session_id)
    try:
        await _safe_edit_live_text(
            bot,
            rec,
            _live_caption("⏱ Live mode reached max duration.", "STOPPED"),
            rec.camera_idx,
        )
    except Exception:
        pass


async def _on_live_session_end(rec: LiveSessionRecord, reason: str):
    RUNTIME_COUNTERS.incr("live_sessions_ended")
    if reason == "replaced":
        RUNTIME_COUNTERS.incr("live_sessions_replaced")
    elif reason == "manual":
        RUNTIME_COUNTERS.incr("live_sessions_manual_stop")
    elif reason == "error":
        RUNTIME_COUNTERS.incr("live_sessions_end_error")
    elif reason == "finished":
        RUNTIME_COUNTERS.incr("live_sessions_finished")
    log.info("live session ended user=%s session=%s reason=%s", rec.user_id, rec.session_id, reason)


APP_BOT = None
USER_TIMEZONE_CACHE: dict[int, str] = {}


def _is_valid_timezone_name(name: str) -> bool:
    candidate = (name or "").strip()
    if not candidate:
        return False
    if candidate.upper() == "UTC":
        return True
    try:
        ZoneInfo(candidate)
        return True
    except Exception:
        return False


def _normalize_timezone_name(name: str) -> str:
    candidate = (name or "").strip()
    if candidate.upper() == "UTC":
        return "UTC"
    return candidate


def _load_user_timezone_from_store(user_id: int) -> str | None:
    if not SECURE_STORE.enabled:
        return None
    try:
        payload = SECURE_STORE.load_profile("user", f"tg-preferences-{user_id}") or {}
    except Exception:
        return None
    tz_name = str(payload.get("timezone") or "").strip()
    if not _is_valid_timezone_name(tz_name):
        return None
    return _normalize_timezone_name(tz_name)


def _save_user_timezone_to_store(user_id: int, tz_name: str):
    if not SECURE_STORE.enabled:
        return
    payload = {
        "timezone": tz_name,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        SECURE_STORE.save_profile("user", f"tg-preferences-{user_id}", payload)
    except Exception:
        RUNTIME_COUNTERS.incr("secure_profile_errors")


def _get_user_timezone(user_id: int, context: ContextTypes.DEFAULT_TYPE | None = None) -> str:
    if user_id <= 0:
        return "UTC"
    if context is not None:
        tz_name = str(context.user_data.get("timezone") or "").strip()
        if _is_valid_timezone_name(tz_name):
            tz_name = _normalize_timezone_name(tz_name)
            USER_TIMEZONE_CACHE[user_id] = tz_name
            return tz_name
    cached = USER_TIMEZONE_CACHE.get(user_id)
    if cached and _is_valid_timezone_name(cached):
        return cached
    stored = _load_user_timezone_from_store(user_id)
    if stored:
        USER_TIMEZONE_CACHE[user_id] = stored
        if context is not None:
            context.user_data["timezone"] = stored
        return stored
    return "UTC"


def _set_user_timezone(user_id: int, context: ContextTypes.DEFAULT_TYPE | None, tz_name: str):
    tz_normalized = _normalize_timezone_name(tz_name)
    USER_TIMEZONE_CACHE[user_id] = tz_normalized
    if context is not None:
        context.user_data["timezone"] = tz_normalized
    _save_user_timezone_to_store(user_id, tz_normalized)


def _ui_admin_args(user_id: int) -> list[str]:
    return ["--admin"] if USER_MANAGER.is_admin(user_id) else []


async def _live_runner(rec: LiveSessionRecord):
    if APP_BOT is None:
        raise RuntimeError("bot runtime is not initialized")
    await _live_session_loop(APP_BOT, rec)


LIVE_SESSIONS = LiveSessionRuntime(runner=_live_runner, on_end=_on_live_session_end)


def run_ui(subcmd: str, *extra: str, tz: str = "UTC") -> dict:
    callback_data = _arg_value(extra, "--data")
    if subcmd == "callback" and callback_data:
        cache_key = build_runtime_cache_key(
            connection=tuple(AXXON_CFG.as_cli),
            runtime="ui",
            subcmd=subcmd,
            extra=tuple(extra),
            tz=tz,
        )
        return READ_CACHE.load_ui_payload(
            callback_data,
            cache_key,
            lambda: _run_ui_uncached(subcmd, *extra, tz=tz),
        )
    return _run_ui_uncached(subcmd, *extra, tz=tz)


def _ui_timeout_seconds(subcmd: str) -> int:
    if subcmd in {"face-search", "plate-search", "event-search", "single-camera-export", "archive-jump"}:
        return 90
    return 25


def _api_timeout_seconds(subcmd: str) -> int:
    if subcmd in {"search-events", "face-search", "plate-search", "single-camera-export", "archive-jump"}:
        return 90
    if subcmd in {"frame-from-event", "clip-from-event", "box-from-event"}:
        return 60
    if subcmd == "notifier-pull":
        return max(30, BOT_CFG.subscription_notifier_timeout_sec + 10)
    return 25


def _run_ui_uncached(subcmd: str, *extra: str, tz: str = "UTC") -> dict:
    cmd = [
        sys.executable, str(UI),
        *AXXON_CFG.as_cli,
        "--tz", tz,
        subcmd,
        *extra,
    ]
    timeout_sec = _ui_timeout_seconds(subcmd)
    log.debug("run_ui: %s", " ".join(cmd[:3] + [subcmd] + list(extra)))
    result = run_command(cmd, timeout_sec=timeout_sec)
    if not isinstance(result.parsed, dict):
        raise RuntimeError(f"UI command failed ({subcmd}): unexpected payload")
    return result.parsed


def run_api(subcmd: str, *extra: str):
    cmd = [
        sys.executable, str(API),
        *AXXON_CFG.as_cli,
        subcmd,
        *extra,
    ]
    log.debug("run_api: %s", " ".join(cmd[:3] + [subcmd] + list(extra)))
    out = subprocess.check_output(cmd, text=True, timeout=_api_timeout_seconds(subcmd))
    text = str(out or "").strip()
    if subcmd in {"frame-from-event", "clip-from-event", "live-snapshot"}:
        return text
    return json.loads(text)


def _arg_value(args: tuple[str, ...], flag: str) -> str:
    for idx, value in enumerate(args):
        if value == flag and idx + 1 < len(args):
            return str(args[idx + 1])
    return ""


def fetch_detectors() -> list[dict]:
    cache_key = build_runtime_cache_key(
        connection=tuple(AXXON_CFG.as_cli),
        runtime="api",
        subcmd="list-detectors",
    )
    return READ_CACHE.load_detector_inventory(
        cache_key,
        lambda: normalize_detector_rows(run_api("list-detectors")),
    )


def fetch_camera_rows() -> list[dict]:
    cache_key = build_runtime_cache_key(
        connection=tuple(AXXON_CFG.as_cli),
        runtime="api",
        subcmd="list-cameras",
        view="VIEW_MODE_FULL",
    )
    return READ_CACHE.load_camera_catalog(
        cache_key,
        lambda: [
            {"name": x.get("name"), "access_point": x.get("access_point")}
            for x in normalize_camera_rows(run_api("list-cameras", "--view", "VIEW_MODE_FULL"))
        ],
    )


def kb(buttons_raw):
    rows = []
    for row in buttons_raw or []:
        rows.append([InlineKeyboardButton(x["text"], callback_data=x["callback_data"]) for x in row])
    return InlineKeyboardMarkup(rows) if rows else None


def _is_live_subscription_alert_callback(callback_data: str, message: Any) -> bool:
    if not callback_data.startswith("al:flag:"):
        return False
    if not message:
        return False
    text = str(getattr(message, "caption", "") or getattr(message, "text", "") or "")
    if "🔔 Sub #" in text:
        return True
    markup = getattr(message, "reply_markup", None)
    if not markup:
        return False
    has_alert_review = False
    has_alert_clip = False
    for row in (getattr(markup, "inline_keyboard", None) or []):
        for b in row:
            cb = str(getattr(b, "callback_data", "") or "")
            if cb.startswith("al:flag:"):
                has_alert_review = True
            if cb.startswith("sub:clip:ET_Alert:"):
                has_alert_clip = True
    return has_alert_review and has_alert_clip


def _extract_live_alert_clip_rows(message: Any) -> list[list[dict[str, str]]]:
    out: list[list[dict[str, str]]] = []
    markup = getattr(message, "reply_markup", None)
    for row in (getattr(markup, "inline_keyboard", None) or []):
        clip_row: list[dict[str, str]] = []
        for b in row:
            cb = str(getattr(b, "callback_data", "") or "")
            if cb.startswith("sub:clip:ET_Alert:"):
                clip_row.append({"text": str(getattr(b, "text", "") or "🎬 Clip"), "callback_data": cb})
        if clip_row:
            out.append(clip_row)
    return out


async def _guard(update: Update) -> bool:
    user = update.effective_user
    if not user:
        return False
    if USER_MANAGER.is_authorized(user.id):
        return True
    msg = f"⛔️ Access denied. Your Telegram user id: {user.id}"
    if update.callback_query:
        await update.callback_query.answer("Not authorized", show_alert=True)
        await update.effective_chat.send_message(msg)
    elif update.message:
        await update.message.reply_text(msg)
    return False


async def show_payload(update: Update, payload: dict, edit: bool = False):
    text = payload.get("text", "")
    markup = kb(payload.get("buttons"))
    media = payload.get("media_path")
    user = update.effective_user
    user_id = user.id if user else 0

    chat = update.effective_chat

    if media:
        p = Path(media)
        if p.exists():
            media_fp = f"media:{p.suffix.lower()}:{p}:{text}"
            if not SEND_THROTTLE.allow(user_id, media_fp):
                media = None
                RUNTIME_COUNTERS.incr("media_suppressed")
            elif p.suffix.lower() in {".mp4", ".mov", ".mkv"}:
                with p.open("rb") as fh:
                    await chat.send_video(video=fh, caption=text)
                RUNTIME_COUNTERS.incr("videos_sent")
            else:
                with p.open("rb") as fh:
                    await chat.send_photo(photo=fh, caption=text)
                RUNTIME_COUNTERS.incr("photos_sent")

    if update.callback_query and edit:
        try:
            msg = update.callback_query.message
            if msg and (getattr(msg, "photo", None) or getattr(msg, "video", None)):
                await update.callback_query.edit_message_caption(caption=text, reply_markup=markup)
            else:
                await update.callback_query.edit_message_text(text=text, reply_markup=markup)
            RUNTIME_COUNTERS.incr("messages_edited")
        except Exception:
            text_fp = f"text:{text}"
            if SEND_THROTTLE.allow(user_id, text_fp):
                await chat.send_message(text=text, reply_markup=markup)
                RUNTIME_COUNTERS.incr("messages_sent")
            else:
                RUNTIME_COUNTERS.incr("text_suppressed")
    else:
        text_fp = f"text:{text}"
        if SEND_THROTTLE.allow(user_id, text_fp):
            await chat.send_message(text=text, reply_markup=markup)
            RUNTIME_COUNTERS.incr("messages_sent")
        else:
            RUNTIME_COUNTERS.incr("text_suppressed")

    meta = payload.get("meta") or {}
    kind = meta.get("kind")
    if kind:
        RUNTIME_COUNTERS.incr(f"{kind}_views")
    page_size = meta.get("page_size")
    if isinstance(page_size, int):
        RUNTIME_COUNTERS.incr("items_shown_total", page_size)


def _new_subscription_draft(context: ContextTypes.DEFAULT_TYPE, data: dict[str, Any]) -> str:
    drafts = context.user_data.setdefault("subscription_drafts", {})
    next_id = int(context.user_data.get("subscription_draft_next_id") or 1)
    context.user_data["subscription_draft_next_id"] = next_id + 1
    draft_id = str(next_id)
    drafts[draft_id] = data
    return draft_id


def _get_subscription_draft(context: ContextTypes.DEFAULT_TYPE, draft_id: str) -> dict[str, Any] | None:
    drafts = context.user_data.get("subscription_drafts") or {}
    return drafts.get(draft_id)


def _drop_subscription_draft(context: ContextTypes.DEFAULT_TYPE, draft_id: str):
    drafts = context.user_data.get("subscription_drafts") or {}
    drafts.pop(draft_id, None)


def _new_macro_execution_draft(context: ContextTypes.DEFAULT_TYPE, data: dict[str, Any]) -> str:
    drafts = context.user_data.setdefault("macro_execution_drafts", {})
    next_id = int(context.user_data.get("macro_execution_draft_next_id") or 1)
    context.user_data["macro_execution_draft_next_id"] = next_id + 1
    draft_id = str(next_id)
    drafts[draft_id] = {
        **data,
        "created_monotonic": time.monotonic(),
    }
    return draft_id


def _get_macro_execution_draft(context: ContextTypes.DEFAULT_TYPE, draft_id: str) -> dict[str, Any] | None:
    drafts = context.user_data.get("macro_execution_drafts") or {}
    draft = drafts.get(draft_id)
    if not draft:
        return None
    created_monotonic = float(draft.get("created_monotonic") or 0.0)
    if created_monotonic > 0 and (time.monotonic() - created_monotonic) > MACRO_CONFIRM_TTL_SEC:
        drafts.pop(draft_id, None)
        return None
    return draft


def _drop_macro_execution_draft(context: ContextTypes.DEFAULT_TYPE, draft_id: str):
    drafts = context.user_data.get("macro_execution_drafts") or {}
    drafts.pop(draft_id, None)


def _new_ptz_control_draft(context: ContextTypes.DEFAULT_TYPE, data: dict[str, Any]) -> str:
    drafts = context.user_data.setdefault("ptz_control_drafts", {})
    next_id = int(context.user_data.get("ptz_control_draft_next_id") or 1)
    context.user_data["ptz_control_draft_next_id"] = next_id + 1
    draft_id = str(next_id)
    drafts[draft_id] = {
        **data,
        "created_monotonic": time.monotonic(),
    }
    return draft_id


def _get_ptz_control_draft(context: ContextTypes.DEFAULT_TYPE, draft_id: str) -> dict[str, Any] | None:
    drafts = context.user_data.get("ptz_control_drafts") or {}
    draft = drafts.get(draft_id)
    if not draft:
        return None
    created_monotonic = float(draft.get("created_monotonic") or 0.0)
    if created_monotonic > 0 and (time.monotonic() - created_monotonic) > PTZ_CONFIRM_TTL_SEC:
        drafts.pop(draft_id, None)
        return None
    return draft


def _drop_ptz_control_draft(context: ContextTypes.DEFAULT_TYPE, draft_id: str):
    drafts = context.user_data.get("ptz_control_drafts") or {}
    drafts.pop(draft_id, None)


def _macro_confirm_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm macro execute", callback_data=f"macro:confirm:{draft_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"macro:cancel:{draft_id}")],
        [InlineKeyboardButton("🏠 Main", callback_data="home")],
    ])


def _macro_policy_api_args(user_id: int) -> list[str]:
    policy = build_macro_execution_policy(
        execution_enabled=BOT_CFG.macro_execution_enabled,
        admin=USER_MANAGER.is_admin(user_id),
        allowed_macro_ids=BOT_CFG.macro_allowed_ids,
        allowed_macro_names=BOT_CFG.macro_allowed_names,
    )
    return macro_execution_policy_to_api_args(policy)


def _ptz_policy_api_args(user_id: int) -> list[str]:
    policy = build_ptz_control_policy(
        control_enabled=BOT_CFG.ptz_control_enabled,
        admin=USER_MANAGER.is_admin(user_id),
        allowed_camera_access_points=BOT_CFG.ptz_allowed_camera_aps,
        allowed_camera_names=BOT_CFG.ptz_allowed_camera_names,
    )
    return ptz_control_policy_to_api_args(policy)


def _macro_execution_result_text(result: dict[str, Any]) -> str:
    macro = result.get("macro") if isinstance(result.get("macro"), dict) else {}
    guardrails = result.get("guardrails") if isinstance(result.get("guardrails"), dict) else {}
    execution = result.get("execution") if isinstance(result.get("execution"), dict) else {}
    reasons = [str(item).strip() for item in (guardrails.get("reasons") or []) if str(item).strip()]
    warnings = [str(item).strip() for item in (guardrails.get("warnings") or []) if str(item).strip()]
    attempted = bool(execution.get("attempted"))
    ok = bool(execution.get("ok"))

    lines = [
        "✅ Macro executed" if ok else ("⛔️ Macro execution blocked" if not attempted else "⚠️ Macro execution failed"),
        f"Macro: {macro.get('name') or '—'}",
        f"ID: {macro.get('id') or '—'}",
        f"Actions: {', '.join(macro.get('action_families') or []) or 'unknown'}",
    ]
    if execution.get("transport"):
        lines.append(f"Transport: {execution.get('transport')}")
    if execution.get("error"):
        lines.append(f"Error: {execution.get('error')}")
    if reasons:
        lines.extend(["", "Guardrails:"])
        lines.extend([f"- {item}" for item in reasons])
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend([f"- {item}" for item in warnings])
    return "\n".join(lines)


def _ptz_control_result_text(result: dict[str, Any]) -> str:
    camera = result.get("camera") if isinstance(result.get("camera"), dict) else {}
    ptz = result.get("ptz") if isinstance(result.get("ptz"), dict) else {}
    selected_preset = ptz.get("selected_preset") if isinstance(ptz.get("selected_preset"), dict) else {}
    guardrails = result.get("guardrails") if isinstance(result.get("guardrails"), dict) else {}
    execution = result.get("execution") if isinstance(result.get("execution"), dict) else {}
    reasons = [str(item).strip() for item in (guardrails.get("reasons") or []) if str(item).strip()]
    warnings = [str(item).strip() for item in (guardrails.get("warnings") or []) if str(item).strip()]
    attempted = bool(execution.get("attempted"))
    ok = bool(execution.get("ok"))

    lines = [
        "✅ PTZ preset executed" if ok else ("⛔️ PTZ control blocked" if not attempted else "⚠️ PTZ control failed"),
        f"Camera: {camera.get('name') or '—'}",
        f"Source: {camera.get('access_point') or '—'}",
        (
            f"Preset: {selected_preset.get('label') or '—'}"
            f" ({selected_preset.get('position') or '—'})"
        ),
    ]
    if execution.get("transport"):
        lines.append(f"Transport: {execution.get('transport')}")
    if execution.get("error"):
        lines.append(f"Error: {execution.get('error')}")
    if reasons:
        lines.extend(["", "Guardrails:"])
        lines.extend([f"- {item}" for item in reasons])
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend([f"- {item}" for item in warnings])
    return "\n".join(lines)


def _state_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 BEGAN", callback_data=f"{prefix}:BEGAN"),
            InlineKeyboardButton("✅ HAPP.", callback_data=f"{prefix}:HAPPENED"),
            InlineKeyboardButton("🛑 ENDED", callback_data=f"{prefix}:ENDED"),
        ],
        [InlineKeyboardButton("All States", callback_data=f"{prefix}:ALL")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])


def _confirm_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm subscription", callback_data=f"sub:confirm:{draft_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])


def _states_from_choice(raw: str) -> list[str]:
    # Product decision: always track BEGAN for subscriptions.
    return ["BEGAN"]


async def _start_draft_state_selection(q, context: ContextTypes.DEFAULT_TYPE, draft_data: dict[str, Any]):
    # Product decision: subscriptions are BEGAN-only.
    draft_data = dict(draft_data)
    draft_data["states"] = ["BEGAN"]
    draft_id = _new_subscription_draft(context, draft_data)
    lines = [
        "🔔 Create subscription from current filters",
        "",
        draft_data.get("summary") or "",
        "",
        "State: BEGAN (fixed)",
        "Press confirm to start.",
    ]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm subscription", callback_data=f"sub:confirm:{draft_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])
    await q.edit_message_text(text="\n".join(lines), reply_markup=kb)


TELEGRAM_MENU_COMMANDS = [
    BotCommand("start", "main menu"),
    BotCommand("events", "recent events feed"),
    BotCommand("alerts", "recent alerts feed"),
    BotCommand("cameras", "cameras and actions"),
    BotCommand("archive", "archive jump and preview"),
    BotCommand("search", "time-range event search"),
    BotCommand("face", "upload photo or reply /face"),
    BotCommand("plate", "license plate search"),
    BotCommand("export", "single-camera clip export"),
    BotCommand("server", "server info"),
    BotCommand("subscribe", "create a subscription"),
    BotCommand("subscriptions", "list active subscriptions"),
    BotCommand("stop", "stop all subscriptions or /stop <id>"),
    BotCommand("status", "API status"),
    BotCommand("tz", "set timezone, e.g. /tz Europe/Rome"),
    BotCommand("help", "show help"),
]


async def _register_telegram_commands(app: Application):
    try:
        await app.bot.set_my_commands(TELEGRAM_MENU_COMMANDS)
        if BotCommandScopeAllPrivateChats is not None:
            await app.bot.set_my_commands(
                TELEGRAM_MENU_COMMANDS,
                scope=BotCommandScopeAllPrivateChats(),
            )
        if BotCommandScopeAllGroupChats is not None:
            await app.bot.set_my_commands(
                TELEGRAM_MENU_COMMANDS,
                scope=BotCommandScopeAllGroupChats(),
            )
        if MenuButtonCommands is not None:
            await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        log.info(
            "registered %s Telegram menu commands for default/private/group scopes and enabled commands menu button",
            len(TELEGRAM_MENU_COMMANDS),
        )
    except Exception:
        log.exception("failed to register Telegram menu commands")


async def cmd_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


async def cmd_stop_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.args = []
    await cmd_stop(update, context)


def _normalized_text_shortcut(text: object) -> str:
    raw = str(text or "").strip().casefold()
    if not raw:
        return ""
    raw = re.sub(r"^/\s+", "/", raw)
    return raw


TEXT_SHORTCUT_HANDLERS = {
    "start": "cmd_start",
    "/start": "cmd_start",
    "help": "cmd_help",
    "/help": "cmd_help",
    "events": "cmd_events",
    "/events": "cmd_events",
    "alerts": "cmd_alerts",
    "/alerts": "cmd_alerts",
    "cameras": "cmd_cameras",
    "/cameras": "cmd_cameras",
    "server": "cmd_server",
    "/server": "cmd_server",
    "status": "cmd_status",
    "/status": "cmd_status",
    "search": "cmd_search",
    "/search": "cmd_search",
    "archive": "cmd_archive",
    "/archive": "cmd_archive",
    "plate": "cmd_plate",
    "/plate": "cmd_plate",
    "export": "cmd_export",
    "/export": "cmd_export",
    "subscribe": "cmd_subscribe",
    "/subscribe": "cmd_subscribe",
    "subscriptions": "cmd_subscriptions",
    "/subscriptions": "cmd_subscriptions",
    "admin": "cmd_admin",
    "/admin": "cmd_admin",
}
UI_MODE_KEY = "ui_mode"


def _parse_manual_accuracy_percent(text: object) -> int | None:
    raw = str(text or "").strip().casefold()
    if not raw:
        return None
    if raw.endswith("%"):
        raw = raw[:-1].strip()
    try:
        value = float(raw)
    except ValueError:
        return None
    if value <= 0:
        return None
    if value <= 1:
        value *= 100
    percent = int(round(value))
    if 1 <= percent <= 100:
        return percent
    return None


async def _handle_face_search_threshold_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    wizard = context.user_data.get(FACE_SEARCH_WIZARD_KEY)
    if not isinstance(wizard, dict):
        return False
    if wizard.get("accuracy_percent"):
        return False
    accuracy_percent = _parse_manual_accuracy_percent(text)
    if accuracy_percent is None:
        await update.effective_chat.send_message(
            text="Enter similarity as 90, 87, 0.87, or 87%.",
            reply_markup=kb(build_face_search_wizard_threshold_buttons(str(wizard.get("draft_id") or ""))),
        )
        return True
    wizard["accuracy_percent"] = accuracy_percent
    await update.effective_chat.send_message(
        text=_face_search_period_prompt_text(list(wizard.get("terms") or []), accuracy_percent),
        reply_markup=kb(build_face_search_wizard_period_buttons(str(wizard.get("draft_id") or ""))),
    )
    return True


async def msg_text_shortcut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = getattr(update.effective_message, "text", "")
    if await _handle_face_search_threshold_text(update, context, raw_text):
        return
    text = _normalized_text_shortcut(raw_text)
    handler_name = TEXT_SHORTCUT_HANDLERS.get(text)
    if not handler_name:
        return
    handler = globals().get(handler_name)
    if handler is None:
        return
    await handler(update, context)


def _get_ui_mode(context: ContextTypes.DEFAULT_TYPE | None) -> str:
    mode = str((context.user_data if context else {}).get(UI_MODE_KEY) or "operator").strip().lower()
    return "admin" if mode == "admin" else "operator"


def _set_ui_mode(context: ContextTypes.DEFAULT_TYPE | None, mode: str) -> str:
    normalized = "admin" if str(mode).strip().lower() == "admin" else "operator"
    if context is not None:
        context.user_data[UI_MODE_KEY] = normalized
    return normalized


def _fallback_home_payload(*, mode: str = "operator") -> dict[str, object]:
    mode = "admin" if str(mode).strip().lower() == "admin" else "operator"
    title = "🛰 Axxon One Admin Console" if mode == "admin" else "🛰 Axxon One Operator Console"
    mode_button = "⚙️ Mode: Admin" if mode == "admin" else "⚙️ Mode: Operator"
    next_mode = "operator" if mode == "admin" else "admin"
    buttons = [
        [{"text": "🚨 Events", "callback_data": "ev:feed:0"}, {"text": "🚨 Alerts", "callback_data": "al:feed:0"}],
        [{"text": "📷 Cameras", "callback_data": "cam:list:0"}, {"text": "🔎 Search", "callback_data": "sea:menu"}],
        [{"text": "🎬 Archive", "callback_data": "arch:menu"}, {"text": "🖥 Server", "callback_data": "srv:menu"}],
    ]
    if mode == "admin":
        buttons.append([{"text": "🛠 Admin", "callback_data": "adm:menu"}, {"text": "🛠 Health", "callback_data": "sys:health"}])
    else:
        buttons.append([{"text": "🔔 Subscribe", "callback_data": "sub:det:list"}, {"text": "📋 Subs", "callback_data": "sub:list"}])
    buttons.append([{"text": mode_button, "callback_data": f"mode:{next_mode}"}, {"text": "❓ Help", "callback_data": "home:help"}])
    return {
        "text": f"{title}\n\nFast home mode. Pick a surface below.",
        "buttons": buttons,
    }


_UI_ERROR_SECTIONS: dict[str, tuple[str, list[list[dict[str, str]]]]] = {
    "events": ("Events", [[{"text": "🚨 Events", "callback_data": "ev:feed:0"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "alerts": ("Alerts", [[{"text": "🚨 Alerts", "callback_data": "al:feed:0"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "cameras": ("Cameras", [[{"text": "📷 Cameras", "callback_data": "cam:list:0"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "search": ("Search", [[{"text": "🔎 Search", "callback_data": "sea:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "face": ("Face search", [[{"text": "🔎 Search", "callback_data": "sea:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "plate": ("Plate search", [[{"text": "🔎 Search", "callback_data": "sea:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "archive": ("Archive", [[{"text": "🎬 Archive", "callback_data": "arch:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "export": ("Export", [[{"text": "🎬 Archive", "callback_data": "arch:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "macro": ("Macro control", [[{"text": "🛠 Admin", "callback_data": "adm:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "ptz": ("PTZ control", [[{"text": "🛠 Admin", "callback_data": "adm:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "server": ("Server", [[{"text": "🏠 Main", "callback_data": "home"}], [{"text": "🖥 Server", "callback_data": "srv:menu"}]]),
    "admin": ("Admin view", [[{"text": "🛠 Admin", "callback_data": "adm:menu"}], [{"text": "🏠 Home", "callback_data": "home"}]]),
    "home": ("Home", [[{"text": "🏠 Home", "callback_data": "home"}]]),
}


def _ui_error_payload(section: str, *, cause: str | None = None) -> dict[str, object]:
    label, buttons = _UI_ERROR_SECTIONS.get(section, _UI_ERROR_SECTIONS["home"])
    cause_text = str(cause or "").lower()
    if "timed out" in cause_text:
        headline = f"⚠️ Action failed: {label} timed out."
    else:
        headline = f"⚠️ Action failed: {label} is unavailable right now."
    return {
        "text": "\n".join([headline, "Try again shortly."]),
        "buttons": buttons,
    }


def _ui_error_section_from_callback(callback_data: str) -> str:
    data = str(callback_data or "")
    if data.startswith("ev:"):
        return "events"
    if data.startswith("al:"):
        return "alerts"
    if data.startswith("cam:"):
        return "cameras"
    if data.startswith("sea:") or data.startswith("lpr:"):
        return "search"
    if data.startswith("arch:"):
        return "archive"
    if data.startswith("srv:") or data.startswith("sys:"):
        return "server"
    if data.startswith("adm:"):
        return "admin"
    return "home"


def _run_ui_payload_or_error(subcmd: str, *extra: str, tz: str = "UTC", section: str) -> dict[str, object]:
    try:
        return run_ui(subcmd, *extra, tz=tz)
    except Exception as exc:
        log.warning("ui bridge failed section=%s subcmd=%s err=%s", section, subcmd, exc)
        return _ui_error_payload(section, cause=str(exc))


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    mode = _get_ui_mode(context)
    payload = _fallback_home_payload(mode=mode)
    await show_payload(update, payload, edit=False)


async def cmd_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    tz_name = _get_user_timezone(user_id, context)
    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "ev:feed:0",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="events",
    )
    await show_payload(update, payload, edit=False)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    text = "\n".join([
        "🤖 Commands",
        "",
        "Monitor and feeds:",
        "/start - main menu",
        "/events - events feed",
        "/alerts - alerts feed",
        "/cameras - cameras and actions",
        "/server - server info (usage/version/statistics)",
        "/status - API status",
        "",
        "Search and archive:",
        "Use the Search menu from /start for /search, /plate, and /face shortcuts.",
        "Use the Archive menu from /start for /archive and /export shortcuts.",
        "/search - time-range event search",
        "/plate - license plate search",
        "/face - face search for an uploaded photo or a replied photo",
        "  upload-first flow asks for similarity and period presets before search",
        "/archive - archive jump and preview",
        "/export - single-camera clip export",
        "",
        "Subscriptions:",
        "/subscribe - subscription by selected detectors",
        "/subscriptions - active subscriptions list",
        "/stop - stop all subscriptions",
        "/stop <id> - stop subscription by id",
        "",
        "Admin tools:",
        "/admin - read-only admin overview",
        "/macro - admin-only guarded macro execution preview",
        "/ptz - admin-only guarded PTZ preset preview",
        "",
        "Search example:",
        "/search from=2026-03-10T08:00:00Z to=2026-03-10T09:00:00Z mode=summary",
        "(upload photo) send a Telegram photo",
        "(upload photo) choose 90/85/80 then 15m/1h/6h/24h",
        "(reply to photo) /face camera=1.Lobby last=7200",
        "/plate plate=BE59922",
        "/archive camera=2.Gate at=2026-03-10T10:55:00Z",
        "/export from=2026-03-10T10:50:00Z to=2026-03-10T10:55:00Z camera=2.Gate",
        "/macro id=941f88d1-b512-4189-84a6-7d274892dd95",
        "/ptz camera=2.Gate preset=Home",
        "",
        "Settings:",
        "/tz <IANA zone> - set your timezone (example: /tz Europe/Rome or /tz UTC)",
        "",
        "Help:",
        "/help - this help",
    ])
    await update.effective_chat.send_message(text=text)


async def cmd_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    args = context.args or []
    if not args:
        current = _get_user_timezone(user_id, context)
        await update.effective_chat.send_message(
            text=(
                f"Current timezone: {current}\n"
                "Use /tz Europe/Rome or /tz UTC."
            ),
        )
        return

    candidate = " ".join(args).strip()
    if not _is_valid_timezone_name(candidate):
        await update.effective_chat.send_message(
            text=(
                "Invalid timezone. Use IANA format, for example:\n"
                "/tz UTC\n"
                "/tz Europe/Rome"
            ),
        )
        return

    tz_name = _normalize_timezone_name(candidate)
    _set_user_timezone(user_id, context, tz_name)
    await update.effective_chat.send_message(text=f"Timezone updated: {tz_name}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    tz_name = _get_user_timezone(user_id, context)
    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "sys:health",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="server",
    )
    await show_payload(update, payload, edit=False)


def _face_search_home_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]])


def _face_search_scope_line(terms: list[str]) -> str | None:
    kept = [str(term).strip() for term in (terms or []) if str(term).strip()]
    if not kept:
        return None
    summary = " · ".join(kept[:2])
    if len(kept) > 2:
        summary = f"{summary} · ..."
    return f"Scope kept: {summary}"


def _face_search_entry_text() -> str:
    return "\n".join([
        "🙂 Face search",
        "Upload a face photo.",
        "",
        "Requirements:",
        "• JPG, PNG, or GIF",
        "• Up to 4 MB",
        "• Front-facing face",
        "• Clear image with even lighting",
        "• Face should take most of the frame",
        "• Head and shoulders preferred",
    ])


def _face_search_threshold_prompt_text(terms: list[str]) -> str:
    lines = [
        "🙂 Face search",
        "Reference photo saved.",
        "Choose similarity.",
    ]
    scope_line = _face_search_scope_line(terms)
    if scope_line:
        lines.extend(["", scope_line])
    return "\n".join(lines)


def _face_search_period_prompt_text(terms: list[str], accuracy_percent: int) -> str:
    lines = [
        "🙂 Face search",
        f"Similarity: {accuracy_percent}%",
        "Choose period.",
    ]
    scope_line = _face_search_scope_line(terms)
    if scope_line:
        lines.extend(["", scope_line])
    return "\n".join(lines)


def _face_search_running_text(accuracy_percent: int, period_seconds: int) -> str:
    return "\n".join([
        "🙂 Face search",
        f"Similarity: {accuracy_percent}%",
        f"Period: {format_face_search_wizard_period_label(period_seconds)}",
        "Running search...",
    ])


async def _send_face_search_message(
    update: Update,
    text: str,
    *,
    edit: bool,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return
    await update.effective_chat.send_message(text=text, reply_markup=reply_markup)


def _new_face_search_wizard(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    file_id: str,
    suffix: str,
    terms: list[str],
) -> dict[str, Any]:
    next_id = int(context.user_data.get(FACE_SEARCH_WIZARD_NEXT_ID_KEY) or 1)
    context.user_data[FACE_SEARCH_WIZARD_NEXT_ID_KEY] = next_id + 1
    wizard = {
        "draft_id": str(next_id),
        "file_id": file_id,
        "suffix": suffix or ".jpg",
        "terms": list(terms or []),
    }
    context.user_data[FACE_SEARCH_WIZARD_KEY] = wizard
    return wizard


def _get_face_search_wizard(context: ContextTypes.DEFAULT_TYPE, draft_id: str) -> dict[str, Any] | None:
    wizard = context.user_data.get(FACE_SEARCH_WIZARD_KEY)
    if not isinstance(wizard, dict):
        return None
    if str(wizard.get("draft_id") or "") != str(draft_id or ""):
        return None
    return wizard


def _drop_face_search_wizard(context: ContextTypes.DEFAULT_TYPE, draft_id: str | None = None) -> None:
    wizard = context.user_data.get(FACE_SEARCH_WIZARD_KEY)
    if not isinstance(wizard, dict):
        return
    if draft_id is not None and str(wizard.get("draft_id") or "") != str(draft_id):
        return
    context.user_data.pop(FACE_SEARCH_WIZARD_KEY, None)


async def _start_face_search_wizard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    terms: list[str],
) -> None:
    file_id, suffix = face_reference_attachment(update.effective_message)
    if not file_id:
        await update.effective_chat.send_message(
            text="Upload a Telegram photo or reply /face to a photo. Telegram photos and .jpg image files work best."
        )
        return
    wizard = _new_face_search_wizard(context, file_id=file_id, suffix=suffix or ".jpg", terms=list(terms or []))
    context.user_data.pop(FACE_SEARCH_PENDING_KEY, None)
    await update.effective_chat.send_message(
        text=_face_search_threshold_prompt_text(wizard["terms"]),
        reply_markup=kb(build_face_search_wizard_threshold_buttons(wizard["draft_id"])),
    )


async def _download_face_reference_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    reference_file_id: str | None = None,
    reference_suffix: str | None = None,
) -> tuple[Path | None, str | None]:
    file_id = str(reference_file_id or "").strip()
    suffix = str(reference_suffix or "").strip() or ".jpg"
    if not file_id:
        message = update.effective_message
        file_id, suffix = face_reference_attachment(message)
    if not file_id:
        return None, "Upload a Telegram photo or reply /face to a photo. Telegram photos and .jpg image files work best."
    out_path = Path(f"/tmp/axxon_tg_face_search_{uuid.uuid4().hex}{suffix}")
    try:
        tg_file = await context.bot.get_file(file_id)
        await tg_file.download_to_drive(custom_path=str(out_path))
    except Exception as ex:
        log.exception("failed to download face-search reference image")
        return None, f"Unable to download the reference image.\n{ex}"
    return out_path, None


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    tz_name = _get_user_timezone(update.effective_user.id, context)
    try:
        payload = _run_ui_payload_or_error("event-search", *(context.args or []), tz=tz_name, section="search")
    except Exception as ex:
        await update.effective_chat.send_message(text=f"⚠️ Event search failed.\n{ex}")
        return
    await show_payload(update, payload, edit=False)


def _face_result_caption(item: dict[str, Any], idx: int) -> str:
    score = item.get("similarity")
    try:
        score_text = f"{float(score):.0%}"
    except (TypeError, ValueError):
        score_text = str(score or "—")
    return "\n".join([
        f"🙂 Face result #{idx}",
        f"Score: {score_text}",
        f"Camera: {item.get('camera') or '—'}",
        f"Timestamp: {SUBSCRIPTIONS._fmt_ts_utc(str(item.get('timestamp') or ''))}",
    ])


async def _send_face_search_result_cards(update: Update, payload: dict[str, Any]) -> None:
    result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
    items = result.get("items") if isinstance(result.get("items"), list) else []
    if not items:
        return
    chat = update.effective_chat
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        event_id = str(item.get("event_guid") or item.get("id") or "").strip()
        if not event_id:
            continue
        raw_event = item.get("raw_event") if isinstance(item.get("raw_event"), dict) else None
        if raw_event:
            media_path = await asyncio.to_thread(SUBSCRIPTIONS._build_combined_event_image_from_raw, raw_event, event_id, "ET_DetectorEvent")
        else:
            media_path = await asyncio.to_thread(SUBSCRIPTIONS._build_combined_event_image, event_id, "ET_DetectorEvent")
        if not media_path:
            continue
        p = Path(media_path)
        if not p.exists():
            continue
        with p.open("rb") as fh:
            await chat.send_photo(photo=fh, caption=_face_result_caption(item, idx))


async def cmd_face(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    terms = list(context.args or [])
    context.user_data[FACE_SEARCH_PENDING_KEY] = {"terms": terms}
    _drop_face_search_wizard(context, None)
    await update.effective_chat.send_message(text=_face_search_entry_text())


async def _run_face_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    terms: list[str] | None = None,
    reference_file_id: str | None = None,
    reference_suffix: str | None = None,
    edit: bool = False,
):
    reference_path, error_text = await _download_face_reference_image(
        update,
        context,
        reference_file_id=reference_file_id,
        reference_suffix=reference_suffix,
    )
    if error_text:
        await _send_face_search_message(
            update,
            error_text,
            edit=edit,
            reply_markup=_face_search_home_markup() if edit else None,
        )
        return

    tz_name = _get_user_timezone(update.effective_user.id, context)
    try:
        payload = _run_ui_payload_or_error(
            "face-search",
            "--image",
            str(reference_path),
            *(terms or []),
            tz=tz_name,
            section="face",
        )
    except Exception as ex:
        await _send_face_search_message(
            update,
            f"⚠️ Face search failed.\n{ex}",
            edit=edit,
            reply_markup=_face_search_home_markup() if edit else None,
        )
        return
    finally:
        try:
            if reference_path and reference_path.exists():
                reference_path.unlink()
        except Exception:
            log.debug("face search reference cleanup failed", exc_info=True)
    await show_payload(update, payload, edit=edit)
    await _send_face_search_result_cards(update, payload)


async def msg_face_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    should_search, terms = should_start_face_search_from_upload(update.effective_message)
    pending = context.user_data.get(FACE_SEARCH_PENDING_KEY) if hasattr(context, 'user_data') else None
    if pending and isinstance(pending, dict):
        pending_terms = list(pending.get("terms") or [])
        terms = pending_terms or terms
        should_search = True
    if not should_search:
        return
    if face_search_terms_support_wizard(terms):
        await _start_face_search_wizard(update, context, terms=terms)
        return
    context.user_data.pop(FACE_SEARCH_PENDING_KEY, None)
    await _run_face_search(update, context, terms=terms)


async def cmd_plate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    tz_name = _get_user_timezone(update.effective_user.id, context)
    try:
        payload = _run_ui_payload_or_error("plate-search", *(context.args or []), tz=tz_name, section="plate")
    except Exception as ex:
        await update.effective_chat.send_message(text=f"⚠️ License plate search failed.\n{ex}")
        return
    await show_payload(update, payload, edit=False)


async def cmd_archive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    tz_name = _get_user_timezone(update.effective_user.id, context)
    try:
        if context.args:
            payload = _run_ui_payload_or_error("archive-jump", *(context.args or []), tz=tz_name, section="archive")
        else:
            payload = _run_ui_payload_or_error(
                "callback",
                "--seconds",
                "1800",
                "--data",
                "arch:wiz:0",
                tz=tz_name,
                section="archive",
            )
    except Exception as ex:
        await update.effective_chat.send_message(text=f"⚠️ Archive jump failed.\n{ex}")
        return
    await show_payload(update, payload, edit=False)


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    tz_name = _get_user_timezone(update.effective_user.id, context)
    try:
        payload = _run_ui_payload_or_error(
            "single-camera-export",
            *(context.args or []),
            tz=tz_name,
            section="export",
        )
    except Exception as ex:
        await update.effective_chat.send_message(text=f"⚠️ Single-camera export failed.\n{ex}")
        return
    await show_payload(update, payload, edit=False)


async def cmd_macro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    if not USER_MANAGER.is_admin(user_id):
        await update.effective_chat.send_message(
            text=(
                "⛔️ Macro execution is restricted to configured Telegram admins.\n"
                "This flow remains disabled for operator accounts."
            )
        )
        return

    tz_name = _get_user_timezone(user_id, context)
    extra = [
        *_macro_policy_api_args(user_id),
        *(context.args or []),
    ]
    try:
        payload = _run_ui_payload_or_error("macro-execution", *extra, tz=tz_name, section="macro")
    except Exception as ex:
        await update.effective_chat.send_message(text=f"⚠️ Macro execution preview failed.\n{ex}")
        return

    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("allowed"):
        macro_id = str(meta.get("macro_id") or "").strip()
        macro_name = str(meta.get("macro_name") or "").strip()
        draft_id = _new_macro_execution_draft(
            context,
            {
                "macro_id": macro_id,
                "macro_name": macro_name,
            },
        )
        payload["buttons"] = [
            [
                {"text": "✅ Confirm macro execute", "callback_data": f"macro:confirm:{draft_id}"},
            ],
            [
                {"text": "❌ Cancel", "callback_data": f"macro:cancel:{draft_id}"},
            ],
            [
                {"text": "🏠 Main", "callback_data": "home"},
            ],
        ]
        log.info("macro preview allowed user=%s macro_id=%s macro_name=%s", user_id, macro_id, macro_name)
    else:
        log.info("macro preview blocked user=%s details=%s", user_id, meta)
    await show_payload(update, payload, edit=False)


async def cmd_ptz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    if not USER_MANAGER.is_admin(user_id):
        await update.effective_chat.send_message(
            text=(
                "⛔️ PTZ control is restricted to configured Telegram admins.\n"
                "This guarded preset flow is not available to operator accounts."
            )
        )
        return

    tz_name = _get_user_timezone(user_id, context)
    extra = [
        *_ptz_policy_api_args(user_id),
        *(context.args or []),
    ]
    try:
        payload = _run_ui_payload_or_error("ptz-control", *extra, tz=tz_name, section="ptz")
    except Exception as ex:
        await update.effective_chat.send_message(text=f"⚠️ PTZ preview failed.\n{ex}")
        return

    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("allowed"):
        camera_access_point = str(meta.get("camera_access_point") if meta.get("camera_access_point") is not None else "").strip()
        camera_name = str(meta.get("camera_name") if meta.get("camera_name") is not None else "").strip()
        preset_label = str(meta.get("preset_label") if meta.get("preset_label") is not None else "").strip()
        preset_position = str(meta.get("preset_position") if meta.get("preset_position") is not None else "").strip()
        speed = str(meta.get("speed") if meta.get("speed") is not None else "").strip()
        draft_id = _new_ptz_control_draft(
            context,
            {
                "camera_access_point": camera_access_point,
                "camera_name": camera_name,
                "preset_label": preset_label,
                "preset_position": preset_position,
                "speed": speed,
            },
        )
        payload["buttons"] = [
            [
                {"text": "✅ Confirm PTZ preset", "callback_data": f"ptz:confirm:{draft_id}"},
            ],
            [
                {"text": "❌ Cancel", "callback_data": f"ptz:cancel:{draft_id}"},
            ],
            [
                {"text": "🏠 Main", "callback_data": "home"},
            ],
        ]
        log.info(
            "ptz preview allowed user=%s camera_ap=%s preset=%s position=%s",
            user_id,
            camera_access_point,
            preset_label,
            preset_position,
        )
    else:
        log.info("ptz preview blocked user=%s details=%s", user_id, meta)
    await show_payload(update, payload, edit=False)


async def cmd_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    tz_name = _get_user_timezone(user_id, context)
    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "srv:menu",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="server",
    )
    await show_payload(update, payload, edit=False)


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    if not USER_MANAGER.is_admin(user_id):
        await update.effective_chat.send_message(
            text=(
                "⛔️ Admin view is restricted to configured Telegram admins.\n"
                "This read-only visibility surface is not available to operator accounts."
            )
        )
        return
    tz_name = _get_user_timezone(user_id, context)
    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "adm:menu",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="admin",
    )
    await show_payload(update, payload, edit=False)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    tz_name = _get_user_timezone(user_id, context)
    health = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "sys:health",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="server",
    )
    health_lines = [x.strip() for x in (health.get("text") or "").splitlines() if x.strip()]
    day, counters = RUNTIME_COUNTERS.snapshot()
    sub_stats = SUBSCRIPTIONS.stats(user_id)

    lines = [
        "📊 Runtime stats",
        f"UTC day: {day}",
        f"Daily counters: {'on' if BOT_CFG.enable_daily_counters else 'off'}",
        "",
        "Throttling:",
        f"- max sends/window: {BOT_CFG.send_rate_limit_count} / {BOT_CFG.send_rate_limit_period_sec}s",
        f"- duplicate window: {BOT_CFG.duplicate_window_sec}s",
        "",
        "Subscription limits:",
        f"- max subscriptions/user: {BOT_CFG.max_subscriptions_per_user}",
        f"- max events/day: {BOT_CFG.max_events_per_day}",
        f"- min interval: {BOT_CFG.min_notification_interval_sec}s",
        f"- poll interval: {BOT_CFG.subscription_poll_interval_sec}s",
        f"- live path: DomainNotifier.PullEvents",
        f"- notifier timeout: {BOT_CFG.subscription_notifier_timeout_sec}s",
        "- fallback transport: disabled",
        "",
        "Your subscription stats:",
        f"- active: {sub_stats['active_subscriptions']}/{sub_stats['max_subscriptions']}",
        f"- events today: {sub_stats['events_today']}/{sub_stats['max_events_per_day']}",
        f"- events remaining: {sub_stats['events_remaining']}",
        "",
        "Health:",
    ]
    if health_lines:
        lines.extend([f"- {line}" for line in health_lines[:3]])
    else:
        lines.append("- no health details")

    if BOT_CFG.enable_daily_counters:
        lines.extend(["", "Counters:"])
        if counters:
            for key in sorted(counters.keys()):
                lines.append(f"- {key}: {counters[key]}")
        else:
            lines.append("- empty")
    await update.effective_chat.send_message(text="\n".join(lines))


async def cmd_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    rows = SUBSCRIPTIONS.list_subscriptions(user_id)
    if not rows:
        await update.effective_chat.send_message(text="🔕 No active subscriptions. Use /subscribe or create from feed callbacks.")
        return

    lines = ["🔔 Active subscriptions", ""]
    for rec in rows:
        lines.append(f"#{rec.subscription_id} · {rec.source} · states: {', '.join(rec.states)}")
        lines.append(f"  {rec.summary}")
        lines.append(f"  sent: {rec.sent_events} · last: {rec.last_event_id or '-'}")
    lines.extend(["", "Use /stop <id> to stop one, or /stop to stop all."])
    await update.effective_chat.send_message(text="\n".join(lines))


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return

    user_id = update.effective_user.id
    args = context.args or []
    if args and args[0].strip().lower() not in {"all", "*"}:
        sub_id = args[0].strip()
        removed = await SUBSCRIPTIONS.stop_subscription(user_id, sub_id)
        if removed:
            text = f"⏹ Subscription #{sub_id} stopped."
        else:
            text = f"⚠️ Subscription #{sub_id} not found."
        await update.effective_chat.send_message(text=text)
        return

    removed_count = await SUBSCRIPTIONS.stop_all(user_id)
    if removed_count:
        text = f"⏹ Stopped {removed_count} subscription(s)."
    else:
        text = "⏹ No active subscriptions."
    await update.effective_chat.send_message(text=text)


async def cmd_counterwatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    await update.effective_chat.send_message(
        text=(
            "ℹ️ Counter watch now lives inside /subscribe.\n"
            "Choose detector(s), and if their type is NeuroCounter or VaCrowdDetector, "
            "the bot will start counter-style live updating messages automatically."
        )
    )


async def cmd_counterstop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    stopped = await COUNTER_WATCH.stop(update.effective_user.id)
    await update.effective_chat.send_message(text="⏹ Counter watch stopped." if stopped else "⏹ No active counter watch.")


async def cmd_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    tz_name = _get_user_timezone(user_id, context)
    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "al:feed:0",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="alerts",
    )
    await show_payload(update, payload, edit=False)


async def cmd_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    user_id = update.effective_user.id
    tz_name = _get_user_timezone(user_id, context)
    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        "cam:list:0",
        *_ui_admin_args(user_id),
        tz=tz_name,
        section="cameras",
    )
    await show_payload(update, payload, edit=False)


async def cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    chat = update.effective_chat
    try:
        detectors = fetch_detectors()
    except Exception as ex:
        await chat.send_message(text=f"❌ Failed to load detectors: {ex}")
        return
    if not detectors:
        await chat.send_message(text="⚠️ No detectors available.")
        return

    if not SUBSCRIPTIONS.can_add_subscription(update.effective_user.id):
        await chat.send_message(
            text=(
                f"⚠️ Max subscriptions reached ({BOT_CFG.max_subscriptions_per_user}). "
                "Use /subscriptions and /stop first."
            )
        )
        return

    context.user_data["all_detectors"] = detectors
    context.user_data["selected_detectors"] = []
    context.user_data["detectors_current_page"] = 0
    keyboard = get_detector_keyboard(0, detectors, [])
    await chat.send_message(
        text=(
            "📋 Select detectors to monitor:\n\n"
            "Click on a detector to select/deselect it. Use navigation buttons to browse."
        ),
        reply_markup=keyboard,
    )


async def _handle_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> bool:
    q = update.callback_query
    if not q:
        return False
    log.debug("subscription callback user=%s data=%s", update.effective_user.id if update.effective_user else None, data)

    detectors = context.user_data.get("all_detectors") or []
    selected = context.user_data.get("selected_detectors") or []
    page = int(context.user_data.get("detectors_current_page") or 0)

    if data == "sub:det:list":
        try:
            detectors = fetch_detectors()
        except Exception as ex:
            await q.edit_message_text(text=f"❌ Failed to load detectors: {ex}")
            return True
        context.user_data["all_detectors"] = detectors
        context.user_data["selected_detectors"] = []
        context.user_data["detectors_current_page"] = 0
        await q.edit_message_text(
            text=(
                "📋 Select detectors to monitor:\n\n"
                "Click on a detector to select/deselect it. Use navigation buttons to browse."
            ),
            reply_markup=get_detector_keyboard(0, detectors, []),
        )
        return True

    if data.startswith("page:"):
        if not detectors:
            return True
        page = int(data.split(":", 1)[1])
        context.user_data["detectors_current_page"] = page
        await q.edit_message_text(
            text=f"📋 Select detectors to monitor:\n\nShowing page {page + 1} of {(len(detectors) + 4) // 5}",
            reply_markup=get_detector_keyboard(page, detectors, selected),
        )
        return True

    if data.startswith("detector:"):
        if not detectors:
            return True
        detector_id = data.split(":", 1)[1]
        if detector_id in selected:
            selected.remove(detector_id)
        else:
            selected.append(detector_id)
        context.user_data["selected_detectors"] = selected
        await q.edit_message_text(
            text=f"📋 Select detectors to monitor:\n\nShowing page {page + 1} of {(len(detectors) + 4) // 5}",
            reply_markup=get_detector_keyboard(page, detectors, selected),
        )
        return True

    if data == "confirm_detectors":
        selected_set = set(selected)
        selected_rows = [x for x in detectors if x["access_point"] in selected_set]
        if not selected_rows:
            await q.answer("Select at least one detector", show_alert=True)
            return True
        detector_types = [str(x.get("detector_type") or "") for x in selected_rows]
        detector_aps = [str(x.get("access_point") or "") for x in selected_rows]
        camera_aps = [str(x.get("camera_access_point") or "") for x in selected_rows]
        summary = f"detectors: {len(selected_rows)}"
        draft = {
            "source": "detectors",
            "filters": {
                "event_type": "ET_DetectorEvent",
                "detector_names": detector_names,
                "detector_access_points": detector_aps,
                "camera_access_points": camera_aps,
                "include": _build_detector_notifier_include(selected_rows),
            },
            "detector_rows": selected_rows,
            "summary": summary,
        }
        await _start_draft_state_selection(q, context, draft)
        return True

    if data == "all_alerts":
        draft = {
            "source": "all_alerts",
            "filters": {
                "event_type": "ET_Alert",
                "include": _build_notifier_include(event_type="ET_Alert"),
            },
            "summary": "all alerts",
        }
        await _start_draft_state_selection(q, context, draft)
        return True

    if data.startswith("sub:new:ev:"):
        raw = data.split(":", 3)[3] if len(data.split(":", 3)) == 4 else "all"
        categories = [x for x in raw.split(",") if x] if raw != "all" else ["lpr", "motion", "alert"]
        labels = ", ".join(categories)
        draft = {
            "source": "events_filter",
            "filters": {
                "event_type": "ET_DetectorEvent",
                "categories": categories,
                "include": _build_notifier_include(event_type="ET_DetectorEvent"),
            },
            "summary": f"event categories: {labels}",
        }
        await _start_draft_state_selection(q, context, draft)
        return True

    if data.startswith("sub:new:cam:"):
        parts = data.split(":")
        idx = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else -1
        cams = fetch_camera_rows()
        if idx < 0 or idx >= len(cams):
            await q.answer("Camera not found", show_alert=True)
            return True
        cam = cams[idx]
        camera_access_point = str(cam.get("access_point") or "").strip()
        draft = {
            "source": "camera_filter",
            "filters": {
                "event_type": "ET_DetectorEvent",
                "subject": camera_access_point,
                "camera_access_points": [camera_access_point],
                "include": _build_notifier_include(event_type="ET_DetectorEvent", subjects=[camera_access_point]),
            },
            "summary": f"camera: {cam.get('name')}",
        }
        await _start_draft_state_selection(q, context, draft)
        return True

    if data.startswith("sub:new:alert"):
        draft = {
            "source": "alerts_feed",
            "filters": {
                "event_type": "ET_Alert",
                "include": _build_notifier_include(event_type="ET_Alert"),
            },
            "summary": "alerts feed",
        }
        await _start_draft_state_selection(q, context, draft)
        return True

    if data.startswith("sub:state:"):
        parts = data.split(":")
        if len(parts) < 4:
            return True
        draft_id = parts[2]
        choice = parts[3]
        draft = _get_subscription_draft(context, draft_id)
        if not draft:
            await q.answer("Draft expired. Start again.", show_alert=True)
            return True
        states = _states_from_choice(choice)
        draft["states"] = states
        lines = [
            "✅ Confirm subscription",
            "",
            f"Source: {draft.get('source')}",
            f"Filter: {draft.get('summary')}",
            f"States: {', '.join(states)}",
            "",
            "Press confirm to start async notifications.",
        ]
        await q.edit_message_text(text="\n".join(lines), reply_markup=_confirm_keyboard(draft_id))
        return True

    if data.startswith("sub:confirm:"):
        draft_id = data.split(":", 2)[2]
        draft = _get_subscription_draft(context, draft_id)
        if not draft:
            await q.answer("Draft expired. Start again.", show_alert=True)
            return True
        states = draft.get("states") or ["BEGAN", "HAPPENED", "ENDED"]
        user_id = update.effective_user.id
        filters = draft.get("filters") or {}
        detector_rows = draft.get("detector_rows") or []
        counter_rows = [row for row in detector_rows if _is_counter_detector_row(row)]
        regular_rows = [row for row in detector_rows if not _is_counter_detector_row(row)]
        created: list[SubscriptionRecord] = []

        async def _create_counter_subscription(row: dict[str, Any]) -> tuple[bool, str, SubscriptionRecord | None]:
            summary = f"counter: {row.get('name') or 'Detector'}"
            counter_filters = {
                "event_type": "ET_DetectorEvent",
                "detector_names": [str(row.get("name") or "")],
                "detector_access_points": [str(row.get("access_point") or "")],
                "camera_access_points": [str(row.get("camera_access_point") or "")],
                "include": _build_detector_notifier_include([row]),
                "counter_mode": True,
            }
            ok, reason, rec = await SUBSCRIPTIONS.create_subscription(
                user_id=user_id,
                bot=context.bot,
                source="counter_detector",
                filters=counter_filters,
                states=states,
                summary=summary,
            )
            if ok and rec:
                placeholder = await update.effective_chat.send_message(
                    text="\n".join([
                        f"📟 <b>Crowd counter · Sub #{rec.subscription_id}</b>",
                        f"📷 <b>{row.get('camera_name') or '-'}</b>",
                        f"🧠 <b>{row.get('name') or '-'}</b>",
                        "🔢 <b>…</b>",
                        "🕒 Event: <code>-</code>",
                        f"🔄 Updated: <code>starting every {COUNTER_WATCH_POLL_SEC}s</code>",
                    ]),
                    parse_mode='HTML',
                )
                await COUNTER_WATCH.start_subscription(rec, context.bot, row, message_id=int(placeholder.message_id))
            return ok, reason, rec

        if regular_rows:
            ok, reason, rec = await SUBSCRIPTIONS.create_subscription(
                user_id=user_id,
                bot=context.bot,
                source=draft.get("source") or "manual",
                filters=filters,
                states=states,
                summary=draft.get("summary") or "",
            )
            if not ok or not rec:
                _drop_subscription_draft(context, draft_id)
                if reason == "max_subscriptions":
                    await q.edit_message_text(
                        text=(
                            f"⚠️ Max subscriptions reached ({BOT_CFG.max_subscriptions_per_user}).\n"
                            "Use /subscriptions and /stop before creating a new one."
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
                    )
                else:
                    await q.edit_message_text(
                        text="⚠️ Failed to create subscription.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
                    )
                return True
            created.append(rec)

        for row in counter_rows:
            ok, reason, rec = await _create_counter_subscription(row)
            if not ok or not rec:
                _drop_subscription_draft(context, draft_id)
                if reason == "max_subscriptions":
                    await q.edit_message_text(
                        text=(
                            f"⚠️ Max subscriptions reached ({BOT_CFG.max_subscriptions_per_user}).\n"
                            "Use /subscriptions and /stop before creating a new one."
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
                    )
                else:
                    await q.edit_message_text(
                        text="⚠️ Failed to create counter subscription.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
                    )
                return True
            created.append(rec)

        _drop_subscription_draft(context, draft_id)
        if not created:
            await q.edit_message_text(
                text="⚠️ Failed to create subscription.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
            )
            return True

        stats = SUBSCRIPTIONS.stats(user_id)
        started_ids = ", ".join(f"#{rec.subscription_id}" for rec in created)
        await q.edit_message_text(
            text=(
                "✅ Subscription started.\n\n"
                f"IDs: {started_ids}\n"
                f"Filter: {draft.get('summary') or ''}\n"
                f"States: {', '.join(states)}\n"
                f"Active: {stats['active_subscriptions']}/{stats['max_subscriptions']}\n"
                f"Daily cap left: {stats['events_remaining']}"
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        return True

    if data == "cancel":
        await q.edit_message_text(
            text="❌ Subscription action cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        return True

    return False


async def _handle_face_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> bool:
    callback = parse_face_search_wizard_callback(data)
    if not callback:
        return False

    q = update.callback_query
    if not q:
        return False

    await q.answer()
    wizard = _get_face_search_wizard(context, callback.draft_id)
    if not wizard:
        await q.edit_message_text(
            text="⚠️ Face search draft expired. Upload the photo again.",
            reply_markup=_face_search_home_markup(),
        )
        return True

    if callback.action == "cancel":
        _drop_face_search_wizard(context, callback.draft_id)
        await q.edit_message_text(
            text="🙂 Face search canceled.",
            reply_markup=_face_search_home_markup(),
        )
        return True

    if callback.action == "back":
        wizard.pop("accuracy_percent", None)
        await q.edit_message_text(
            text=_face_search_threshold_prompt_text(list(wizard.get("terms") or [])),
            reply_markup=kb(build_face_search_wizard_threshold_buttons(callback.draft_id)),
        )
        return True

    if callback.action == "acc":
        try:
            accuracy_percent = int(callback.value)
        except ValueError:
            await q.edit_message_text(
                text="⚠️ Invalid similarity preset. Choose again.",
                reply_markup=kb(build_face_search_wizard_threshold_buttons(callback.draft_id)),
            )
            return True
        wizard["accuracy_percent"] = accuracy_percent
        await q.edit_message_text(
            text=_face_search_period_prompt_text(list(wizard.get("terms") or []), accuracy_percent),
            reply_markup=kb(build_face_search_wizard_period_buttons(callback.draft_id)),
        )
        return True

    if callback.action == "last":
        try:
            period_seconds = int(callback.value)
        except ValueError:
            await q.edit_message_text(
                text="⚠️ Invalid period preset. Choose again.",
                reply_markup=kb(build_face_search_wizard_period_buttons(callback.draft_id)),
            )
            return True

        accuracy_percent = int(wizard.get("accuracy_percent") or 0)
        if accuracy_percent <= 0:
            await q.edit_message_text(
                text=_face_search_threshold_prompt_text(list(wizard.get("terms") or [])),
                reply_markup=kb(build_face_search_wizard_threshold_buttons(callback.draft_id)),
            )
            return True

        terms = build_face_search_wizard_terms(
            wizard.get("terms") or [],
            accuracy_percent=accuracy_percent,
            period_seconds=period_seconds,
        )
        reference_file_id = str(wizard.get("file_id") or "")
        reference_suffix = str(wizard.get("suffix") or ".jpg")
        _drop_face_search_wizard(context, callback.draft_id)
        await q.edit_message_text(text=_face_search_running_text(accuracy_percent, period_seconds))
        await _run_face_search(
            update,
            context,
            terms=terms,
            reference_file_id=reference_file_id,
            reference_suffix=reference_suffix,
            edit=True,
        )
        return True

    return True


async def _handle_macro_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> bool:
    if not data.startswith("macro:"):
        return False
    q = update.callback_query
    user_id = update.effective_user.id

    if data.startswith("macro:cancel:"):
        draft_id = data.split(":", 2)[2]
        _drop_macro_execution_draft(context, draft_id)
        await q.answer()
        await q.edit_message_text(
            text="❌ Macro execution cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        log.info("macro execution cancelled user=%s draft=%s", user_id, draft_id)
        return True

    if not data.startswith("macro:confirm:"):
        return False

    if not USER_MANAGER.is_admin(user_id):
        _drop_macro_execution_draft(context, data.split(":", 2)[2])
        await q.answer("Admin access required", show_alert=True)
        return True

    draft_id = data.split(":", 2)[2]
    draft = _get_macro_execution_draft(context, draft_id)
    if not draft:
        await q.answer("Draft expired. Run /macro again.", show_alert=True)
        return True

    macro_id = str(draft.get("macro_id") or "").strip()
    macro_name = str(draft.get("macro_name") or "").strip()
    _drop_macro_execution_draft(context, draft_id)
    await q.answer()

    try:
        result = run_api("macro-execute", "--macro-id", macro_id, *_macro_policy_api_args(user_id))
    except Exception as ex:
        log.exception("macro execution failed user=%s macro_id=%s err=%s", user_id, macro_id, ex)
        await q.edit_message_text(
            text=f"⚠️ Macro execution failed.\n{ex}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        return True

    if not isinstance(result, dict):
        await q.edit_message_text(
            text="⚠️ Macro execution returned an unexpected payload.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        return True

    execution = result.get("execution") if isinstance(result.get("execution"), dict) else {}
    log.info(
        "macro execution result user=%s macro_id=%s macro_name=%s attempted=%s ok=%s",
        user_id,
        macro_id,
        macro_name,
        execution.get("attempted"),
        execution.get("ok"),
    )
    await q.edit_message_text(
        text=_macro_execution_result_text(result),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
    )
    return True


async def _handle_ptz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> bool:
    if not data.startswith("ptz:"):
        return False
    q = update.callback_query
    user_id = update.effective_user.id

    if data.startswith("ptz:cancel:"):
        draft_id = data.split(":", 2)[2]
        _drop_ptz_control_draft(context, draft_id)
        await q.answer()
        await q.edit_message_text(
            text="❌ PTZ control cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        log.info("ptz execution cancelled user=%s draft=%s", user_id, draft_id)
        return True

    if not data.startswith("ptz:confirm:"):
        return False

    if not USER_MANAGER.is_admin(user_id):
        _drop_ptz_control_draft(context, data.split(":", 2)[2])
        await q.answer("Admin access required", show_alert=True)
        return True

    draft_id = data.split(":", 2)[2]
    draft = _get_ptz_control_draft(context, draft_id)
    if not draft:
        await q.answer("Draft expired. Run /ptz again.", show_alert=True)
        return True

    camera_access_point = str(draft.get("camera_access_point") or "").strip()
    camera_name = str(draft.get("camera_name") or "").strip()
    preset_label = str(draft.get("preset_label") or "").strip()
    preset_position = str(draft.get("preset_position") or "").strip()
    speed = str(draft.get("speed") or "").strip()
    _drop_ptz_control_draft(context, draft_id)
    await q.answer()

    try:
        result = run_api(
            "ptz-execute",
            "--camera-ap", camera_access_point,
            "--position", preset_position,
            "--speed", speed or "5",
            *_ptz_policy_api_args(user_id),
        )
    except Exception as ex:
        log.exception(
            "ptz execution failed user=%s camera_ap=%s preset=%s position=%s err=%s",
            user_id,
            camera_access_point,
            preset_label,
            preset_position,
            ex,
        )
        await q.edit_message_text(
            text=f"⚠️ PTZ control failed.\n{ex}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        return True

    if not isinstance(result, dict):
        await q.edit_message_text(
            text="⚠️ PTZ control returned an unexpected payload.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
        )
        return True

    execution = result.get("execution") if isinstance(result.get("execution"), dict) else {}
    log.info(
        "ptz execution result user=%s camera_ap=%s camera=%s preset=%s position=%s attempted=%s ok=%s",
        user_id,
        camera_access_point,
        camera_name,
        preset_label,
        preset_position,
        execution.get("attempted"),
        execution.get("ok"),
    )
    await q.edit_message_text(
        text=_ptz_control_result_text(result),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main", callback_data="home")]]),
    )
    return True


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _guard(update):
        return
    q = update.callback_query
    RUNTIME_COUNTERS.incr("callbacks_total")
    user_tz = _get_user_timezone(update.effective_user.id, context)
    is_live_start = bool(q.data.startswith("cam:live:start:"))
    is_live_stop = (q.data == "cam:live:stop")

    if is_live_start:
        parts = q.data.split(":")
        idx = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else -1
        if idx < 0:
            await q.answer("Invalid camera", show_alert=True)
            return
        active = LIVE_SESSIONS.get(update.effective_user.id)
        if active and active.camera_idx == idx:
            await q.answer("Live mode is already running for this camera")
            return
        try:
            payload = await asyncio.to_thread(_build_live_snapshot_payload, idx)
            media_path = str(payload.get("media_path") or "")
            if not media_path:
                raise RuntimeError("camera snapshot not available")
            prepared_media_path, overlay_note = await asyncio.to_thread(
                _prepare_live_overlay_media, media_path, 1
            )
            caption = _live_caption(payload.get("text", "📸 Live snapshot"), "ON", overlay_note=overlay_note)
            rec = LiveSessionRecord(
                user_id=update.effective_user.id,
                camera_idx=idx,
                chat_id=q.message.chat_id if q.message else update.effective_chat.id,
                message_id=q.message.message_id if q.message else 0,
            )
            try:
                await _upsert_live_photo(context.bot, rec, caption, prepared_media_path)
            finally:
                _cleanup_live_overlay_media(media_path, prepared_media_path, remove_original=True)
            replaced = await LIVE_SESSIONS.start(rec)
            RUNTIME_COUNTERS.incr("live_sessions_start_requests")
            if replaced:
                RUNTIME_COUNTERS.incr("live_sessions_replaced_on_start")
            start_msg = "Live mode switched to selected camera" if replaced else "Live mode started"
            await q.answer(start_msg)
        except Exception as ex:
            log.exception("live start failed user=%s data=%s err=%s", update.effective_user.id, q.data, ex)
            RUNTIME_COUNTERS.incr("live_session_start_errors")
            await q.answer("Failed to start live mode", show_alert=True)
        return

    if is_live_stop:
        rec = LIVE_SESSIONS.get(update.effective_user.id)
        if not rec:
            await q.answer("Live mode is not running")
            return
        await LIVE_SESSIONS.stop(update.effective_user.id, reason="manual")
        RUNTIME_COUNTERS.incr("live_session_stop_requests")
        try:
            await _safe_edit_live_text(
                context.bot,
                rec,
                _live_caption("⏹ Live mode stopped.", "STOPPED"),
                rec.camera_idx,
            )
        except Exception:
            pass
        await q.answer("Live mode stopped")
        return

    if await _handle_ptz_callback(update, context, q.data):
        RUNTIME_COUNTERS.incr("ptz_callbacks")
        return

    if await _handle_macro_callback(update, context, q.data):
        RUNTIME_COUNTERS.incr("macro_callbacks")
        return

    if q.data.startswith("adm:") and not USER_MANAGER.is_admin(update.effective_user.id):
        await q.answer("Admin access required", show_alert=True)
        return

    if await _handle_face_search_callback(update, context, q.data):
        RUNTIME_COUNTERS.incr("face_search_callbacks")
        return

    await q.answer()
    user_id = update.effective_user.id

    if q.data == "home":
        payload = _fallback_home_payload(mode=_get_ui_mode(context))
        await show_payload(update, payload, edit=True)
        return

    if q.data.startswith("mode:"):
        mode = q.data.split(":", 1)[1]
        _set_ui_mode(context, mode)
        payload = _fallback_home_payload(mode=_get_ui_mode(context))
        await show_payload(update, payload, edit=True)
        return

    if q.data == "home:help":
        await cmd_help(update, context)
        return

    if await _handle_subscription_callback(update, context, q.data):
        RUNTIME_COUNTERS.incr("subscription_callbacks")
        return

    if _is_live_subscription_alert_callback(q.data, q.message):
        payload = _run_ui_payload_or_error(
            "callback",
            "--seconds",
            "1800",
            "--data",
            q.data,
            *_ui_admin_args(user_id),
            tz=user_tz,
            section=_ui_error_section_from_callback(q.data),
        )
        text = payload.get("text", "")
        buttons = list(payload.get("buttons") or [])
        buttons.extend(_extract_live_alert_clip_rows(q.message))
        markup = kb(buttons)
        try:
            if getattr(q.message, "photo", None):
                await q.edit_message_caption(caption=text, reply_markup=markup)
            else:
                await q.edit_message_text(text=text, reply_markup=markup)
            RUNTIME_COUNTERS.incr("messages_edited")
        except Exception as ex:
            log.exception("live alert inline update failed data=%s err=%s", q.data, ex)
            await q.answer("Failed to update card", show_alert=True)
        return
    # UI-only subscription controls (no slash needed)

    if q.data.startswith("sub:clip:"):
        parts = q.data.split(":", 3)
        if len(parts) < 4:
            await q.answer("Invalid request", show_alert=True)
            return
        event_kind, event_id = parts[2], parts[3]
        raw = SUBSCRIPTIONS._find_raw_event(event_id, event_type=event_kind)
        if not raw:
            await q.answer("Event not found in history window", show_alert=True)
            return
        ej = Path(f"/tmp/sub_clip_{event_id}.json")
        ej.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        out = Path(f"/tmp/sub_clip_{event_id}.mp4")
        try:
            clip_path = run_api("clip-from-event", "--event-json", str(ej), "--out", str(out), "--pre", "15", "--post", "15")
            p = Path(str(clip_path))
            if not p.exists():
                raise RuntimeError("clip not created")
            with p.open("rb") as fh:
                await update.effective_chat.send_video(video=fh, caption=f"🎬 Clip -15/+15 sec\nEvent: {event_id}")
            await q.answer("Clip sent")
        except Exception as ex:
            log.exception("sub clip failed event=%s err=%s", event_id, ex)
            await q.answer("Failed to build clip", show_alert=True)
        return

    if q.data == "sub:list":
        rows = SUBSCRIPTIONS.list_subscriptions(user_id)
        if not rows:
            await q.edit_message_text(
                text="🔕 No active subscriptions. Use Subscribe to create one.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔔 Create", callback_data="sub:det:list")],
                    [InlineKeyboardButton("🏠 Home", callback_data="home")],
                ]),
            )
            return
        lines = ["📋 Active subscriptions", ""]
        buttons = []
        for rec in rows[:10]:
            lines.append(f"#{rec.subscription_id} · {rec.source} · {', '.join(rec.states)}")
            buttons.append([InlineKeyboardButton(f"⏹ Stop #{rec.subscription_id}", callback_data=f"sub:stop:{rec.subscription_id}")])
        buttons.append([InlineKeyboardButton("⏹ Stop all", callback_data="sub:stop:all")])
        buttons.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
        await q.edit_message_text(text="\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))
        return

    if q.data == "sub:stats":
        s = SUBSCRIPTIONS.stats(user_id)
        await q.edit_message_text(
            text=(
                "📊 Subscription stats\n\n"
                f"Active: {s['active_subscriptions']}/{s['max_subscriptions']}\n"
                f"Events today: {s['events_today']}/{s['max_events_per_day']}\n"
                f"Remaining: {s['events_remaining']}"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Subscriptions", callback_data="sub:list")],
                [InlineKeyboardButton("🏠 Home", callback_data="home")],
            ]),
        )
        return

    if q.data.startswith("sub:stop:"):
        sid = q.data.split(":", 2)[2]
        if sid == "all":
            n = await SUBSCRIPTIONS.stop_all(user_id)
            txt = f"⏹ Stopped subscriptions: {n}" if n else "⏹ No active subscriptions"
        else:
            ok = await SUBSCRIPTIONS.stop_subscription(user_id, sid)
            txt = f"⏹ Subscribe #{sid} stopped" if ok else f"⚠️ Subscribe #{sid} not found"
        await q.edit_message_text(
            text=txt,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Subscriptions", callback_data="sub:list")],
                [InlineKeyboardButton("🏠 Home", callback_data="home")],
            ]),
        )
        return

    payload = _run_ui_payload_or_error(
        "callback",
        "--seconds",
        "1800",
        "--data",
        q.data,
        *_ui_admin_args(user_id),
        tz=user_tz,
        section=_ui_error_section_from_callback(q.data),
    )
    await show_payload(update, payload, edit=True)


def main():
    global APP_BOT
    if not BOT_CFG.token:
        raise SystemExit("Set TG_BOT_TOKEN env var")
    if not (AXXON_CFG.host and AXXON_CFG.password):
        raise SystemExit("Set AXXON_HOST and AXXON_PASS env vars")

    app = Application.builder().token(BOT_CFG.token).post_init(_register_telegram_commands).build()
    APP_BOT = app.bot
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("tz", cmd_timezone))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("archive", cmd_archive))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("face", cmd_face))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, msg_face_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_text_shortcut))
    app.add_handler(CommandHandler("plate", cmd_plate))
    app.add_handler(CommandHandler("export", cmd_export))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("macro", cmd_macro))
    app.add_handler(CommandHandler("ptz", cmd_ptz))
    app.add_handler(CommandHandler("server", cmd_server))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("subscribe", cmd_subscribe))
    app.add_handler(CommandHandler("subscriptions", cmd_subscriptions))
    app.add_handler(CommandHandler("events", cmd_events))
    app.add_handler(CommandHandler("alerts", cmd_alerts))
    app.add_handler(CommandHandler("cameras", cmd_cameras))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
