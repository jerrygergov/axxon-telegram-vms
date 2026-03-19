# 11 Priority gRPC Methods for First Wrapper

## Goal
Pick the smallest useful read-only surface for the first Axxon One + Telegram integration wrapper.

## Priority 1 — authentication and session bootstrap
### REST
- `/v1/authentication/authenticate_ex2`
- `/v1/authentication/renew`
- `/v1/authentication:approve`
- `/v1/authentication:decline`
- `/api/v1/auth/tokens`
- `/grpc`

### Why first
Without stable auth/session handling, every other wrapper is fragile.

## Priority 2 — host and multidomain discovery
### REST
- `/hosts`
- `/hosts/{host}`

### gRPC
- `axxonsoft.bl.domain.DomainService.GetHostPlatformInfo`

### Why early
Lets the wrapper discover target nodes and report health/capabilities into Telegram.

## Priority 3 — macro inventory (read-only)
### gRPC
- `axxonsoft.bl.logic.LogicService.ListMacrosV2`
- `axxonsoft.bl.logic.LogicService.BatchGetMacros`

### Why early
Macros are one of the most integration-relevant domains and likely provide event/action visibility without needing media reverse-engineering first.

## Priority 4 — ACFA inventory and actions/events metadata
### gRPC
- `axxonsoft.bl.domain.DomainService.ListAcfaComponents2`
- `axxonsoft.bl.domain.DomainService.BatchGetAcfaComponents`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsActions`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsEvents`

### Why early
Useful for structured operational alerts and Telegram summaries.

## Priority 5 — PTZ information and safe control session model
### gRPC
- `axxonsoft.bl.ptz.TelemetryService.AcquireSessionId`
- `axxonsoft.bl.ptz.TelemetryService.KeepAlive`
- `axxonsoft.bl.ptz.TelemetryService.GetPositionInformation`
- `axxonsoft.bl.ptz.TelemetryService.GetTours`
- `axxonsoft.bl.ptz.TelemetryService.GoPreset`

### Why later than inventory APIs
PTZ has more state/session complexity than plain read-only inventory methods.

## Defer for now
- websocket/media reverse
- direct stream transport emulation
- write-heavy configurator mutations
- anything requiring full browser parity

## Recommended first wrapper order
1. auth/session module
2. hosts discovery module
3. macro inventory module
4. ACFA inventory module
5. PTZ info module
6. only then selective PTZ control
