# ROADMAP

## Current baseline (completed)

- [x] Single runtime path under `scripts/` only
- [x] Telegram home/events/alerts/cameras flows
- [x] Event and alert open/frame/clip actions
- [x] Alert review actions (`confirmed`/`suspicious`/`false`) with API fallback messaging
- [x] Async subscriptions:
  - `/subscribe` detector flow
  - callback-driven create flows from events/camera/alerts
  - `/subscriptions`, `/stop`, `/stop <id>`
- [x] Subscription safeguards:
  - per-user max active subscriptions
  - per-day event cap
  - duplicate window and send throttling
  - notifier pull + fallback polling
- [x] Live merged media path for subscription notifications (frame + crop panel)
- [x] Self-check pipeline (`scripts/self_check.sh` + CI workflow)

## Next improvements

- [ ] Behavioral unit tests for `SubscriptionRuntime` logic (limits, dedupe, stop semantics)
- [ ] Timeout wrappers for all subprocess boundaries in callback/runtime paths
- [ ] Startup dependency checks for `ffmpeg` and `ffprobe`
- [ ] Optional strict ACL mode for production (`fail-fast` when no allowlist)
- [ ] Integration smoke schedule with real Axxon test target
