# Implementation Plan — Axxon Telegram VMS Next Phase

## Executive summary

See also: `support/docs/EXECUTION_MODE.md` for the required active supervision loop for Codex-driven execution.


The bot already has a strong operator baseline: events, alerts, cameras, snapshots, clips, subscriptions, live monitor, and server information. The next phase should **not** be a random pile of features. It should be a structured transition from a Telegram-first utility bot into a more durable **operator/control plane** with a future path toward a web-based app.

The safest execution order is:

1. strengthen the internal foundations first (client layer, normalization, caching, architecture boundaries),
2. improve current operator UX (labels, grouping, role-aware views, favorites, digests, topics),
3. add high-value search/archive/export capabilities,
4. add read-only operational domains (macros, ACFA, PTZ, hosts),
5. only then add selective control actions and future AI/VLM workflows.

This plan is designed to be executed incrementally with low breakage risk and continuous validation.

---

## Assumptions and current state

Current repository strengths:
- Telegram-first runtime already works (`scripts/axxon_tg_bot.py` and UI helpers)
- event/alert/camera/server flows already exist
- subscriptions already exist with dedupe/throttle/day caps
- camera workspace, snapshots, clips, live monitor exist
- tests already exist for several runtime pieces
- references and live Axxon samples are already checked into the repo
- raw frontend reverse/reference artifacts are expected at `/home/%username%/axxon-telegram-vms/support/references/web-bundles-raw` and should be treated as an implementation reference source for web/API behavior

## Additional implementation reference sources

Before phases that touch search, archive, macros, PTZ, hosts, admin/config, or other surfaces that may appear in the unpacked frontend bundles, inspect these local reference sources first:
- `/home/%username%/axxon-telegram-vms/docs`
- `/home/%username%/axxon-telegram-vms/references`
- `/home/%username%/axxon-telegram-vms/support/references/web-bundles-raw`

Use them as supporting sources of implementation hints/examples for both human supervision and Codex passes. Prefer checked-in support/docs/references first, then bundle artifacts for extra implementation clues. Do not treat bundle findings as sole proof of backend capability; confirm against live behavior, checked-in references, or direct API evidence before shipping behavior.

Current technical debt / constraints:
- subprocess-heavy path through API tooling is still a bottleneck
- event semantics and labels are still weaker than operator expectations
- no unified normalized domain model yet
- no caching layer yet
- no proper host/domain-aware UI model yet
- Telegram topics / broadcast digest routing is not yet first-class
- advanced search/export features need deeper API mapping and validation

---

# Phase 0 — Analysis and guardrails

## Step 1 — Freeze and document the current runtime baseline
Create a short technical baseline document in `support/docs/` that lists:
- current commands
- current callback flows
- current runtime modules
- current tests
- environment variables in active use
- known pain points already observed from screenshots and live samples

**Goal:** prevent refactor drift and give every later step a regression checklist.

## Step 2 — Build a feature/API feasibility matrix
Create a matrix that maps each requested feature to:
- likely API surface
- current evidence in repo/support/docs/reverse notes
- confidence level
- blockers
- MVP scope
- deferred scope

Features to map explicitly:
- macros list/run
- archive search/jump/export
- face search
- plate search with mask
- time-range event search
- multi-camera export
- topics/digests
- PTZ / ACFA / admin future
- external VLM clip analysis

**Goal:** separate “likely implementable now” from “needs deeper reverse/API confirmation”.

## Step 3 — Add a standing regression checklist
Create a reusable checklist for all future tasks:
- `/start` works
- home renders
- alerts/events/cameras/server flows still open
- subscriptions still create/list/stop
- live snapshot still works
- latest event frame still works
- tests pass

**Goal:** every feature step must be validated against the same baseline.

---

# Phase 1 — Architecture foundation

## Step 4 — Introduce a unified service boundary inside Python
Define a new internal architecture split, for example:
- `client/` — raw Axxon transport clients
- `services/` — business operations / orchestration
- `models/` — normalized domain models
- `ui/` — Telegram formatting / menus / callbacks
- `jobs/` — long-running export/search tasks

Do this first as structure and adapters, not as a full rewrite.

**Goal:** prepare the repo for both Telegram growth and a future web app.

## Step 5 — Add a direct unified Python client layer
Start replacing subprocess-heavy API calls with direct Python client modules.
Recommended first clients:
- auth/session client
- events client
- alerts client
- cameras client
- archive/export client
- grpc call wrapper
- hosts client

Keep a compatibility bridge during migration so the bot keeps running.

**Goal:** reduce shell/process overhead and make the system testable.

## Step 6 — Implement a unified normalized domain model
Introduce canonical models such as:
- `NormalizedEvent`
- `NormalizedAlert`
- `NormalizedCamera`
- `NormalizedDetector`
- `NormalizedHost`
- `NormalizedMacro`
- `NormalizedAcfaUnit`
- `NormalizedArchiveSegment`
- `NormalizedSearchResult`

