# 10 Integration Notes for Axxon Telegram

Concrete helper notes derived from bundle evidence.

## Best candidate surfaces for a Telegram bot/client

### 1) Prefer auth -> bearer token -> `POST /grpc`
Why:
- both bundles use the same auth/session stack
- configurator clearly sends many higher-value operations through `POST /grpc`
- gRPC method names are preserved in JS, so the callable surface is discoverable

Start points:
- `POST /v1/authentication/authenticate_ex2`
- `POST /v1/authentication/renew`
- `POST /grpc`

## Good first Telegram features

### Host / system introspection
Likely easiest low-risk commands:
- list hosts via `GET /hosts`
- inspect host via `GET /hosts/${host}`
- get platform info via:
  - `axxonsoft.bl.domain.DomainService.GetHostPlatformInfo`

Suggested bot commands:
- `/hosts`
- `/host <name>`
- `/health <host>`

### ACFA lookup helpers
Concrete methods:
- `axxonsoft.bl.domain.DomainService.ListAcfaComponents2`
- `axxonsoft.bl.domain.DomainService.BatchGetAcfaComponents`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsActions`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsEvents`

Suggested bot commands:
- `/acfa units`
- `/acfa unit <id>`
- `/acfa actions <id>`
- `/acfa events <id>`

### Macro inventory and trigger-adjacent tooling
Concrete methods:
- `axxonsoft.bl.logic.LogicService.ListMacrosV2`
- `axxonsoft.bl.logic.LogicService.BatchGetMacros`

Useful because macros already encapsulate actions like:
- PTZ goto preset
- push event
- web query
- alert raise/close
- ACFA actions

Suggested bot commands:
- `/macros`
- `/macro <name>`

### PTZ helpers
Two concrete paths exist:
- webclient telemetry endpoints under `control/telemetry/...`
- gRPC `axxonsoft.bl.ptz.TelemetryService.*`

Safer bot approach:
- use gRPC methods if request shapes are confirmed from live traces/docs
- remember PTZ is session-based (`AcquireSessionId` / `KeepAlive` / release)

Suggested bot commands:
- `/ptz presets <camera>`
- `/ptz goto <camera> <preset>`
- `/ptz pos <camera>`

## Surfaces to avoid first
- raw websocket/media transport
  - useful for live UI, but higher complexity for a Telegram bot
- direct browser-only helper endpoints unless needed
  - `/api/v1/mwc`
  - `/api/v1/wc-proxy`

## Practical implementation shape
1. login once and cache bearer token with expiry handling
2. build a tiny `grpc_call(method, data)` wrapper over `POST /grpc`
3. add read-only commands first: hosts, macros, ACFA inventory, PTZ info
4. only then add mutating commands: PTZ move, ACFA action, macro execution
5. if multidomain is enabled, model host/domain explicitly in bot commands

## Concrete unknowns still needing live capture/docs
- exact request/response schema for each `/grpc` method
- whether macro execution itself is exposed by a discovered method or only via another surface
- preferred surface for camera/event subscriptions if Telegram alerts should be near-real-time

## Bottom line
For an Axxon Telegram integration, the cleanest path is not websocket/media reverse-engineering first. It is:
- auth
- optional `/hosts` discovery
- `POST /grpc`
- targeted method wrappers for host info, ACFA, macros, and PTZ
