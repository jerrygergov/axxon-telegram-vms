import unittest
from pathlib import Path


class SubscriptionRuntimeSurfaceTests(unittest.TestCase):
    def test_runtime_limits_and_commands_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("class SubscriptionRuntime", src)
        self.assertIn("/subscriptions", src)
        self.assertIn("max_subscriptions_per_user", src)
        self.assertIn("max_events_per_day", src)
        self.assertIn("min_notification_interval_sec", src)

    def test_callback_creation_flow_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("sub:new:ev:", src)
        self.assertIn("sub:new:cam:", src)
        self.assertIn("sub:state:", src)
        self.assertIn("sub:confirm:", src)
        self.assertIn("all_alerts", src)

    def test_notifier_semantics_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("DomainNotifier.PullEvents", src)
        self.assertIn("DisconnectEventChannel", src)

    def test_merged_media_helpers_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("pick_primary_rectangle", src)
        self.assertIn("normalized_to_pixel_crop", src)
        self.assertIn("hstack=inputs=2", src)

    def test_alert_rectangle_fallback_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("pick_primary_rectangle", src)
        self.assertIn("event_type == \"ET_Alert\"", src)
        self.assertIn("alert has no rectangle in raw payload", src)
        self.assertIn("fallback to export mode", src)

    def test_subscription_runtime_is_notifier_only(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertNotIn("def _cards_for_debug_fallback", src)
        loop_src = src.split("async def _subscription_loop", 1)[1].split("async def create_subscription", 1)[0]
        self.assertNotIn("subscription_fallback_polling", loop_src)
        self.assertNotIn("_cards_for_debug_fallback", loop_src)

    def test_counterwatch_is_notifier_only(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertNotIn("def _latest_counter_event_debug_fallback", src)
        watch_src = src.split("async def _watch_loop", 1)[1].split("async def start", 1)[0]
        self.assertNotIn("subscription_fallback_polling", watch_src)
        self.assertNotIn("_latest_counter_event_debug_fallback", watch_src)
        self.assertNotIn('run_api("events"', watch_src)


if __name__ == "__main__":
    unittest.main()
