import unittest

from axxon_telegram_vms.services import (
    build_single_camera_export_request,
    parse_single_camera_export_terms,
    resolve_single_camera_export_selection,
    shape_single_camera_export_result,
    single_camera_export_request_to_api_args,
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


class SingleCameraExportServiceTests(unittest.TestCase):
    def test_parse_terms_builds_api_args(self):
        request = parse_single_camera_export_terms(
            [
                "from=2026-03-10T10:50:00Z",
                "to=2026-03-10T10:55:00Z",
                "camera=Gate",
                "waittimeout=120000",
            ]
        )

        self.assertEqual(
            single_camera_export_request_to_api_args(request),
            [
                "--begin", "20260310T105000",
                "--end", "20260310T105500",
                "--waittimeout-ms", "120000",
                "--camera", "Gate",
            ],
        )

    def test_selection_resolves_explicit_camera_without_search_rows(self):
        request = build_single_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_names=["Gate"],
        )

        selection = resolve_single_camera_export_selection(request, CAMERAS)

        self.assertEqual(selection.camera, "2.Gate")
        self.assertEqual(selection.camera_access_point, "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0")
        self.assertEqual(selection.request_begin, "20260310T105000")
        self.assertEqual(selection.request_end, "20260310T105500")
        self.assertEqual(selection.target_timestamp, "20260310T105230")
        self.assertEqual(selection.timestamp_source, "range_midpoint")

    def test_api_args_prefer_camera_access_point(self):
        request = build_single_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_names=["Gate"],
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            waittimeout_ms=120000,
        )

        self.assertEqual(
            single_camera_export_request_to_api_args(request),
            [
                "--begin", "20260310T105000",
                "--end", "20260310T105500",
                "--waittimeout-ms", "120000",
                "--camera-ap", "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
            ],
        )

    def test_shape_result_includes_artifact_and_status_summary(self):
        request = build_single_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_access_points=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            waittimeout_ms=120000,
            archive_name="hosts/ServerA/MultimediaStorage.Main/MultimediaStorage",
        )
        selection = resolve_single_camera_export_selection(request, CAMERAS)

        result = shape_single_camera_export_result(
            request,
            selection,
            artifact_path="/tmp/export-clip.mp4",
            artifact_size_bytes=654321,
            export_status={
                "id": "exp-123",
                "state": 2,
                "progress": 1.0,
                "files": ["ServerA_2.Gate[20260310T105000-20260310T105500].mp4"],
            },
        )

        self.assertTrue(result["export"]["ok"])
        self.assertEqual(result["selection"]["video_id"], "ServerA/DeviceIpint.2/SourceEndpoint.video:0:0")
        self.assertEqual(result["export"]["path"], "/tmp/export-clip.mp4")
        self.assertEqual(result["export"]["size_bytes"], 654321)
        self.assertEqual(result["export"]["archive"], "hosts/ServerA/MultimediaStorage.Main/MultimediaStorage")
        self.assertEqual(result["export"]["status"]["state"], 2)


if __name__ == "__main__":
    unittest.main()
