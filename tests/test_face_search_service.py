import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from axxon_telegram_vms.services import (
    build_face_search_backend_request,
    detect_face_search_capability,
    face_search_request_to_api_args,
    load_face_search_reference_image,
    parse_face_search_terms,
    resolve_face_search_selection,
    shape_face_search_results,
)


DETECTOR_ROWS = [
    {
        "camera_access_point": "hosts/ServerA/DeviceIpint.10/SourceEndpoint.video:0:0",
        "camera_name": "1.Lobby",
        "detector_access_point": "hosts/ServerA/AVDetector.9/EventSupplier",
        "detector_name": "1.Face detection",
        "detector_type_name": "Face detection",
        "events": ["faceAppeared"],
    },
    {
        "camera_access_point": "hosts/ServerA/DeviceIpint.11/SourceEndpoint.video:0:0",
        "camera_name": "2.Gate",
        "detector_access_point": "hosts/ServerA/AVDetector.10/EventSupplier",
        "detector_name": "Camera B detection",
        "detector_type_name": "Face detector",
        "events": ["faceAppeared"],
    },
    {
        "camera_access_point": "hosts/ServerA/DeviceIpint.12/SourceEndpoint.video:0:0",
        "camera_name": "3.Yard",
        "detector_access_point": "hosts/ServerA/AppDataDetector.2/EventSupplier",
        "detector_name": "3.Vehicle",
        "detector_type_name": "Situation detector",
        "events": ["moveInZone"],
    },
]

SEARCH_MATCHES = [
    {
        "score": 0.994738,
        "event": {
            "event_type": "ET_DetectorEvent",
            "body": {
                "guid": "face-1",
                "timestamp": "20260310T105500",
                "event_type": "faceAppeared",
                "state": "SPECIFIED",
                "origin_ext": {
                    "access_point": "hosts/ServerA/DeviceIpint.10/SourceEndpoint.video:0:0",
                    "friendly_name": "1.Lobby",
                },
                "detector_ext": {
                    "access_point": "hosts/ServerA/AVDetector.9/EventSupplier",
                    "friendly_name": "1.Face detection",
                },
                "detectors_group": ["DG_FACE_DETECTOR"],
            },
            "localization": {"text": "Face appeared"},
        },
    },
    {
        "score": 0.962100,
        "event": {
            "event_type": "ET_DetectorEvent",
            "body": {
                "guid": "face-2",
                "timestamp": "20260310T104500",
                "event_type": "faceAppeared",
                "state": "SPECIFIED",
                "origin_ext": {
                    "access_point": "hosts/ServerA/DeviceIpint.10/SourceEndpoint.video:0:0",
                    "friendly_name": "1.Lobby",
                },
                "detector_ext": {
                    "access_point": "hosts/ServerA/AVDetector.9/EventSupplier",
                    "friendly_name": "1.Face detection",
                },
                "detectors_group": ["DG_FACE_DETECTOR"],
            },
            "localization": {"text": "Face appeared"},
        },
    },
]


