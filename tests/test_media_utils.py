import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from media_utils import is_meaningful_rectangle_candidate, normalized_to_pixel_crop, pick_primary_rectangle, pick_primary_rectangle_candidate, rectangle_candidate_to_pixel_crop


class MediaUtilsTests(unittest.TestCase):
    def test_pick_primary_detector_rectangle(self):
        event = {
            "body": {
                "details": [
                    {"rectangle": {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4}},
                ]
            }
        }
        rect = pick_primary_rectangle(event)
        self.assertIsNotNone(rect)
        self.assertAlmostEqual(rect["x"], 0.1)
        self.assertAlmostEqual(rect["y"], 0.2)
        self.assertAlmostEqual(rect["w"], 0.3)
        self.assertAlmostEqual(rect["h"], 0.4)

    def test_pick_primary_lpr_xyxy(self):
        event = {"body": {"data": {"Hypotheses": [{"PlateRectangle": [0.2, 0.1, 0.5, 0.3]}]}}}
        rect = pick_primary_rectangle(event)
        self.assertIsNotNone(rect)
        self.assertAlmostEqual(rect["x"], 0.2)
        self.assertAlmostEqual(rect["y"], 0.1)
        self.assertAlmostEqual(rect["w"], 0.3)
        self.assertAlmostEqual(rect["h"], 0.2)

    def test_pick_primary_lpr_dict_fallback(self):
        event = {
            "body": {
                "details": [
                    {
                        "auto_recognition_result": {
                            "hypotheses": [
                                {"plate_rectangle": {"left": 0.3, "top": 0.4, "right": 0.6, "bottom": 0.8}}
                            ]
                        }
                    }
                ]
            }
        }
        rect = pick_primary_rectangle(event)
        self.assertEqual(rect, {"x": 0.3, "y": 0.4, "w": 0.3, "h": 0.4})

    def test_pick_primary_alert_nested_detector_rectangle(self):
        event = {
            "body": {
                "detector": {
                    "details": [
                        {"rectangle": {"x": 0.21, "y": 0.31, "w": 0.11, "h": 0.22}},
                    ],
                    "data": {
                        "rectangles": [
                            [0.1, 0.1, 0.2, 0.2, 1],
                        ]
                    },
                }
            }
        }
        rect = pick_primary_rectangle(event)
        self.assertIsNotNone(rect)
        self.assertAlmostEqual(rect["x"], 0.21)
        self.assertAlmostEqual(rect["y"], 0.31)
        self.assertAlmostEqual(rect["w"], 0.11)
        self.assertAlmostEqual(rect["h"], 0.22)

    def test_normalized_to_pixel_crop_clamps(self):
        crop = normalized_to_pixel_crop({"x": 0.95, "y": 0.95, "w": 0.2, "h": 0.2}, 100, 100)
        self.assertEqual(crop, (95, 95, 5, 5))

    def test_pick_primary_rectangle_ignores_absolute_pixel_values(self):
        event = {"body": {"data": {"Hypotheses": [{"PlateRectangle": [120, 80, 240, 160]}]}}}
        rect = pick_primary_rectangle(event)
        self.assertIsNone(rect)

    def test_rectangle_candidate_to_pixel_crop_accepts_absolute_pixel_values(self):
        crop = rectangle_candidate_to_pixel_crop({"x": 120, "y": 80, "w": 120, "h": 80}, 1920, 1080)
        self.assertEqual(crop, (120, 80, 120, 80))

    def test_pick_primary_rectangle_candidate_prefers_tighter_meaningful_box(self):
        event = {
            "body": {
                "details": [
                    {"rectangle": {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}},
                    {"rectangle": {"x": 0.25, "y": 0.35, "w": 0.2, "h": 0.1}},
                ]
            }
        }
        rect = pick_primary_rectangle_candidate(event)
        self.assertIsNotNone(rect)
        self.assertAlmostEqual(rect["x"], 0.25)
        self.assertAlmostEqual(rect["y"], 0.35)
        self.assertAlmostEqual(rect["w"], 0.2)
        self.assertAlmostEqual(rect["h"], 0.1)

    def test_is_meaningful_rectangle_candidate_rejects_full_frame_normalized_box(self):
        self.assertFalse(is_meaningful_rectangle_candidate({"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}))
        self.assertTrue(is_meaningful_rectangle_candidate({"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4}))


if __name__ == "__main__":
    unittest.main()
