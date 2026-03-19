import os
import unittest

from scripts.config_loader import load_tg_bot_config, parse_csv_text, parse_ids


class ConfigLoaderTests(unittest.TestCase):
    def test_parse_ids_filters_invalid(self):
        os.environ["AUTHORIZED_USERS"] = "1, abc, 2, ,3"
        self.assertEqual(parse_ids("AUTHORIZED_USERS"), [1, 2, 3])

    def test_parse_csv_text_dedupes_and_trims(self):
        os.environ["TG_MACRO_ALLOWED_NAMES"] = " Manual Alert Test ,manual alert test,Webhook Trigger "
        self.assertEqual(parse_csv_text("TG_MACRO_ALLOWED_NAMES"), ["Manual Alert Test", "Webhook Trigger"])

    def test_tg_limits_defaults_and_bounds(self):
        os.environ["TG_SEND_RATE_LIMIT_COUNT"] = "0"
        os.environ["TG_SEND_RATE_LIMIT_PERIOD_SEC"] = "-5"
        os.environ["TG_DUPLICATE_WINDOW_SEC"] = "-1"
        os.environ["TG_MAX_SUBSCRIPTIONS_PER_USER"] = "0"
        os.environ["TG_MAX_EVENTS_PER_DAY"] = "-10"
        os.environ["TG_MIN_NOTIFICATION_INTERVAL_SEC"] = "-7"
        os.environ["TG_SUBSCRIPTION_POLL_INTERVAL_SEC"] = "0"
        os.environ["TG_SUBSCRIPTION_POLL_WINDOW_SEC"] = "1"
        os.environ["TG_SUBSCRIPTION_POLL_LIMIT"] = "0"
        os.environ["TG_SUBSCRIPTION_USE_NOTIFIER"] = "1"
        os.environ["TG_SUBSCRIPTION_NOTIFIER_TIMEOUT_SEC"] = "0"
        os.environ["TG_SUBSCRIPTION_FALLBACK_POLLING"] = "1"
        os.environ["TG_LIVE_OVERLAY"] = "0"

        cfg = load_tg_bot_config()
        self.assertEqual(cfg.send_rate_limit_count, 1)
        self.assertEqual(cfg.send_rate_limit_period_sec, 1)
        self.assertEqual(cfg.duplicate_window_sec, 0)
        self.assertEqual(cfg.max_subscriptions_per_user, 1)
        self.assertEqual(cfg.max_events_per_day, 1)
        self.assertEqual(cfg.min_notification_interval_sec, 0)
        self.assertEqual(cfg.subscription_poll_interval_sec, 1)
        self.assertEqual(cfg.subscription_poll_window_sec, 30)
        self.assertEqual(cfg.subscription_poll_limit, 1)
        self.assertTrue(cfg.subscription_use_notifier)
        self.assertEqual(cfg.subscription_notifier_timeout_sec, 1)
        self.assertTrue(cfg.subscription_fallback_polling)
        self.assertFalse(cfg.live_overlay)

    def test_tg_subscription_fallback_default_off(self):
        os.environ.pop("TG_SUBSCRIPTION_FALLBACK_POLLING", None)
        os.environ.pop("TG_SUBSCRIPTION_USE_NOTIFIER", None)
        cfg = load_tg_bot_config()
        self.assertTrue(cfg.subscription_use_notifier)
        self.assertFalse(cfg.subscription_fallback_polling)

    def test_tg_live_overlay_default_on(self):
        os.environ.pop("TG_LIVE_OVERLAY", None)
        cfg = load_tg_bot_config()
        self.assertTrue(cfg.live_overlay)

    def test_macro_guardrail_config_defaults_and_parsing(self):
        os.environ["TG_MACRO_EXECUTION_ENABLED"] = "1"
        os.environ["TG_MACRO_ALLOWED_IDS"] = "id-1,id-2,id-1"
        os.environ["TG_MACRO_ALLOWED_NAMES"] = "Manual Alert Test,Webhook Trigger"
        os.environ["TG_MACRO_CONFIRM_TTL_SEC"] = "10"

        cfg = load_tg_bot_config()

        self.assertTrue(cfg.macro_execution_enabled)
        self.assertEqual(cfg.macro_allowed_ids, ["id-1", "id-2"])
        self.assertEqual(cfg.macro_allowed_names, ["Manual Alert Test", "Webhook Trigger"])
        self.assertEqual(cfg.macro_confirm_ttl_sec, 30)

    def test_ptz_guardrail_config_defaults_and_parsing(self):
        os.environ["TG_PTZ_CONTROL_ENABLED"] = "1"
        os.environ["TG_PTZ_ALLOWED_CAMERA_APS"] = "hosts/A/cam1,hosts/A/cam2,hosts/A/cam1"
        os.environ["TG_PTZ_ALLOWED_CAMERA_NAMES"] = "2.Gate PTZ,2.gate ptz"
        os.environ["TG_PTZ_CONFIRM_TTL_SEC"] = "5"

        cfg = load_tg_bot_config()

        self.assertTrue(cfg.ptz_control_enabled)
        self.assertEqual(cfg.ptz_allowed_camera_aps, ["hosts/A/cam1", "hosts/A/cam2"])
        self.assertEqual(cfg.ptz_allowed_camera_names, ["2.Gate PTZ"])
        self.assertEqual(cfg.ptz_confirm_ttl_sec, 30)


if __name__ == "__main__":
    unittest.main()
