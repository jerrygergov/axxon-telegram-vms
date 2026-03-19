# Regression Checklist

Use this checklist for every foundation or migration pass until the runtime is intentionally moved away from `scripts/`.

## Required local checks

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
./scripts/self_check.sh
```

When live Axxon credentials are available, also run:

```bash
python3 scripts/full_verification.py
```

`scripts/full_verification.py` writes `full_verification_results.json` with pass/fail per API check and Telegram flow family.

`./scripts/self_check.sh` should report:

- syntax validation for `scripts/` and `axxon_telegram_vms/`
- unit test success
- mocked Telegram flow smoke coverage for home, alerts, cameras, search, and archive navigation
- integration smoke either passing or explicitly skipped because `AXXON_HOST` and `AXXON_PASS` are unset
- final `SELF_CHECK_OK`

## API Correctness Checks

Before merging Axxon One request-surface changes, explicitly verify:

- `/grpc` parsing accepts documented `--ngpboundary` multipart packets, SSE `data:` packets, and plain JSON responses.
- multi-camera event search resolves scope to exact camera or detector subjects and issues one `ReadEvents` call per resolved subject; an unmatched scope must not fall back to a broad paged query.
- multi-camera LPR search resolves scope to exact camera or detector subjects and issues one `ReadLprEvents` call per resolved subject; an unmatched scope must not fall back to a broad paged query.
- PTZ preset execution acquires a session, calls `GoPreset`, and attempts `ReleaseSessionId` even when `GoPreset` fails.
- archive frame retrieval uses the documented `POST /export/archive/...` `jpg` flow rather than the undocumented single-frame `/archive/media/...?...threshold=` shape.
- `scripts/full_verification.py` records `PASS`, `FAIL`, or `SKIP` per live request family and reports an explicit env skip when `AXXON_HOST` or `AXXON_PASS` are unset.

## Manual runtime checklist

Verify these user-visible flows still work:

- `/start` opens the home menu.
- `/home` renders the same main dashboard path.
- the home menu exposes `🔎 Search` and `🎬 Archive` entry points.
- `/events` opens the recent events feed.
- `/alerts` opens the alerts feed, then open one alert and verify review, frame, clip, and archive actions.
- `/cameras` opens the cameras flow and workspace.
- open one camera and verify live snapshot, live monitor, and incident-list actions.
- the Search submenu reaches event, plate, and face-search help/entry surfaces.
- upload one reference image through the face-search wizard and verify the guided prompts continue.
- the Archive submenu reaches archive-jump and single-camera export help/entry surfaces.
- complete one archive jump with a known camera and timestamp.
- `/server` or `/serverinfo` opens the server info card.
- `/subscribe` still starts detector-based subscription creation.
- `/subscriptions` still lists active subscriptions.
- `/stop` and `/stop <id>` still stop subscriptions.
- callback-driven subscription creation from events/cameras/alerts still opens and confirms.
- latest event frame retrieval still works.
- clip callbacks still work for events and alerts.
- live snapshot/live monitor still starts and stops cleanly.
- admin-only server/security cards remain readable and action-safe.

## Foundation guardrails

Before merging any architecture groundwork:

- `scripts/axxon_tg_bot.py` remains the active bot entrypoint.
- `scripts/axxon_tg_ui.py` remains the active Telegram payload bridge.
- command aliases are preserved.
- callback prefix families are preserved.
- new package code is additive and not required for startup.
- no end-user feature behavior changes are introduced in a foundation-only pass.

## Validation Record

- Validation date: `2026-03-12`
- Python interpreter: `/opt/homebrew/opt/python@3.11/bin/python3.11`
- Focused correctness matrix: passed for `tests/test_web_api_parsing.py`, `tests/test_client_foundation.py`, `tests/test_event_search_service.py`, `tests/test_scope_resolution_service.py`, `tests/test_event_search_execution.py`, `tests/test_license_plate_search_service.py`, `tests/test_license_plate_search_execution.py`, `tests/test_ptz_control_service.py`, `tests/test_web_api_ptz_execution.py`, `tests/test_web_api_archive_frame.py`, `tests/test_web_api_surface.py`, and `tests/test_full_verification.py`.
- Broader regression sweep: `tests/test_architecture_foundation.py` passed and `./scripts/self_check.sh` returned `SELF_CHECK_OK` on `2026-03-12`; integration smoke was skipped because `AXXON_HOST` and `AXXON_PASS` were unset.
- Live verification: `PYTHONPATH=. /opt/homebrew/bin/python3.11 scripts/full_verification.py` wrote `full_verification_results.json` with `live_verification_ran=false` on `2026-03-12` because `AXXON_HOST` and `AXXON_PASS` were unset.
- Deferred follow-up: evaluate `EventHistoryService.FindSimilarObjects2` separately as a capability enhancement, not as part of this correctness pass.
