import unittest

from axxon_telegram_vms.services import (
    archive_jump_request_to_api_args,
    build_archive_jump_request,
    derive_archive_jump_selection,
    parse_archive_jump_terms,
    shape_archive_jump_result,
)


CAMERAS = [
    {
        "name": "2.Gate",
        "access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
    },
    {
        "name": "1.Yard",
        "access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
    },
]

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
        "timestamp": "20260310T101500",
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
]


class ArchiveJumpServiceTests(unittest.TestCase):
    def test_parse_archive_terms_builds_api_args_for_exact_timestamp(self):
        request = parse_archive_jump_terms(
            [
                "camera=Gate",
                "at=2026-03-10T10:55:00Z",
            ]
        )

        self.assertEqual(request.query.scope.camera_names, ("Gate",))
        self.assertEqual(
            archive_jump_request_to_api_args(request),
            [
                "--begin", "20260310T105500",
                "--end", "20260310T105500",
                "--scan-limit", "400",
                "--preview-width", "1280",
                "--preview-height", "720",
                "--preview-threshold-ms", "250",
                "--context-window-sec", "300",
                "--at", "20260310T105500",
                "--camera", "Gate",
            ],
        )

    def test_selection_prefers_matching_event_when_range_search_has_results(self):
        request = build_archive_jump_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_names=["Gate"],
            categories=["lpr"],
        )

        selection = derive_archive_jump_selection(request, SEARCH_CARDS, CAMERAS)

        self.assertEqual(selection.camera, "2.Gate")
        self.assertEqual(selection.camera_access_point, "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0")
        self.assertEqual(selection.target_timestamp, "20260310T105500")
        self.assertEqual(selection.timestamp_source, "matching_event")
        self.assertEqual(selection.matched_count, 2)

    def test_selection_falls_back_to_range_midpoint_when_camera_is_explicit(self):
        request = build_archive_jump_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
        )

        selection = derive_archive_jump_selection(request, [], CAMERAS)

        self.assertEqual(selection.camera, "2.Gate")
        self.assertEqual(selection.target_timestamp, "20260310T103000")
        self.assertEqual(selection.timestamp_source, "range_midpoint")

    def test_shape_result_builds_context_handle_and_archive_presence(self):
        request = build_archive_jump_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
        )
        selection = derive_archive_jump_selection(request, [], CAMERAS)

        result = shape_archive_jump_result(
            request,
            selection,
            preview_path="/tmp/archive-preview.jpg",
            preview_mode="media",
            archives=[{"name": "hosts/ServerA/MultimediaStorage.Main/MultimediaStorage", "default": True}],
            depth={"start": "20260301T000000", "end": "20260311T000000"},
            intervals=[{"begin": "20260310T102000", "end": "20260310T104000"}],
        )

        self.assertTrue(result["preview"]["ok"])
        self.assertTrue(result["archive"]["in_archive"])
        self.assertEqual(
            result["archive"]["context_handle"],
            {
                "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "video_id": "ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "timestamp": "20260310T103000",
                "request_begin": "20260310T100000",
                "request_end": "20260310T110000",
                "interval_begin": "20260310T102000",
                "interval_end": "20260310T104000",
                "archive": "hosts/ServerA/MultimediaStorage.Main/MultimediaStorage",
            },
        )


if __name__ == "__main__":
    unittest.main()
