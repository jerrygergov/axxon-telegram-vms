#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
source "$ROOT/scripts/python_runtime.sh"

PYTHON_BIN="$(axxon_resolve_python_bin)"

echo "[1/4] syntax check (no pyc writes)"
"$PYTHON_BIN" - <<'PY'
import pathlib

for root in ("scripts", "axxon_telegram_vms"):
    base = pathlib.Path(root)
    if not base.exists():
        continue
    for path in sorted(base.rglob("*.py")):
        src = path.read_text(encoding="utf-8")
        compile(src, str(path), "exec")
print("syntax_ok")
PY

echo "[2/4] unit tests (includes mocked Telegram flow smoke)"
"$PYTHON_BIN" -m unittest discover -s tests -p 'test_*.py' -v

echo "[3/4] telegram payload smoke (local only)"
if [[ -n "${AXXON_HOST:-}" && -n "${AXXON_PASS:-}" ]]; then
  "$PYTHON_BIN" scripts/axxon_tg_ui.py \
    --host "$AXXON_HOST" \
    --user "${AXXON_USER:-root}" \
    --password "$AXXON_PASS" \
    --port "${AXXON_PORT:-80}" \
    home --seconds 600 --limit 20 >/tmp/axxon_selfcheck_home.json
  "$PYTHON_BIN" scripts/axxon_tg_ui.py \
    --host "$AXXON_HOST" \
    --user "${AXXON_USER:-root}" \
    --password "$AXXON_PASS" \
    --port "${AXXON_PORT:-80}" \
    callback --data 'ev:feed:0' --seconds 1200 >/tmp/axxon_selfcheck_events.json
  "$PYTHON_BIN" scripts/axxon_tg_ui.py \
    --host "$AXXON_HOST" \
    --user "${AXXON_USER:-root}" \
    --password "$AXXON_PASS" \
    --port "${AXXON_PORT:-80}" \
    callback --data 'al:feed:0' --seconds 1200 >/tmp/axxon_selfcheck_alerts.json
  "$PYTHON_BIN" scripts/axxon_tg_ui.py \
    --host "$AXXON_HOST" \
    --user "${AXXON_USER:-root}" \
    --password "$AXXON_PASS" \
    --port "${AXXON_PORT:-80}" \
    callback --data 'cam:list:0' --seconds 1200 >/tmp/axxon_selfcheck_cameras.json
  "$PYTHON_BIN" scripts/axxon_tg_ui.py \
    --host "$AXXON_HOST" \
    --user "${AXXON_USER:-root}" \
    --password "$AXXON_PASS" \
    --port "${AXXON_PORT:-80}" \
    callback --data 'lpr:menu' --seconds 1200 >/tmp/axxon_selfcheck_lpr.json
  "$PYTHON_BIN" scripts/axxon_tg_ui.py \
    --host "$AXXON_HOST" \
    --user "${AXXON_USER:-root}" \
    --password "$AXXON_PASS" \
    --port "${AXXON_PORT:-80}" \
    callback --data 'sys:health' --seconds 1200 >/tmp/axxon_selfcheck_status.json

  EVENT_ID="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
try:
    data = json.loads(Path('/tmp/axxon_selfcheck_events.json').read_text(encoding='utf-8'))
    cards = data.get('cards') or []
    print((cards[0] or {}).get('id') or '')
except Exception:
    print('')
PY
)"
  if [[ -n "$EVENT_ID" ]]; then
    "$PYTHON_BIN" scripts/axxon_tg_ui.py \
      --host "$AXXON_HOST" \
      --user "${AXXON_USER:-root}" \
      --password "$AXXON_PASS" \
      --port "${AXXON_PORT:-80}" \
      callback --data "ev:open:${EVENT_ID}" --seconds 1800 >/tmp/axxon_selfcheck_open.json
    "$PYTHON_BIN" scripts/axxon_tg_ui.py \
      --host "$AXXON_HOST" \
      --user "${AXXON_USER:-root}" \
      --password "$AXXON_PASS" \
      --port "${AXXON_PORT:-80}" \
      callback --data "ev:frame:${EVENT_ID}" --seconds 1800 >/tmp/axxon_selfcheck_frame.json
    "$PYTHON_BIN" scripts/axxon_tg_ui.py \
      --host "$AXXON_HOST" \
      --user "${AXXON_USER:-root}" \
      --password "$AXXON_PASS" \
      --port "${AXXON_PORT:-80}" \
      callback --data "ev:clip30:${EVENT_ID}" --seconds 1800 >/tmp/axxon_selfcheck_clip.json
  else
    echo "No event id in smoke window -> skipping open/frame/clip smoke"
  fi
  echo "smoke outputs: /tmp/axxon_selfcheck_{home,events,alerts,cameras,lpr,status,open,frame,clip}.json"
else
  echo "AXXON_HOST/AXXON_PASS not set -> skipping integration smoke"
fi

echo "[4/4] git cleanliness"
git status --short

echo "SELF_CHECK_OK"