These should hide raw payload differences and provide stable UI-ready fields.

**Goal:** stop leaking raw API payload semantics into Telegram UI.

## Step 7 — Implement a unified event normalization layer
Build a dedicated normalization pipeline for event-like objects.
It must handle:
- Axxon detector event semantics
- alert state/priority/localization fields
- BEGAN/ENDED semantics where applicable
- one-phase event families (LPR/Face/Meta/Neurotracker etc.)
- detector/camera/source friendly naming

**Goal:** this is the foundation for better labels, search, digests, subscriptions, and exports.

## Step 8 — Add a caching layer
Introduce a repository-wide caching utility for read-heavy data:
- camera catalog
- detector inventory
- host/platform info
- macro inventory
- ACFA inventory
- PTZ capabilities / presets / tours
- server stats

Support TTL + explicit invalidation.

**Goal:** lower latency and reduce API churn.

## Step 9 — Add background job primitives
Introduce a lightweight job model for long-running operations:
- export clip
- export frames
- large search
- face search upload+match
- future VLM analysis

Minimum fields:
- job id
- user id
- status
- progress text
- started/finished timestamps
- output artifact paths/urls
- error info

**Goal:** avoid blocking Telegram request paths.

---

# Phase 2 — UX and product cleanup

## Step 10 — Redesign command and menu grouping
Restructure commands into clearer groups:
- Operator: home, alerts, events, cameras, archive, search
- Subscriptions: subscribe, subscriptions, stop, stopall, digest
- Operations/admin: server, hosts, macros, PTZ, ACFA, stats
- Utility: help, status, tz, profile

Keep aliases, but reduce top-level clutter in menus.

**Goal:** improve discoverability and reduce cognitive overload.

## Step 11 — Add role-aware UI split (operator/admin)
Implement role-based UI rendering:
- operator view: alerts, events, cameras, archive, subscriptions, favorites
- admin view: hosts, server diagnostics, macros, PTZ, ACFA, future config

This should be a UI capability split first, not yet full permissioned config editing.

**Goal:** prepare for future admin/configuration capabilities without polluting operator UX.

## Step 12 — Add favorites / pinned cameras
Implement per-user saved favorites:
- favorite cameras
- pinned detectors
- default host/domain
- saved quick views

Store in secure profile storage if enabled.

**Goal:** make frequent workflows fast and personal.

## Step 13 — Improve operator labels everywhere
Use normalized event semantics to redesign labels for:
- home latest alerts
- alert buttons
- event list buttons
- detector list buttons
- camera incidents
- subscription notification titles

Use strict human-readable priority order:
- localization text
- detector friendly name
- camera/source label
- relevant extracted entity (plate/face/object)
- state and severity only when meaningful

**Goal:** this is the highest-ROI UX improvement.

## Step 14 — Add digest-capable notifications
Extend subscriptions to support:
- event bundling
- time-window grouping
- per-detector/camera aggregation
- daily/shift summary
- quiet-hours aware behavior

**Goal:** reduce Telegram noise and increase usefulness.

## Step 15 — Add Telegram topic-aware routing and broadcast digest support
Implement topic-aware delivery model:
- per-topic subscriptions
- per-topic event stream rules
- route different detectors/cameras/categories into different Telegram topics
- support digest broadcasting to topics/groups

Store topic routing in user/admin-configurable profiles.

**Goal:** make the bot usable in multi-stream operational chats.

---

# Phase 3 — Read-only operational domains

## Step 16 — Add hosts/domain visibility
Implement:
- `/hosts`
- `/host <name>`
- host status cards
- domain/platform summaries

Ground this on known host/multidomain surfaces and cache the results.

**Goal:** make the bot usable in multidomain setups.

## Step 17 — Add macro inventory (read-only first)
Implement:
- list macros
- inspect macro details
- filter/search macros
- show macro type, trigger/action family, enablement state, target scope

Ground this in documented/reversed macro surfaces.

**Goal:** expose automation inventory before allowing execution.

## Step 18 — Add PTZ read-only visibility
Implement:
- PTZ capability detection per camera
- presets/tours listing
- current position info (if available)
- session-aware safe read-only access model

**Goal:** build PTZ confidence before enabling control actions.

## Step 19 — Add ACFA read-only visibility
Implement:
- ACFA unit inventory
- event/action metadata
- per-unit summaries
- host/domain linkage where available

**Goal:** expose a new operational domain with low initial risk.

---

# Phase 4 — Search and archive foundation

## Step 20 — Build a shared query/filter abstraction
Before implementing many search commands, create reusable filter objects for:
- time range
- host/domain
- camera list
- detector list
- event categories/types
- state filters
- severity/priority
- text/contains/mask fields

**Goal:** avoid ad hoc query logic in every feature.

