# Webclient connection / bootstrap / auth / stream notes

Sources inspected:
- `webclient_unpacked/dist/02.js`
- `webclient_unpacked/dist/03.js`
- `webclient_unpacked/dist/conn.js`

## Auth endpoints and flow found
Concrete endpoints in `02.js`:
- `POST /v1/authentication/authenticate_ex2` with `{user_name,password}`
- `GET/POST /v1/authentication/renew`
- `GET/POST /v1/authentication/close_session`
- `POST /v1/authentication:approve` with `{session_id}`
- `POST /v1/authentication:decline` with `{session_id}`
- `POST /grpc` method `axxonsoft.bl.auth.AuthenticationService.AuthenticateBySecondFactor`
- `POST /api/v1/auth/tokens` with bearer token
- `GET /languages` with bearer token as a post-login capability/validity check

The client treats `SECOND_FACTOR_NEEDED` as a normal auth state, not a fatal error.

## Cloud / bridge / VMS token bootstrap
The same bundle has cloud/bridge token helpers:
- `GET ../vmsToken?authToken=${token}`
- `POST ../renewVMSToken?vmsToken=${nextToken}`

This implies at least two token layers:
1. auth/cloud token
2. VMS token / next token used for downstream media or VMS access

## Host / multidomain bootstrap
`03.js` contains:
- `GET /hosts`
- `GET /hosts/{host}`
- `POST /grpc` method `axxonsoft.bl.domain.DomainService.GetHostPlatformInfo`

`conn.js` rewrites paths for `/multidomain` and sends connect frames per domain:
```js
{method:"connect",domainId:Number(n),relativeUrl:r}
```
So the webclient can multiplex multiple domain connections over one websocket worker connection.

## Websocket model
`conn.js` shows the worker-side transport logic:
- build ws URL from current origin/path or `wsURL` override
- token is supplied as `authToken` or `auth_token` query parameter
- on open, client sends per-domain `connect` commands with `relativeUrl: /ws?authToken=${token}`
- incoming messages are either:
  - JSON control/event frames
  - binary frames with header + key + pts + payload

Binary frame decode fields observed:
- `type`
- `key`
- `pts`
- `payload`
- checksum over payload

Worker also reacts to posted methods:
- `update_token`
- `update_domains`
- `debug`

## Stream/media clues
`02.js` exposes media-related endpoints:
- `live/media/${vsid}`
- `live/media/snapshot/${vsid}`
- export endpoints keyed by `vsid`, begin/end time, mode

The bundle checks browser `MediaSource` support for:
- H.264 MP4 (`avc1...`)
- H.265 MP4 (`hvc1...`)

Selection logic:
- use MP4/MSE when supported for H.264/H.265
- otherwise fall back to JPEG stream mode

This is the most concrete stream-path clue in the bundle: live view prefers MSE MP4, fallback is JPEG.
