# Axxon One API Correctness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make every active Axxon One API request in the runtime either fully documented and correctness-preserving or explicitly rejected instead of silently returning partial or misleading data.

**Architecture:** Keep `scripts/axxon_web_api.py` as the active runtime surface and use `axxon_telegram_vms/` for shared parsing, request-building, and result-shaping helpers. Fix correctness in four passes: normalize `/grpc` transport parsing, resolve event and LPR scope into exact backend subjects before paging, enforce PTZ session cleanup, and replace undocumented archive-frame requests with the documented export contract.

**Tech Stack:** Python 3.11, stdlib `unittest`, `urllib`, Axxon One HTTP API, Axxon One `/grpc` wrapper, checked-in docs under `support/references/`, checked-in protos under `support/protos/`

---

## Current Findings

- `axxon_telegram_vms/client/transport.py:12-39` only parses SSE-style `data:` lines or plain JSON, but `support/references/grpc_examples_of_grpc_api_methods.md:148-170` shows streamed `/grpc` responses as multipart `--ngpboundary` chunks.
- `axxon_telegram_vms/services/event_search.py:331-370` and `scripts/axxon_web_api.py:774-802` only push a single subject into `ReadEvents`, then paginate and filter locally. `support/protos/axxonsoft/bl/events/EventHistory.proto:402-412` explicitly says limit/offset is not reliable for fan-out queries.
- `axxon_telegram_vms/services/license_plate_search.py:393-430` has the same correctness gap for `ReadLprEvents`.
- `scripts/axxon_web_api.py:2050-2066` acquires a PTZ session and sends `GoPreset`, but `support/protos/axxonsoft/bl/ptz/Telemetry.proto:406-423` exposes `ReleaseSessionId` and the runtime never calls it.
- `axxon_telegram_vms/client/transport.py:111-129` and `scripts/axxon_web_api.py:404-416` use `/archive/media/{video_id}/{timestamp}?threshold=...` as a single-frame path, while the checked-in HTTP docs document `/archive/media` for archive streams and `POST /export/archive/...` with `format: "jpg"` for frame export.

## Request Inventory

### Requests That Already Match The Checked-In Docs

- `axxonsoft.bl.domain.DomainService.ListCameras`
- `axxonsoft.bl.events.DomainNotifier.PullEvents`
- `axxonsoft.bl.events.DomainNotifier.DisconnectEventChannel`
- `axxonsoft.bl.logic.LogicService.BeginAlertReview`
- `axxonsoft.bl.logic.LogicService.ContinueAlertReview`
- `axxonsoft.bl.logic.LogicService.CompleteAlertReview`
- `axxonsoft.bl.logic.LogicService.ListMacrosV2`
- `axxonsoft.bl.logic.LogicService.ListMacros`
- `GET /macro/execute/{id}`
- `axxonsoft.bl.security.SecurityService.ListConfig`
- `axxonsoft.bl.security.SecurityService.ListGlobalPermissions`
- `axxonsoft.bl.events.EventHistoryService.FindSimilarObjects`
- `axxonsoft.bl.ptz.TelemetryService.GetPositionInformation`
- `axxonsoft.bl.ptz.TelemetryService.AcquireSessionId`
- `axxonsoft.bl.ptz.TelemetryService.GoPreset`
- `GET /v1/telemetry/presets`
- `POST /export/archive/{VIDEOSOURCEID}/{BEGINTIME}/{ENDTIME}`
- `GET /export/{id}/status`
- `GET /export/{id}/file`
- `DELETE /export/{id}`
- `GET /archive/list/{video_id}`
- `GET /archive/contents/intervals/{video_id}/{end}/{begin}`
- `GET /archive/statistics/depth/{video_id}`
- `GET /live/media/{video_id}`
- `GET /live/media/snapshot/{video_id}`
- `GET /statistics/hardware`
- `GET /statistics/hardware/domain`
- `GET /hosts`
- `GET /hosts/{host}`
- `GET /currentuser`
- `GET /product/version`
- `GET /statistics/webserver`

