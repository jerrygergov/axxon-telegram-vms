#!/usr/bin/env bash

AXXON_TG_MIN_PYTHON_LABEL="3.11+"

axxon_python_supports_runtime() {
  local python_bin="${1:-}"
  if [[ -z "$python_bin" ]]; then
    return 1
  fi
  if [[ "$python_bin" == */* ]]; then
    [[ -x "$python_bin" ]] || return 1
  else
    command -v "$python_bin" >/dev/null 2>&1 || return 1
  fi
  "$python_bin" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1
}

axxon_python_version_text() {
  local python_bin="${1:-}"
  "$python_bin" -V 2>&1
}

axxon_resolve_python_bin() {
  local override="${AXXON_TG_PYTHON_BIN:-}"
  local candidate=""
  local python3_path=""
  local python3_dir=""
  local sibling=""

  if [[ -n "$override" ]]; then
    if axxon_python_supports_runtime "$override"; then
      printf '%s\n' "$override"
      return 0
    fi
    printf 'AXXON_TG_PYTHON_BIN=%s is not usable. Axxon Telegram VMS requires Python %s.\n' \
      "$override" "$AXXON_TG_MIN_PYTHON_LABEL" >&2
    return 1
  fi

  if command -v python3 >/dev/null 2>&1; then
    python3_path="$(command -v python3)"
    if axxon_python_supports_runtime "$python3_path"; then
      printf '%s\n' "python3"
      return 0
    fi
    python3_dir="$(dirname "$python3_path")"
    for candidate in python3.11 python3.12 python3.13; do
      sibling="$python3_dir/$candidate"
      if axxon_python_supports_runtime "$sibling"; then
        printf '%s\n' "$candidate"
        return 0
      fi
    done
  else
    for candidate in python3.11 python3.12 python3.13; do
      if axxon_python_supports_runtime "$candidate"; then
        printf '%s\n' "$candidate"
        return 0
      fi
    done
  fi

  printf 'Axxon Telegram VMS requires Python %s. Install a compatible interpreter or set AXXON_TG_PYTHON_BIN.\n' \
    "$AXXON_TG_MIN_PYTHON_LABEL" >&2
  return 1
}
