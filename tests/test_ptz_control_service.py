import unittest

from axxon_telegram_vms.services import (
    build_ptz_control_policy,
    build_ptz_goto_preset_backend_request,
    evaluate_ptz_control_guardrails,
    parse_ptz_control_terms,
    ptz_control_request_to_api_args,
    select_ptz_camera_record,
    select_ptz_preset_record,
    shape_ptz_control_result,
    summarize_ptz_preset_row,
)


CAMERAS = [
    {
        "access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
        "display_name": "Gate PTZ",
        "display_id": "2",
        "camera_access": "CAMERA_ACCESS_FULL",
        "ptzs": [
            {
                "is_active": True,
                "pointMove": False,
                "areaZoom": False,
            }
        ],
    },
    {
        "access_point": "hosts/ServerA/DeviceIpint.3/SourceEndpoint.video:0:0",
        "display_name": "Lobby",
        "display_id": "3",
        "camera_access": "CAMERA_ACCESS_FULL",
        "ptzs": [],
    },
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


class PtzControlServiceTests(unittest.TestCase):
    def test_parse_terms_accepts_multi_token_camera_and_preset(self):
        request = parse_ptz_control_terms(["camera=2.Gate", "PTZ", "preset=Home", "Position", "speed=7"])

        self.assertEqual(request.camera_name, "2.Gate PTZ")
        self.assertEqual(request.preset_label, "Home Position")
        self.assertEqual(request.speed, 7)
        self.assertEqual(
            ptz_control_request_to_api_args(request),
            ["--camera", "2.Gate PTZ", "--preset", "Home Position", "--speed", "7"],
        )

    def test_guardrails_allow_allowlisted_admin_camera_and_preset(self):
        request = parse_ptz_control_terms(["camera=2.Gate PTZ", "position=12"])
        camera = select_ptz_camera_record(request, CAMERAS)
        preset = select_ptz_preset_record(request, PRESETS)
        policy = build_ptz_control_policy(
            control_enabled=True,
            admin=True,
            allowed_camera_access_points=[camera.camera_access_point],
        )

        decision = evaluate_ptz_control_guardrails(
            request,
            camera,
            preset,
            policy,
            position_info=POSITION_INFO,
            preview_error=None,
        )

        self.assertTrue(decision.allowed)
        self.assertIn("Guardrails are re-checked immediately before execution.", decision.warnings)

    def test_guardrails_block_non_ptz_camera(self):
        request = parse_ptz_control_terms(["camera=3.Lobby", "position=12"])
        camera = select_ptz_camera_record(request, CAMERAS)
        preset = select_ptz_preset_record(request, PRESETS)
        policy = build_ptz_control_policy(
            control_enabled=True,
            admin=True,
            allowed_camera_names=[camera.camera_name],
        )

        decision = evaluate_ptz_control_guardrails(
            request,
            camera,
            preset,
            policy,
            position_info=POSITION_INFO,
            preview_error=None,
        )

        self.assertFalse(decision.allowed)
        self.assertTrue(any("no PTZ inventory" in item for item in decision.reasons))

    def test_backend_request_shape_uses_position_and_speed(self):
        request = parse_ptz_control_terms(["camera_ap=hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0", "position=18", "speed=6"])
        camera = select_ptz_camera_record(request, CAMERAS)
        preset = select_ptz_preset_record(request, PRESETS)

        payload = build_ptz_goto_preset_backend_request(
            request,
            camera,
            preset,
            session_id=41,
        )

        self.assertEqual(
            payload,
            {
                "access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                "session_id": 41,
                "position": 18,
                "speed": 6,
            },
        )

    def test_shape_result_keeps_preview_and_execution_state(self):
        request = parse_ptz_control_terms(["camera=2.Gate PTZ", "preset=Home", "Position"])
        camera = select_ptz_camera_record(request, CAMERAS)
        preset = select_ptz_preset_record(request, PRESETS)
        policy = build_ptz_control_policy(
            control_enabled=False,
            admin=True,
            allowed_camera_names=[camera.camera_name],
        )
        decision = evaluate_ptz_control_guardrails(
            request,
            camera,
            preset,
            policy,
            position_info=POSITION_INFO,
            preview_error=None,
        )

        result = shape_ptz_control_result(
            request,
            camera,
            decision,
            policy=policy,
            position_info=POSITION_INFO,
            presets=[summarize_ptz_preset_row(item) for item in PRESETS],
            preset=preset,
            preview_error=None,
            attempted=False,
            ok=False,
            transport=None,
            response=None,
            error=None,
        )

        self.assertEqual(result["request"]["action"], "goto_preset")
        self.assertEqual(result["camera"]["name"], "2.Gate PTZ")
        self.assertEqual(result["ptz"]["selected_preset"]["position"], 12)
        self.assertFalse(result["guardrails"]["allowed"])
        self.assertFalse(result["execution"]["attempted"])
        self.assertTrue(result["execution"]["blocked"])


if __name__ == "__main__":
    unittest.main()
