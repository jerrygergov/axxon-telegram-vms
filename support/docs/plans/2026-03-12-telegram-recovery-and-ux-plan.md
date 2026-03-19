# Telegram Recovery And UX Rehabilitation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Stabilize broken Telegram bot flows, make the bot reliably runnable and testable, and replace the current operator-heavy text surface with a guided Telegram-first UX.

**Architecture:** Keep `scripts/` as the active runtime and treat `axxon_telegram_vms/` as additive support only. Recover the bot in three passes: first make the runtime/test environment deterministic, then fix and simplify the Telegram interaction model, then add end-to-end verification around the highest-risk flows.

**Tech Stack:** Python, `python-telegram-bot`, `unittest`, shell scripts, Axxon One Web API (`/grpc`, `/archive/media`, `/export`)

---

## Current Findings

- The active runtime still lives in [scripts/axxon_tg_bot.py](scripts/axxon_tg_bot.py), [scripts/axxon_tg_ui.py](scripts/axxon_tg_ui.py), and [scripts/axxon_web_api.py](scripts/axxon_web_api.py).
- The UI copy is still command-centric and exposes internal concepts such as raw IDs, `key=value` syntax, and API-shaped terminology in user-facing text.
- The local validation path currently fails before Telegram-specific regressions can even be trusted:
  - `python3` on this machine is `3.9.12`, but the codebase uses `X | None` annotations without `from __future__ import annotations`.
  - `scripts.*` imports are shadowed by an installed third-party `scripts` package because the repository has no local [scripts/__init__.py](scripts/__init__.py).
- The highest-risk runtime files by size and responsibility are:
  - [scripts/axxon_tg_bot.py](scripts/axxon_tg_bot.py)
  - [scripts/axxon_web_api.py](scripts/axxon_web_api.py)
  - [scripts/axxon_tg_ui.py](scripts/axxon_tg_ui.py)
- Existing tests already cover useful surfaces and should be extended, not bypassed:
  - [tests/test_ui_payloads.py](tests/test_ui_payloads.py)
  - [tests/test_telegram_commands_menu.py](tests/test_telegram_commands_menu.py)
  - [tests/test_telegram_face_search_wizard_bot.py](tests/test_telegram_face_search_wizard_bot.py)
  - [tests/test_subscription_runtime.py](tests/test_subscription_runtime.py)

## Working Rules

- Do not rewrite into `axxon_telegram_vms/` during this recovery plan.
- Fix runtime determinism before changing user-visible behavior.
- Use TDD for every bugfix and every user-facing text/navigation change.
- Keep slash commands and callback prefixes backward-compatible unless a migration alias is also added.
- Prefer guided Telegram interactions over exposing typed syntax in the primary path.

### Task 1: Stabilize The Runtime And Test Harness

**Files:**
- Create: `scripts/__init__.py`
- Modify: `scripts/self_check.sh`
- Modify: `scripts/run_axxon_tg_bot.sh`
- Modify: `README.md`
- Test: `tests/test_config_loader.py`
- Test: `tests/test_ui_payloads.py`
- Test: `tests/test_telegram_face_search_wizard_bot.py`
- Create: `tests/test_runtime_environment.py`

**Step 1: Write the failing test**

Add `RuntimeEnvironmentTests` in `tests/test_runtime_environment.py` covering:

