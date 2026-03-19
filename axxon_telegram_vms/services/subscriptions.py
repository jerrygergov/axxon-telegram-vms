"""Pure subscription orchestration helpers and state containers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import time
from typing import Any
from collections.abc import Callable

from axxon_telegram_vms.models import EventQuery


def subscription_query_from_filters(
    filters: dict[str, Any] | None,
    *,
    states: list[str] | None = None,
) -> EventQuery:
    return EventQuery.from_legacy_filters(filters or {}, states=states)


def filter_cards_for_subscription(cards: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply the subscription's pure card filters to raw Telegram card rows."""

    query = subscription_query_from_filters(filters)
    return [card for card in cards if isinstance(card, dict) and query.matches_card(card)]


def subscription_states_match(card: dict[str, Any], states: list[str]) -> bool:
    """Keep detector-state matching semantics separate from alert status rows."""

    event_type = str(card.get("event_type") or "")
    if event_type == "ET_Alert":
        return True
    if event_type == "lotsObjects":
        return True
    normalized_states = {str(state or "").upper() for state in states if str(state or "").strip()}
    if not normalized_states or normalized_states == {"BEGAN", "HAPPENED", "ENDED"}:
        return True
    return str(card.get("state") or "").upper() in normalized_states


def build_live_poll_filters(
    filters: dict[str, Any],
    *,
    poll_interval_sec: int,
    poll_limit: int,
) -> dict[str, Any]:
    """Keep fallback polling wide enough to catch slightly delayed live alert cards."""

    live_filters = dict(filters)
    live_filters["seconds"] = max(60, int(poll_interval_sec) * 4)
    live_filters["limit"] = max(100, int(poll_limit))
    return live_filters


def build_notifier_include_filters(filters: dict[str, Any]) -> list[dict[str, str]]:
    """Translate legacy subscription filters into DomainNotifier include entries."""

    query = subscription_query_from_filters(filters)
    event_types = query.taxonomy.event_types or (str(filters.get("event_type") or "ET_DetectorEvent"),)

    explicit_include = (
        filters.get("include")
        or filters.get("live_include_filters")
        or filters.get("notifier_include_filters")
        or ()
    )
    if explicit_include:
        include: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for raw_entry in explicit_include:
            if not isinstance(raw_entry, dict):
                continue
            raw_subject = str(raw_entry.get("subject") or "").strip()
            raw_event_type = str(raw_entry.get("event_type") or "").strip()
            normalized_event_types = (raw_event_type,) if raw_event_type else event_types
            for event_type in normalized_event_types:
                normalized_event_type = str(event_type or "").strip() or "ET_DetectorEvent"
                key = (normalized_event_type, raw_subject)
                if key in seen:
                    continue
                seen.add(key)
                entry = {"event_type": normalized_event_type}
                if raw_subject:
                    entry["subject"] = raw_subject
                include.append(entry)
        if include:
            return include

    subjects: tuple[str, ...] = ()
    live_include_subjects = tuple(
        str(value).strip()
        for value in (filters.get("live_include_subjects") or ())
        if str(value).strip()
    )
    if live_include_subjects:
        subjects = live_include_subjects
    else:
        live_subject_kind = str(filters.get("live_subject_kind") or "").strip().lower()
        if live_subject_kind == "camera" and query.scope.camera_access_points:
            subjects = query.scope.camera_access_points
        elif live_subject_kind == "detector" and query.scope.detector_access_points:
            subjects = query.scope.detector_access_points
        elif query.scope.detector_access_points:
            subjects = query.scope.detector_access_points
        elif query.scope.camera_access_points:
            subjects = query.scope.camera_access_points
        elif query.scope.subjects:
            subjects = query.scope.subjects

    include: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for event_type in event_types:
        normalized_event_type = str(event_type or "").strip() or "ET_DetectorEvent"
        if subjects:
            for subject in subjects:
                normalized_subject = str(subject or "").strip()
                key = (normalized_event_type, normalized_subject)
                if key in seen:
                    continue
                seen.add(key)
                include.append({
                    "event_type": normalized_event_type,
                    "subject": normalized_subject,
                })
            continue
        key = (normalized_event_type, "")
        if key in seen:
            continue
        seen.add(key)
        include.append({"event_type": normalized_event_type})
    return include


@dataclass
class SubscriptionRecord:
    subscription_id: str
    channel_id: str
    user_id: int
    source: str
    filters: dict[str, Any]
    states: list[str]
    summary: str
    created_at: str
    sent_events: int = 0
    last_event_id: str = ""
    last_event_ts: str = ""

    def as_meta(self) -> dict[str, Any]:
        return {
            "id": self.subscription_id,
            "channel_id": self.channel_id,
            "source": self.source,
            "filters": self.filters,
            "states": self.states,
            "summary": self.summary,
            "created_at": self.created_at,
            "sent_events": self.sent_events,
            "last_event_id": self.last_event_id,
            "last_event_ts": self.last_event_ts,
        }


