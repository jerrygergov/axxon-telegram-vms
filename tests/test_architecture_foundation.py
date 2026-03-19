import importlib
import unittest

from axxon_telegram_vms import ACTIVE_RUNTIME_ENTRYPOINTS, ARCHITECTURE_LANES


class ArchitectureFoundationTests(unittest.TestCase):
    def test_active_runtime_remains_script_based(self):
        self.assertEqual(
            ACTIVE_RUNTIME_ENTRYPOINTS,
            (
                "scripts/axxon_tg_bot.py",
                "scripts/axxon_tg_ui.py",
                "scripts/axxon_web_api.py",
            ),
        )

    def test_expected_placeholder_lanes_exist(self):
        self.assertEqual(
            tuple(lane.name for lane in ARCHITECTURE_LANES),
            ("client", "services", "models", "jobs", "ui"),
        )
        by_name = {lane.name: lane for lane in ARCHITECTURE_LANES}
        self.assertEqual(by_name["client"].status, "seeded")
        self.assertEqual(by_name["services"].status, "seeded")
        self.assertEqual(by_name["models"].status, "seeded")
        self.assertEqual(by_name["jobs"].status, "seeded")
        self.assertEqual(by_name["ui"].status, "placeholder")
        self.assertIn("scripts/axxon_web_api.py", ARCHITECTURE_LANES[0].seed_modules)
        self.assertIn("axxon_telegram_vms/client/session.py", ARCHITECTURE_LANES[0].seed_modules)
        self.assertIn("axxon_telegram_vms/client/transport.py", ARCHITECTURE_LANES[0].seed_modules)
        self.assertIn("scripts/axxon_tg_bot.py", ARCHITECTURE_LANES[1].seed_modules)
        self.assertIn("axxon_telegram_vms/services/subscriptions.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/event_search.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/external_analysis.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/face_search.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/admin_view.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/license_plate_search.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/macro_execution.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/multi_camera_export.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/services/ptz_control.py", by_name["services"].seed_modules)
        self.assertIn("axxon_telegram_vms/models/event_normalization.py", by_name["models"].seed_modules)
        self.assertIn("axxon_telegram_vms/models/query_filters.py", by_name["models"].seed_modules)
        self.assertIn("axxon_telegram_vms/models/request_envelopes.py", by_name["models"].seed_modules)
        self.assertIn("axxon_telegram_vms/jobs/external_analysis.py", by_name["jobs"].seed_modules)
        self.assertIn("axxon_telegram_vms/jobs/live_sessions.py", by_name["jobs"].seed_modules)
        self.assertIn("scripts/tg_admin_ui.py", by_name["ui"].seed_modules)

    def test_placeholder_subpackages_are_importable(self):
        for lane_name in ("client", "services", "models", "jobs", "ui"):
            module = importlib.import_module(f"axxon_telegram_vms.{lane_name}")
            self.assertEqual(module.PACKAGE_LANE, lane_name)

    def test_models_lane_exports_first_real_normalization_seam(self):
        models = importlib.import_module("axxon_telegram_vms.models")
        self.assertTrue(hasattr(models, "NormalizedDetectorRow"))
        self.assertTrue(hasattr(models, "NormalizedEvent"))
        self.assertTrue(hasattr(models, "EventQuery"))
        self.assertTrue(hasattr(models, "RequestEnvelope"))
        self.assertTrue(callable(models.normalize_event))
        self.assertTrue(callable(models.build_request_envelope))

    def test_client_lane_exports_first_transport_foundation_seam(self):
        client = importlib.import_module("axxon_telegram_vms.client")
        self.assertTrue(callable(client.load_axxon_config))
        self.assertTrue(callable(client.build_server_info_payload))
        self.assertTrue(callable(client.parse_grpc_response))
        self.assertTrue(hasattr(client, "TTLCache"))
        self.assertTrue(hasattr(client, "RuntimeReadCache"))
        self.assertTrue(hasattr(client, "WebSessionContract"))
        self.assertTrue(callable(client.build_web_session_contract))
        self.assertTrue(callable(client.shape_web_session_summary))

    def test_services_lane_exports_first_orchestration_foundation_seam(self):
        services = importlib.import_module("axxon_telegram_vms.services")
        self.assertTrue(hasattr(services, "SubscriptionRecord"))
        self.assertTrue(hasattr(services, "SubscriptionLedger"))
        self.assertTrue(hasattr(services, "EventSearchRequest"))
        self.assertTrue(hasattr(services, "ExternalAnalysisRequest"))
        self.assertTrue(hasattr(services, "FaceSearchRequest"))
        self.assertTrue(hasattr(services, "LicensePlateSearchRequest"))
        self.assertTrue(hasattr(services, "AdminViewPolicy"))
        self.assertTrue(hasattr(services, "MacroExecutionRequest"))
        self.assertTrue(hasattr(services, "MultiCameraExportRequest"))
        self.assertTrue(hasattr(services, "PtzControlRequest"))
        self.assertTrue(callable(services.build_admin_view_policy))
        self.assertTrue(callable(services.subscription_query_from_filters))
        self.assertTrue(callable(services.parse_event_search_terms))
        self.assertTrue(callable(services.build_external_analysis_request))
        self.assertTrue(callable(services.parse_face_search_terms))
        self.assertTrue(callable(services.parse_license_plate_search_terms))
        self.assertTrue(callable(services.parse_macro_execution_terms))
        self.assertTrue(callable(services.parse_multi_camera_export_terms))
        self.assertTrue(callable(services.parse_ptz_control_terms))
        self.assertTrue(callable(services.shape_event_search_results))
        self.assertTrue(callable(services.shape_face_search_results))
        self.assertTrue(callable(services.shape_license_plate_search_results))
        self.assertTrue(callable(services.shape_admin_view_result))
        self.assertTrue(callable(services.shape_external_analysis_submission))
        self.assertTrue(callable(services.shape_macro_execution_preview))
        self.assertTrue(callable(services.shape_multi_camera_export_result))
        self.assertTrue(callable(services.shape_ptz_control_preview))
        self.assertTrue(callable(services.subscription_states_match))

    def test_jobs_lane_exports_first_job_foundation_seam(self):
        jobs = importlib.import_module("axxon_telegram_vms.jobs")
        self.assertTrue(hasattr(jobs, "ExternalAnalysisJobRecord"))
        self.assertTrue(hasattr(jobs, "LiveSessionRecord"))
        self.assertTrue(hasattr(jobs, "LiveSessionRuntime"))
        self.assertTrue(callable(jobs.build_external_analysis_job_record))


if __name__ == "__main__":
    unittest.main()
