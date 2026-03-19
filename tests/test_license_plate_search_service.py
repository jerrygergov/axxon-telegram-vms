import unittest
from datetime import datetime, timezone

from axxon_telegram_vms.services import (
    build_license_plate_search_backend_request,
    build_license_plate_search_request,
    license_plate_search_request_to_api_args,
    parse_license_plate_search_terms,
    shape_license_plate_search_results,
)


SEARCH_CARDS = [
    {
        "id": "evt-1",
        "timestamp": "20260310T105500",
        "category": "lpr",
        "event_type": "plateRecognized",
        "state": "HAPPENED",
        "camera": "2.Gate",
        "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
        "detector": "2.LPR",
        "detector_access_point": "hosts/ServerA/AVDetector.2/EventSupplier",
        "plate": "AB1234",
        "confidence": 99.0,
    },
    {
        "id": "evt-2",
        "timestamp": "20260310T104500",
        "category": "lpr",
        "event_type": "listed_lpr_detected",
        "state": "HAPPENED",
        "camera": "2.Gate",
        "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
        "detector": "2.LPR",
        "detector_access_point": "hosts/ServerA/AVDetector.2/EventSupplier",
        "plate": "AB5234",
        "confidence": 95.0,
    },
    {
        "id": "evt-3",
        "timestamp": "20260310T103500",
        "category": "lpr",
        "event_type": "plateRecognized",
        "state": "HAPPENED",
        "camera": "1.Yard",
        "camera_access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "1.LPR",
        "detector_access_point": "hosts/ServerA/AVDetector.1/EventSupplier",
        "plate": "ZZ0001",
        "confidence": 91.0,
    },
]


class LicensePlateSearchServiceTests(unittest.TestCase):
    def test_parse_terms_builds_default_window_and_api_args(self):
        request = parse_license_plate_search_terms(
            [
                "plate=AB1234",
                "camera=Gate",
                "host=ServerA",
                "page=2",
                "page_size=3",
                "sort=asc",
            ],
            now_provider=lambda: datetime(2026, 3, 10, 11, 0, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(request.match_mode, "exact")
        self.assertEqual(request.match_value, "AB1234")
        self.assertEqual(request.time_source, "window")
        self.assertEqual(request.query.scope.hosts, ("ServerA",))
        self.assertEqual(request.query.scope.camera_names, ("Gate",))
        self.assertFalse(request.query.descending)
        self.assertEqual(
            license_plate_search_request_to_api_args(request),
            [
                "--begin", "20260310T100000",
                "--end", "20260310T110000",
                "--page", "2",
                "--page-size", "3",
                "--scan-limit", "400",
                "--ascending",
                "--plate", "AB1234",
                "--scope-host", "ServerA",
                "--camera", "Gate",
            ],
        )

    def test_backend_request_prefers_native_lpr_mask_search(self):
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            mask="*5234",
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            page_size=4,
            descending=False,
        )

        backend_request = build_license_plate_search_backend_request(
            request,
            batch_size=150,
            offset=25,
        )

        self.assertEqual(
            backend_request,
            {
                "begin": "20260310T100000",
                "end": "20260310T110000",
                "subject": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "plate": None,
                "search_predicate": "*5234",
                "limit": 150,
                "offset": 25,
                "descending": False,
            },
        )

    def test_api_args_prefer_access_points_over_names(self):
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            plate="AB1234",
            camera_names=["Gate"],
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            detector_names=["LPR"],
            detector_access_points=["hosts/ServerA/AVDetector.2/EventSupplier"],
        )

        self.assertEqual(
            license_plate_search_request_to_api_args(request),
            [
                "--begin", "20260310T100000",
                "--end", "20260310T110000",
                "--page", "1",
                "--page-size", "5",
                "--scan-limit", "400",
                "--plate", "AB1234",
                "--camera-ap", "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "--detector-ap", "hosts/ServerA/AVDetector.2/EventSupplier",
            ],
        )

    def test_backend_request_accepts_resolved_subject_override(self):
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            contains="123",
            hosts=["ServerA", "ServerB"],
            camera_names=["Gate"],
        )

        backend_request = build_license_plate_search_backend_request(
            request,
            batch_size=120,
            offset=10,
            subject="hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
        )

        self.assertEqual(
            backend_request,
            {
                "begin": "20260310T100000",
                "end": "20260310T110000",
                "subject": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
                "plate": None,
                "search_predicate": "*123*",
                "limit": 120,
                "offset": 10,
                "descending": True,
            },
        )

    def test_shape_results_filters_on_plate_and_builds_pagination(self):
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            contains="234",
            page=2,
            page_size=1,
        )

        result = shape_license_plate_search_results(
            SEARCH_CARDS,
            request,
            scanned_count=3,
            complete=True,
        )

        self.assertEqual(result["summary"]["matched"], 2)
        self.assertEqual(result["summary"]["top_cameras"], [{"name": "2.Gate", "count": 2}])
        self.assertEqual(result["summary"]["top_plates"], [{"name": "AB1234", "count": 1}, {"name": "AB5234", "count": 1}])
        self.assertEqual(result["pagination"]["page"], 2)
        self.assertEqual(result["pagination"]["page_count"], 2)
        self.assertTrue(result["pagination"]["has_previous"])
        self.assertFalse(result["pagination"]["has_next"])
        self.assertEqual([item["id"] for item in result["items"]], ["evt-2"])


if __name__ == "__main__":
    unittest.main()
