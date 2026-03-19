import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_tg_bot import _is_counter_detector_row


class CounterWatchDetectorSelectionTests(unittest.TestCase):
    def test_accepts_neurocounter(self):
        self.assertTrue(_is_counter_detector_row({"detector_type": "NeuroCounter"}))

    def test_accepts_vacrowddetector(self):
        self.assertTrue(_is_counter_detector_row({"detector_type": "VaCrowdDetector"}))

    def test_rejects_name_only_counter_hint_without_supported_type(self):
        self.assertFalse(_is_counter_detector_row({"detector_type": "MoveInZone", "name": "Counter-ish detector"}))


if __name__ == "__main__":
    unittest.main()
