# Macros / Events / Push / Web Query (bundle extraction)

Sources inspected:
- `web_configurator_ui_unpacked/build/assets/1.chunk.js`
- configurator locale chunks for stable enum labels

## Macro action enum names found
A concrete action enum is embedded in the bundle (names preserved in minified output):

- `WRITE_ARCHIVE_ACTION = "write_archive"`
- `RAISE_ALERT_ACTION = "raise_alert"`
- `CLOSE_ALERT_ACTION = "close_alert"`
- `SWITCH_RELAY = "switch_relay"`
- `ARM_STATE = "arm_state"`
- `DISARM_STATE = "disarm_state"`
- `REPLICATION = "replication"`
- `EXPORT = "export"`
- `GOTO_PTZ = "goto_ptz"`
- `INVOKE_MACRO_ACTION = "macro"`
- `WEB_QUERY_ACTION = "web_query"`
- `AUDIO_NOTIFICATION = "audio_notification"`
- `EMAIL_NOTIFICATION = "email_notification"`
- `PUSH_EVENT_ACTION = "push_event"`
- `SERVICE_STATE_ACTION = "service_state"`
- `ACFA = "acfa"`
- `GUI = "gui"`

Macro flow/control enum values also appear:
- `AFTER`
- `TIMEOUT`
- `WAIT`
- `ABORT`
- `CHECK`
- `ACTION`

## Macro event source / category clues
A second enum groups event domains:
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

This is useful because it shows the event engine spans system health, archive/storage, analytics/detectors, access/control, and ACFA.

## Push event action clues
Concrete push-event form fields present in the UI strings:
- title
- subtitle
- body
- recipients
- during
- offset
- all-in-one notification toggle

Bundle keys:
- `macros.push-event-action-form.title`
- `...subtitle`
- `...body`
- `...recipients`
- `...during`
- `...offset`
- `...all-notification`

So push events are not just internal signals; they appear to support templated user-facing notifications with recipient selection and time-windowing/offset semantics.

## Web query action clues
Concrete web-query form fields found:
- auth method
- query method
- port
- username
- path
- query

Enumerated options:
- auth: `AM_BASIC`, `QA_DIGEST`
- method: `QM_POST`, `QM_GET`, `QM_PUT`, `QM_DELETE`

Bundle keys:
- `macros.web-query-action-form.auth-method`
- `...auth-method-AM_BASIC`
- `...auth-method-QA_DIGEST`
- `...query-method-QM_POST|GET|PUT|DELETE`
- `...port`
- `...username`
- `...path`
- `...query`

This is strong evidence that macros can call arbitrary HTTP endpoints with at least Basic/Digest auth and standard CRUD verbs.

## Event/condition catalog clues
Concrete condition labels visible in bundle strings include:

Detector / analytics:
- `MotionDetected`
- `QueueDetected`
- `PeopleCount`
- `PeopleIn` / `PeopleOut`
- `faceAppeared`
- `plateRecognized`
- `VehicleRecognized`
- `TamperingDetected`
- `NoiseAudio`
- `SignalAudio`

Archive / alert / arm:
- `archive_write_on` / `archive_write_off`
- `alert_ac_alert_raised`
- `alert_ac_alert_taken`
- `alert_ac_alert_missed`
- `alert_ac_alert_closed`
- `arm_cs_arm` / `arm_cs_disarm` / `arm_cs_armprivate`

Device / server / license / storage health:
- `device_ipds_connected` / `...disconnected` / `...signal_lost` / `...signal_restored` / `...authorization_failed`
- `server_state_ss_offline` / `...online`
- `license_ls_unavailable` / `...ok`
- `statistics_archive_channel_starving`
- `statistics_archive_usage`
- `statistics_disk_space_usage`
- `statistics_memory_total_usage`
- `statistics_net_max_usage`
- `statistics_cpu_total_usage`
- `volume_health_vh_corrupted` / `...restored`

This is a broad event/rule engine, not just detector automation.

## ACFA integration clues inside macros
Macro action labels explicitly include ACFA:
- `macros.rule.acfa` = execute ACFA action
- ACFA action form fields: `component`, `action`
- visible ACFA actions: `ALARM`, `HANDLE_ALARM`, `ARM`, `DISARM`

That means ACFA is a first-class macro target, not an external plugin-only surface.
