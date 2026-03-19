import unittest
from pathlib import Path

from scripts.unification_helpers import normalize_detector_rows


class UnificationParityTests(unittest.TestCase):
    def test_normalize_detectors_filters_invalid_rows(self):
        raw = [
            {
                "detector_access_point": "hosts/A/det/1",
                "detector_name": "Line Cross",
                "camera_name": "Gate Cam",
                "camera_access_point": "hosts/A/cam/1",
            },
            {
                "detector_access_point": "",
                "detector_name": "Broken",
                "camera_name": "Skip Cam",
            },
        ]
        out = normalize_detector_rows(raw)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["access_point"], "hosts/A/det/1")
        self.assertEqual(out[0]["name"], "Line Cross")
        self.assertEqual(out[0]["camera_name"], "Gate Cam")
        self.assertEqual(out[0]["camera_access_point"], "hosts/A/cam/1")

    def test_home_menu_defines_subscription_callback(self):
        src = Path("scripts/axxon_tg_ui.py").read_text(encoding="utf-8")
        self.assertIn("sub:det:list", src)
        self.assertIn("sub:new:ev:", src)
        self.assertIn("sub:new:cam:", src)
        self.assertIn("srv:menu", src)
        self.assertIn("sea:menu", src)
        self.assertIn("sea:event", src)
        self.assertIn("sea:face", src)
        self.assertIn("arch:jump", src)
        self.assertIn("arch:export", src)


if __name__ == "__main__":
    unittest.main()
