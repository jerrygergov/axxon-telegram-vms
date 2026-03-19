# Camera / Detector / Archive model (bundle extraction)

Sources inspected:
- `web_configurator_ui_unpacked/build/assets/1.chunk.js`
- configurator locale chunks (`8.chunk.js`, `17.chunk.js`, `33.chunk.js`) for stable labels / enum names

## Concrete component types exposed by configurator
The configurator bundle exposes camera-adjacent component classes and creation flows via UI labels and wizard steps:

- `DeviceIpint` → camera device
- `VideoChannel` → video channel / stream-bearing child unit
- `Telemetry` → PTZ/telemetry child
- `EmbeddedStorage` → built-in storage on device
- `MultimediaStorage` → archive root object
- `ArchiveVolume` → archive volume / path / size
- `Detector` → built-in detector
- `DetectorEx` → external detector
- `AVDetector` → detector (video analytics style naming in UI)
- `AppDataDetector` → sub-detector / meta-detector
- `VisualElement` → visual element

These names are present in creation labels such as:
- `unit.camera-editor.AVDetector` = create detector
- `unit.camera-editor.Detector` = create internal detector
- `unit.camera-editor.DetectorEx` = create external detector
- `unit.camera-editor.AppDataDetector` = create sub-detector
- `unit.camera-editor.VisualElement` = create visual element
- `steps-unit-factory.create-MultimediaStorage` = create archive
- `steps-unit-factory.create-ArchiveVolume` = create volume

## Archive model clues
Archive-related UI strings strongly imply this model:

- Archive (`MultimediaStorage`) contains one or more `ArchiveVolume` children
- Archive editor shows:
  - storage type
  - volumes
  - bound cameras
  - archive name
  - volume path
  - volume size
- Camera editor has separate tabs for:
  - `archive_tab`
  - `embedded_tab`
  - `streams_tab`
  - `telemetry_tab`
  - `detectors`

Concrete archive / binding phrases from bundle:
- `units.bind-to-archives`
- `units.bind-channel-to-archives`
- `unit.archiveBinding`
- `unit.recordingMode`
- `unit.camera-bar-editor.arch_params`
- `unit.camera-bar-editor.configure_contexts`
- `unit.camera-bar-editor.configure_replication`
- `unit.camera-bar-editor.replication_params`

This suggests camera/channel-to-archive binding is explicit and per-channel, not just per device.

## Camera stream model clues
Configurator strings expose up to three stream properties on a camera/unit:
- `main-stream`
- `second-stream`
- `third-stream`

Other stream-related flags:
- `onlyKeyFrames`
- `useForGreenStream` (adaptive / optimal stream selection)
- `breakUnusedConnections` (stop unused streaming from camera to server)
- `isVideoBufferOn`

The detector wizard also binds detectors to a chosen `VideoChannel` and stream flavor:
- `step-detector-factory.videoChannel`
- `stream-high`
- `stream-low`
- `stream`

## Detector model clues
Detector flow appears layered:

1. choose video channel
2. choose detector type
3. optionally avoid re-creating if already exists
4. configure detector
5. optionally create macros

Concrete hints:
- `step-detector-factory.not-create-detector-again`
- `info-message.macro.detector_already_connected_to_channel`
- `unit.camera-editor.sub-detectors`
- detector conditions reference detector lifecycle events:
  - `detector_began`
  - `detector_ended`
  - `detector_happened`
  - `detector_specified`
  - `detectorParameters`

This points to detector instances attached to channels, with sub-detectors and event-param filtering.

## Domain / camera APIs found in configurator bundle
Concrete calls in `1.chunk.js`:

- `GET /domain/cameras`
- `POST /domain/cameras:batchGet`
- gRPC `/grpc` → `axxonsoft.bl.domain.DomainService.ListComponents`
- gRPC `/grpc` → `axxonsoft.bl.domain.DomainService.ListAcfaComponents2`
- gRPC `/grpc` → `axxonsoft.bl.domain.DomainService.BatchGetAcfaComponents`

Interpretation: classic camera objects are exposed over REST-ish `/domain/cameras`, while richer domain traversal and ACFA inventory use the gRPC-over-HTTP gateway.

## Practical reverse-engineering takeaways
- Treat **camera**, **video channel**, **archive binding**, **telemetry**, and **detectors** as separate but linked entities.
- Archive configuration is multi-level: archive → volumes, plus camera/channel binding and recording/replication parameters.
- Detector objects are not just boolean features on a camera; the UI suggests first-class units with subtype hierarchy and macro/event wiring.
