# 12 Telegram Integration Backlog

## Phase 0 — foundation
- implement auth/session client
- support token renewal
- support approve/decline flow if second factor is required
- add `/grpc` caller with bearer auth
- add optional `/hosts` discovery support

## Phase 1 — read-only Telegram commands
- `/axxon hosts`
- `/axxon macros`
- `/axxon acfa units`
- `/axxon acfa events`
- `/axxon ptz status <camera>`

## Phase 2 — event-oriented summaries
- map macro/event categories into Telegram-friendly text
- summarize ACFA actions/events
- expose health/platform info per host

## Phase 3 — safe control actions
- PTZ preset jump
- PTZ position readback
- ACFA action execution only after explicit confirmation

## Phase 4 — optional richer features
- stream/snapshot enrichment
- browser/webclient-assisted fallback flows
- media transport integration if needed

## Message design guidance
- keep outputs concise by default
- prefer structured bullets over raw JSON in Telegram
- include stable identifiers when useful
- separate read-only commands from control commands clearly

## Engineering guidance
- start with read-only wrappers
- log raw request/response samples during development
- preserve host/domain context in every command
- keep auth/session state isolated from Telegram formatting layer
