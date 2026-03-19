import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from axxon_tg_ui import callback_payload


EVENT_CARD = {
    "id": "11111111-1111-1111-1111-111111111111",
    "timestamp": "20260308T224316.914000",
    "category": "motion",
    "event_type": "moveInZone",
    "state": "BEGAN",
    "camera": "Camera A",
    "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
    "detector": "Vehicle Detector",
    "detector_access_point": "hosts/AXXON_SERVER/AppDataDetector.1/EventSupplier",
    "text": "Vehicle entered zone",
    "label_primary": "Object moving in area detected",
    "label_secondary": "Vehicle Detector · Camera A",
    "label_status": "began",
}

ALERT_CARD = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "timestamp": "20260308T224204.094721",
    "category": "alert",
    "event_type": "ET_Alert",
    "state": "ST_WANT_REACTION",
    "priority": "AP_MEDIUM",
    "camera": "Camera A",
    "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
    "detector": "Person Detector",
    "alert_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "text": "Camera \"Camera A\": Alarm initiated by macro \"Camera A: Person Detector\"",
    "label_primary": 'Alarm initiated by macro "Camera A: Person Detector"',
    "label_status": "P2 active",
}


def _fake_run_api(args):
    cmd = args[0]
    if cmd == "server-version":
        return {"version": "1.2.3", "httpSdk": "sdk-9"}
    if cmd == "dashboard":
        return {"by_category": {"lpr": 1, "motion": 3}}
    if cmd == "telegram-cards":
        if "--event-type" in args:
            event_type = args[args.index("--event-type") + 1]
            return [ALERT_CARD] if event_type == "ET_Alert" else [EVENT_CARD]
        return [EVENT_CARD]
    raise AssertionError(f"unexpected run_api args: {args}")


class TelegramFlowSmokeTests(unittest.TestCase):
    def test_home_payload_contains_core_actions(self):
        with patch("axxon_tg_ui.run_api", side_effect=_fake_run_api):
            payload = callback_payload([], 1800, "home")
        buttons = payload["buttons"]
        self.assertEqual(buttons[1][0]["text"], "📷 Cameras")
        self.assertEqual(buttons[2][1]["callback_data"], "sea:menu")

    def test_alert_feed_to_open_alert_keeps_review_actions(self):
        with patch("axxon_tg_ui.run_api", side_effect=_fake_run_api):
            feed = callback_payload([], 1800, "al:feed:0")
            opened = callback_payload([], 1800, f"al:open:{ALERT_CARD['id']}")
        self.assertTrue(feed["buttons"][0][0]["callback_data"].startswith("al:open:"))
        button_labels = [button["text"] for row in opened["buttons"] for button in row]
        self.assertIn("✅ Confirmed", button_labels)
        self.assertIn("🎬 Archive", button_labels)

    def test_camera_list_to_open_camera_shows_live_actions(self):
        camera_rows = [
            {
                "name": "2.Gate",
                "access_point": "hosts/AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
                "detectors": [{"name": "LPR"}, {"name": "Motion"}],
            }
        ]
        with patch("tg_camera_ui.camera_rows", return_value=camera_rows):
            listing = callback_payload([], 1800, "cam:list:0")
            opened = callback_payload([], 1800, "cam:open:0")
        self.assertEqual(listing["buttons"][0][0]["callback_data"], "cam:open:0")
        button_labels = [button["text"] for row in opened["buttons"] for button in row]
        self.assertIn("▶ Live monitor", button_labels)
        self.assertIn("📸 Live snapshot", button_labels)

    def test_search_menu_to_face_help_is_guided(self):
        with patch("axxon_tg_ui.run_api", side_effect=_fake_run_api):
            menu = callback_payload([], 1800, "sea:menu")
            face_help = callback_payload([], 1800, "sea:face")
        self.assertIn("Choose what you want to search", menu["text"])
        self.assertIn("Upload a Telegram photo", face_help["text"])

    def test_archive_menu_to_jump_help_is_guided(self):
        with patch("axxon_tg_ui.run_api", side_effect=_fake_run_api):
            menu = callback_payload([], 1800, "arch:menu")
            jump_help = callback_payload([], 1800, "arch:jump")
        self.assertIn("Choose Jump for a quick archive preview", menu["text"])
        self.assertIn("Start with one camera and one moment in time", jump_help["text"])


if __name__ == "__main__":
    unittest.main()
