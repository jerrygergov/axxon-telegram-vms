#!/usr/bin/env python3
"""Compatibility wrapper around the seeded live-session jobs seam."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from axxon_telegram_vms.jobs.live_sessions import (  # noqa: E402
    LiveSessionRecord,
    LiveSessionRuntime,
)

__all__ = ["LiveSessionRecord", "LiveSessionRuntime"]
