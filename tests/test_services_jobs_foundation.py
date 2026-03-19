import asyncio
import unittest

from axxon_telegram_vms.jobs import LiveSessionRecord, LiveSessionRuntime
from axxon_telegram_vms.services import (
    SubscriptionLedger,
    SubscriptionPolicy,
    SubscriptionRecord,
    build_live_poll_filters,
    build_notifier_include_filters,
    filter_cards_for_subscription,
    subscription_query_from_filters,
    subscription_states_match,
)


class ServicesFoundationTests(unittest.TestCase):
    def test_subscription_ledger_tracks_ids_stats_and_delivery_limits(self):
        clock_now = [10.0]
        utc_day = ["2026-03-09"]
        ledger = SubscriptionLedger(
            SubscriptionPolicy(
                max_subscriptions_per_user=2,
                max_events_per_day=2,
                duplicate_window_sec=5,
                min_notification_interval_sec=3,
            ),
            clock=lambda: clock_now[0],
            day_provider=lambda: utc_day[0],
        )

        first = SubscriptionRecord(
            subscription_id=ledger.next_subscription_id(42),
            channel_id="chan-1",
            user_id=42,
            source="events",
            filters={"event_type": "ET_DetectorEvent"},
            states=["BEGAN"],
            summary="first",
            created_at="2026-03-09T00:00:00+00:00",
        )
        second = SubscriptionRecord(
            subscription_id=ledger.next_subscription_id(42),
            channel_id="chan-2",
            user_id=42,
            source="alerts",
            filters={"event_type": "ET_Alert"},
            states=["BEGAN"],
            summary="second",
            created_at="2026-03-09T00:00:01+00:00",
        )
        ledger.add(second)
        ledger.add(first)

        self.assertEqual([row.subscription_id for row in ledger.list_subscriptions(42)], ["1", "2"])
        self.assertFalse(ledger.can_add_subscription(42))
        self.assertEqual(
            ledger.stats(42).as_legacy_dict(),
            {
                "active_subscriptions": 2,
                "max_subscriptions": 2,
                "events_today": 0,
                "max_events_per_day": 2,
                "events_remaining": 2,
            },
        )

        self.assertEqual(ledger.allow_event_delivery(42, "evt-1"), (True, "ok"))
        self.assertEqual(ledger.allow_event_delivery(42, "evt-1"), (False, "duplicate"))
        clock_now[0] = 16.0
        self.assertEqual(ledger.allow_event_delivery(42, "evt-2"), (True, "ok"))
        self.assertEqual(ledger.allow_event_delivery(42, "evt-3"), (False, "daily_cap"))
        self.assertEqual(ledger.events_today(42), 2)

        ledger.mark_notification_sent(42, now=16.0)
        self.assertEqual(ledger.notification_wait_seconds(42, now=17.0), 2.0)
        self.assertEqual(ledger.notification_wait_seconds(42, now=20.5), 0.0)

        utc_day[0] = "2026-03-10"
        self.assertEqual(ledger.events_today(42), 0)
        self.assertEqual(ledger.stats(42).events_remaining, 2)

        removed = ledger.remove(42, "1")
        self.assertIsNotNone(removed)
        self.assertEqual([row.subscription_id for row in ledger.list_subscriptions(42)], ["2"])

    def test_subscription_filter_helpers_keep_runtime_semantics(self):
        cards = [
            {
                "id": "1",
                "event_type": "ET_DetectorEvent",
                "category": "motion",
                "state": "BEGAN",
                "detector": "Vehicle Detector",
                "detector_access_point": "det-1",
                "camera_access_point": "cam-1",
            },
            {
                "id": "2",
                "event_type": "ET_DetectorEvent",
                "category": "lpr",
                "state": "HAPPENED",
                "detector": "2.LPR",
                "detector_access_point": "det-2",
                "camera_access_point": "cam-2",
            },
            {
                "id": "3",
                "event_type": "ET_Alert",
                "category": "alert",
                "state": "ST_WANT_REACTION",
                "detector": "3.Alert",
                "detector_access_point": "det-3",
                "camera_access_point": "cam-3",
            },
        ]

        filtered = filter_cards_for_subscription(
            cards,
            {
                "categories": ["motion"],
                "detector_names": ["Vehicle"],
                "camera_access_points": ["cam-1"],
            },
        )
        self.assertEqual([card["id"] for card in filtered], ["1"])
        self.assertTrue(subscription_states_match(cards[2], ["ENDED"]))
        self.assertTrue(subscription_states_match(cards[1], ["BEGAN", "HAPPENED", "ENDED"]))
        self.assertFalse(subscription_states_match(cards[1], ["BEGAN"]))
        self.assertEqual(
            build_live_poll_filters({"subject": "cam-1"}, poll_interval_sec=3, poll_limit=25),
            {"subject": "cam-1", "seconds": 60, "limit": 100},
        )
        self.assertEqual(
            build_notifier_include_filters(
                {
                    "event_type": "ET_DetectorEvent",
                    "detector_access_points": ["det-1", "det-2"],
                    "camera_access_points": ["cam-1", "cam-2"],
                    "live_include_subjects": ["cam-1", "det-2", "cam-1"],
                }
            ),
            [
                {"event_type": "ET_DetectorEvent", "subject": "cam-1"},
                {"event_type": "ET_DetectorEvent", "subject": "det-2"},
            ],
        )
        self.assertEqual(
            build_notifier_include_filters(
                {
                    "event_type": "ET_DetectorEvent",
                    "include": [
                        {"event_type": "ET_DetectorEvent", "subject": "det-1"},
                        {"subject": "cam-2"},
                        {"event_type": "ET_DetectorEvent", "subject": "det-1"},
                    ],
                }
            ),
            [
                {"event_type": "ET_DetectorEvent", "subject": "det-1"},
                {"event_type": "ET_DetectorEvent", "subject": "cam-2"},
            ],
        )

    def test_shared_query_bridge_handles_text_host_and_mask_filters(self):
        cards = [
            {
                "id": "1",
                "timestamp": "20260310T101500",
                "event_type": "listed_lpr_detected",
                "category": "lpr",
                "state": "HAPPENED",
                "priority": "AP_HIGH",
                "camera_access_point": "hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0",
                "detector_access_point": "hosts/ServerA/AVDetector.2/EventSupplier",
                "detector": "2.LPR",
                "text": "LP recognized from list Not listed · YZ45246",
                "plate": "YZ45246",
                "server": "ServerA",
            },
            {
                "id": "2",
                "timestamp": "20260310T101700",
                "event_type": "moveInZone",
                "category": "motion",
                "state": "BEGAN",
                "camera_access_point": "hosts/ServerB/DeviceIpint.1/SourceEndpoint.video:0:0",
                "detector_access_point": "hosts/ServerB/AVDetector.1/EventSupplier",
                "detector": "Vehicle Detector",
                "text": "Object moving in area detected",
                "server": "ServerB",
            },
        ]

        query = subscription_query_from_filters(
            {
                "host": "ServerA",
                "event_type": "ET_DetectorEvent",
                "contains": "YZ45246",
                "mask": "*5246",
                "camera_access_points": ["hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0"],
            },
            states=["HAPPENED"],
        )
        self.assertEqual(query.scope.hosts, ("ServerA",))
        self.assertEqual(query.taxonomy.states, ("HAPPENED",))
        self.assertEqual(query.text.mask, "*5246")

        filtered = filter_cards_for_subscription(
            cards,
            {
                "host": "ServerA",
                "event_type": "ET_DetectorEvent",
                "contains": "YZ45246",
                "mask": "*5246",
                "camera_access_points": ["hosts/ServerA/DeviceIpint.7/SourceEndpoint.video:0:0"],
            },
        )
        self.assertEqual([card["id"] for card in filtered], ["1"])


