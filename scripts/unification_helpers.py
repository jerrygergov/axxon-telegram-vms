#!/usr/bin/env python3

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from axxon_telegram_vms.models import normalize_detector_rows_legacy


def normalize_detector_rows(rows) -> list[dict]:
    return normalize_detector_rows_legacy(rows)