### Requests That Need Implementation Work

- `/grpc` response parsing for multipart boundary streams
- `EventHistoryService.ReadEvents` execution for multi-subject and name-based search
- `EventHistoryService.ReadLprEvents` execution for multi-subject and name-based search
- `TelemetryService.ReleaseSessionId` integration after PTZ execution
- Archive frame retrieval path used by `media_frame`

## Working Rules

- Use `/opt/homebrew/bin/python3.11` for every verification command in this plan. Do not rely on the system `python3`, which is older on this machine.
- Keep the active runtime in `scripts/axxon_web_api.py`; do not move the runtime surface during this correctness pass.
- Prefer documented server behavior over inferred behavior. If a request shape cannot be proved by `support/references/` or `support/protos/`, remove it from the primary path.
- For distributed event queries, correctness is more important than throughput. Do not silently return partial pages when the backend fan-out semantics are unsafe.
- If an exact implementation is not possible for a query shape, return an explicit truncation or narrowing error instead of pretending the result set is complete.
- Use TDD for each task. Add or extend tests first, run them red, then implement the smallest change that makes them pass.

### Task 1: Normalize `/grpc` Stream Parsing

**Files:**
- Modify: `axxon_telegram_vms/client/transport.py:12-39`
- Modify: `scripts/axxon_web_api.py:144-148`
- Modify: `tests/test_web_api_parsing.py`
- Modify: `tests/test_client_foundation.py`

**Step 1: Write the failing test**

Extend `tests/test_web_api_parsing.py` with multipart coverage:

```python
def test_parse_multipart_ngpboundary_packets(self):
    raw = "\r\n".join(
        [
            "--ngpboundary",
            "Content-Type: application/json; charset=utf-8",
            "Content-Length: 16",
            "",
            '{"result": true}',
            "--ngpboundary",
            "Content-Type: application/json; charset=utf-8",
            "Content-Length: 25",
            "",
            '{"items": [{"id": "1"}]}',
            "--ngpboundary--",
        ]
    )

    out = _parse_grpc_response(raw)

    self.assertEqual(out, [{"result": True}, {"items": [{"id": "1"}]}])
```

Extend `tests/test_client_foundation.py` so the public seam preserves SSE and plain JSON behavior while also accepting multipart payloads.

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_parsing.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_client_foundation.py
```

Expected:
- Multipart parsing test fails because `parse_grpc_response()` currently returns `[]`.
- Existing SSE and plain JSON assertions still pass.

**Step 3: Write minimal implementation**

Implement in `axxon_telegram_vms/client/transport.py`:

- Detect multipart payloads that start with `--ngpboundary` or another `--<boundary>` marker.
- Split the stream into body chunks, discard per-part headers, and `json.loads()` only the body section of each chunk.
- Preserve the current SSE parser for `data:` lines.
- Preserve the current plain JSON parser as the final fallback.
- Ignore malformed chunks, but do not drop valid chunks that appear before or after them.

Keep `scripts/axxon_web_api.py` delegating to the shared parser so both the package seam and the active script runtime stay aligned.

**Step 4: Run focused verification**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_parsing.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_client_foundation.py
```

Expected:
- Multipart, SSE, JSON object, and JSON list parsing all pass.
- No other transport helper regression appears in the foundation test file.

**Step 5: Commit**

```bash
git add axxon_telegram_vms/client/transport.py scripts/axxon_web_api.py tests/test_web_api_parsing.py tests/test_client_foundation.py
git commit -m "fix: parse multipart grpc responses"
```

### Task 2: Make Event Search Exact Before Paging

**Files:**
- Create: `axxon_telegram_vms/services/scope_resolution.py`
- Modify: `axxon_telegram_vms/services/event_search.py:331-370`
- Modify: `axxon_telegram_vms/services/__init__.py`
- Modify: `scripts/axxon_web_api.py:169-211`
- Modify: `scripts/axxon_web_api.py:774-802`
- Test: `tests/test_event_search_service.py`
- Create: `tests/test_scope_resolution_service.py`
- Create: `tests/test_event_search_execution.py`

