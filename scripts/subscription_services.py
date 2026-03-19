#!/usr/bin/env python3
"""Compatibility wrapper around the seeded subscription services seam."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from axxon_telegram_vms.services import (  # noqa: E402
    SubscriptionLedger,
    SubscriptionPolicy,
    SubscriptionRecord,
    SubscriptionStats,
    build_live_poll_filters,
    build_notifier_include_filters,
    filter_cards_for_subscription,
    subscription_query_from_filters,
    subscription_states_match,
)

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
