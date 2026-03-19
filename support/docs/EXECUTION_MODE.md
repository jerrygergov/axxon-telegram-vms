# Execution Mode — Codex Supervision

This project is executed in an **active orchestration** mode.

## Rule
Do not go passive between phases.

For each roadmap phase/pass:
1. launch Codex (or another coding agent) on the next planned slice
2. monitor process output and logs while it runs
3. when it completes, inspect the diff immediately
4. run tests / self-checks / smoke validation yourself
5. if the result is weak or incomplete, return it for fixes immediately
6. if the result is accepted, immediately launch the next phase unless blocked by a real owner-level product/API decision

## Watchdogs
Cron/watchdog jobs are backup observability only. They do not replace active supervision.

## Escalation rule
Only interrupt the owner for:
- product decisions
- unclear external API surface that cannot be confirmed safely
- credentials/access blockers
- destructive/risky migration choices
- privacy/compliance decisions

Everything else should be driven forward without waiting.
