import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_tg_ui import alert_flag_to_severity


class AlertActionTests(unittest.TestCase):
    def test_alert_flag_to_severity_mapping(self):
        self.assertEqual(alert_flag_to_severity("confirmed"), "SV_ALARM")
        self.assertEqual(alert_flag_to_severity("suspicious"), "SV_WARNING")
        self.assertEqual(alert_flag_to_severity("false"), "SV_FALSE")
        self.assertIsNone(alert_flag_to_severity("unknown"))

    def test_web_api_alert_review_command_surface(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("alert-review", src)
        self.assertIn("BeginAlertReview", src)
        self.assertIn("CompleteAlertReview", src)
        self.assertIn("SV_FALSE", src)
        self.assertIn("SV_WARNING", src)
        self.assertIn("SV_ALARM", src)

    def test_live_alert_callback_updates_same_message_path_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("_is_live_subscription_alert_callback", src)
        self.assertIn("_extract_live_alert_clip_rows", src)
        self.assertIn("if _is_live_subscription_alert_callback(q.data, q.message):", src)
        self.assertIn("edit_message_caption", src)
        self.assertIn("sub:clip:ET_Alert:", src)


if __name__ == "__main__":
    unittest.main()
