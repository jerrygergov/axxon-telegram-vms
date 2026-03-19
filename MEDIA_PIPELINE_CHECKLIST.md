# Media Pipeline Verification Checklist

Use this checklist before declaring event-image delivery fixed.

## Code-path sanity
- [x] `run_api()` returns plain text for file-producing subcommands (`frame-from-event`, `clip-from-event`, `live-snapshot`)
- [x] rectangle extraction is centralized in `scripts/media_utils.py`
- [x] box drawing uses shared rectangle extraction
- [x] crop selection uses shared rectangle extraction
- [x] full-frame rectangles are not preferred for crop panels when tighter boxes exist

## Automated checks
- [x] focused unit tests pass
- [x] no regression in rectangle normalization / pixel crop conversion

## Live Axxon verification
- [x] fetch recent real detector events
- [x] confirm at least one event has raw rectangle candidates
- [x] confirm at least one event has a meaningful non-full-frame rectangle
- [x] `frame-from-event` succeeds for a real event
- [x] `box-from-event` succeeds for a real event
- [x] crop image file is generated for a meaningful event
- [x] merged image file is generated for a meaningful event
- [x] final runtime helper returns `_merged.jpg` for a meaningful event

## Bot runtime verification
- [x] bot restarted on latest code
- [x] bot polling is healthy after restart
- [x] bot log has no fresh `combined_image: frame build failed` errors after fix

## Ship gate
- [x] changes committed
- [x] changes pushed to `main`
- [x] final smoke result written down with one successful event id (`3bceda56-aeff-45f7-a8b4-d51997baefbf`)


## Latest verification result

```json
{
  "fetched_events": 250,
  "has_raw_rect_event": true,
  "has_meaningful_rect_event": true,
  "event_id": "3bceda56-aeff-45f7-a8b4-d51997baefbf",
  "event_type": "moveInZone",
  "state": "BEGAN",
  "final_path": "/tmp/ax_sub_3bceda56-aeff-45f7-a8b4-d51997baefbf_merged.jpg",
  "frame_exists": true,
  "boxed_exists": true,
  "crop_exists": true,
  "merged_exists": true,
  "bot_pid_ok": true,
  "polling_ok": true,
  "fresh_frame_build_failures": []
}
```
