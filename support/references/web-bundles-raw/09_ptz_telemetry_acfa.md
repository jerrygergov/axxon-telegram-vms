# PTZ / Telemetry / ACFA clues (bundle extraction)

Sources inspected:
- `webclient_unpacked/dist/02.js`
- `web_configurator_ui_unpacked/build/assets/1.chunk.js`
- configurator locale chunks for stable UI names

## Webclient PTZ / telemetry REST endpoints
`webclient_unpacked/dist/02.js` contains a concrete endpoint table for PTZ/telemetry:

- `control/telemetry/list/${objid}`
- `control/telemetry/session/acquire/${tcid}`
- `control/telemetry/session/release/${tcid}`
- `control/telemetry/session/keepalive/${tcid}`
- `control/telemetry/info/${tcid}`
- `control/telemetry/move/${tcid}`
- `control/telemetry/zoom/${tcid}`
- `control/telemetry/focus/${tcid}`
- `control/telemetry/iris/${tcid}`
- `control/telemetry/move/point/${tcid}`
- `control/telemetry/zoom/area/${tcid}`
- `control/telemetry/auto/${tcid}`
- `control/telemetry/preset/info/${tcid}`
- `control/telemetry/preset/go/${tcid}`
- `control/telemetry/preset/set/${tcid}`
- `control/telemetry/preset/remove/${tcid}`
- `control/telemetry/position/${tcid}`

This is concrete evidence that PTZ control is lease/session-based: acquire → keepalive → release.

## Implications of the telemetry session model
Because the webclient explicitly acquires and keeps alive a telemetry session, PTZ control likely enforces:
- controller ownership / lock semantics
- timeout-based session expiry
- priority or role-based arbitration

That is reinforced by configurator role labels such as:
- `TELEMETRY_PRIORITY_HIGHEST`
- `HIGH`
- `NORMAL`
- `LOW`
- `LOWEST`
- `NO_ACCESS`

## PTZ operations supported
Beyond basic pan/tilt/zoom, the bundle shows support for:
- focus control
- iris control
- point move
- area zoom
- automatic mode
- preset management
- position readback

Configurator UI strings add higher-level PTZ concepts:
- created presets
- tours
- patrols
- organize patrol presets
- overview camera
- PTZ/overview calibration workflow using 6–10 reference points

This indicates the platform supports both direct PTZ control and calibrated overview-to-PTZ workflows.

## Macro/PTZ intersection
Macro action enum includes `goto_ptz`, with form fields:
- speed
- control priority
- preset number

So PTZ can be invoked by automation, not only by operator live control.

## ACFA API clues
Configurator bundle contains concrete gRPC gateway calls:

- `axxonsoft.bl.domain.DomainService.ListAcfaComponents2`
- `axxonsoft.bl.domain.DomainService.BatchGetAcfaComponents`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsActions`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsEvents`

All are issued through `POST /grpc` with payload:
```json
{ "method": "...", "data": ... }
```

This suggests:
- ACFA inventory lives partly under domain service enumeration
- action/event semantics live under a dedicated ACFA service
- the web configurator consumes ACFA through the same HTTP gRPC bridge as auth/domain calls

## ACFA object model hints
UI/domain strings show:
- `ACFA_DEVICE` as a distinct device category
- dedicated access rights: `ACFA_ACCESS_*`
- dedicated macro trigger menus: `acfa`, `acfa_events`, `acfa_source`
- macro actions: `ALARM`, `HANDLE_ALARM`, `ARM`, `DISARM`

That implies ACFA units are first-class domain components with their own:
- inventory
- events
- actions
- permissions
- macro bindings

## Short summary
Most concrete low-level findings here are solid, not speculative:
- PTZ is controlled via explicit telemetry session endpoints and per-operation REST calls.
- Macro engine can drive PTZ via `goto_ptz`.
- ACFA is exposed through gRPC gateway methods for component listing, event listing, and action listing.
- Role model includes PTZ priority and dedicated ACFA permissions, implying arbitration and access control are built into the platform.