**Step 1: Write the failing test**

Create `tests/test_scope_resolution_service.py` with inventory-to-subject resolution coverage:

```python
import unittest

from axxon_telegram_vms.services.scope_resolution import resolve_scope_subjects
from axxon_telegram_vms.services import build_event_search_request


CAMERA_ROWS = [
    {
        "access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        "display_name": "Gate",
        "display_id": "1",
        "detectors": [{"access_point": "hosts/ServerA/AppDataDetector.1/EventSupplier", "display_name": "LPR"}],
    },
    {
        "access_point": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
        "display_name": "Gate",
        "display_id": "2",
        "detectors": [{"access_point": "hosts/ServerB/AppDataDetector.7/EventSupplier", "display_name": "LPR"}],
    },
]


class ScopeResolutionTests(unittest.TestCase):
    def test_resolve_camera_name_and_host_to_exact_subjects(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            hosts=["ServerA"],
            camera_names=["Gate"],
        )

        resolved = resolve_scope_subjects(request.query.scope, CAMERA_ROWS, include_detectors=True)

        self.assertEqual(resolved.camera_access_points, ("hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",))
        self.assertEqual(resolved.detector_access_points, ())
```

Create `tests/test_event_search_execution.py` with a fake client that proves multi-scope search does not use one global offset across all subjects:

```python
class EventSearchExecutionTests(unittest.TestCase):
    def test_event_search_reads_each_exact_subject_and_merges_results(self):
        client = FakeEventClient(...)
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_names=["Gate"],
            hosts=["ServerA", "ServerB"],
            page_size=2,
        )

        rows, scanned, complete = _event_search_rows(client, request, batch_size=50)

        self.assertEqual([row["id"] for row in rows], ["evt-a", "evt-b"])
        self.assertEqual(client.read_calls, [
            {"subject": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0", "offset": 0},
            {"subject": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0", "offset": 0},
        ])
        self.assertTrue(complete)
```

Also extend `tests/test_event_search_service.py` so backend-planning logic no longer assumes a single `subject`.

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_event_search_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_scope_resolution_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_event_search_execution.py
```

Expected:
- The new scope-resolution module is missing.
- `_event_search_rows()` still performs a single paged read and cannot produce exact per-subject execution.

**Step 3: Write minimal implementation**

Implement a shared resolver in `axxon_telegram_vms/services/scope_resolution.py`:

- Convert `host`, `domain`, `camera`, `camera_ap`, `detector`, and `detector_ap` selectors into exact access points using `list_cameras(view="VIEW_MODE_FULL")` inventory.
- Preserve the distinction between camera subjects and detector subjects.
- Partition resolved subjects by node if needed, because `SearchFilter.subjects` must stay on one node.
- Return explicit resolution metadata: matched subjects, unresolved selectors, and whether any local-only filters remain.

Implement event-search execution changes:

- Keep `build_event_search_backend_request()` responsible only for one exact backend shard, not the whole broad query.
- In `_event_search_rows()`, fetch camera inventory once, resolve exact subjects, then execute `ReadEvents` per resolved subject or per same-node shard.
- Merge all backend rows locally by `(timestamp, id)` before paging the final result.
- Only use backend `offset` for a single resolved shard. Do not share one global offset across multiple subjects.
- If the query still contains a predicate that cannot be pushed down exactly, exhaust all resolved shards for the bounded time window before final paging. If the runtime has to stop early because of a safety cap, surface that as explicit truncation in the result metadata instead of pretending the page is complete.

**Step 4: Run focused verification**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_scope_resolution_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_event_search_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_event_search_execution.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_surface.py
```

Expected:
- Scope selectors resolve to exact subjects.
- Event search merges multi-subject results without reusing invalid fan-out offsets.
- CLI surface remains intact.

**Step 5: Commit**

