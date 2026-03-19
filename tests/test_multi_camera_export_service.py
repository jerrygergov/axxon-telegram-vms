import unittest

from axxon_telegram_vms.services import (
    MULTI_CAMERA_EXPORT_IMAGE_FORMAT,
    build_multi_camera_export_request,
    multi_camera_export_plan_to_backend_request,
    parse_multi_camera_export_terms,
    resolve_multi_camera_export_selection,
    shape_multi_camera_export_result,
)


CAMERAS = [
    {
        "name": "3.Lobby",
        "access_point": "hosts/ServerA/DeviceIpint.3/SourceEndpoint.video:0:0",
    },
    {
        "name": "2.Gate",
        "access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
    },
    {
        "name": "1.Yard",
        "access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
    },
]


class MultiCameraExportServiceTests(unittest.TestCase):
    def test_parse_terms_supports_exact_timestamp_image_set_mode(self):
        request = parse_multi_camera_export_terms(
            [
                "at=2026-03-10T10:55:00Z",
                "camera=Gate,Yard",
                "max_cameras=3",
            ]
        )

        self.assertEqual(request.mode, "frame_set")
        self.assertEqual(request.export_format, MULTI_CAMERA_EXPORT_IMAGE_FORMAT)
        self.assertEqual(request.request_begin, "20260310T105500")
        self.assertEqual(request.request_end, "20260310T105500")
        self.assertEqual(request.max_cameras, 3)

    def test_selection_resolves_unique_camera_batch_and_backend_requests(self):
        request = build_multi_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_access_points=[
                "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
            ],
            waittimeout_ms=120000,
        )

        selection = resolve_multi_camera_export_selection(request, CAMERAS)

        self.assertEqual(selection.camera_count, 2)
        self.assertEqual([plan.camera for plan in selection.plans], ["2.Gate", "1.Yard"])
        self.assertEqual(
            multi_camera_export_plan_to_backend_request(selection.plans[0]),
            {
                "video_id": "ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "begin": "20260310T105000",
                "end": "20260310T105500",
                "waittimeout_ms": 120000,
                "archive": None,
                "format": "mp4",
            },
        )

    def test_access_point_selectors_take_priority_over_names(self):
        request = build_multi_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_names=["Gate", "Yard"],
            camera_access_points=[
                "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
            ],
            waittimeout_ms=120000,
        )

        selection = resolve_multi_camera_export_selection(request, CAMERAS)

        self.assertEqual(selection.camera_count, 2)
        self.assertEqual([plan.camera_access_point for plan in selection.plans], [
            "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
            "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        ])

    def test_selection_enforces_safe_camera_cap(self):
        request = build_multi_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_names=["Gate", "Yard", "Lobby"],
            max_cameras=2,
        )

        with self.assertRaisesRegex(ValueError, "safe MVP cap"):
            resolve_multi_camera_export_selection(request, CAMERAS)

    def test_shape_result_aggregates_batch_summary(self):
        request = build_multi_camera_export_request(
            begin="20260310T105000",
            end="20260310T105500",
            camera_names=["Gate", "Yard", "Lobby"],
            archive_name="hosts/ServerA/MultimediaStorage.Main/MultimediaStorage",
        )
        selection = resolve_multi_camera_export_selection(request, CAMERAS)

        result = shape_multi_camera_export_result(
            request,
            selection,
            export_results=[
                {
                    "camera_access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                    "artifact_path": "/tmp/gate.mp4",
                    "artifact_size_bytes": 654321,
                    "export_status": {
                        "id": "exp-1",
                        "state": 2,
                        "progress": 1.0,
                        "files": ["ServerA_2.Gate[20260310T105000-20260310T105500].mp4"],
                    },
                },
                {
                    "camera_access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "error": "no data to export",
                    "export_status": {
                        "id": "exp-2",
                        "state": 6,
                        "progress": 1.0,
                        "error": "no data to export",
                    },
                },
            ],
        )

        self.assertEqual(result["selection"]["camera_count"], 3)
        self.assertEqual(result["batch"]["summary"]["state"], "partial")
        self.assertEqual(result["batch"]["summary"]["ready"], 1)
        self.assertEqual(result["batch"]["summary"]["failed"], 1)
        self.assertEqual(result["batch"]["summary"]["pending"], 1)
        self.assertEqual(result["batch"]["summary"]["total_size_bytes"], 654321)
        self.assertEqual(result["batch"]["exports"][0]["export"]["state"], "ready")
        self.assertEqual(result["batch"]["exports"][1]["export"]["state"], "failed")
        self.assertEqual(result["batch"]["exports"][2]["export"]["state"], "planned")
        self.assertEqual(
            result["batch"]["exports"][0]["request"]["archive"],
            "hosts/ServerA/MultimediaStorage.Main/MultimediaStorage",
        )


if __name__ == "__main__":
    unittest.main()
