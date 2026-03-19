import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import run_ptz_execute_flow
from axxon_telegram_vms.services import (
    build_ptz_control_policy,
    parse_ptz_control_terms,
    select_ptz_camera_record,
    select_ptz_preset_record,
    summarize_ptz_preset_row,
)


CAMERAS = [
    {
        "access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
        "display_name": "Gate PTZ",
        "display_id": "2",
        "camera_access": "CAMERA_ACCESS_FULL",
        "ptzs": [{"is_active": True, "pointMove": False, "areaZoom": False}],
    }
]

PRESETS = [
    {"label": "Home Position", "position": 12},
    {"label": "Road Overview", "position": 18},
]

POSITION_INFO = {
    "capabilities": {
        "move_supported": {"is_absolute": True},
        "zoom_supported": {"is_absolute": True},
        "iris_supported": None,
        "focus_supported": None,
        "is_tours_supported": False,
    },
    "absolute_position": {
        "pan": 0.1,
        "tilt": 0.2,
        "zoom": 0.3,
    },
}


class FakePtzClient:
    def __init__(self, *, go_preset_error: str | None = None, release_error: str | None = None):
        self.go_preset_error = go_preset_error
        self.release_error = release_error
        self.calls: list[str] = []

    def ptz_acquire_session(self, access_point: str):
        self.calls.append("acquire")
        return {"session_id": 41, "error_code": "NotError"}

    def ptz_go_preset(self, access_point: str, session_id: object, position: int, speed: int):
        self.calls.append("go_preset")
        if self.go_preset_error:
            raise RuntimeError(self.go_preset_error)
        return {"error_code": "NotError"}

    def ptz_release_session(self, session_id: object, access_point: str):
        self.calls.append("release")
        if self.release_error:
            raise RuntimeError(self.release_error)
        return {"released": True}


def _build_runtime_inputs():
    request = parse_ptz_control_terms(["camera=2.Gate", "PTZ", "preset=Home", "Position"])
    camera = select_ptz_camera_record(request, CAMERAS)
    preset = select_ptz_preset_record(request, PRESETS)
    policy = build_ptz_control_policy(
        control_enabled=True,
        admin=True,
        allowed_camera_access_points=[camera.camera_access_point],
    )
    return request, camera, preset, policy


class PtzExecutionTests(unittest.TestCase):
    def test_release_session_runs_after_successful_preset(self):
        request, camera, preset, policy = _build_runtime_inputs()
        client = FakePtzClient()

        result = run_ptz_execute_flow(
            client,
            request=request,
            camera=camera,
            preset=preset,
            policy=policy,
            position_info=POSITION_INFO,
            presets=[summarize_ptz_preset_row(item) for item in PRESETS],
        )

        self.assertTrue(result["execution"]["attempted"])
        self.assertTrue(result["execution"]["ok"])
        self.assertEqual(client.calls, ["acquire", "go_preset", "release"])
        self.assertEqual(result["execution"]["response"]["release"], {"released": True})

    def test_release_session_runs_after_command_failure(self):
        request, camera, preset, policy = _build_runtime_inputs()
        client = FakePtzClient(go_preset_error="boom")

        result = run_ptz_execute_flow(
            client,
            request=request,
            camera=camera,
            preset=preset,
            policy=policy,
            position_info=POSITION_INFO,
            presets=[summarize_ptz_preset_row(item) for item in PRESETS],
        )

        self.assertEqual(client.calls, ["acquire", "go_preset", "release"])
        self.assertFalse(result["execution"]["ok"])
        self.assertEqual(result["execution"]["error"], "boom")


if __name__ == "__main__":
    unittest.main()