```bash
git add axxon_telegram_vms/services/scope_resolution.py axxon_telegram_vms/services/event_search.py axxon_telegram_vms/services/__init__.py scripts/axxon_web_api.py tests/test_event_search_service.py tests/test_scope_resolution_service.py tests/test_event_search_execution.py tests/test_web_api_surface.py
git commit -m "fix: make event search exact before paging"
```

### Task 3: Apply The Same Exact-Scope Model To LPR Search

**Files:**
- Modify: `axxon_telegram_vms/services/license_plate_search.py:393-430`
- Modify: `axxon_telegram_vms/services/__init__.py`
- Modify: `scripts/axxon_web_api.py:213-243`
- Modify: `scripts/axxon_web_api.py:2373-2408`
- Test: `tests/test_license_plate_search_service.py`
- Create: `tests/test_license_plate_search_execution.py`

**Step 1: Write the failing test**

Create `tests/test_license_plate_search_execution.py`:

```python
import unittest

from axxon_telegram_vms.services import build_license_plate_search_request
from axxon_web_api import _license_plate_search_rows


class LicensePlateSearchExecutionTests(unittest.TestCase):
    def test_contains_search_reads_each_resolved_camera_scope(self):
        client = FakeLprClient(...)
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            contains="123",
            camera_names=["Gate"],
            hosts=["ServerA", "ServerB"],
            page_size=5,
        )

        rows, scanned, complete = _license_plate_search_rows(client, request, batch_size=50)

        self.assertEqual([row["plate"] for row in rows], ["AB1234", "CD1234"])
        self.assertEqual(len(client.read_calls), 2)
        self.assertTrue(complete)
```

Extend `tests/test_license_plate_search_service.py` so backend planning no longer assumes only one subject and keeps native `search_predicate` only when it remains exact.

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_license_plate_search_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_license_plate_search_execution.py
```

Expected:
- The runtime does not have a correctness-preserving multi-scope LPR execution path yet.
- Service tests still encode a single `subject` contract.

**Step 3: Write minimal implementation**

Implement in `axxon_telegram_vms/services/license_plate_search.py` and `scripts/axxon_web_api.py`:

- Reuse the shared scope-resolution helper from Task 2.
- Treat exact plate and mask search as native backend predicates when possible.
- Execute `ReadLprEvents` per exact subject or per same-node shard instead of one broad fan-out request with a shared offset.
- Merge rows locally before pagination.
- Preserve explicit truncation metadata when an operator asks for a search shape that still cannot be fully exhausted under the safety cap.

Keep the request model aligned with the proto:

- `values` for exact plate equality
- `search_predicate` for mask and contains searches
- resolved `subjects` only after inventory-based narrowing

**Step 4: Run focused verification**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_license_plate_search_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_license_plate_search_execution.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_scope_resolution_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_surface.py
```

Expected:
- LPR search uses native plate predicates and exact subject fan-out.
- Multi-camera or name-scoped queries no longer miss hits because of a shared backend offset.

**Step 5: Commit**

```bash
git add axxon_telegram_vms/services/license_plate_search.py axxon_telegram_vms/services/__init__.py scripts/axxon_web_api.py tests/test_license_plate_search_service.py tests/test_license_plate_search_execution.py tests/test_scope_resolution_service.py tests/test_web_api_surface.py
git commit -m "fix: make lpr search exact before paging"
```

### Task 4: Release PTZ Sessions Deterministically

**Files:**
- Modify: `scripts/axxon_web_api.py:654-687`
- Modify: `scripts/axxon_web_api.py:1992-2105`
- Modify: `tests/test_web_api_surface.py`
- Create: `tests/test_web_api_ptz_execution.py`

**Step 1: Write the failing test**

Create `tests/test_web_api_ptz_execution.py` with a fake client proving release happens on both success and failure:

