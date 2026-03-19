# MIGRATION PARITY

Status date (UTC): 2026-03-10
Runtime baseline: `scripts/*`

## Runtime ownership map

- Telegram command handlers: `scripts/axxon_tg_bot.py`
- UI callback payload builder: `scripts/axxon_tg_ui.py`
- Axxon Web API adapter and media/alert actions: `scripts/axxon_web_api.py`
- ACL + detector keyboard compatibility helpers: `scripts/legacy_compat.py`
- Script-level compatibility wrappers: `scripts/unification_helpers.py`, `scripts/config_loader.py`, `scripts/axxon_web_api.py`
- Additive package seams:
  - pure normalization in `axxon_telegram_vms.models`
  - config/transport helpers plus TTL-backed runtime read-cache helpers in `axxon_telegram_vms.client`
  - pure subscription ledger/filter helpers in `axxon_telegram_vms.services`
  - live-session job primitives in `axxon_telegram_vms.jobs`
  - script wrappers for those seams: `scripts/subscription_services.py`, `scripts/live_session_runtime.py`

## Feature parity checks

- [x] `/start`, `/help`, `/events`, `/alerts`, `/cameras`, `/status`
- [x] `/subscribe` detector selection flow
- [x] `/subscriptions` listing
- [x] `/stop` and `/stop <id>`
- [x] Feed callbacks with back/main navigation
- [x] Event and alert frame/clip buttons
- [x] Alert action buttons (`confirmed`, `suspicious`, `false`)
- [x] Async subscription runtime with notifier pull/fallback polling
- [x] Live media merge path retained for subscription notifications

## Removed legacy artifacts

- Removed: `unified/legacy_from_axxon_telegram_bot/`
- Removed: `support/docs/UNIFICATION_PLAN.md`
- Removed: tracked `__pycache__` content under `scripts/` and `tests/`

## Legacy-to-current mapping

- Legacy `axxon_bot.utils.storage.UserManager`
  - now local: `scripts/legacy_compat.py:UserManager`
- Legacy `axxon_bot.bot.keyboards.get_detector_keyboard`
  - now local: `scripts/legacy_compat.py:get_detector_keyboard`
- Legacy detector row normalization naming
  - active function: `scripts/unification_helpers.py:normalize_detector_rows`
