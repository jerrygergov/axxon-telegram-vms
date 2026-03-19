# Axxon Telegram VMS

Telegram-first VMS interface on top of Axxon One Web API (`/grpc`, `/archive/media`, `/export`).

## Active runtime architecture

Single production path:
- `scripts/axxon_tg_bot.py` - Telegram polling runtime and subscription engine
- `scripts/axxon_tg_ui.py` - callback/menu payload builder
- `scripts/tg_ui_common.py` - shared Telegram UI formatting and API bridge helpers
- `scripts/tg_camera_ui.py` - camera list/workspace/snapshot/stream-link payloads
- `scripts/tg_server_ui.py` - server overview/version/statistics payloads
- `scripts/axxon_web_api.py` - Axxon Web API adapter CLI
- `scripts/camera_catalog.py` - normalized camera row and live video-id helpers
- `scripts/config_loader.py` - env/config loading
- `scripts/secure_profile_storage.py` - optional encrypted profile persistence
- `scripts/media_utils.py` - merged media rectangle/crop helpers
- `scripts/legacy_compat.py` - local ACL + detector keyboard compatibility layer

No external legacy module imports are required at runtime.

Foundation groundwork added on March 9, 2026:
- `scripts/` remains the only active runtime path.
- `axxon_telegram_vms/` is a dormant internal package skeleton for staged migration work.
- `axxon_telegram_vms.models` holds the accepted normalized-model seams from foundation pass 2.
- normalized event cards now also carry concise operator label fields used by the current home/alerts/events detector-button flows.
- `axxon_telegram_vms.client` now holds additive config parsing, pure transport helpers, and an unused TTL cache utility from foundation pass 3.
- `support/docs/RUNTIME_BASELINE.md` and `support/docs/REGRESSION_CHECKLIST.md` freeze the current baseline and validation path.

## Telegram features (kept)

- Home dashboard, events feed, alerts feed, cameras flow
- Cleaner operator-oriented camera workspace and server overview cards
- Server section (usage/version/statistics)
- Event/alert card open actions
- Frame action and clip action buttons
- Alert review actions (`confirmed`, `suspicious`, `false`) where API permits
- Detector-based and callback-based subscription creation
- Async subscription delivery with dedupe/throttling/day limits
- Optional merged live media (boxed + crop panel) in subscription notifications
- In-chat live camera monitor with direct fresh-frame fetching and low-fps refresh (default 3s cadence)

## Environment

Runtime:
- Python 3.11+ on the shell path, or set `AXXON_TG_PYTHON_BIN` to a compatible interpreter

Required:
- `TG_BOT_TOKEN`
- `AXXON_HOST`
- `AXXON_PASS`

Optional:
- `AXXON_PORT` (default `80`)
- `AXXON_USER` (default `root`)
- `AUTHORIZED_USERS`, `ADMIN_USERS` (comma-separated Telegram user IDs)
- `TG_MAX_SUBSCRIPTIONS_PER_USER`, `TG_MAX_EVENTS_PER_DAY`, `TG_MIN_NOTIFICATION_INTERVAL_SEC`
- `TG_SUBSCRIPTION_POLL_INTERVAL_SEC`, `TG_SUBSCRIPTION_POLL_WINDOW_SEC`, `TG_SUBSCRIPTION_POLL_LIMIT`
- `TG_SUBSCRIPTION_ATTACH_MEDIA`
- `TG_SUBSCRIPTION_USE_NOTIFIER`, `TG_SUBSCRIPTION_NOTIFIER_TIMEOUT_SEC`, `TG_SUBSCRIPTION_FALLBACK_POLLING`
- `TG_LIVE_IN_CHAT_INTERVAL_SEC`, `TG_LIVE_IN_CHAT_MAX_DURATION_SEC`, `TG_LIVE_OVERLAY`
  - default live cadence is `3` seconds per frame update (about `0.33 fps`)
- `AXXON_SECURE_PROFILE_ENABLED`, `AXXON_SECURE_PROFILE_MASTER_KEY`, `AXXON_SECURE_PROFILE_DIR`, `AXXON_SECURE_PROFILE_NAME`

### Persistent per-user settings

If you want user settings such as `/tz Europe/Rome` to survive bot restarts, enable secure profile storage in `.env`:

```env
AXXON_SECURE_PROFILE_ENABLED=1
AXXON_SECURE_PROFILE_MASTER_KEY=<generate-a-private-fernet-key>
AXXON_SECURE_PROFILE_DIR=/home/%username%/axxon-telegram-vms/.secure_profiles
```

Notes:
- `AXXON_SECURE_PROFILE_ENABLED=1` turns on persistent encrypted profile storage.
- `AXXON_SECURE_PROFILE_MASTER_KEY` must be generated once and kept private.
- `AXXON_SECURE_PROFILE_DIR` is the local directory where encrypted per-user settings are stored.
- After this one-time server setup, outside users only need to use normal bot commands like `/tz ...`; they do **not** need VPS access.

## Run

```bash
export AXXON_TG_PYTHON_BIN="$(command -v python3.12 || command -v python3.11)"
export TG_BOT_TOKEN='...'
export AXXON_HOST='...'
export AXXON_PASS='...'
export AXXON_USER='root'
export AXXON_PORT='80'

./scripts/run_axxon_tg_bot.sh
```

## Usage

- Open `/start` and use `🔎 Search` for event, plate, and face-search entry/help flows.
- Upload a Telegram photo for face search, then pick similarity and period presets; use replied `/face key=value` for the typed path.
- Open `/start` and use `🎬 Archive` for archive-jump and single-camera export entry/help flows.
- Open `/start` and use `🖥 Server` from the home menu.
- Telegram admins also get a `🛠 Admin view` shortcut on the home menu for the read-only admin surface.
- Open `📷 Cameras` to reach the camera workspace, then use `▶ Live monitor` for low-fps in-chat refresh.
- Or run `/server` (`/serverinfo`) to open the same card directly.
- Server actions:
  - `Refresh` -> `/info/usage` + `/info/version` + `/statistics/server`
  - `Domain` -> `/info/usage?domain=1`
  - `Version` and `Stats` for focused views

Execution supervision mode for roadmap work: see `support/docs/EXECUTION_MODE.md`.

## Checks

```bash
./scripts/self_check.sh
```

`scripts/self_check.sh` performs:
- syntax/compile validation for `scripts/*.py`
- unit tests (`tests/test_*.py`)
- optional integration smoke callbacks when `AXXON_HOST` + `AXXON_PASS` are available