```python
import unittest

from axxon_web_api import run_ptz_execute_flow


class PtzExecutionTests(unittest.TestCase):
    def test_release_session_runs_after_successful_preset(self):
        client = FakePtzClient()

        result = run_ptz_execute_flow(client, request=..., camera=..., preset=..., policy=...)

        self.assertTrue(result["execution"]["attempted"])
        self.assertEqual(client.calls, ["acquire", "go_preset", "release"])

    def test_release_session_runs_after_command_failure(self):
        client = FakePtzClient(go_preset_error="boom")

        result = run_ptz_execute_flow(client, request=..., camera=..., preset=..., policy=...)

        self.assertEqual(client.calls, ["acquire", "go_preset", "release"])
        self.assertFalse(result["execution"]["ok"])
```

Also extend `tests/test_web_api_surface.py` so the active runtime surface contains `TelemetryService.ReleaseSessionId`.

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_surface.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_ptz_execution.py
```

Expected:
- `ReleaseSessionId` is absent from the active runtime.
- No helper exists for a deterministic acquire/go/release flow.

**Step 3: Write minimal implementation**

Implement in `scripts/axxon_web_api.py`:

- Add `AxxonClient.ptz_release_session(session_id, access_point)` that calls `axxonsoft.bl.ptz.TelemetryService.ReleaseSessionId`.
- Extract the current PTZ execute block into a small helper such as `run_ptz_execute_flow(...)` so it can be tested without the CLI parser.
- Wrap `GoPreset` execution in `try/finally` so release is attempted whenever acquire succeeded and returned a session id.
- Record release failures separately in logs and in the result payload without hiding the original `GoPreset` failure.

**Step 4: Run focused verification**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_ptz_execution.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_ptz_control_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_surface.py
```

Expected:
- Release is attempted after success and after `GoPreset` failure.
- Existing PTZ guardrail/service tests still pass.

**Step 5: Commit**

```bash
git add scripts/axxon_web_api.py tests/test_web_api_surface.py tests/test_web_api_ptz_execution.py
git commit -m "fix: release ptz sessions after preset control"
```

### Task 5: Replace Undocumented Archive Frame Retrieval

**Files:**
- Modify: `scripts/axxon_web_api.py:404-416`
- Modify: `axxon_telegram_vms/client/transport.py:111-129`
- Modify: `tests/test_client_foundation.py`
- Create: `tests/test_web_api_archive_frame.py`

**Step 1: Write the failing test**

Create `tests/test_web_api_archive_frame.py`:

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from axxon_web_api import AxxonClient


class ArchiveFrameTests(unittest.TestCase):
    def test_media_frame_uses_export_archive_jpg_contract(self):
        client = FakeArchiveClient()
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "frame.jpg"
            client.media_frame("ServerA/DeviceIpint.1/SourceEndpoint.video:0:0", "20260310T105500", out)

        self.assertEqual(client.export_calls[0]["begin_ts"], "20260310T105500")
        self.assertEqual(client.export_calls[0]["end_ts"], "20260310T105500")
        self.assertEqual(client.export_calls[0]["export_format"], "jpg")
```

Update `tests/test_client_foundation.py` so it no longer treats `build_archive_frame_url()` as the endorsed single-frame contract. Replace that assertion with checks for the documented export request helper or for the `media_frame()` behavior via the fake client.

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_client_foundation.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_archive_frame.py
```

Expected:
- `media_frame()` still performs a direct `GET /archive/media/...`.
- Foundation test still encodes the undocumented URL shape.

**Step 3: Write minimal implementation**

Implement:

- Change `AxxonClient.media_frame()` to use the documented export path with `begin_ts == end_ts`, `export_format="jpg"`, and a `waittimeout` derived from the requested threshold or a safe documented minimum.
- Remove the undocumented `/archive/media/{video_id}/{timestamp}?threshold=...` request from the primary frame path.
- Either delete `build_archive_frame_url()` if no callers remain, or rename and comment it as a legacy archive-stream helper rather than a supported frame helper.

Do not add a silent fallback back to the undocumented request shape. If the export flow fails, return the export error.

