#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv-axxon-tg"
BOT="$ROOT/scripts/axxon_tg_bot.py"
RELAY="$ROOT/scripts/archive_stream_relay.py"
ENV_FILE="$ROOT/.env"
source "$ROOT/scripts/python_runtime.sh"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

PYTHON_BIN="$(axxon_resolve_python_bin)"

if [[ -n "${AXXON_TG_DRY_RUN:-}" ]]; then
  printf 'PYTHON_BIN=%s\n' "$PYTHON_BIN"
  axxon_python_version_text "$PYTHON_BIN"
  exit 0
fi

if [[ ! -x "$VENV/bin/python" ]] || ! axxon_python_supports_runtime "$VENV/bin/python"; then
  rm -rf "$VENV"
  "$PYTHON_BIN" -m venv "$VENV"
  "$VENV/bin/pip" install python-telegram-bot
fi

: "${TG_BOT_TOKEN:?TG_BOT_TOKEN is required}"
: "${AXXON_HOST:?AXXON_HOST is required}"
: "${AXXON_PASS:?AXXON_PASS is required}"
export AXXON_PORT="${AXXON_PORT:-80}"
export AXXON_USER="${AXXON_USER:-root}"
export AXXON_RELAY_HOST="${AXXON_RELAY_HOST:-0.0.0.0}"
export AXXON_RELAY_PORT="${AXXON_RELAY_PORT:-8099}"
export AXXON_RELAY_PUBLIC_BASE="${AXXON_RELAY_PUBLIC_BASE:-http://127.0.0.1:${AXXON_RELAY_PORT}}"

mkdir -p "$ROOT/tmp" "$ROOT/.runtime"
export TG_BOT_LOG_FILE="${TG_BOT_LOG_FILE:-$ROOT/tmp/bot.log}"

if [[ "${AXXON_RELAY_AUTOSTART:-1}" = "1" ]] && [[ -f "$RELAY" ]]; then
  if ! python3 - <<'PY' >/dev/null 2>&1
import os, socket
host = os.environ.get('AXXON_RELAY_HOST', '0.0.0.0')
port = int(os.environ.get('AXXON_RELAY_PORT', '8099'))
target = '127.0.0.1' if host in ('0.0.0.0', '::') else host
s = socket.socket()
s.settimeout(0.5)
try:
    s.connect((target, port))
    raise SystemExit(0)
except Exception:
    raise SystemExit(1)
finally:
    s.close()
PY
  then
    nohup "$VENV/bin/python" "$RELAY" --serve --host "$AXXON_RELAY_HOST" --port "$AXXON_RELAY_PORT" > "$ROOT/tmp/archive_stream_relay.log" 2>&1 &
  fi
fi

exec "$VENV/bin/python" "$BOT"
