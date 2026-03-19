import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from camera_catalog import normalize_camera_rows, normalize_video_id


class CameraCatalogTests(unittest.TestCase):
    def test_normalize_video_id_strips_hosts_prefix(self):
        self.assertEqual(normalize_video_id("hosts/AXXON/DeviceIpint.1/SourceEndpoint.video:0:0"), "AXXON/DeviceIpint.1/SourceEndpoint.video:0:0")
        self.assertEqual(normalize_video_id("AXXON/DeviceIpint.1/SourceEndpoint.video:0:0"), "AXXON/DeviceIpint.1/SourceEndpoint.video:0:0")

    def test_normalize_camera_rows_filters_blank_access_points(self):
        rows = normalize_camera_rows([
            {"access_point": "hosts/A/cam/1", "display_name": "Gate", "detectors": [{"id": 1}]},
            {"access_point": "", "display_name": "Broken"},
        ])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Gate")
        self.assertEqual(rows[0]["access_point"], "hosts/A/cam/1")
        self.assertEqual(rows[0]["detectors"], [{"id": 1}])


if __name__ == "__main__":
    unittest.main()
