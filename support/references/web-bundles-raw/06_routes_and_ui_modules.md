# 06 Routes and UI Modules

## Web Configurator routes confirmed in bundle
- `/devices`
- `/groups`
- `/detectors`
- `/storage`
- `/templates`
- `/users`
- `/roles`
- `/time_zones`
- `/macros`
- `/configurator`

## Web Configurator domain areas confirmed by code / strings
- devices and discovery
- groups
- detectors
- storage / archives / volumes
- templates
- users / roles / permissions
- time zones
- macros
- ACFA
- telemetry / PTZ
- privacy mask
- replication
- embedded storage
- manual camera add

## Webclient pages / modes confirmed
- `index.html` → main app
- `embedded.html` / `embedded.js`
- `stats.html` / `stats.js`
- `bookmarks.html` / `bookmarks.js`
- `reports/` with separate report viewer/designer assets
- service worker registration is present (`service-worker.js`)

## Webclient application modes / concepts seen in bootstrap
- `LIVE`
- `ARCH`
- `ARCH_SEARCH`
- layouts
- camera selection
- playback setup
- embedded postMessage handling

## Notes
- web configurator is a feature-heavy admin SPA
- webclient is a separate operator/viewer SPA with live/archive/layout concerns
- both are built bundles with lazy-loaded chunks; source code is not present

## Next reverse targets
1. `webclient` bootstrap and connection layer (`app.js`, `conn.js`)
2. configurator lazy chunks around macros / telemetry / ACFA
3. route-to-chunk mapping for configurator chunks 39-48 and others
