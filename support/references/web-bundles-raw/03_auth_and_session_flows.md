# 03 Auth and Session Flows

## Status
Initial reverse pass completed from `web-configurator-ui` bundle.

## Confirmed auth/session endpoints
- `/v1/authentication/authenticate_ex2`
- `/v1/authentication/close_session`
- `/v1/authentication/renew`
- `/v1/authentication:approve`
- `/v1/authentication:decline`
- `/api/v1/auth/tokens`
- `/grpc`
- `/vmsToken?authToken=...`
- `/renewVMSToken?vmsToken=...`
- `/hosts`
- `/hosts/{host}`
- `/languages`

## Confirmed token/session storage keys
- `authData`
- `cloudToken`
- `nextToken`
- `accessToken`
- `refreshToken`
- `expiredDate`
- `host`
- `port`

## Observed auth flow building blocks
- login dialog uses username/password and optional host/port
- main login request goes to `/v1/authentication/authenticate_ex2`
- session close goes to `/v1/authentication/close_session`
- token renewal goes to `/v1/authentication/renew`
- second-factor approval/decline uses:
  - `/v1/authentication:approve`
  - `/v1/authentication:decline`
- second-factor auth is also sent through `/grpc` using:
  - `axxonsoft.bl.auth.AuthenticationService.AuthenticateBySecondFactor`
- a separate token exchange endpoint exists:
  - `/api/v1/auth/tokens`
- cloud / bridge mode uses:
  - `/vmsToken?authToken=...`
  - `/renewVMSToken?vmsToken=...`

## Error / auth state constants found
- `AUTHENTICATE_CODE_OK`
- `AUTHENTICATE_CODE_GENERAL_ERROR`
- `AUTHENTICATE_CODE_WRONG_CREDENTIALS`
- `AUTHENTICATE_CODE_USER_LOCKED`
- `AUTHENTICATE_CODE_IP_BLOCKED`
- `AUTHENTICATE_CODE_ALREADY_LOGGED`
- `AUTHENTICATE_CODE_PASSWORD_INVALID`
- `AUTHENTICATE_CODE_SECOND_FACTOR_AUTH_NEEDED`
- `ACCESS_FORBIDDEN`
- `CONNECTION_LIMIT`
- `INCORRECT_CLIENT_TYPE`

## Important behavior notes
- bundle stores auth/session info in browser storage and keeps explicit expiration timestamps
- both cloud token flow and local token flow exist
- there is an approval-based auth mode (`Approve to login` / supervisor flow)
- configurator uses `/grpc` as an HTTP gateway, not only REST
- host-specific APIs exist (`/hosts`, `/hosts/{host}`), likely for multi-node / multi-domain admin UI

## Open questions
- exact shape of `/v1/authentication/authenticate_ex2` request/response
- exact contract for `/api/v1/auth/tokens`
- exact relation between cloud token, next token, access token, and refresh token
- whether the same auth stack is shared 1:1 with `webclient` or only partially