**Step 4: Run focused verification**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_client_foundation.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_archive_frame.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_surface.py
```

Expected:
- Archive frame retrieval uses the documented export contract.
- No transport/helper test still depends on the undocumented single-frame URL.

**Step 5: Commit**

```bash
git add scripts/axxon_web_api.py axxon_telegram_vms/client/transport.py tests/test_client_foundation.py tests/test_web_api_archive_frame.py tests/test_web_api_surface.py
git commit -m "fix: use documented export contract for archive frames"
```

### Task 6: Run The Final Regression Matrix And Update Operator Docs

**Files:**
- Modify: `support/docs/REGRESSION_CHECKLIST.md`
- Modify: `scripts/full_verification.py`
- Test: `tests/test_web_api_parsing.py`
- Test: `tests/test_client_foundation.py`
- Test: `tests/test_event_search_service.py`
- Test: `tests/test_scope_resolution_service.py`
- Test: `tests/test_event_search_execution.py`
- Test: `tests/test_license_plate_search_service.py`
- Test: `tests/test_license_plate_search_execution.py`
- Test: `tests/test_ptz_control_service.py`
- Test: `tests/test_web_api_ptz_execution.py`
- Test: `tests/test_web_api_archive_frame.py`
- Test: `tests/test_web_api_surface.py`

**Step 1: Write the failing test or checklist delta**

Update `support/docs/REGRESSION_CHECKLIST.md` to add explicit operator checks for:

- `/grpc` multipart parsing
- multi-camera event search
- multi-camera LPR search
- PTZ acquire/go/release lifecycle
- archive frame export via `jpg`

Update `scripts/full_verification.py` so the live verification set exercises at least:

- one `ReadEvents` call
- one `ReadLprEvents` call
- one frame export
- one PTZ session lifecycle only if PTZ is explicitly enabled for the target camera

**Step 2: Run the local regression suite**

Run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_parsing.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_client_foundation.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_event_search_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_scope_resolution_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_event_search_execution.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_license_plate_search_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_license_plate_search_execution.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_ptz_control_service.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_ptz_execution.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_archive_frame.py
PYTHONPATH=. /opt/homebrew/bin/python3.11 tests/test_web_api_surface.py
```

Expected:
- All focused correctness tests pass under Python 3.11.

**Step 3: Run live verification against a real server**

Only if host and credentials are available in the environment, run:

```bash
PYTHONPATH=. /opt/homebrew/bin/python3.11 scripts/full_verification.py
```

Expected:
- `full_verification_results.json` shows pass/fail per live request family.
- Any live-only failure is captured with the exact backend error instead of being ignored.

**Step 4: Record the final outcome**

Update `support/docs/REGRESSION_CHECKLIST.md` with:

- date of validation
- Python interpreter used
- whether live verification ran
- any intentionally deferred follow-up, such as evaluating `FindSimilarObjects2` as a separate enhancement

**Step 5: Commit**

```bash
git add support/docs/REGRESSION_CHECKLIST.md scripts/full_verification.py full_verification_results.json
git commit -m "test: add regression matrix for api correctness"
```

## Non-Goals

- Do not migrate face search from `FindSimilarObjects` to `FindSimilarObjects2` in this plan. That is a capability expansion, not a correctness fix for currently wrong requests.
- Do not redesign the Telegram UX while doing this work.
- Do not rewrite the active runtime out of `scripts/`.
- Do not add undocumented fallbacks just to preserve old behavior.

## Exit Criteria

- `/grpc` parsing accepts documented multipart boundary streams, SSE streams, and plain JSON payloads.
- Event search and LPR search either run against exact resolved subjects or explicitly declare truncation/incompleteness.
- PTZ preset execution always attempts `ReleaseSessionId` after a successful acquire.
- Archive frame retrieval uses the documented export contract.
- The request families already verified as correct remain unchanged except for regression-test coverage.

Plan complete and saved to `support/docs/plans/2026-03-12-axxon-one-api-correctness-plan.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