## Step 21 — Implement search-all-events by time range
Add a proper search mode, not just recent feeds.
Support:
- all events in a time range
- camera/detector/host scoping
- type/category filtering
- summary mode and paginated list mode

This should become the backbone for later archive and export flows.

## Step 22 — Implement archive jump/search workflows
Add archive navigation flows that let a user:
- choose a camera
- choose a time / range
- jump to archive context
- fetch preview frames and adjacent navigation

First MVP can return:
- preview frame
- exact timestamp information
- deep link or archive context handle

**Goal:** provide a real investigative workflow in Telegram.

## Step 23 — Implement quick export of frames and single-camera clips
Add first-class export jobs for:
- one frame at timestamp
- one frame around event
- clip by explicit start/end
- clip around event with predefined windows

This is the first export MVP and should be robust before doing multi-camera export.

## Step 24 — Implement multi-camera export model
Add support for:
- one timestamp across multiple cameras → image set/contact sheet
- one time window across multiple cameras → separate clips or packaged output

Be careful with:
- Telegram limits
- output size
- timeout behavior
- temporary storage cleanup

**Goal:** support operator investigations across multiple viewpoints.

---

# Phase 5 — Advanced search domains

## Step 25 — Implement license plate search, including masks
Add a first-class plate search flow:
- exact plate search
- masked search / wildcard support
- time-range filters
- camera/group/host filters
- result cards with time/camera/plate/confidence

This is likely one of the highest-value near-term features.

## Step 26 — Investigate and implement face search by uploaded image
This should be treated as a gated feature because it may require additional API confirmation.
Build it in two substeps:
1. confirm Axxon-side upload/search surface and request format
2. implement Telegram upload → image preservation → search job → results UI

Results should show:
- best matches
- time
- camera
- similarity/confidence if available
- jump/export actions

**Goal:** add a high-value forensic workflow if the backend surface is real and stable.

---

# Phase 6 — Controlled action features

## Step 27 — Add macro execution with strict guardrails
After macro inventory is stable, add execution support with:
- allowlist/role gating
- confirmation prompts
- audit logging
- visible failure/success feedback

Do not start with unrestricted macro execution.

## Step 28 — Add selective PTZ control actions
Add only safe, high-value PTZ actions first:
- go preset
- basic tour control
- maybe bounded step move

Use the session model correctly and log everything.

## Step 29 — Prepare admin-view foundation for future Axxon configuration support
Do not implement full configuration editing yet, but prepare:
- admin menu structure
- permission model
- draft service boundaries for future config writes
- audit and dry-run concepts

**Goal:** make future admin/config features possible without destabilizing current operator workflows.

---

# Phase 7 — Future intelligence and web-app path

## Step 30 — Build future-facing extension points for VLM and web app evolution
Introduce two future-facing abstraction points:

### A. External analysis pipeline
Define interfaces for sending exported clips/images to external VLM providers with:
- prompt presets
- provider adapters
- async job handling
- result summarization
- privacy/audit controls

### B. UI-independent service layer
Ensure all new business logic lives behind service/client/model layers so it can later power:
- Telegram bot
- future web app
- future API service

This is the step that turns short-term bot work into long-term platform work.

---

# Feasibility guidance by feature

## High feasibility now
- command/menu regrouping
- role-aware views
- favorites/pinned cameras
- caching layer
- unified event normalization layer
- unified normalized domain model
- direct Python client migration
- search all events in time range
- archive jump/search workflows (MVP)
- frame/clip export (single camera)
- digest + Telegram topic routing
- macro inventory (read-only)
- PTZ read-only
- ACFA read-only

## Medium feasibility now, but needs careful API validation
- macro execution
- PTZ control
- multi-camera export
- plate search with masks

## Feasible only after deeper API confirmation / targeted reverse
- face search by uploaded image
- reliable playback-from-point flows beyond jump/export model
- future admin configuration writes
- external VLM automation with meaningful privacy controls

---

# Testing and validation plan

## Required tests to add during implementation
- normalization unit tests
- caching behavior tests
- client-layer tests with mocked responses
- subscription/digest routing tests
- topic routing tests
- archive/export job tests
- plate search filter tests
- favorites/profile persistence tests
- macro/PTZ permission tests

## Required live validation passes
- real server auth/session validation
- real camera/event/alert rendering check
- archive export smoke tests
- topic delivery smoke tests
- regression checks for existing callbacks and commands

## Release strategy
- keep features behind incremental command/UI rollout
- introduce read-only surfaces first
- use migration shims where subprocess and direct-client paths coexist
- add audit logging before control actions

---

# Recommended first execution slice

If work starts immediately, the first 5 implementation slices should be:
1. unified client/model/service scaffolding
2. event normalization + better labels
3. caching layer
4. search-all-events by time range
5. archive quick export flow (single camera)

That sequence gives immediate value while also reducing future rework.
