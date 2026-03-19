# Runtime Hardening Design

Date: 2026-03-12

## Goal

Stabilize the active Telegram runtime under `scripts/` so local development, test execution, and operator-facing error handling are deterministic before any broader architectural refactor.

## Scope

This pass focuses on correctness and stability:

- make local `scripts.*` imports resolve to this repository consistently
- eliminate import-time crashes caused by runtime evaluation of modern type annotations
- unify subprocess timeout and error handling across the bot and UI bridge
- keep existing command and callback surfaces stable
- improve Telegram failure messaging so operators are not left in dead-end states

This pass does not introduce feature expansion, command renames, callback prefix changes, or a broad migration of runtime ownership out of `scripts/`.

## Current Problems

Repository inspection and `./scripts/self_check.sh` showed three immediate failure classes:

1. local `scripts.*` imports are unstable because the environment contains an installed third-party `scripts` package
2. several active script modules use postponed-evaluation-sensitive annotations such as `str | None` without enabling postponed annotation evaluation
3. subprocess boundaries are inconsistent:
   - `scripts/axxon_tg_bot.py` has timeout handling for `run_ui`, but not for `run_api`
   - `scripts/tg_ui_common.py` shells out with no timeout normalization
   - failure formatting differs by caller

## Architecture

The hardening pass keeps the current runtime split:

- `scripts/axxon_tg_bot.py` remains the active Telegram entrypoint
- `scripts/axxon_tg_ui.py` remains the payload builder
- `scripts/axxon_web_api.py` remains the Axxon adapter CLI

The internal refactor is intentionally narrow:

- add `scripts/__init__.py` so the repo owns the `scripts` package name locally
- add postponed annotation evaluation to script modules that use modern type hints
- introduce one small shared subprocess helper in `scripts/`
- route existing subprocess callers through that helper instead of open-coded `subprocess.check_output` / `subprocess.run`

## Runtime Behavior

The shared subprocess layer should provide:

- command execution with explicit timeout
- consistent stdout/stderr capture
- JSON parsing with plain-text fallback
- one stable exception shape for timeout and non-zero exit cases

The bot/UI layers should convert those failures into operator-safe messages:

- short summary first
- no raw stack traces
- no raw JSON dumps
- at least one clear recovery action such as `Home`, `Back`, or section navigation
- partial data should still render when possible

## Telegram UX Guardrails

For this pass, UX improvements are limited to resilience and recoverability:

- callback and command failures should never strand the operator
- error copy should be concise and action-oriented
- success-path menu layouts should remain unchanged unless a bug fix requires a small wording change

## Verification

Validation should follow the existing project path:

1. focused unit tests for import/runtime compatibility and subprocess helper behavior
2. full `python3 -m unittest discover -s tests -p 'test_*.py' -v`
3. full `./scripts/self_check.sh`

## Risks And Controls

Risks:

- accidental changes to command or callback behavior while touching shared helpers
- broad import churn if the compatibility fix is too invasive
- regressions in long-running archive/search/export paths if timeouts are set incorrectly

Controls:

- no callback namespace changes
- no command removals
- TDD for each behavior change
- preserve current success-path behavior unless tests prove it is already wrong
