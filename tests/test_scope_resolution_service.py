import unittest

from axxon_telegram_vms.services import build_event_search_request
from axxon_telegram_vms.services.scope_resolution import resolve_scope_subjects


CAMERA_ROWS = [
    {
        "access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
        "display_name": "Gate",
        "display_id": "1",
        "detectors": [{"access_point": "hosts/ServerA/AppDataDetector.1/EventSupplier", "display_name": "LPR", "display_id": "1"}],
    },
    {
        "access_point": "hosts/ServerB/DeviceIpint.2/SourceEndpoint.video:0:0",
        "display_name": "Gate",
        "display_id": "2",
        "detectors": [{"access_point": "hosts/ServerB/AppDataDetector.7/EventSupplier", "display_name": "LPR", "display_id": "7"}],
    },
]


class ScopeResolutionTests(unittest.TestCase):
    def test_preserves_explicit_camera_access_point_without_inventory_match(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            camera_access_points=["hosts/ServerZ/DeviceIpint.9/SourceEndpoint.video:0:0"],
        )

        resolved = resolve_scope_subjects(request.query.scope, CAMERA_ROWS, include_detectors=True)

        self.assertEqual(
            resolved.camera_access_points,
            ("hosts/ServerZ/DeviceIpint.9/SourceEndpoint.video:0:0",),
        )
        self.assertEqual(resolved.detector_access_points, ())

    def test_resolve_camera_name_and_host_to_exact_camera_subjects(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            hosts=["ServerA"],
            camera_names=["Gate"],
        )

        resolved = resolve_scope_subjects(request.query.scope, CAMERA_ROWS, include_detectors=True)

        self.assertEqual(
            resolved.camera_access_points,
            ("hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",),
        )
        self.assertEqual(resolved.detector_access_points, ())

    def test_resolve_detector_scope_to_exact_detector_subjects(self):
        request = build_event_search_request(
            begin="20260310T100000",
            end="20260310T110000",
            hosts=["ServerB"],
            camera_names=["Gate"],
            detector_names=["LPR"],
        )

        resolved = resolve_scope_subjects(request.query.scope, CAMERA_ROWS, include_detectors=True)

        self.assertEqual(resolved.camera_access_points, ())
        self.assertEqual(
            resolved.detector_access_points,
            ("hosts/ServerB/AppDataDetector.7/EventSupplier",),
        )


if __name__ == "__main__":
    unittest.main()
