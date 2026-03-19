# Future Extension Foundation

Step 30 is an additive architecture pass only. It does not add a real VLM provider integration, a new web app, or a transport rewrite.

## External analysis seam

New package-owned contracts now define the minimum truthful surface for future exported-media analysis:

- `axxon_telegram_vms.models.request_envelopes`
  - cross-surface request actor + audit policy + dry-run envelope
  - small log/audit context shaping for future control/analysis runners
- `axxon_telegram_vms.services.external_analysis`
  - exported artifact references for images/clips
  - prompt preset contracts
  - provider capability contracts
  - submission evaluation and result-summary shaping
- `axxon_telegram_vms.jobs.external_analysis`
  - async job record for planned/submitted/running/succeeded/failed/dry-run states

This foundation is designed to sit behind existing export/search flows without claiming that a provider is already wired.

## Session and web-app seam

`axxon_telegram_vms.client.session` now captures the observed auth/session contract from the checked-in bundle references:

- auth/session endpoints from:
  - `support/references/web-bundles-raw/03_auth_and_session_flows.md`
  - `support/references/web-bundles-raw/04_api_endpoints_map.md`
- web-app/operator routing context from:
  - `support/references/web-bundles-raw/06_routes_and_ui_modules.md`
- token/storage concepts:
  - `authData`
  - `cloudToken`
  - `nextToken`
  - `accessToken`
  - `refreshToken`
  - `expiredDate`
  - `host`
  - `port`

The seam exposes:

- documented endpoint URLs
- normalized token bundles
- safe session summaries without echoing raw bearer tokens
- storage snapshots that line up with the observed browser/session keys

## Intentional non-goals in this pass

- no fake VLM adapter implementation
- no provider secrets/config surface
- no persistent async job runner
- no new Telegram command/UI surface
- no bearer-auth transport migration in `scripts/`
- no browser/web SPA code

## Next-step uses

These seams are intended to support future passes that need:

- exported clip/image handoff to a real provider adapter
- queue-backed external analysis runners
- bearer/session-aware web or API services
- shared audit/dry-run envelopes across admin/control/analysis surfaces
