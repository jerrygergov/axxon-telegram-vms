# REVIEW_CODEX

Date (UTC): 2026-02-28  
Scope: full project revision and cleanup

## Summary

Project runtime is now consolidated to a single active path under `scripts/` with no dependency on the archived legacy tree. Telegram-exposed flows were preserved:
- subscriptions
- live merged media in subscription notifications
- clip button flows
- alert action flows

## Removed files/modules

- `unified/legacy_from_axxon_telegram_bot/` (entire tree)
  - included previously archived `axxon_bot/*` modules
- `support/docs/UNIFICATION_PLAN.md`
- tracked bytecode caches:
  - `scripts/__pycache__/*`
  - `tests/__pycache__/*`

## Runtime cleanup changes

- `scripts/axxon_tg_bot.py`
  - removed `sys.path` injection and legacy imports
  - switched to local `UserManager` and detector keyboard provider
  - renamed internal detector selection keys/functions away from `legacy_*`
- `scripts/legacy_compat.py` (new)
  - local ACL behavior shim
  - local detector keyboard builder
- `scripts/unification_helpers.py`
  - primary name is now `normalize_detector_rows`
  - legacy compatibility alias removed in cleanup follow-up
- `tests/test_unification_parity.py`
  - updated to use active helper name

## Risk assessment

- Low risk:
  - ACL default behavior remains unchanged (empty allowlist still permits all users).
  - Subscription runtime logic, notifier flow, media merge, clip callbacks, and alert actions were not functionally removed.
- Medium risk:
  - detector keyboard/ACL code moved from archived tree to local helper; behavior is intentionally mirrored but should be regression-checked in real Telegram chat.
  - in-memory subscription state remains non-persistent across process restart (existing behavior, not introduced by this cleanup).

## Follow-up recommendations

1. Add behavioral tests for `SubscriptionRuntime` limits/dedupe/stop behavior instead of string-surface tests.
2. Add strict ACL deployment mode (fail startup when no allowlist is configured in production).
3. Add subprocess timeout wrappers around all `run_api`/`run_ui` call paths in async handlers.
4. Add startup dependency checks for `ffmpeg`/`ffprobe` and expose status via `/status`.
