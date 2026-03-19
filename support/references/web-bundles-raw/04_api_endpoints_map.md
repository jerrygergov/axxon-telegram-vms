# 04 API Endpoints Map

Tight grouped index from extracted `webclient` + `web-configurator-ui` bundles.
Only concrete strings/method names seen in bundle output are included.

## 1) Shared auth / session surface
Seen in both bundles.

### REST / HTTP
- `POST /v1/authentication/authenticate_ex2`
- `POST /v1/authentication/close_session`
- `POST /v1/authentication/renew`
- `POST /v1/authentication:approve`
- `POST /v1/authentication:decline`
- `POST /api/v1/auth/tokens`
- `GET /languages`
- `GET /vmsToken?authToken=...`
- `POST /renewVMSToken?vmsToken=...`
- `POST /grpc`

### gRPC-over-HTTP methods tied to auth
- `axxonsoft.bl.auth.AuthenticationService.AuthenticateBySecondFactor`

### Storage/session keys referenced by auth logic
- `authData`
- `cloudToken`
- `nextToken`
- `accessToken`
- `refreshToken`
- `expiredDate`
- `host`
- `port`

---

## 2) Hosts / multidomain / node info
Concrete in both zips; stronger host-detail flow is visible in configurator.

### REST / HTTP
- `GET /hosts`
- `GET /hosts/${host}`
- `POST /grpc` for per-host platform info

### gRPC-over-HTTP methods
- `axxonsoft.bl.domain.DomainService.GetHostPlatformInfo`
- `axxonsoft.bl.discovery.DiscoveryService.DiscoverNode`
- `axxonsoft.bl.discovery.DiscoveryService.GetNodeDiscoveryProgress`
- `axxonsoft.bl.domain.DomainService.ListComponents`

### Notes
- configurator fetches `/hosts`, then `/hosts/${host}`
- multidomain/webclient code keeps a per-domain websocket URL map like:
  - `domainId -> /ws?authToken=${token}`

---

## 3) web-configurator-ui: configurator REST surface
Concrete REST strings visible in configurator bundle.

### Configurator REST
- `GET /configurator/devices_catalog/vendors`
- `GET /configurator/devices_catalog/devices`
- `GET /configurator/device-additional-data:acquire?uid=${uid}`

### Domain / component gRPC methods used by configurator
- `axxonsoft.bl.domain.DomainService.ListAcfaComponents2`
- `axxonsoft.bl.domain.DomainService.BatchGetAcfaComponents`

### ACFA-specific gRPC methods used by configurator
- `axxonsoft.bl.acfa.AcfaService.ListUnitsActions`
- `axxonsoft.bl.acfa.AcfaService.ListUnitsEvents`

---

## 4) webclient: websocket / media / event transport
Concrete transport strings from `webclient` bundle.

### Websocket endpoints
- `/ws?authToken=${token}`
- worker reconnect/update-token flow is explicit
- domain list updates rewrite websocket targets per domain

### Websocket usage families
- live state/event stream
- multidomain per-domain websocket fan-out
- binary payloads over websocket worker (`binaryType = "arraybuffer"`)

### HTTP helpers around webclient transport
- `/api/v1/mwc`
- `/api/v1/wc-proxy`

### Notes
- one websocket path is reused for general live/event data
- code also shows a separate events-oriented websocket helper that rebinds domains and token updates

---

## 5) webclient: PTZ / telemetry transport
Concrete PTZ endpoint table from `webclient` bundle.

### Telemetry/PTZ REST-like paths
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

### Matching gRPC method family seen elsewhere
- `axxonsoft.bl.ptz.TelemetryService.AcquireSessionId`
- `axxonsoft.bl.ptz.TelemetryService.KeepAlive`
- `axxonsoft.bl.ptz.TelemetryService.Move`
- `axxonsoft.bl.ptz.TelemetryService.AbsoluteMove`
- `axxonsoft.bl.ptz.TelemetryService.Zoom`
- `axxonsoft.bl.ptz.TelemetryService.Focus`
- `axxonsoft.bl.ptz.TelemetryService.Iris`
- `axxonsoft.bl.ptz.TelemetryService.GetPositionInformation`
- `axxonsoft.bl.ptz.TelemetryService.GoPreset`
- `axxonsoft.bl.ptz.TelemetryService.SetPreset`
- `axxonsoft.bl.ptz.TelemetryService.RemovePreset`
- `axxonsoft.bl.ptz.TelemetryService.GetTours`
- `axxonsoft.bl.ptz.TelemetryService.SetTourPoint`
- `axxonsoft.bl.ptz.TelemetryService.StartFillTour`
- `axxonsoft.bl.ptz.TelemetryService.StopFillTour`
- `axxonsoft.bl.ptz.TelemetryService.RemoveTour`

### Practical read
- PTZ is clearly lease/session based: acquire -> keepalive -> operate -> release

---

## 6) Macros / events / automation / ACFA
Concrete method names + enum-backed action/event families.

### Macro-related gRPC methods
- `axxonsoft.bl.logic.LogicService.ListMacrosV2`
- `axxonsoft.bl.logic.LogicService.BatchGetMacros`

### Macro action families confirmed from bundle enums
- `write_archive`
- `raise_alert`
- `close_alert`
- `switch_relay`
- `arm_state`
- `disarm_state`
- `replication`
- `export`
- `goto_ptz`
- `macro`
- `web_query`
- `audio_notification`
- `email_notification`
- `push_event`
- `service_state`
- `acfa`
- `gui`

### Web query action shape
- auth methods: `AM_BASIC`, `QA_DIGEST`
- verbs: `QM_GET`, `QM_POST`, `QM_PUT`, `QM_DELETE`
- fields seen: `port`, `username`, `path`, `query`

### ACFA/event families surfaced in automation UI
- `ACFA`
- `ALERT`
- `ARCHIVE_WRITE`
- `ARM`
- `AUDIT`
- `DETECTOR`
- `DEVICE`
- `GROUP`
- `LICENSE`
- `PTZ`
- `RECOGNITION`
- `RELAY`
- `SERVER_STATE`
- `STATISTICS`
- `TEXT`
- `TIMEZONE`
- `VOLUME_HEALTH`

---

## 7) Small but concrete extras
### Webclient-only third-party/API strings seen in bundle
- `/v1/configsync/layouts`
- `/v3/ac-backend/domains?page[limit]=200`
- `/api/4_1/rs/suggest/address`
- `/api/4_1/rs/suggest/bank`
- `/api/4_1/rs/suggest/email`
- `/api/4_1/rs/suggest/fio`
- `/api/4_1/rs/suggest/party`
- `/api/4_1/rs/suggest/party_by`
- `/api/4_1/rs/suggest/party_kz`

These look auxiliary/UI integrations, not core Axxon control APIs.

---

## Short integration takeaways
- Lowest-friction programmatic entry appears to be bearer-authenticated `POST /grpc` plus selected REST helpers.
- Auth/session stack is shared across webclient and configurator.
- Multidomain support is real, not cosmetic: `/hosts`, `/hosts/${host}`, per-domain websocket mapping, host platform info.
- PTZ is exposed twice conceptually: direct webclient telemetry endpoints and gRPC `TelemetryService` methods.
- ACFA and macros are first-class surfaces, not just UI labels.
