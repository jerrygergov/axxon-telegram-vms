# Architecture Foundation Skeleton

This is the safe internal structure introduced in the March 9, 2026 foundation passes.

## Safety rule

`scripts/` remains the production runtime. The new package tree is intentionally dormant until later migration passes move behavior behind compatibility adapters.

## New package skeleton

`axxon_telegram_vms/` still keeps the runtime split explicit, but passes 2-5 and Step 30 now seed the first real low-risk seams in `models`, `client`, `services`, and `jobs`:

- `axxon_telegram_vms.client`: config loading, pure transport/request helpers, a small TTL-backed runtime read-cache helper for narrow inventory/server caching, and future web/session contracts.
- `axxon_telegram_vms.services`: pure orchestration/state helpers for subscription-style workflows plus future external-analysis contracts.
- `axxon_telegram_vms.models`: normalized detector rows plus additive event normalization helpers used by low-risk script wrappers, along with cross-surface request/audit envelopes.
- `axxon_telegram_vms.jobs`: live-session job primitives extracted behind a package seam plus future external-analysis job records.
- `axxon_telegram_vms.ui`: future Telegram and possible web-facing presentation helpers.

The lane registry lives in `axxon_telegram_vms/foundation.py` so tests and docs can pin the intended split without forcing a runtime cutover.

## Seed mapping from the current runtime

- `client`: `scripts/axxon_web_api.py`, `scripts/config_loader.py`, transport-facing helpers in `scripts/tg_ui_common.py`
- `client` pass 3 seam:
  - `axxon_telegram_vms.client.config`
  - `axxon_telegram_vms.client.session`
  - `axxon_telegram_vms.client.transport`
  - `axxon_telegram_vms.client.cache`
  - `axxon_telegram_vms.client.runtime_cache`
- `services`: orchestration in `scripts/axxon_tg_bot.py`, `scripts/live_session_runtime.py`
- `services` pass 4 seam:
  - `axxon_telegram_vms.services.subscriptions`
- `services` Step 30 seam:
  - `axxon_telegram_vms.services.external_analysis`
- `models`: normalization helpers in `scripts/camera_catalog.py`, `scripts/unification_helpers.py`
- `models` pass 2 and 5 seams:
  - `axxon_telegram_vms.models.detectors`
  - `axxon_telegram_vms.models.event_normalization`
  - `axxon_telegram_vms.models.query_filters`
  - `axxon_telegram_vms.models.request_envelopes`
- `jobs`: future extraction point for subscription workers, exports, searches, and live monitor job state
- `jobs` pass 4 seam:
  - `axxon_telegram_vms.jobs.live_sessions`
- `jobs` Step 30 seam:
  - `axxon_telegram_vms.jobs.external_analysis`
- `ui`: `scripts/axxon_tg_ui.py`, `scripts/tg_camera_ui.py`, `scripts/tg_server_ui.py`, formatting helpers in `scripts/tg_ui_common.py`

## Pass 2-5 and Step 30 scope

Only low-risk config/model/transport/orchestration helpers moved:

- detector row normalization now has a dataclass-backed seam in `axxon_telegram_vms.models.detectors`
- detector event + alert normalization now has a dataclass-backed seam in `axxon_telegram_vms.models.event_normalization`
- shared event/archive query models now live in `axxon_telegram_vms.models.query_filters`:
  - time-range bounds
  - host/domain/camera/detector scope filters
  - category/type/state/severity/priority taxonomy filters
  - text/contains/mask matching fields
- cross-surface request actor/audit/dry-run envelopes now live in `axxon_telegram_vms.models.request_envelopes`
- env/config parsing now lives in `axxon_telegram_vms.client.config`
- observed web/session endpoint and token-storage contracts now live in `axxon_telegram_vms.client.session`
- gRPC response parsing, server-info shaping, and media URL/header helpers now live in `axxon_telegram_vms.client.transport`
- `axxon_telegram_vms.client.cache.TTLCache` now backs a narrow `axxon_telegram_vms.client.runtime_cache` helper with explicit TTL/invalidation behavior
- `scripts/axxon_tg_bot.py` now uses that helper only for low-risk read-heavy paths:
  - detector inventory
  - subscription camera inventory
  - read-only `cam:list`, `cam:open`, `cam:stream`
  - read-only `srv:menu`, `srv:domain`, `srv:version`, `srv:stats`
- subscription state filtering, fallback poll shaping, and per-user subscription ledger state now live in `axxon_telegram_vms.services.subscriptions`
- the subscription seam can now materialize a typed `EventQuery` bridge from legacy filter dicts without changing callback ownership
- external exported-media analysis contracts now live in `axxon_telegram_vms.services.external_analysis`
- live-session record/runtime primitives now live in `axxon_telegram_vms.jobs.live_sessions`
- future async analysis job records now live in `axxon_telegram_vms.jobs.external_analysis`
- `scripts/unification_helpers.py` and `scripts/axxon_web_api.py` call those helpers, but all transport, callbacks, and Telegram orchestration remain in `scripts/`
- `scripts/config_loader.py` is now a compatibility wrapper over the package seam
- `scripts/live_session_runtime.py` is now a compatibility wrapper over the jobs seam
- `scripts/axxon_tg_bot.py` still owns handlers, notifier/API calls, and notification delivery, but now delegates pure subscription ledger/filter logic to the package seam

Still intentionally pending:

- direct `AxxonClient` extraction and broader transport rewrite
- moving full subscription runtime loops, exports, searches, and other handler orchestration into package-owned services
- runtime cache adoption beyond the current narrow bot-side inventory/server slice
- generic export/search job records beyond the live-session runtime primitive
- actual provider adapters, async runners, and bearer-auth transport adoption for the Step 30 seams
- UI refactors beyond current script wrappers
- first package-owned UI navigation/button helper extraction; the callback surface is still string-pinned in several tests, so the safe next seam remains a small shared top-level nav helper rather than a broad UI migration

## Migration constraints for later passes

- Move behavior one seam at a time behind adapters.
- Keep `scripts/` entrypoints stable until the replacement path is proven.
- Add tests before redirecting imports.
- Prefer extracting pure helpers first, then orchestration, then transport.
