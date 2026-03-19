# Telegram Recovery E2E Report

Date: 2026-03-12

## Status

Live Telegram acceptance is blocked in this workspace snapshot.

- `AXXON_HOST` was not set in the environment.
- `AXXON_PASS` was not set in the environment.
- `TG_BOT_TOKEN` was not set in the environment.

The recovery work can be verified locally with unit and smoke tests, but a real Telegram chat session was not executed on March 12, 2026.

## Automated Evidence

- `./scripts/self_check.sh` passed in the recovery worktree after the Telegram smoke suite was added.
- `python3 scripts/full_verification.py` is now environment-driven and records pass/fail per API check and Telegram flow family in `full_verification_results.json`.

## Flows Pending Live Acceptance

- `/start` and `/home`
- alerts feed, alert open, frame, clip, archive, and review actions
- cameras feed, camera open, live snapshot, live monitor, and incident list
- search menu, plate search, and the face-search upload wizard
- archive menu, archive jump, and single-camera export
- subscriptions create, list, and stop
- server and admin cards

## Next Live Run

Run these commands in an environment that has a reachable Axxon target and a Telegram bot token:

```bash
python3 scripts/full_verification.py
./scripts/run_axxon_tg_bot.sh
```

Then complete the manual checklist in `support/docs/REGRESSION_CHECKLIST.md` and update this report with pass/fail evidence per flow.
