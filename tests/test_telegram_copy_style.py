import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from axxon_tg_ui import open_event_payload
from tg_camera_ui import camera_open_payload
from tg_server_ui import server_info_payload


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


def _event_api(args):
    if args[0] == "telegram-cards":
        return [EVENT_CARD]
    raise AssertionError(f"unexpected run_api args: {args}")


class TelegramCopyStyleTests(unittest.TestCase):
    def test_event_card_leads_with_summary_not_raw_id(self):
        with patch("axxon_tg_ui.run_api", side_effect=_event_api):
            payload = open_event_payload([], 1800, EVENT_CARD["id"])
        self.assertIn("What happened:", payload["text"])
        self.assertIn("Where:", payload["text"])
        self.assertIn("When:", payload["text"])
        self.assertNotIn("ID: `", payload["text"])

    def test_camera_open_payload_uses_plain_action_language(self):
        with patch(
            "tg_camera_ui.camera_rows",
            return_value=[
                {
                    "name": "2.Gate",
                    "access_point": "hosts/AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
                    "detectors": [{"name": "LPR"}, {"name": "Motion"}],
                }
            ],
        ):
            payload = camera_open_payload([], 0)
        self.assertIn("Choose an action for this camera.", payload["text"])
        self.assertNotIn("workspace", payload["text"].lower())

    def test_server_info_payload_starts_with_summary(self):
        data = {
            "usage": {
                "servers": [
                    {
                        "name": "AXXON_SERVER",
                        "totalCPU": 12.5,
                        "netMaxUsage": 0.42,
                    }
                ]
            },
            "version": {
                "version": "1.2.3",
                "httpSdk": "sdk-9",
            },
            "statistics": {
                "bytesOut": 10485760,
            },
            "errors": [],
        }
        with patch("tg_server_ui.run_api", return_value=data):
            payload = server_info_payload([])
        self.assertIn("Summary:", payload["text"])
        self.assertIn("Version 1.2.3", payload["text"])


if __name__ == "__main__":
    unittest.main()
