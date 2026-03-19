# Notifier Subscription-Only Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make live Telegram subscriptions for detector events, alerts, and counters use only Axxon notifier subscriptions via `DomainNotifier.PullEvents` and stop only via `DisconnectEventChannel`.

**Architecture:** Keep `scripts/axxon_tg_bot.py` as the active runtime and keep the pure notifier include shaping in `axxon_telegram_vms/services/subscriptions.py`. Remove history/polling fallback behavior from live subscription paths while preserving current normalized card filtering and reconnect behavior.

**Tech Stack:** Python 3.12, python-telegram-bot, Axxon One gRPC `/grpc` bridge, unittest/pytest.

---

### Task 1: Lock The Contract With Failing Tests

**Files:**
- Modify: `tests/test_services_jobs_foundation.py`
- Modify: `tests/test_subscription_runtime.py`

**Step 1: Write the failing test**

Add assertions that:

- `build_notifier_include_filters()` prefers explicit `include`
- `SubscriptionRuntime` contains no `_cards_for_debug_fallback`
- `_subscription_loop()` contains no polling fallback branch
- `/counterwatch` contains no `_latest_counter_event_debug_fallback`
- `/counterwatch` contains no `subscription_fallback_polling` branch

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_services_jobs_foundation.py tests/test_subscription_runtime.py -q`
Expected: FAIL on the remaining counter fallback/runtime strings.

**Step 3: Write minimal implementation**

Remove the remaining counter fallback/history path and keep the notifier-only assertions satisfiable.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_services_jobs_foundation.py tests/test_subscription_runtime.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_services_jobs_foundation.py tests/test_subscription_runtime.py scripts/axxon_tg_bot.py axxon_telegram_vms/services/subscriptions.py
git commit -m "test: lock notifier-only subscription runtime"
```

### Task 2: Remove Counter History Fallback

**Files:**
- Modify: `scripts/axxon_tg_bot.py`

**Step 1: Write the failing test**

Use the surface test from Task 1 as the red test for `/counterwatch` fallback removal.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_subscription_runtime.py -q`
Expected: FAIL because `_latest_counter_event_debug_fallback` and the fallback branch still exist.

**Step 3: Write minimal implementation**

Remove:

- `_latest_counter_event_debug_fallback()`
- the `run_api("events", ...)` counter path
- the `if card is None and BOT_CFG.subscription_fallback_polling and stream.error:` branch

Keep:

- `PullEvents` stream startup
- reconnect on notifier closure
- `DisconnectEventChannel` on stop
- counter parsing from normalized cards with `object_count`

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_subscription_runtime.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/axxon_tg_bot.py tests/test_subscription_runtime.py
git commit -m "fix: remove counter history fallback"
```

### Task 3: Keep Multi-Source Include As First-Class Input

**Files:**
- Modify: `axxon_telegram_vms/services/subscriptions.py`
- Modify: `scripts/axxon_tg_bot.py`
- Modify: `tests/test_services_jobs_foundation.py`

**Step 1: Write the failing test**

Use the explicit `include` test as the red test for first-class include shaping.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_services_jobs_foundation.py -q`
Expected: FAIL if explicit `include` is not the first input consumed.

**Step 3: Write minimal implementation**

Ensure the notifier include helper:

- accepts `filters["include"]` first
- dedupes `(event_type, subject)` pairs
- falls back to legacy subjects only when explicit `include` is missing

Ensure detector selection drafts store multi-source include arrays in the subscription record.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_services_jobs_foundation.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add axxon_telegram_vms/services/subscriptions.py scripts/axxon_tg_bot.py tests/test_services_jobs_foundation.py
git commit -m "fix: use explicit notifier include filters"
```

### Task 4: Verify Full Runtime Safety

**Files:**
- Modify: none expected
- Test: `tests/test_models_normalization.py`
- Test: `tests/test_services_jobs_foundation.py`
- Test: `tests/test_subscription_runtime.py`

**Step 1: Run targeted verification**

Run: `python3 -m pytest tests/test_models_normalization.py tests/test_services_jobs_foundation.py tests/test_subscription_runtime.py -q`
Expected: PASS

**Step 2: Run full unit verification**

Run: `python3.12 -m unittest discover -s tests -p 'test_*.py' -v`
Expected: PASS with at most known skips only.

**Step 3: Check git state**

Run: `git status --short`
Expected: only intended files modified.

**Step 4: Commit**

```bash
git add scripts/axxon_tg_bot.py axxon_telegram_vms/services/subscriptions.py tests/test_services_jobs_foundation.py tests/test_subscription_runtime.py
git commit -m "fix: enforce notifier-only live subscriptions"
```
