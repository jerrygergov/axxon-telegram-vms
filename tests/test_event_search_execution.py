import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import _event_search_rows
from axxon_telegram_vms.services import build_event_search_request


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
            "text": "Gate B",
        }
    ],
}


class FakeEventClient:
    def __init__(self):
        self.read_calls: list[dict[str, object]] = []

    def list_cameras(self, view: str = None, filter_prefix: str = None):
        self.last_view = view
        self.last_filter_prefix = filter_prefix
        return CAMERA_ROWS

    def read_events(
        self,
        begin: str,
        end: str,
        subject: str = None,
        event_type: str = None,
        values: str = None,
        limit: int = 100,
        offset: int = 0,
        descending: bool = True,
    ):
        self.read_calls.append(
            {
                "subject": subject,
                "event_type": event_type,
                "limit": limit,
                "offset": offset,
                "descending": descending,
            }
        )
        rows = list(EVENTS_BY_SUBJECT.get(subject, ()))
        return rows[offset : offset + limit]


class EventSearchExecutionTests(unittest.TestCase):
    def test_event_search_uses_explicit_camera_access_point_without_inventory_match(self):
        client = FakeEventClient()
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_access_points=["hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0"],
            categories=["lpr"],
            page_size=2,
        )

        rows, scanned, complete = _event_search_rows(client, request, batch_size=50)

        self.assertEqual([row["id"] for row in rows], ["evt-b"])
        self.assertEqual(
            client.read_calls,
            [
                {
                    "subject": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
                    "event_type": "ET_DetectorEvent",
                    "limit": 50,
                    "offset": 0,
                    "descending": True,
                }
            ],
        )
        self.assertEqual(scanned, 1)
        self.assertTrue(complete)

    def test_event_search_reads_each_exact_subject_and_merges_results(self):
        client = FakeEventClient()
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            hosts=["ServerA", "ServerB"],
            camera_names=["Gate"],
            categories=["lpr"],
            page_size=2,
        )

        rows, scanned, complete = _event_search_rows(client, request, batch_size=50)

        self.assertEqual([row["id"] for row in rows], ["evt-a", "evt-b"])
        self.assertEqual(
            client.read_calls,
            [
                {
                    "subject": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "event_type": "ET_DetectorEvent",
                    "limit": 50,
                    "offset": 0,
                    "descending": True,
                },
                {
                    "subject": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
                    "event_type": "ET_DetectorEvent",
                    "limit": 50,
                    "offset": 0,
                    "descending": True,
                },
            ],
        )
        self.assertEqual(scanned, 2)
        self.assertTrue(complete)

    def test_event_search_with_unmatched_scope_does_not_fallback_to_broad_query(self):
        client = FakeEventClient()
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            hosts=["ServerC"],
            camera_names=["Gate"],
            categories=["lpr"],
            page_size=2,
        )

        rows, scanned, complete = _event_search_rows(client, request, batch_size=50)

        self.assertEqual(rows, [])
        self.assertEqual(scanned, 0)
        self.assertTrue(complete)
        self.assertEqual(client.read_calls, [])


if __name__ == "__main__":
    unittest.main()