```python
import importlib.util
import unittest
from pathlib import Path


class RuntimeEnvironmentTests(unittest.TestCase):
    def test_local_scripts_package_wins_import_resolution(self):
        spec = importlib.util.find_spec("scripts")
        self.assertIsNotNone(spec)
        self.assertIn("axxon-telegram-vms/scripts", str(spec.origin))

    def test_runtime_declares_supported_python_version(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("Python 3.11", readme)
```

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_runtime_environment -v
```

Expected:
- `scripts` resolves to site-packages instead of the repository.
- README does not clearly pin the supported Python version/runtime expectation.

**Step 3: Write minimal implementation**

Implement:
- Add `scripts/__init__.py` so `scripts.*` imports resolve locally.
- Pick one runtime policy and apply it consistently:
  - Recommended: standardize on Python `3.11+` and make [scripts/self_check.sh](scripts/self_check.sh) and [scripts/run_axxon_tg_bot.sh](scripts/run_axxon_tg_bot.sh) fail fast with a clear version error.
  - Alternative only if 3.9 support is required: add `from __future__ import annotations` to all active `scripts/*.py` and any directly imported package modules, then verify no runtime syntax regressions remain.
- Update [README.md](README.md) to state the supported Python version and startup assumptions.

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_runtime_environment -v
python3 -m unittest tests.test_config_loader tests.test_ui_payloads tests.test_telegram_face_search_wizard_bot -v
```

Expected:
- Local imports resolve correctly.
- Environment assumptions are explicit.
- UI tests at least import successfully under the chosen Python policy.

**Step 5: Commit**

```bash
git add scripts/__init__.py scripts/self_check.sh scripts/run_axxon_tg_bot.sh README.md tests/test_runtime_environment.py
git commit -m "fix: stabilize runtime import and python version contract"
```

### Task 2: Make The Bot Observable Before Fixing Telegram Flows

**Files:**
- Modify: `scripts/axxon_tg_bot.py`
- Modify: `scripts/tg_ui_common.py`
- Modify: `scripts/axxon_tg_ui.py`
- Test: `tests/test_telegram_face_search_wizard_bot.py`
- Create: `tests/test_bot_callback_diagnostics.py`

**Step 1: Write the failing test**

Add `BotCallbackDiagnosticsTests` in `tests/test_bot_callback_diagnostics.py` covering:

```python
class BotCallbackDiagnosticsTests(unittest.TestCase):
    def test_callback_failures_return_operator_safe_message(self):
        payload = {
            "text": "⚠️ Action failed. Please try again or return home.",
            "buttons": [[{"text": "🏠 Main", "callback_data": "home"}]],
        }
        self.assertIn("Action failed", payload["text"])
```

Extend [tests/test_telegram_face_search_wizard_bot.py](tests/test_telegram_face_search_wizard_bot.py) to assert that callback failures and invalid wizard state produce explicit user-safe replies instead of silent cancellation.

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_bot_callback_diagnostics tests.test_telegram_face_search_wizard_bot -v
```

Expected:
- Current runtime lacks a normalized failure message contract for callback exceptions and expired state.

**Step 3: Write minimal implementation**

Implement in [scripts/axxon_tg_bot.py](scripts/axxon_tg_bot.py) and [scripts/tg_ui_common.py](scripts/tg_ui_common.py):
- Add one structured helper for Telegram-safe error messages.
- Log callback family, command name, and upstream subprocess/API failure details.
- Add subprocess timeout handling around `run_api` so Telegram actions fail fast with traceable logs.
- Ensure expired draft/wizard state returns a recoverable message and a `home` or local retry button.

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_bot_callback_diagnostics tests.test_telegram_face_search_wizard_bot tests.test_ui_payloads -v
```

Expected:
- Failures are visible in logs and understandable in chat.
- Wizard and callback regressions are covered by tests.

**Step 5: Commit**

```bash
git add scripts/axxon_tg_bot.py scripts/tg_ui_common.py scripts/axxon_tg_ui.py tests/test_bot_callback_diagnostics.py tests/test_telegram_face_search_wizard_bot.py
git commit -m "fix: add observable telegram callback failure handling"
```

### Task 3: Replace The Home And Help Surface With Guided Navigation

**Files:**
- Modify: `scripts/axxon_tg_bot.py`
- Modify: `scripts/axxon_tg_ui.py`
- Test: `tests/test_telegram_commands_menu.py`
- Test: `tests/test_ui_payloads.py`

**Step 1: Write the failing test**

Extend [tests/test_ui_payloads.py](tests/test_ui_payloads.py) with assertions like:

```python
self.assertIn("Choose what you want to do", payload["text"])
self.assertNotIn("Investigate: Search ->", payload["text"])
self.assertIn("Recent alerts", payload["text"])
```

Extend [tests/test_telegram_commands_menu.py](tests/test_telegram_commands_menu.py) to require:
- grouped help text
- clearer bot command descriptions
- removal of operator-hostile text such as “entry/help surfaces”

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_ui_payloads tests.test_telegram_commands_menu -v
```

Expected:
- Current home/help copy still contains internal wording and flat command dumps.

**Step 3: Write minimal implementation**

Implement in [scripts/axxon_tg_ui.py](scripts/axxon_tg_ui.py) and [scripts/axxon_tg_bot.py](scripts/axxon_tg_bot.py):
- Rewrite `home_payload` to use plain action-oriented language:
  - “Recent alerts”
  - “Open cameras”
  - “Find events”
  - “Check server”
- Replace the current flat help text with grouped sections:
  - Monitor
  - Search
  - Archive
  - Subscriptions
  - Admin-only tools
- Keep slash command compatibility, but stop teaching the user the whole command matrix on first contact.
- Preserve admin-only visibility rules.

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_ui_payloads tests.test_telegram_commands_menu -v
```

Expected:
- Home and help text become shorter, clearer, and easier to scan.

**Step 5: Commit**

```bash
git add scripts/axxon_tg_bot.py scripts/axxon_tg_ui.py tests/test_ui_payloads.py tests/test_telegram_commands_menu.py
git commit -m "feat: redesign telegram home and help copy"
```

### Task 4: Simplify Search And Archive UX Around Guided Entry Points

**Files:**
- Modify: `scripts/axxon_tg_ui.py`
- Modify: `scripts/axxon_tg_bot.py`
- Modify: `axxon_telegram_vms/ui/telegram_face_search.py`
- Test: `tests/test_ui_payloads.py`
- Test: `tests/test_telegram_face_search_helpers.py`
- Test: `tests/test_telegram_face_search_wizard_bot.py`

**Step 1: Write the failing test**

Add assertions to [tests/test_ui_payloads.py](tests/test_ui_payloads.py):

```python
self.assertIn("Use the buttons below", payload["text"])
self.assertNotIn("Use explicit key=value terms", payload["text"])
self.assertNotIn("These flows are not fake button workflows", payload["text"])
```

Add assertions to [tests/test_telegram_face_search_helpers.py](tests/test_telegram_face_search_helpers.py) and [tests/test_telegram_face_search_wizard_bot.py](tests/test_telegram_face_search_wizard_bot.py) that the face-search wizard text is short, step-based, and recoverable.

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_ui_payloads tests.test_telegram_face_search_helpers tests.test_telegram_face_search_wizard_bot -v
```

Expected:
- Search/archive help still teaches command syntax first instead of guided choices.

**Step 3: Write minimal implementation**

Implement:
- Rewrite search/archive entry payloads in [scripts/axxon_tg_ui.py](scripts/axxon_tg_ui.py) to separate:
  - primary guided path
  - advanced typed path
- Make the typed syntax secondary and collapsible in wording:
  - “Advanced: send `/search ...`”
  - “Advanced: reply `/face ...` to a photo”
- Keep the face-search wizard as the preferred path for normal users.
- For archive/export, lead with “what this action does” and “what information you need” instead of raw examples first.

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_ui_payloads tests.test_telegram_face_search_helpers tests.test_telegram_face_search_wizard_bot -v
```

Expected:
- Search and archive entry points are understandable without reading implementation syntax.

**Step 5: Commit**

```bash
git add scripts/axxon_tg_ui.py scripts/axxon_tg_bot.py axxon_telegram_vms/ui/telegram_face_search.py tests/test_ui_payloads.py tests/test_telegram_face_search_helpers.py tests/test_telegram_face_search_wizard_bot.py
git commit -m "feat: simplify telegram search and archive entry flows"
```

### Task 5: Rewrite Event, Alert, Camera, And Server Cards For Readability

**Files:**
- Modify: `scripts/axxon_tg_ui.py`
- Modify: `scripts/tg_camera_ui.py`
- Modify: `scripts/tg_server_ui.py`
- Modify: `scripts/tg_admin_ui.py`
- Test: `tests/test_ui_payloads.py`
- Create: `tests/test_telegram_copy_style.py`

**Step 1: Write the failing test**

Create `tests/test_telegram_copy_style.py` with intent-level checks:

```python
class TelegramCopyStyleTests(unittest.TestCase):
    def test_copy_avoids_internal_operator_jargon(self):
        src = Path("scripts/axxon_tg_ui.py").read_text(encoding="utf-8")
        self.assertNotIn("entry/help surfaces", src)
        self.assertNotIn("operator console", src.lower())
```

Extend [tests/test_ui_payloads.py](tests/test_ui_payloads.py) to assert:
- event cards do not lead with raw IDs
- camera cards explain actions plainly
- server payloads summarize health before dumping fields

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_telegram_copy_style tests.test_ui_payloads -v
```

Expected:
- Existing text still contains internal wording and machine-shaped card layouts.

**Step 3: Write minimal implementation**

Implement:
- Event/alert cards:
  - lead with “what happened”, “where”, and “when”
  - move raw IDs below or remove from the main card
  - keep action buttons simple and consistent
- Camera workspace:
  - replace “workspace” wording with action-oriented language
  - shorten live/snapshot/incidents descriptions
- Server/admin cards:
  - surface a short status summary first
  - push detailed counters below a clear divider
- Reuse existing normalized label fields where available instead of duplicating raw fields.

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_telegram_copy_style tests.test_ui_payloads -v
```

Expected:
- Core cards become readable in a chat context.

**Step 5: Commit**

```bash
git add scripts/axxon_tg_ui.py scripts/tg_camera_ui.py scripts/tg_server_ui.py scripts/tg_admin_ui.py tests/test_telegram_copy_style.py tests/test_ui_payloads.py
git commit -m "feat: rewrite telegram cards for readability"
```

### Task 6: Fix Subscription And Live-Monitor User Feedback

**Files:**
- Modify: `scripts/axxon_tg_bot.py`
- Modify: `scripts/axxon_tg_ui.py`
- Modify: `scripts/tg_camera_ui.py`
- Modify: `axxon_telegram_vms/services/subscriptions.py`
- Test: `tests/test_subscription_runtime.py`
- Create: `tests/test_subscription_user_feedback.py`

**Step 1: Write the failing test**

Create `tests/test_subscription_user_feedback.py` with checks like:

```python
class SubscriptionUserFeedbackTests(unittest.TestCase):
    def test_live_monitor_start_message_explains_next_state(self):
        self.assertIn("refreshing", payload["text"])

    def test_subscription_limit_message_offers_recovery_path(self):
        self.assertIn("/subscriptions", text)
```

Extend [tests/test_subscription_runtime.py](tests/test_subscription_runtime.py) beyond string-presence checks to cover:
- limit reached
- duplicate suppression
- stop semantics
- expired subscription draft handling

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_subscription_runtime tests.test_subscription_user_feedback -v
```

Expected:
- Current coverage is too shallow and user messages are still terse/inconsistent.

**Step 3: Write minimal implementation**

Implement:
- normalize subscription and live-monitor status copy in [scripts/axxon_tg_bot.py](scripts/axxon_tg_bot.py) and [scripts/axxon_tg_ui.py](scripts/axxon_tg_ui.py)
- ensure every rejection message has a next action
- tighten subscription ledger tests in [axxon_telegram_vms/services/subscriptions.py](axxon_telegram_vms/services/subscriptions.py)
- make live-monitor start/stop messages reflect actual behavior and current limitations

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_subscription_runtime tests.test_subscription_user_feedback -v
```

Expected:
- Subscription and live-monitor UX becomes understandable and predictable.

**Step 5: Commit**

```bash
git add scripts/axxon_tg_bot.py scripts/axxon_tg_ui.py scripts/tg_camera_ui.py axxon_telegram_vms/services/subscriptions.py tests/test_subscription_runtime.py tests/test_subscription_user_feedback.py
git commit -m "fix: improve subscription and live monitor feedback"
```

### Task 7: Add High-Signal Telegram Smoke Coverage For Broken Flows

**Files:**
- Modify: `scripts/self_check.sh`
- Modify: `scripts/full_verification.py`
- Create: `tests/test_telegram_flow_smoke.py`
- Modify: `support/docs/REGRESSION_CHECKLIST.md`

**Step 1: Write the failing test**

Create `tests/test_telegram_flow_smoke.py` with mocked flow checks covering:
- `/start` home payload
- alerts feed -> open alert
- camera list -> open camera -> live snapshot
- search menu -> face wizard start
- archive menu payload

Minimal pattern:

```python
class TelegramFlowSmokeTests(unittest.TestCase):
    def test_home_payload_contains_core_actions(self):
        self.assertEqual(buttons[0][0]["text"], "📷 Cameras")
```

**Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_telegram_flow_smoke -v
```

Expected:
- No single smoke suite currently covers the end-user navigation path as a sequence.

**Step 3: Write minimal implementation**

Implement:
- add mocked Telegram flow smoke tests
- add them to [scripts/self_check.sh](scripts/self_check.sh)
- document manual acceptance checks in [support/docs/REGRESSION_CHECKLIST.md](support/docs/REGRESSION_CHECKLIST.md)
- if integration credentials are available, extend [scripts/full_verification.py](scripts/full_verification.py) to record pass/fail per Telegram flow family

**Step 4: Run focused verification**

Run:

```bash
python3 -m unittest tests.test_telegram_flow_smoke -v
./scripts/self_check.sh
```

Expected:
- The project now has a high-signal regression gate for the Telegram surface.

**Step 5: Commit**

```bash
git add scripts/self_check.sh scripts/full_verification.py support/docs/REGRESSION_CHECKLIST.md tests/test_telegram_flow_smoke.py
git commit -m "test: add telegram flow smoke coverage"
```

### Task 8: Finish With A Live Bot Acceptance Pass

**Files:**
- Modify: `support/docs/REGRESSION_CHECKLIST.md`
- Create: `support/docs/E2E_TELEGRAM_RECOVERY_REPORT.md`

**Step 1: Write the acceptance checklist**

Add a manual checklist for:
- `/start`
- alerts open/frame/clip/review
- cameras open/live snapshot/live monitor/incident list
- search menu and face upload wizard
- archive menu and one archive jump
- subscription create/list/stop
- server/admin cards

**Step 2: Run the bot against a real Axxon target**

Run:

```bash
./scripts/run_axxon_tg_bot.sh
```

Use a real Telegram chat and record each flow result.

Expected:
- Each high-risk flow is marked pass/fail with evidence.

**Step 3: Write the report**

Create [support/docs/E2E_TELEGRAM_RECOVERY_REPORT.md](support/docs/E2E_TELEGRAM_RECOVERY_REPORT.md) including:
- environment
- bot version/commit
- tested flows
- failures remaining
- screenshots or message excerpts if available

**Step 4: Run final verification**

Run:

```bash
./scripts/self_check.sh
git status --short
```

Expected:
- All automated checks pass.
- Remaining defects, if any, are documented explicitly.

**Step 5: Commit**

```bash
git add support/docs/REGRESSION_CHECKLIST.md support/docs/E2E_TELEGRAM_RECOVERY_REPORT.md
git commit -m "docs: record telegram recovery acceptance results"
```

## Recommended Execution Order

1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7
8. Task 8

## Why This Order

- Task 1 is mandatory because the current verification path is not trustworthy.
- Task 2 makes future failures diagnosable instead of opaque.
- Tasks 3-5 address the visible UX debt in the order users feel it: home/help first, then search/archive entry, then detailed cards.
- Task 6 fixes the highest-friction stateful behaviors after the copy/navigation foundation is stable.
- Tasks 7-8 lock the recovered behavior down with both automated and live evidence.
