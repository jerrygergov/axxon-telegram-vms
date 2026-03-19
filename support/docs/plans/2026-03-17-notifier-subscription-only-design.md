# Notifier Subscription-Only Design

Date: 2026-03-17

## Goal

Make every live subscription path in the Telegram runtime use Axxon live event subscriptions only:

- detector event subscriptions
- alert subscriptions
- counter subscriptions and `/counterwatch`

This means `axxonsoft.bl.events.DomainNotifier.PullEvents` for subscribe/start and `axxonsoft.bl.events.DomainNotifier.DisconnectEventChannel` for unsubscribe/stop, with no history polling fallback in these live paths.

## Confirmed External Contract

Per the Axxon One gRPC events documentation, event subscriptions are created by opening a `DomainNotifier.PullEvents` stream with a `subscription_id` and `filters.include[]`.

The runtime must support:

- one subscription with one include entry
- one subscription with multiple include entries
- mixed-host multi-source include arrays

For counter detectors, the live subscription contract remains:

- `event_type = ET_DetectorEvent`
- `subject = camera access point`
- count extracted from `details[].lots_objects.object_count`

For normal detector subscriptions, the live subscription contract remains:

- `event_type = ET_DetectorEvent`
- `subject = detector access point`

For alerts, the live subscription contract remains:

- `event_type = ET_Alert`
- subject omitted unless a narrower subject is explicitly required

## Runtime Design

The runtime already has a notifier stream wrapper around `DomainNotifier.PullEvents`. That wrapper becomes the only live delivery transport for subscriptions and `/counterwatch`.

The Telegram runtime will use one explicit include builder and store the resulting `filters["include"]` in subscription drafts/records. The notifier stream will always derive the outgoing `include` payload from those filters.

No live subscription path may fall back to:

- event history reads
- `telegram-cards`
- polling windows shaped from `build_live_poll_filters`
- counter-specific history replay

## Multi-Source Design

Multi-source detector subscriptions must always materialize an `include` array like:

```json
{
  "filters": {
    "include": [
      {"event_type": "ET_DetectorEvent", "subject": "hosts/Server1/AVDetector.1/EventSupplier"},
      {"event_type": "ET_DetectorEvent", "subject": "hosts/Server1/AVDetector.2/EventSupplier"},
      {"event_type": "ET_DetectorEvent", "subject": "hosts/Server2/AVDetector.1/EventSupplier"}
    ]
  }
}
```

Deduplication happens before the stream starts so repeated subjects do not create repeated include entries.

## Error Handling

If a notifier stream closes unexpectedly, the runtime may reconnect by creating a new `PullEvents` stream with the same `subscription_id` and `include` semantics. It may not switch transport type.

Stopping a subscription or counter watch must always attempt `DisconnectEventChannel`.

## Testing Strategy

Add regression coverage for:

- explicit `include` arrays being accepted as the primary notifier filter input
- runtime subscription loops containing no polling fallback branch
- `/counterwatch` containing no history fallback branch
- multi-source detector drafts producing include arrays

## Files In Scope

- `scripts/axxon_tg_bot.py`
- `scripts/axxon_web_api.py`
- `axxon_telegram_vms/services/subscriptions.py`
- `tests/test_services_jobs_foundation.py`
- `tests/test_subscription_runtime.py`
