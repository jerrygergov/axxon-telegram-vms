#!/usr/bin/env python3
"""Compatibility wrapper around the seeded client config seam."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from axxon_telegram_vms.client.config import (  # noqa: E402
    AxxonConfig,
    SecureProfileConfig,
    TelegramBotConfig,
    load_axxon_config,
    load_secure_profile_config,
    load_tg_bot_config,
    parse_csv_text,
    parse_ids,
)

__all__ = [
    "AxxonConfig",
    "SecureProfileConfig",
    "TelegramBotConfig",
    "load_axxon_config",
    "load_secure_profile_config",
    "load_tg_bot_config",
    "parse_csv_text",
    "parse_ids",
]
