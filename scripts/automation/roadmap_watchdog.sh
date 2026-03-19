#!/usr/bin/env bash
set -euo pipefail
PROJ='/home/%username%/axxon-telegram-vms'
STATUS_DIR="$PROJ/.automation"
STATUS_FILE="$STATUS_DIR/roadmap-watchdog.status"
LOG_FILE="$STATUS_DIR/roadmap-watchdog.log"
mkdir -p "$STATUS_DIR"
stamp() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }
{
  echo "[$(stamp)] watchdog tick"
  echo "git_status:"
  git -C "$PROJ" status --short || true
  echo
} >> "$LOG_FILE" 2>&1
printf 'last_tick=%s\nmode=active\n' "$(stamp)" > "$STATUS_FILE"