class FaceSearchServiceTests(unittest.TestCase):
    def _write_reference_image(self, path: Path) -> None:
        path.write_bytes(b"\xff\xd8\xff\xe0" + (b"\x00" * 32) + b"\xff\xd9")

    def test_parse_terms_builds_default_window_and_api_args(self):
        request = parse_face_search_terms(
            [
                "camera=Lobby",
                "host=ServerA",
                "accuracy=0.82",
                "page=2",
                "page_size=3",
            ],
            now_provider=lambda: datetime(2026, 3, 10, 11, 0, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(request.query.scope.hosts, ("ServerA",))
        self.assertEqual(request.query.scope.camera_names, ("Lobby",))
        self.assertEqual(request.accuracy, 0.82)
        self.assertEqual(request.time_source, "window")
        self.assertEqual(
            face_search_request_to_api_args(request, image_path="/tmp/reference.jpg"),
            [
                "--image", "/tmp/reference.jpg",
                "--begin", "20260310T100000",
                "--end", "20260310T110000",
                "--page", "2",
                "--page-size", "3",
                "--scan-limit", "10",
                "--accuracy", "0.820000",
                "--scope-host", "ServerA",
                "--camera", "Lobby",
            ],
        )

    def test_reference_image_loader_requires_jpeg(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            png_path = Path(tmpdir) / "reference.png"
            png_path.write_bytes(b"\x89PNG\r\n\x1a\n")
            with self.assertRaisesRegex(ValueError, "JPEG"):
                load_face_search_reference_image(png_path)

            jpeg_path = Path(tmpdir) / "reference.jpg"
            self._write_reference_image(jpeg_path)
            reference = load_face_search_reference_image(jpeg_path)

        self.assertEqual(reference.file_name, "reference.jpg")
        self.assertGreater(reference.size_bytes, 10)
        self.assertTrue(reference.jpeg_base64)
        self.assertEqual(len(reference.sha256), 64)

    def test_selection_reports_capability_and_builds_backend_request(self):
        request = parse_face_search_terms(
            [
                "camera=Lobby",
                "from=20260310T100000",
                "to=20260310T110000",
                "accuracy=0.75",
            ],
        )

        capability = detect_face_search_capability(DETECTOR_ROWS)
        selection = resolve_face_search_selection(request, DETECTOR_ROWS)

        self.assertTrue(capability.available)
        self.assertEqual(capability.detector_count, 2)
        self.assertEqual(capability.camera_count, 2)
        self.assertTrue(selection.searchable)
        self.assertEqual(selection.camera_count, 1)
        self.assertEqual(selection.detector_count, 1)

        with tempfile.TemporaryDirectory() as tmpdir:
            reference_path = Path(tmpdir) / "reference.jpg"
            self._write_reference_image(reference_path)
            reference = load_face_search_reference_image(reference_path)
            backend_request = build_face_search_backend_request(request, selection, reference)

        self.assertEqual(
            backend_request,
            {
                "session": 0,
                "is_face": True,
                "minimal_score": 0.75,
                "jpeg_image": reference.jpeg_base64,
                "range": {
                    "begin_time": "20260310T100000",
                    "end_time": "20260310T110000",
                },
                "origin_ids": ["hosts/ServerA/DeviceIpint.10/SourceEndpoint.video:0:0"],
                "limit": 10,
                "offset": 0,
            },
        )

    def test_shape_results_formats_similarity_and_action_commands(self):
        request = parse_face_search_terms(
            [
                "camera=Lobby",
                "from=20260310T100000",
                "to=20260310T110000",
                "page=1",
                "page_size=1",
            ],
        )
        selection = resolve_face_search_selection(request, DETECTOR_ROWS)

        with tempfile.TemporaryDirectory() as tmpdir:
            reference_path = Path(tmpdir) / "reference.jpg"
            self._write_reference_image(reference_path)
            reference = load_face_search_reference_image(reference_path)
            result = shape_face_search_results(
                SEARCH_MATCHES,
                request,
                selection,
                reference,
                scanned_count=2,
                complete=True,
            )

        self.assertEqual(result["summary"]["matched"], 2)
        self.assertEqual(result["summary"]["top_cameras"], [{"name": "1.Lobby", "count": 2}])
        self.assertEqual(result["pagination"]["page_count"], 2)
        self.assertTrue(result["pagination"]["has_next"])
        self.assertEqual(result["items"][0]["id"], "face-1")
        self.assertEqual(result["items"][0]["event_guid"], "face-1")
        self.assertEqual(result["items"][0]["similarity"], 0.994738)
        self.assertIn("raw_event", result["items"][0])
        self.assertIn("/archive camera_ap=hosts/ServerA/DeviceIpint.10/SourceEndpoint.video:0:0", result["items"][0]["archive_command"])
        self.assertIn("/export from=20260310T105445", result["items"][0]["export_command"])


if __name__ == "__main__":
    unittest.main()
