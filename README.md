# Axxon Telegram VMS

Telegram-first bot for Axxon One.

It gives you:
- Telegram bot UI for cameras, events, alerts, archive, plate search, face search
- subscriptions and async event delivery
- archive jump / export helpers
- optional MJPEG archive relay links for opening archive frames/streams outside the Axxon UI

## What runs in production

Main processes:
- `scripts/axxon_tg_bot.py` — Telegram bot runtime
- `scripts/archive_stream_relay.py` — small HTTP relay for signed archive MJPEG/HLS links
- `scripts/axxon_web_api.py` — CLI/API adapter used by the bot and support flows

## Requirements

- Python 3.11+
- Axxon One reachable over Web API
- Telegram bot token

Required env:
- `TG_BOT_TOKEN`
- `AXXON_HOST`
- `AXXON_PASS`

Common optional env:
- `AXXON_PORT` — default `80`
- `AXXON_USER` — default `root`
- `AUTHORIZED_USERS`, `ADMIN_USERS`
- `AXXON_RELAY_HOST` — default `0.0.0.0`
- `AXXON_RELAY_PORT` — default `8099`
- `AXXON_RELAY_PUBLIC_BASE` — public base URL for bot-generated relay links, for example:
  - `http://141.227.158.112:8099`
  - or your reverse-proxied HTTPS URL

Important:
- if `AXXON_RELAY_PUBLIC_BASE` is not set correctly, archive relay links may fall back to localhost-style URLs such as `http://127.0.0.1:8099/...`, which are useless outside the server itself

## Quick run

### Manual bot run

```bash
export AXXON_TG_PYTHON_BIN="$(command -v python3.12 || command -v python3.11)"
export TG_BOT_TOKEN='...'
export AXXON_HOST='...'
export AXXON_PASS='...'
export AXXON_USER='root'
export AXXON_PORT='80'
export AXXON_RELAY_PUBLIC_BASE='http://YOUR_PUBLIC_HOST:8099'

./scripts/run_axxon_tg_bot.sh
```

This script:
- creates/reuses `.venv-axxon-tg`
- loads `.env` if present
- ensures bot log/runtime directories exist
- can autostart relay unless disabled

## Systemd services

Service files live in:
- `deploy/systemd/axxon-tg-bot.service`
- `deploy/systemd/axxon-archive-relay.service`

### Bot service

Purpose:
- runs the Telegram bot
- handles subscriptions, menus, callbacks, searches, archive actions

Typical commands:

```bash
sudo systemctl status axxon-tg-bot.service
sudo systemctl restart axxon-tg-bot.service
sudo journalctl -u axxon-tg-bot.service -f
```

### Relay service

Purpose:
- serves signed temporary archive links like `/stream/<token>`
- protects archive access behind short-lived signed tokens
- lets the bot send usable MJPEG/HLS links to Telegram users

Typical commands:

```bash
sudo systemctl status axxon-archive-relay.service
sudo systemctl restart axxon-archive-relay.service
sudo journalctl -u axxon-archive-relay.service -f
```

### Recommended bot + relay setup

Set these in `.env` or systemd environment:

```env
AXXON_RELAY_HOST=0.0.0.0
AXXON_RELAY_PORT=8099
AXXON_RELAY_PUBLIC_BASE=http://YOUR_PUBLIC_HOST:8099
```

Why this matters:
- the relay service listens locally on the server
- the bot generates links for Telegram users
- those links must use the **public address**, not `127.0.0.1`

## What the relay is and why it exists

The relay is a tiny HTTP service that creates short-lived signed URLs for archive playback.

Without it:
- the bot would have to send raw internal archive/media links
- those links may expose internal Axxon details or be unusable externally

With it:
- the bot sends a signed temporary URL
- the relay validates the token
- then it serves MJPEG/HLS archive output for that camera/timestamp

In short:
- **bot** = control plane
- **relay** = temporary archive link transport

## Checks

Run local checks:

```bash
./scripts/self_check.sh
```

What it does:
- syntax/compile checks
- unit tests
- optional integration smoke when Axxon creds are present

## Logs and useful paths

Common paths:
- bot log: `tmp/bot.log`
- relay log when autostarted manually: `tmp/archive_stream_relay.log`
- env file: `.env`

Useful commands:

```bash
tail -f tmp/bot.log
sudo journalctl -u axxon-tg-bot.service -n 100 --no-pager
sudo journalctl -u axxon-archive-relay.service -n 100 --no-pager
```

## Project scope

This is a small practical Telegram/Axxon integration project.

README is intentionally kept short and operational.
More detailed internals should live in:
- tests
- deploy files
- support/docs/ when truly needed
