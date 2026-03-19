# Runtime Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Stabilize the active `scripts/` runtime so local imports, annotation evaluation, and subprocess failure handling are deterministic and operator-safe.

**Architecture:** Keep the existing `scripts/` runtime ownership intact while adding a narrow compatibility layer and a shared subprocess helper. Fix the import/runtime contract first, then migrate subprocess call sites, then tighten Telegram failure presentation without changing command or callback namespaces.

**Tech Stack:** Python 3, `unittest`, `python-telegram-bot`, subprocess-based Axxon CLI bridge

---

### Task 1: Fix Local Runtime Import And Annotation Compatibility

**Files:**
- Create: `scripts/__init__.py`
- Create: `tests/test_runtime_compatibility.py`
- Modify: `scripts/tg_ui_common.py`
- Modify: `scripts/camera_catalog.py`
- Modify: `scripts/media_utils.py`
- Modify: `scripts/axxon_web_api.py`
- Modify: `scripts/axxon_tg_bot.py`

**Step 1: Write the failing test**

```python
import importlib
import unittest


class RuntimeCompatibilityTests(unittest.TestCase):
    def test_scripts_package_resolves_to_repo(self):
        mod = importlib.import_module("scripts")
        self.assertIn("axxon-telegram-vms/scripts", str(getattr(mod, "__file__", "")))

    def test_active_script_modules_import_under_current_python(self):
        importlib.import_module("scripts.tg_ui_common")
        importlib.import_module("scripts.camera_catalog")
        importlib.import_module("scripts.media_utils")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_runtime_compatibility -v`
Expected: FAIL because `scripts` resolves incorrectly and one or more modules crash at import time.

**Step 3: Write minimal implementation**

```python
# scripts/__init__.py
"""Active runtime package for local imports and tests."""
```

Add postponed annotation evaluation to the script modules using `X | None` style hints.

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_runtime_compatibility -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/__init__.py tests/test_runtime_compatibility.py \
  scripts/tg_ui_common.py scripts/camera_catalog.py scripts/media_utils.py \
  scripts/axxon_web_api.py scripts/axxon_tg_bot.py
git commit -m "fix: stabilize script runtime imports"
```

### Task 2: Introduce Shared Subprocess Helper

**Files:**
- Create: `scripts/process_bridge.py`
- Create: `tests/test_process_bridge.py`
- Modify: `scripts/tg_ui_common.py`
- Modify: `scripts/axxon_tg_bot.py`

**Step 1: Write the failing test**

```python
import json
import unittest
from unittest.mock import patch

from scripts.process_bridge import CommandExecutionError, run_command


class ProcessBridgeTests(unittest.TestCase):
    @patch("scripts.process_bridge.subprocess.run")
    def test_run_command_parses_json_stdout(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({"ok": True})
        mock_run.return_value.stderr = ""
        self.assertEqual(run_command(["tool"], timeout_sec=1).parsed, {"ok": True})
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_process_bridge -v`
Expected: FAIL because `scripts.process_bridge` does not exist.

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    text: str
    parsed: object


class CommandExecutionError(RuntimeError):
    pass
```

Then implement `run_command()` with timeout, stdout/stderr capture, JSON parsing, and plain-text fallback.

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_process_bridge -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/process_bridge.py tests/test_process_bridge.py \
  scripts/tg_ui_common.py scripts/axxon_tg_bot.py
git commit -m "refactor: unify subprocess command handling"
```

### Task 3: Harden Telegram Failure Presentation

**Files:**
- Modify: `scripts/axxon_tg_bot.py`
- Modify: `tests/test_server_info_resilience.py`
- Modify: `tests/test_ui_payloads.py`

**Step 1: Write the failing test**

```python
def test_callback_failure_keeps_recovery_button(self):
    with patch("axxon_tg_ui._callback_payload_impl", side_effect=RuntimeError("boom")):
        payload = callback_payload([], 1800, "srv:menu")
    self.assertTrue(payload["buttons"])
```

Add one more test for bot-side subprocess failure shaping if missing.

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_server_info_resilience tests.test_ui_payloads -v`
Expected: FAIL once the new bot-side failure expectation is added.

**Step 3: Write minimal implementation**

```python
except CommandExecutionError as exc:
    return {
        "text": f"⚠️ {summary}",
        "buttons": [[btn("🏠 Main", "home")]],
    }
```

Apply the same pattern to bot-owned command/callback paths that currently surface raw runtime errors.

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_server_info_resilience tests.test_ui_payloads -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/axxon_tg_bot.py tests/test_server_info_resilience.py tests/test_ui_payloads.py
git commit -m "fix: keep telegram failures recoverable"
```

### Task 4: Full Verification

**Files:**
- Modify: `scripts/self_check.sh` if verification needs path or timeout normalization
- Modify: `README.md` only if runtime/version assumptions change materially

**Step 1: Run the focused tests**

Run: `python3 -m unittest tests.test_runtime_compatibility tests.test_process_bridge -v`
Expected: PASS

**Step 2: Run the full unit suite**

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`
Expected: PASS

**Step 3: Run the project verification script**

Run: `./scripts/self_check.sh`
Expected: `SELF_CHECK_OK`

**Step 4: Update docs only if needed**

If the import/runtime contract or local verification contract changes materially, update `README.md` or `support/docs/RUNTIME_BASELINE.md` minimally.

**Step 5: Commit**

```bash
git add scripts/self_check.sh README.md support/docs/RUNTIME_BASELINE.md
git commit -m "docs: align runtime verification contract"
```
