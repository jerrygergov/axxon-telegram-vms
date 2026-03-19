import unittest
from pathlib import Path


class WebApiSurfaceTests(unittest.TestCase):
    def test_notifier_commands_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("notifier-pull", src)
        self.assertIn("notifier-disconnect", src)
        self.assertIn("DomainNotifier.PullEvents", src)
        self.assertIn("DomainNotifier.DisconnectEventChannel", src)

    def test_alert_review_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("alert-review", src)
        self.assertIn("BeginAlertReview", src)
        self.assertIn("CompleteAlertReview", src)

    def test_server_info_commands_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("server-usage", src)
        self.assertIn("server-version", src)
        self.assertIn("server-statistics", src)
        self.assertIn("server-info", src)
        self.assertIn("/info/usage", src)
        self.assertIn("/info/version", src)
        self.assertIn("/statistics/server", src)

    def test_search_events_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("search-events", src)
        self.assertIn("build_event_search_request", src)
        self.assertIn("shape_event_search_results", src)

    def test_plate_search_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("plate-search", src)
        self.assertIn("ReadLprEvents", src)
        self.assertIn("build_license_plate_search_request", src)
        self.assertIn("shape_license_plate_search_results", src)

    def test_face_search_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("face-search", src)
        self.assertIn("FindSimilarObjects", src)
        self.assertIn("build_face_search_request", src)
        self.assertIn("shape_face_search_results", src)

    def test_archive_jump_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("archive-jump", src)
        self.assertIn("archive/contents/intervals", src)
        self.assertIn("archive/statistics/depth", src)
        self.assertIn("build_archive_jump_request", src)

    def test_single_camera_export_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("single-camera-export", src)
        self.assertIn("build_single_camera_export_request", src)
        self.assertIn("resolve_single_camera_export_selection", src)
        self.assertIn("shape_single_camera_export_result", src)
        self.assertIn("export/archive/", src)

    def test_multi_camera_export_plan_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("multi-camera-export-plan", src)
        self.assertIn("build_multi_camera_export_request", src)
        self.assertIn("resolve_multi_camera_export_selection", src)
        self.assertIn("shape_multi_camera_export_result", src)

    def test_macro_execution_commands_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("macro-preview", src)
        self.assertIn("macro-execute", src)
        self.assertIn("ListMacrosV2", src)
        self.assertIn("macro/execute/", src)
        self.assertIn("shape_macro_execution_preview", src)
        self.assertIn("shape_macro_execution_result", src)

    def test_ptz_control_commands_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("ptz-preview", src)
        self.assertIn("ptz-execute", src)
        self.assertIn("TelemetryService.AcquireSessionId", src)
        self.assertIn("TelemetryService.ReleaseSessionId", src)
        self.assertIn("TelemetryService.GoPreset", src)
        self.assertIn("/v1/telemetry/presets", src)
        self.assertIn("shape_ptz_control_preview", src)
        self.assertIn("shape_ptz_control_result", src)

    def test_admin_view_command_present(self):
        src = Path("scripts/axxon_web_api.py").read_text(encoding="utf-8")
        self.assertIn("admin-view", src)
        self.assertIn("SecurityService.ListConfig", src)
        self.assertIn("SecurityService.ListGlobalPermissions", src)
        self.assertIn("/hosts", src)
        self.assertIn("/currentuser", src)
        self.assertIn("shape_admin_view_result", src)


if __name__ == "__main__":
    unittest.main()
