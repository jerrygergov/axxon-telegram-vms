import unittest

from axxon_telegram_vms.services import (
    build_event_search_backend_request,
    build_event_search_request,
    event_search_request_to_api_args,
    parse_event_search_terms,
    shape_event_search_results,
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
        "text": "Plate recognized",
        "plate": "AB1234",
    },
    {
        "id": "evt-2",
        "timestamp": "20260310T104500",
        "category": "motion",
        "event_type": "moveInZone",
        "state": "BEGAN",
        "camera": "1.Yard",
        "camera_access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "Vehicle Detector",
        "detector_access_point": "hosts/ServerA/AppDataDetector.1/EventSupplier",
        "text": "Object moving in area detected",
    },
    {
        "id": "evt-3",
        "timestamp": "20260310T103500",
        "category": "lpr",
        "event_type": "listed_lpr_detected",
        "state": "HAPPENED",
        "camera": "2.Gate",
        "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
        "detector": "2.LPR",
        "detector_access_point": "hosts/ServerA/AVDetector.2/EventSupplier",
        "text": "Listed plate",
        "plate": "BC2345",
    },
    {
        "id": "evt-4",
        "timestamp": "20260310T102500",
        "category": "alert",
        "event_type": "ET_Alert",
        "state": "ST_WANT_REACTION",
        "camera": "1.Yard",
        "camera_access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "Vehicle Detector",
        "text": "Yard alert",
        "priority": "AP_HIGH",
    },
    {
        "id": "evt-5",
        "timestamp": "20260310T101500",
        "category": "lpr",
        "event_type": "plateRecognized",
        "state": "HAPPENED",
        "camera": "2.Gate",
        "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
        "detector": "2.LPR",
        "detector_access_point": "hosts/ServerA/AVDetector.2/EventSupplier",
        "text": "Plate recognized",
        "plate": "CD3456",
    },
]


class EventSearchServiceTests(unittest.TestCase):
    def test_parse_terms_builds_shared_query_and_api_args(self):
        request = parse_event_search_terms(
            [
                "from=2026-03-10T10:00:00Z",
                "to=2026-03-10T11:00:00Z",
                "camera=Gate",
                "detector=LPR",
                "category=lpr",
                "host=ServerA",
                "mode=list",
                "page=2",
                "page_size=3",
                "sort=asc",
            ]
        )

        self.assertEqual(request.mode, "list")
        self.assertEqual(request.page, 2)
        self.assertEqual(request.page_size, 3)
        self.assertFalse(request.query.descending)
        self.assertEqual(request.query.scope.hosts, ("ServerA",))
        self.assertEqual(request.query.scope.camera_names, ("Gate",))
        self.assertEqual(request.query.scope.detector_names, ("LPR",))
        self.assertEqual(request.query.taxonomy.categories, ("lpr",))
        self.assertEqual(
            event_search_request_to_api_args(request),
            [
                "--begin", "20260310T100000",
                "--end", "20260310T110000",
                "--mode", "list",
                "--page", "2",
                "--page-size", "3",
                "--scan-limit", "1200",
                "--ascending",
                "--scope-host", "ServerA",
                "--camera", "Gate",
                "--detector", "LPR",
                "--category", "lpr",
            ],
        )

    def test_backend_request_uses_practical_subject_and_detector_event_hint(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            categories=["lpr"],
            page_size=4,
            descending=False,
        )

        backend_request = build_event_search_backend_request(request, batch_size=150, offset=300)

        self.assertEqual(
            backend_request,
            {
                "begin": "20260310T100000",
                "end": "20260310T110000",
                "subject": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "event_type": "ET_DetectorEvent",
                "limit": 150,
                "offset": 300,
                "descending": False,
            },
        )

    def test_api_args_prefer_access_points_over_names(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_names=["Gate"],
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            detector_names=["LPR"],
            detector_access_points=["hosts/ServerA/AVDetector.2/EventSupplier"],
        )

        self.assertEqual(
            event_search_request_to_api_args(request),
            [
                "--begin", "20260310T100000",
                "--end", "20260310T110000",
                "--mode", "summary",
                "--page", "1",
                "--page-size", "5",
                "--scan-limit", "1200",
                "--camera-ap", "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "--detector-ap", "hosts/ServerA/AVDetector.2/EventSupplier",
            ],
        )

    def test_backend_request_accepts_resolved_subject_override(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            hosts=["ServerA", "ServerB"],
            camera_names=["Gate"],
            categories=["lpr"],
        )

        backend_request = build_event_search_backend_request(
            request,
            batch_size=120,
            offset=40,
            subject="hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
        )

        self.assertEqual(
            backend_request,
            {
                "begin": "20260310T100000",
                "end": "20260310T110000",
                "subject": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
                "event_type": "ET_DetectorEvent",
                "limit": 120,
                "offset": 40,
                "descending": True,
            },
        )

    def test_shape_results_builds_summary_and_pagination(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            mode="list",
            page=2,
            page_size=2,
        )

        result = shape_event_search_results(
            SEARCH_CARDS,
            request,
            scanned_count=5,
            complete=True,
        )

        self.assertEqual(result["summary"]["matched"], 5)
        self.assertEqual(result["summary"]["by_category"], {"alert": 1, "lpr": 3, "motion": 1})
        self.assertEqual(result["pagination"]["page"], 2)
        self.assertEqual(result["pagination"]["page_count"], 3)
        self.assertTrue(result["pagination"]["has_previous"])
        self.assertTrue(result["pagination"]["has_next"])
        self.assertEqual([item["id"] for item in result["items"]], ["evt-3", "evt-4"])

    def test_shape_results_marks_truncation_for_summary_mode(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_names=["Gate"],
            detector_names=["LPR"],
            categories=["lpr"],
            mode="summary",
        )

        result = shape_event_search_results(
            SEARCH_CARDS,
            request,
            scanned_count=1200,
            complete=False,
        )

        self.assertEqual(result["summary"]["matched"], 3)
        self.assertTrue(result["summary"]["truncated"])
        self.assertEqual(result["summary"]["top_cameras"], [{"name": "2.Gate", "count": 3}])
        self.assertEqual(result["summary"]["top_detectors"], [{"name": "2.LPR", "count": 3}])


if __name__ == "__main__":
    unittest.main()
