import json
import unittest
from pathlib import Path

from axxon_telegram_vms.models import (
    NormalizedDetectorRow,
    normalize_detector_rows,
    normalize_event,
    normalize_event_card,
)


RAW_DIR = Path(__file__).resolve().parents[1] / "support" / "references" / "live-data-model" / "raw"


def _load_json(name: str):
    return json.loads((RAW_DIR / name).read_text(encoding="utf-8"))


class ModelsNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detector_rows = _load_json("detectors.list.json")
        cls.recent_events = _load_json("events.recent.json")
        cls.alerts = _load_json("alerts.sample.json")

    def test_detector_rows_normalize_from_live_data(self):
        rows = normalize_detector_rows(self.detector_rows)
        self.assertTrue(rows)
        self.assertIsInstance(rows[0], NormalizedDetectorRow)
        self.assertEqual(rows[0].access_point, "hosts/VIDEO_SERVER/AVDetector.1/EventSupplier")
        self.assertEqual(rows[0].name, "1.Neurotracker")
        self.assertEqual(rows[0].camera_name, "1.Camera A")
        self.assertEqual(rows[0].detector_type_name, "Neural tracker")
        self.assertTrue(rows[0].is_activated)
        self.assertEqual(rows[0].selection_label(), "1.Neurotracker · 1.Camera A · Neural tracker")
        self.assertEqual(rows[1].selection_label(), "1.Vehicle detector · 1.Camera A · Motion in area")
        self.assertEqual(rows[3].selection_label(), "2.License plate recognition RR · 1.Camera A")
        self.assertEqual(
            rows[0].as_legacy_dict(),
            {
                "access_point": "hosts/VIDEO_SERVER/AVDetector.1/EventSupplier",
                "name": "1.Neurotracker",
                "camera_name": "1.Camera A",
                "camera_access_point": "hosts/VIDEO_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
                "detector_type": "NeuroTracker",
                "detector_type_name": "Neural tracker",
                "is_activated": True,
                "selection_label": "1.Neurotracker · 1.Camera A · Neural tracker",
            },
        )

    def test_counter_event_extracts_object_count(self):
        card = normalize_event_card(
            {
                "event_type": "ET_DetectorEvent",
                "body": {
                    "guid": "crowd-1",
                    "event_type": "lotsObjects",
                    "timestamp": "20260310T102000.000",
                    "state": "HAPPENED",
                    "origin_ext": {
                        "friendly_name": "Camera B",
                        "access_point": "hosts/Server/DeviceIpint.2/SourceEndpoint.video:0:0",
                    },
                    "detector_ext": {
                        "friendly_name": "Crowd estimation VA",
                        "access_point": "hosts/Server/AVDetector.7/EventSupplier",
                    },
                    "details": [
                        {
                            "lots_objects": {
                                "object_count": 5,
                            }
                        }
                    ],
                },
                "localization": {
                    "text": "Crowd estimation",
                },
            }
        )
        self.assertEqual(card["event_type"], "lotsObjects")
        self.assertEqual(card["object_count"], 5)
        self.assertEqual(card["camera"], "Camera B")
        self.assertEqual(card["detector"], "Crowd estimation VA")

    def test_motion_event_keeps_paired_phase_semantics(self):
        event = normalize_event(self.recent_events[0])
        self.assertEqual(event.source_kind, "detector_event")
        self.assertEqual(event.category, "motion")
        self.assertEqual(event.camera, "Camera A")
        self.assertEqual(event.detector, "Vehicle detector")
        self.assertEqual(event.phase.family, "paired")
        self.assertEqual(event.phase.label, "ended")
        self.assertTrue(event.phase.is_terminal)
        card = event.to_telegram_card()
        self.assertEqual(card["phase_family"], "paired")
        self.assertEqual(card["phase_label"], "ended")
        self.assertEqual(card["label_primary"], "Object moving in area detected")
        self.assertEqual(card["label_secondary"], "Vehicle detector · Camera A")
        self.assertEqual(card["label_status"], "ended")
        self.assertIn("timeline_before_after", card["actions"])

    def test_lpr_event_extracts_plate_and_instant_semantics(self):
        event = normalize_event(self.recent_events[1])
        self.assertEqual(event.category, "lpr")
        self.assertEqual(event.phase.family, "instant")
        self.assertEqual(event.phase.label, "happened")
        self.assertEqual(event.plate, "YZ45246")
        self.assertEqual(
            event.actions,
            ("frame", "plate_crop", "clip_30s", "similar_plate"),
        )
        card = normalize_event_card(self.recent_events[1])
        self.assertEqual(card["plate"], "YZ45246")
        self.assertEqual(card["phase_family"], "instant")
        self.assertEqual(card["vehicle"], {"brand": None, "model": None, "color": None})
        self.assertEqual(card["label_primary"], "LP recognized from list Not listed · YZ45246")
        self.assertEqual(card["label_secondary"], "Camera A")
        self.assertNotIn("label_status", card)

    def test_alert_normalization_exposes_trigger_semantics(self):
        event = normalize_event(self.alerts[0])
        self.assertEqual(event.source_kind, "alert")
        self.assertEqual(event.category, "alert")
        self.assertEqual(event.phase.family, "alert")
        self.assertEqual(event.phase.label, "active")
        self.assertEqual(event.priority, "AP_MEDIUM")
        self.assertEqual(event.camera, "Camera A")
        self.assertEqual(event.detector, "Person detector")
        self.assertTrue(event.review_available)
        self.assertEqual(event.trigger_event_type, "moveInZone")
        self.assertEqual(event.trigger_state, "BEGAN")
        self.assertEqual(event.trigger_phase_family, "paired")
        self.assertEqual(event.trigger_phase_label, "began")
        card = normalize_event_card(self.alerts[0])
        self.assertEqual(card["phase_family"], "alert")
        self.assertEqual(card["trigger_event_type"], "moveInZone")
        self.assertEqual(card["trigger_phase_label"], "began")
        self.assertEqual(card["label_primary"], 'Alarm initiated by macro "Camera A: Person detector"')
        self.assertEqual(card["label_status"], "P2 active")
        self.assertNotIn("label_secondary", card)


if __name__ == "__main__":
    unittest.main()