@dataclass(frozen=True)
class SubscriptionPolicy:
    max_subscriptions_per_user: int
    max_events_per_day: int
    duplicate_window_sec: float
    min_notification_interval_sec: float


@dataclass(frozen=True)
class SubscriptionStats:
    active_subscriptions: int
    max_subscriptions: int
    events_today: int
    max_events_per_day: int
    events_remaining: int

    def as_legacy_dict(self) -> dict[str, int]:
        return {
            "active_subscriptions": self.active_subscriptions,
            "max_subscriptions": self.max_subscriptions,
            "events_today": self.events_today,
            "max_events_per_day": self.max_events_per_day,
            "events_remaining": self.events_remaining,
        }


class SubscriptionLedger:
    """Runtime-independent subscription state used by the script runtime adapter."""

    def __init__(
        self,
        policy: SubscriptionPolicy,
        *,
        clock: Callable[[], float] | None = None,
        day_provider: Callable[[], str] | None = None,
    ):
        self._policy = policy
        self._clock = clock or time.monotonic
        self._day_provider = day_provider or (lambda: datetime.now(timezone.utc).date().isoformat())
        self._records: dict[int, dict[str, SubscriptionRecord]] = {}
        self._next_id: dict[int, int] = {}
        self._seen_events: dict[int, dict[str, float]] = {}
        self._day = self._day_provider()
        self._events_today: dict[int, int] = {}
        self._last_notification_ts: dict[int, float] = {}

    @property
    def utc_day(self) -> str:
        self._rollover_day()
        return self._day

    def next_subscription_id(self, user_id: int) -> str:
        value = self._next_id.get(user_id, 1)
        self._next_id[user_id] = value + 1
        return str(value)

    def get(self, user_id: int, subscription_id: str) -> SubscriptionRecord | None:
        self._rollover_day()
        return (self._records.get(user_id) or {}).get(subscription_id)

    def add(self, record: SubscriptionRecord) -> None:
        self._rollover_day()
        self._records.setdefault(record.user_id, {})[record.subscription_id] = record

    def remove(self, user_id: int, subscription_id: str) -> SubscriptionRecord | None:
        self._rollover_day()
        user_records = self._records.get(user_id)
        if not user_records:
            return None
        removed = user_records.pop(subscription_id, None)
        if not user_records:
            self._records.pop(user_id, None)
        return removed

    def list_subscriptions(self, user_id: int) -> list[SubscriptionRecord]:
        self._rollover_day()
        rows = list((self._records.get(user_id) or {}).values())
        return sorted(rows, key=lambda row: int(row.subscription_id))

    def can_add_subscription(self, user_id: int) -> bool:
        self._rollover_day()
        return len(self._records.get(user_id) or {}) < self._policy.max_subscriptions_per_user

    def stats(self, user_id: int) -> SubscriptionStats:
        self._rollover_day()
        active = len(self._records.get(user_id) or {})
        used = self._events_today.get(user_id, 0)
        return SubscriptionStats(
            active_subscriptions=active,
            max_subscriptions=self._policy.max_subscriptions_per_user,
            events_today=used,
            max_events_per_day=self._policy.max_events_per_day,
            events_remaining=max(0, self._policy.max_events_per_day - used),
        )

    def allow_event_delivery(self, user_id: int, event_id: str, now: float | None = None) -> tuple[bool, str]:
        self._rollover_day()
        ts_now = self._clock() if now is None else float(now)
        used = self._events_today.get(user_id, 0)
        if used >= self._policy.max_events_per_day:
            return False, "daily_cap"

        seen = self._seen_events.setdefault(user_id, {})
        to_drop = [
            seen_event_id
            for seen_event_id, seen_ts in seen.items()
            if (ts_now - seen_ts) > self._policy.duplicate_window_sec
        ]
        for seen_event_id in to_drop:
            seen.pop(seen_event_id, None)

        if event_id in seen:
            return False, "duplicate"

        seen[event_id] = ts_now
        self._events_today[user_id] = used + 1
        return True, "ok"

    def notification_wait_seconds(self, user_id: int, now: float | None = None) -> float:
        ts_now = self._clock() if now is None else float(now)
        last = self._last_notification_ts.get(user_id)
        if last is None:
            return 0.0
        return max(0.0, self._policy.min_notification_interval_sec - (ts_now - last))

    def mark_notification_sent(self, user_id: int, now: float | None = None) -> None:
        self._last_notification_ts[user_id] = self._clock() if now is None else float(now)

    def events_today(self, user_id: int) -> int:
        self._rollover_day()
        return self._events_today.get(user_id, 0)

    def _rollover_day(self) -> None:
        day_now = self._day_provider()
        if day_now != self._day:
            self._day = day_now
            self._events_today = {}


__all__ = [
    "SubscriptionLedger",
    "SubscriptionPolicy",
    "SubscriptionRecord",
    "SubscriptionStats",
    "build_live_poll_filters",
    "build_notifier_include_filters",
    "filter_cards_for_subscription",
    "subscription_query_from_filters",
    "subscription_states_match",
]