class JobsFoundationTests(unittest.IsolatedAsyncioTestCase):
    async def test_live_session_runtime_handles_replacement_and_manual_stop(self):
        on_end_calls: list[tuple[str, str]] = []

        async def runner(rec: LiveSessionRecord) -> None:
            await asyncio.Event().wait()

        async def on_end(rec: LiveSessionRecord, reason: str) -> None:
            on_end_calls.append((rec.session_id, reason))

        runtime = LiveSessionRuntime(runner=runner, on_end=on_end)
        first = LiveSessionRecord(user_id=7, camera_idx=1, chat_id=70, message_id=700)
        second = LiveSessionRecord(user_id=7, camera_idx=2, chat_id=70, message_id=701)

        self.assertFalse(await runtime.start(first))
        await asyncio.sleep(0)
        self.assertTrue(await runtime.start(second))
        await asyncio.sleep(0)
        self.assertEqual(runtime.get(7).session_id, second.session_id)
        self.assertIn((first.session_id, "replaced"), on_end_calls)

        stopped = await runtime.stop(7, reason="manual")
        await asyncio.sleep(0)
        self.assertEqual(stopped.session_id, second.session_id)
        self.assertIsNone(runtime.get(7))
        self.assertEqual(runtime.active_count(), 0)
        self.assertIn((second.session_id, "manual"), on_end_calls)

    async def test_live_session_runtime_cleans_up_finished_sessions(self):
        on_end_calls: list[tuple[str, str]] = []

        async def runner(rec: LiveSessionRecord) -> None:
            return None

        async def on_end(rec: LiveSessionRecord, reason: str) -> None:
            on_end_calls.append((rec.session_id, reason))

        runtime = LiveSessionRuntime(runner=runner, on_end=on_end)
        record = LiveSessionRecord(user_id=9, camera_idx=3, chat_id=90, message_id=900)

        self.assertFalse(await runtime.start(record))
        await asyncio.sleep(0)
        self.assertIsNone(runtime.get(9))
        self.assertEqual(runtime.active_count(), 0)
        self.assertEqual(on_end_calls, [(record.session_id, "finished")])


if __name__ == "__main__":
    unittest.main()
