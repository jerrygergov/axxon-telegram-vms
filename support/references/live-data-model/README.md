# Live Axxon JSON data model

Generated from the current test server using real API responses.

## Saved files
- `raw/cameras.full.json` — full camera list response
- `raw/detectors.list.json` — normalized detector list used by the bot
- `raw/alerts.sample.json` — one raw alert event
- `raw/events.recent.json` — recent detector events sample
- `raw/events.by-detector.sample.json` — one sample per detector when available
- `raw/model-summary.json` — compact recursive field/type summary

## Notes
- Camera/display labels often become operator-friendly when combining `display_id + display_name`.
- Alerts carry useful operator text in `localization.text`, and often richer state/priority in `body.states[0]`.
- Detector events carry user-facing names in `body.origin_ext.friendly_name` and `body.detector_ext.friendly_name`.
- Alert root body may embed detector/macro details under `body.detector` and `body.macro`.