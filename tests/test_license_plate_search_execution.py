import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import _license_plate_search_rows, _plate_search_image_camera_access_point
from axxon_telegram_vms.services import build_license_plate_search_request


CAMERA_ROWS = [
    {
        "access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        "display_name": "Gate",
        "display_id": "1",
        "detectors": [],
    },
    {
        "access_point": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
        "display_name": "Gate",
        "display_id": "2",
        "detectors": [],
    },
]


EVENTS_BY_SUBJECT = {
    "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0": [
        {
            "id": "evt-a",
            "timestamp": "20260310T105500",
            "category": "lpr",
            "event_type": "plateRecognized",
            "camera": "1.Gate",
            "camera_access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
            "plate": "AB1234",
            "text": "Gate A",
        }
    ],
    "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0": [
        {
            "id": "evt-b",
            "timestamp": "20260310T105400",
            "category": "lpr",
            "event_type": "plateRecognized",
            "camera": "2.Gate",
            "camera_access_point": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
            "plate": "CD1234",
            "text": "Gate B",
        }
    ],
}


class FakeLprClient:
    def __init__(self):
        self.read_calls: list[dict[str, object]] = []

    def list_cameras(self, view: str = None, filter_prefix: str = None):
        self.last_view = view
        self.last_filter_prefix = filter_prefix
        return CAMERA_ROWS

    def read_lpr_events(
        self,
        begin: str,
        end: str,
        subject: str = None,
        plate: str = None,
        search_predicate: str = None,
        limit: int = 100,
        offset: int = 0,
        descending: bool = True,
    ):
        self.read_calls.append(
            {
                "subject": subject,
                "plate": plate,
                "search_predicate": search_predicate,
                "limit": limit,
                "offset": offset,
                "descending": descending,
            }
        )
        rows = list(EVENTS_BY_SUBJECT.get(subject, ()))
        return rows[offset : offset + limit]


class LicensePlateSearchExecutionTests(unittest.TestCase):
    def test_contains_search_reads_each_resolved_camera_scope(self):
        client = FakeLprClient()
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            contains="123",
            camera_names=["Gate"],
            hosts=["ServerA", "ServerB"],
            page_size=5,
        )

        rows, scanned, complete = _license_plate_search_rows(client, request, batch_size=50)

        self.assertEqual([row["plate"] for row in rows], ["AB1234", "CD1234"])
        self.assertEqual(
            client.read_calls,
            [
                {
                    "subject": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "plate": None,
                    "search_predicate": "*123*",
                    "limit": 50,
                    "offset": 0,
                    "descending": True,
                },
                {
                    "subject": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
                    "plate": None,
                    "search_predicate": "*123*",
                    "limit": 50,
                    "offset": 0,
                    "descending": True,
                },
            ],
        )
        self.assertEqual(scanned, 2)
        self.assertTrue(complete)

    def test_plate_search_with_unmatched_scope_does_not_fallback_to_broad_query(self):
        client = FakeLprClient()
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            contains="123",
            camera_names=["Gate"],
            hosts=["ServerC"],
            page_size=5,
        )

        rows, scanned, complete = _license_plate_search_rows(client, request, batch_size=50)

        self.assertEqual(rows, [])
        self.assertEqual(scanned, 0)
        self.assertTrue(complete)
        self.assertEqual(client.read_calls, [])

    def test_plate_search_image_helper_falls_back_to_explicit_subject(self):
        subject = "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0"
        request = build_license_plate_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            contains="123",
            camera_access_points=[subject],
        )

        camera_access_point = _plate_search_image_camera_access_point(
            {"id": "evt-subject-fallback", "timestamp": "20260310T105500"},
            request,
            explicit_subject=subject,
        )

        self.assertEqual(camera_access_point, subject)


if __name__ == "__main__":
    unittest.main()
