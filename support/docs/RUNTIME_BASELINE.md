# Runtime Baseline

Updated on March 10, 2026 after the Step 21 time-range search MVP pass.

## Purpose

This document freezes the current bot/runtime surface before any architectural migration work. Future refactors should treat this as the compatibility baseline until a later pass explicitly updates it.

## Active runtime boundary

The production runtime is still flat and script-based:

- `scripts/axxon_tg_bot.py`: Telegram polling runtime, command handlers, callback bridge, subscription engine.
- `scripts/axxon_tg_ui.py`: Telegram payload builder for home, events, alerts, cameras, server, and callback flows.
- `scripts/axxon_web_api.py`: Web API adapter CLI used by UI/runtime helpers.
- `scripts/tg_camera_ui.py`: camera lists, workspace, incidents, snapshots, stream links.
- `scripts/tg_server_ui.py`: server overview, version, statistics payloads.
- `scripts/tg_ui_common.py`: common button, formatting, timestamp, and `run_api` helpers.
- `scripts/live_session_runtime.py`: in-chat live monitor session runtime.
- `scripts/camera_catalog.py`: camera normalization and video-id helpers.
- `scripts/unification_helpers.py`: detector normalization helpers.
- `scripts/config_loader.py`: environment/config loading.
- `scripts/secure_profile_storage.py`: optional encrypted profile persistence.
- `scripts/media_utils.py`: media rectangle/crop helpers.
- `scripts/legacy_compat.py`: local ACL and detector keyboard compatibility layer.

`axxon_telegram_vms/` now provides additive helper seams for models, services, cache, and live-session helpers, but runtime ownership still remains in `scripts/`.

## Current scripts and tests structure

Runtime and support files live in `scripts/`.

Current tests under `tests/` cover:

- command/menu surface
- subscription runtime surface and limits
- UI payload behavior
- alert action mapping
- camera catalog normalization
- config loader bounds/defaults
- media utilities
- server info resilience
- live snapshot transport helpers
- secure profile storage
- Web API parsing and CLI surface
- detector normalization parity

The standing local check entrypoint is `./scripts/self_check.sh`.

## Telegram command surface

Registered bot commands and aliases:

- `/start`
- `/home`
- `/help`
- `/tz`
- `/status`
- `/server`, `/serverinfo`
- `/stats`, `/stat`
- `/stop`, `/cancel`
- `/stopall`
- `/subscribe`
- `/subscriptions`
- `/events`
- `/alerts`
- `/cameras`
- `/search`

## Callback surface families

UI payload callbacks from `scripts/axxon_tg_ui.py`:

- home: `home`
- camera flows: `cam:list:*`, `cam:open:*`, `cam:inc:*`, `cam:snap:*`, `cam:lsnap:*`, `cam:live:start:*`, `cam:live:stop`, `cam:stream:*`
- alerts/events: `al:feed:*`, `al:open:*`, `al:flag:*`, `al:frame:*`, `al:clip30:*`, `ev:feed:*`, `ev:cam:*`, `ev:det:*`, `ev:list:*`, `ev:open:*`, `ev:frame:*`, `ev:clip30:*`
- server and utility menus: `srv:menu`, `srv:domain`, `srv:version`, `srv:stats`, `sys:health`, `sea:menu`, `sea:event`, `sea:plate`, `sea:face`, `sea:help`, `lpr:menu`, `arch:menu`, `arch:jump`, `arch:export`

Bot-owned callback flows from `scripts/axxon_tg_bot.py`:

- detector selection: `sub:det:list`, `page:*`, `detector:*`, `confirm_detectors`, `all_alerts`
- subscription drafts: `sub:new:ev:*`, `sub:new:cam:*`, `sub:new:alert`, `sub:state:*`, `sub:confirm:*`
- subscription management: `sub:list`, `sub:stats`, `sub:stop:*`, `sub:clip:*`
- generic cancel/home navigation: `cancel`, `home`

## Environment variables currently in use

Required for normal bot runtime:

- `TG_BOT_TOKEN`
- `AXXON_HOST`
- `AXXON_PASS`

Primary Axxon transport and logging config:

- `AXXON_USER` (default `root`)
- `AXXON_PORT` (default `80`)
- `AXXON_LOG_FILE` (default `/tmp/axxon_web_api.log`)

Telegram access control and rate limiting:

- `AUTHORIZED_USERS`
- `ADMIN_USERS`
- `TG_SEND_RATE_LIMIT_COUNT`
- `TG_SEND_RATE_LIMIT_PERIOD_SEC`
- `TG_DUPLICATE_WINDOW_SEC`
- `TG_ENABLE_DAILY_COUNTERS`
- `TG_MAX_SUBSCRIPTIONS_PER_USER`
- `TG_MAX_EVENTS_PER_DAY`
- `TG_MIN_NOTIFICATION_INTERVAL_SEC`

Subscription delivery and polling:

- `TG_SUBSCRIPTION_POLL_INTERVAL_SEC`
- `TG_SUBSCRIPTION_POLL_WINDOW_SEC`
- `TG_SUBSCRIPTION_POLL_LIMIT`
- `TG_SUBSCRIPTION_ATTACH_MEDIA`
- `TG_SUBSCRIPTION_USE_NOTIFIER`
- `TG_SUBSCRIPTION_NOTIFIER_TIMEOUT_SEC`
- `TG_SUBSCRIPTION_FALLBACK_POLLING`

Live monitor and bot logging:

- `TG_LIVE_IN_CHAT_INTERVAL_SEC`
- `TG_LIVE_IN_CHAT_MAX_DURATION_SEC`
- `TG_LIVE_OVERLAY`
- `TG_BOT_LOG_LEVEL`
- `TG_BOT_LOG_FILE`

Optional encrypted profile storage:

- `AXXON_SECURE_PROFILE_ENABLED`
- `AXXON_SECURE_PROFILE_MASTER_KEY`
- `AXXON_SECURE_PROFILE_DIR`
- `AXXON_SECURE_PROFILE_NAME`

## Known pain points to protect during refactor

- The runtime is still a flat `scripts/` namespace with direct intra-script imports.
- `scripts/axxon_tg_bot.py` currently mixes Telegram handlers, orchestration, subscription logic, and transport bridging.
- The API path remains subprocess-heavy through `scripts/axxon_tg_ui.py` and `scripts/axxon_web_api.py`.
- Normalized domain models are partial and helper-based rather than first-class package models.
- There is only a narrow bot-side TTL cache for read-heavy camera/detector/server read-only paths; there is still no broader shared cache or background job layer yet.
- Several tests intentionally pin behavior by reading source files as text, so renames/moves must be staged carefully.

## Baseline invariants for the foundation phase

- Existing `scripts/` entrypoints stay valid.
- Existing Telegram commands and callback prefixes stay stable.
- Existing tests remain discoverable via `python3 -m unittest discover -s tests -p 'test_*.py' -v`.
- Any new internal package work must stay additive until a later migration pass.
