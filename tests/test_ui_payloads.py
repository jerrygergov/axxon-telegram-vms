import unittest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_tg_ui import (
    archive_jump_payload,
    callback_payload,
    event_search_payload,
    face_search_payload,
    macro_execution_payload,
    plate_search_payload,
    ptz_control_payload,
    server_version_payload,
    single_camera_export_payload,
)


EVENT_CARDS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "timestamp": "20260308T224316.914000",
        "category": "motion",
        "event_type": "moveInZone",
        "state": "BEGAN",
        "camera": "Camera A",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "Vehicle Detector",
        "detector_access_point": "hosts/AXXON_SERVER/AppDataDetector.1/EventSupplier",
        "text": "Vehicle entered zone",
        "label_primary": "Object moving in area detected",
        "label_secondary": "Vehicle Detector · Camera A",
        "label_status": "began",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "timestamp": "20260308T224315.914000",
        "category": "motion",
        "event_type": "moveInZone",
        "state": "ENDED",
        "camera": "Camera A",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "Vehicle Detector",
        "detector_access_point": "hosts/AXXON_SERVER/AppDataDetector.1/EventSupplier",
        "text": "Vehicle left zone",
        "label_primary": "Object moving in area detected",
        "label_secondary": "Vehicle Detector · Camera A",
        "label_status": "ended",
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "timestamp": "20260308T224314.914000",
        "category": "motion",
        "event_type": "moveInZone",
        "state": "BEGAN",
        "camera": "Camera A",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "Person Detector",
        "detector_access_point": "hosts/AXXON_SERVER/AppDataDetector.2/EventSupplier",
        "text": "Person entered zone",
        "label_primary": "Object moving in area detected",
        "label_secondary": "Person Detector · Camera A",
        "label_status": "began",
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "timestamp": "20260308T224313.914000",
        "category": "lpr",
        "event_type": "plateRecognized",
        "state": "HAPPENED",
        "camera": "2.Gate",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
        "detector": "License plate recognition RR",
        "detector_access_point": "hosts/AXXON_SERVER/AVDetector.2/EventSupplier",
        "plate": "BE59922",
        "text": "Plate recognized",
        "label_primary": "Recognized LP",
        "label_secondary": "2.Gate · BE59922",
    },
]

ALERT_CARDS = [
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "timestamp": "20260308T224204.094721",
        "category": "alert",
        "event_type": "ET_Alert",
        "state": "ST_WANT_REACTION",
        "priority": "AP_MEDIUM",
        "camera": "Camera A",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
        "detector": "Person Detector",
        "alert_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "text": "Camera \"Camera A\": Alarm initiated by macro \"Camera A: Person Detector\"",
        "label_primary": 'Alarm initiated by macro "Camera A: Person Detector"',
        "label_status": "P2 active",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "timestamp": "20260308T224104.094721",
        "category": "alert",
        "event_type": "ET_Alert",
        "state": "ST_WANT_REACTION",
        "priority": "AP_HIGH",
        "camera": "2.Gate",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
        "detector": "License plate recognition RR",
        "alert_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "text": "Gate alert",
        "label_primary": "Gate alert",
        "label_status": "P3 active",
    },
    {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "timestamp": "20260308T224004.094721",
        "category": "alert",
        "event_type": "ET_Alert",
        "state": "ST_WANT_REACTION",
        "priority": "AP_LOW",
        "camera": "3.Yard",
        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.300/SourceEndpoint.video:0:0",
        "detector": "4.Meta-detector",
        "alert_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "text": "Yard alert",
        "label_primary": "Yard alert",
        "label_status": "P1 active",
    },
]


class UiPayloadTests(unittest.TestCase):
    def _fake_run_api(self, args):
        cmd = args[0]
        if cmd == "server-version":
            return {"version": "1.2.3", "httpSdk": "sdk-9"}
        if cmd == "dashboard":
            return {"by_category": {"lpr": 1, "motion": 3}}
        if cmd == "search-events":
            return {
                "request": {
                    "mode": "list",
                    "page": 1,
                    "page_size": 5,
                    "scan_limit": 1200,
                    "descending": True,
                    "filters": {
                        "range": {
                            "begin_time": "20260308T220000",
                            "end_time": "20260308T230000",
                        },
                        "camera_names": ["2.Gate"],
                        "categories": ["lpr"],
                    },
                },
                "summary": {
                    "matched": 1,
                    "scanned": 5,
                    "complete": True,
                    "truncated": False,
                    "by_category": {"lpr": 1},
                    "top_cameras": [{"name": "2.Gate", "count": 1}],
                    "top_detectors": [{"name": "License plate recognition RR", "count": 1}],
                },
                "pagination": {
                    "page": 1,
                    "page_size": 5,
                    "page_count": 1,
                    "has_previous": False,
                    "has_next": False,
                },
                "items": [EVENT_CARDS[3]],
            }
        if cmd == "plate-search":
            return {
                "request": {
                    "page": 1,
                    "page_size": 5,
                    "scan_limit": 400,
                    "descending": True,
                    "filters": {
                        "range": {
                            "begin_time": "20260308T220000",
                            "end_time": "20260308T230000",
                        },
                        "camera_names": ["2.Gate"],
                        "categories": ["lpr"],
                    },
                    "match": {
                        "mode": "mask",
                        "value": "*9922",
                    },
                    "time_source": "window",
                    "window_seconds": 3600,
                },
                "summary": {
                    "matched": 1,
                    "scanned": 4,
                    "complete": True,
                    "truncated": False,
                    "top_cameras": [{"name": "2.Gate", "count": 1}],
                    "top_plates": [{"name": "BE59922", "count": 1}],
                },
                "pagination": {
                    "page": 1,
                    "page_size": 5,
                    "page_count": 1,
                    "has_previous": False,
                    "has_next": False,
                },
                "items": [
                    {
                        **EVENT_CARDS[3],
                        "confidence": 99.0,
                        "vehicle": {
                            "brand": "Audi",
                            "model": "A4",
                            "color": "Black",
                        },
                    }
                ],
            }
        if cmd == "face-search":
            return {
                "request": {
                    "page": 1,
                    "page_size": 5,
                    "scan_limit": 120,
                    "accuracy": 0.82,
                    "filters": {
                        "range": {
                            "begin_time": "20260308T220000",
                            "end_time": "20260308T230000",
                        },
                        "camera_names": ["1.Lobby"],
                    },
                    "time_source": "window",
                    "window_seconds": 3600,
                },
                "capability": {
                    "available": True,
                    "detector_count": 2,
                    "camera_count": 2,
                    "transport": "grpc:axxonsoft.bl.events.EventHistoryService.FindSimilarObjects",
                },
                "selection": {
                    "searchable": True,
                    "error": None,
                    "camera_count": 1,
                    "detector_count": 1,
                },
                "reference_image": {
                    "file_name": "reference.jpg",
                    "size_bytes": 2048,
                    "sha256": "abc123",
                    "media_type": "image/jpeg",
                },
                "summary": {
                    "matched": 1,
                    "scanned": 5,
                    "complete": True,
                    "truncated": False,
                    "top_cameras": [{"name": "1.Lobby", "count": 1}],
                    "top_detectors": [{"name": "1.Face detection", "count": 1}],
                },
                "pagination": {
                    "page": 1,
                    "page_size": 5,
                    "page_count": 1,
                    "has_previous": False,
                    "has_next": False,
                },
                "items": [
                    {
                        "id": "face-1",
                        "timestamp": "20260308T224313.914000",
                        "camera": "1.Lobby",
                        "camera_access_point": "hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
                        "detector": "1.Face detection",
                        "detector_access_point": "hosts/AXXON_SERVER/AVDetector.9/EventSupplier",
                        "similarity": 0.99,
                        "archive_command": "/archive camera_ap=hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0 at=20260308T224313.914000",
                        "export_command": "/export from=20260308T224258.914000 to=20260308T224328.914000 camera_ap=hosts/AXXON_SERVER/DeviceIpint.1/SourceEndpoint.video:0:0",
                    }
                ],
                "error": None,
            }
        if cmd == "archive-jump":
            return {
                "request": {
                    "filters": {
                        "range": {
                            "begin_time": "20260308T224313.914000",
                            "end_time": "20260308T224313.914000",
                        },
                        "camera_access_points": [EVENT_CARDS[3]["camera_access_point"]],
                    },
                    "requested_timestamp": "20260308T224313.914000",
                    "scan_limit": 400,
                    "preview_width": 1280,
                    "preview_height": 720,
                    "preview_threshold_ms": 250,
                    "context_window_sec": 300,
                },
                "selection": {
                    "camera": "2.Gate",
                    "camera_access_point": EVENT_CARDS[3]["camera_access_point"],
                    "video_id": "AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
                    "timestamp": "20260308T224313.914000",
                    "timestamp_source": "explicit",
                    "request_begin": "20260308T224313.914000",
                    "request_end": "20260308T224313.914000",
                    "context_begin": "20260308T223813.914000",
                    "context_end": "20260308T224813.914000",
                    "matched_count": 1,
                    "matched_event": EVENT_CARDS[3],
                },
                "archive": {
                    "archives": [{"name": "hosts/AXXON_SERVER/MultimediaStorage.Main/MultimediaStorage", "default": True}],
                    "default_archive": "hosts/AXXON_SERVER/MultimediaStorage.Main/MultimediaStorage",
                    "depth": {
                        "start": "20260301T000000",
                        "end": "20260310T230000",
                    },
                    "intervals": [
                        {"begin": "20260308T220000", "end": "20260308T230000"},
                    ],
                    "intervals_more": False,
                    "in_archive": True,
                    "context_handle": {
                        "camera_access_point": EVENT_CARDS[3]["camera_access_point"],
                        "video_id": "AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
                        "timestamp": "20260308T224313.914000",
                        "request_begin": "20260308T224313.914000",
                        "request_end": "20260308T224313.914000",
                        "interval_begin": "20260308T220000",
                        "interval_end": "20260308T230000",
                        "archive": "hosts/AXXON_SERVER/MultimediaStorage.Main/MultimediaStorage",
                    },
                    "errors": [],
                },
                "preview": {
                    "ok": True,
                    "path": "/tmp/archive-preview.jpg",
                    "error": None,
                    "mode": "media",
                    "width": 1280,
                    "height": 720,
                    "threshold_ms": 250,
                },
            }
        if cmd == "single-camera-export":
            return {
                "request": {
                    "filters": {
                        "range": {
                            "begin_time": "20260308T224000",
                            "end_time": "20260308T224500",
                        },
                        "camera_names": ["2.Gate"],
                    },
                    "waittimeout_ms": 90000,
                    "archive": None,
                    "format": "mp4",
                },
                "selection": {
                    "camera": "2.Gate",
                    "camera_access_point": EVENT_CARDS[3]["camera_access_point"],
                    "video_id": "AXXON_SERVER/DeviceIpint.200/SourceEndpoint.video:0:0",
                    "target_timestamp": "20260308T224230",
                    "timestamp_source": "range_midpoint",
                    "request_begin": "20260308T224000",
                    "request_end": "20260308T224500",
                },
                "export": {
                    "ok": True,
                    "path": "/tmp/export-clip.mp4",
                    "file_name": "AXXON_SERVER_2.Gate[20260308T224000-20260308T224500].mp4",
                    "size_bytes": 654336,
                    "archive": None,
                    "format": "mp4",
                    "status": {
                        "id": "exp-123",
                        "state": 2,
                        "progress": 1.0,
                        "files": [
                            "AXXON_SERVER_2.Gate[20260308T224000-20260308T224500].mp4",
                        ],
                    },
                    "error": None,
                },
            }
        if cmd == "macro-preview":
            return {
                "request": {
                    "selector": {
                        "kind": "id",
                        "value": "11111111-1111-1111-1111-111111111111",
                    }
                },
                "macro": {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "name": "Manual Alert Test",
                    "enabled": True,
                    "user_role": None,
                    "is_add_to_menu": True,
                    "mode_kind": "common",
                    "action_families": ["raise_alert"],
                    "conditions_count": 0,
                    "rules_count": 1,
                },
                "guardrails": {
                    "allowed": True,
                    "reasons": [],
                    "warnings": ["Guardrails are re-checked immediately before execution."],
                    "policy": {
                        "execution_enabled": True,
                        "admin": True,
                        "require_admin": True,
                        "require_enabled": True,
                        "require_add_to_menu": True,
                        "allowlist_configured": True,
                        "allowed_mode_kinds": ["common"],
                        "denied_action_families": ["web_query"],
                    },
                },
            }
        if cmd == "ptz-preview":
            return {
                "request": {
                    "camera_selector": {
                        "kind": "camera",
                        "value": "2.Gate PTZ",
                    },
                    "preset_selector": {
                        "kind": "preset",
                        "value": "Home Position",
                    },
                    "action": "goto_preset",
                    "speed": 5,
                },
                "camera": {
                    "name": "2.Gate PTZ",
                    "access_point": "hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0",
                    "display_id": "2",
                    "camera_access": "CAMERA_ACCESS_FULL",
                    "ptz_count": 1,
                    "ptz_active_count": 1,
                    "point_move": False,
                    "area_zoom": False,
                },
                "ptz": {
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
                    "preview_error": None,
                    "preset_count": 2,
                    "presets": [
                        {"label": "Home Position", "position": 12},
                        {"label": "Road Overview", "position": 18},
                    ],
                    "selected_preset": {"label": "Home Position", "position": 12},
                },
                "guardrails": {
                    "allowed": True,
                    "reasons": [],
                    "warnings": ["Guardrails are re-checked immediately before execution."],
                    "policy": {
                        "control_enabled": True,
                        "admin": True,
                        "require_admin": True,
                        "allowlist_configured": True,
                        "allowed_camera_access_points": ["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
                        "allowed_camera_names": [],
                    },
                },
            }
        if cmd == "admin-view":
            return {
                "policy": {
                    "admin": True,
                    "require_admin": True,
                    "read_only": True,
                    "config_write_enabled": False,
                    "dry_run_required": True,
                    "audit_required": True,
                    "future_write_boundaries": ["host_inventory", "role_access_summary", "future_config_dry_run"],
                    "audited_action_surfaces": ["macro_execution", "ptz_control"],
                },
                "summary": {
                    "node_count": 2,
                    "domain_count": 1,
                    "role_count": 2,
                    "user_count": 3,
                    "enabled_user_count": 2,
                    "assignment_count": 3,
                    "ldap_server_count": 1,
                },
                "viewer": {
                    "telegram_admin": True,
                    "axxon_user": "root",
                    "role_names": ["Administrators"],
                },
                "hosts": {
                    "summary": {
                        "node_count": 2,
                        "host_count": 1,
                        "domain_count": 1,
                        "license_status_counts": {"OK": 2},
                    },
                    "domains": [{"name": "Default", "nodes": 2}],
                    "items": [
                        {
                            "node_name": "NODE1",
                            "host_name": "SERVER1",
                            "domain_friendly_name": "Default",
                            "license_status": "OK",
                            "os": "Win32",
                            "machine": "x64 6",
                            "time_zone_label": "UTC+04:00",
                            "cluster_node_count": 2,
                        },
                        {
                            "node_name": "NODE2",
                            "host_name": "SERVER1",
                            "domain_friendly_name": "Default",
                            "license_status": "OK",
                            "os": "Win32",
                            "machine": "x64 6",
                            "time_zone_label": "UTC+04:00",
                            "cluster_node_count": 2,
                        },
                    ],
                },
                "access": {
                    "summary": {
                        "user_count": 3,
                        "enabled_user_count": 2,
                        "disabled_user_count": 1,
                        "role_count": 2,
                        "assignment_count": 3,
                        "ldap_server_count": 1,
                        "password_min_length": 12,
                        "password_complexity_required": True,
                        "roles_with_domain_ops": 1,
                        "roles_with_user_rights_setup": 1,
                        "roles_with_search": 2,
                        "roles_with_export": 2,
                    },
                    "current_user": {
                        "axxon_user": "root",
                        "role_names": ["Administrators"],
                    },
                    "roles": [
                        {
                            "name": "Administrators",
                            "user_count": 1,
                            "feature_access_count": 5,
                            "admin_feature_count": 2,
                            "privileges": {
                                "domain_ops": True,
                                "users_rights_setup": True,
                                "search": True,
                                "export": True,
                            },
                        },
                        {
                            "name": "Operators",
                            "user_count": 2,
                            "feature_access_count": 3,
                            "admin_feature_count": 0,
                            "privileges": {
                                "domain_ops": False,
                                "users_rights_setup": False,
                                "search": True,
                                "export": True,
                            },
                        },
                    ],
                },
                "capabilities": {
                    "server": {
                        "backend_version": "Axxon One 2.0",
                        "api_version": "sdk-9",
                        "errors": [],
                    },
                    "read_surfaces": [
                        {"label": "Server overview", "available": True},
                        {"label": "Host/domain inventory", "available": True},
                        {"label": "Current web user", "available": True},
                        {"label": "Roles and users inventory", "available": True},
                        {"label": "Role access summary", "available": True},
                    ],
                    "guarded_actions": [
                        {"label": "Macro execution", "enabled": True, "allowlist_configured": True, "audited": True},
                        {"label": "PTZ preset control", "enabled": False, "allowlist_configured": False, "audited": True},
                    ],
                    "future_write_plane": {
                        "enabled": False,
                        "require_admin": True,
                        "dry_run_required": True,
                        "audit_required": True,
                        "planned_boundaries": ["host_inventory", "role_access_summary", "future_config_dry_run"],
                    },
                    "telegram_admin_user_count": 1,
                },
                "errors": [{"section": "statistics"}],
            }
        if cmd == "telegram-cards":
            if "--event-type" in args:
                event_type = args[args.index("--event-type") + 1]
                return ALERT_CARDS if event_type == "ET_Alert" else EVENT_CARDS
            return EVENT_CARDS
        if cmd == "events":
            return [{"body": {"guid": EVENT_CARDS[0]["id"], "timestamp": EVENT_CARDS[0]["timestamp"]}}]
        raise AssertionError(f"unexpected run_api args: {args}")

    def test_live_stop_payload_is_operator_friendly(self):
        payload = callback_payload([], 1800, "cam:live:stop")
        self.assertIn("stop requested", payload["text"].lower())
        self.assertTrue(payload["buttons"])
        self.assertEqual(payload["buttons"][0][0]["callback_data"], "cam:list:0")
        self.assertEqual(payload["buttons"][0][1]["callback_data"], "home")

    def test_live_start_payload_explains_refresh_behavior(self):
        payload = callback_payload([], 1800, "cam:live:start:0")
        self.assertIn("refreshes this chat every few seconds", payload["text"].lower())
        self.assertIn("stop it when you are done", payload["text"].lower())

    def test_server_version_payload_uses_dedicated_view(self):
        with patch("axxon_tg_ui.run_api", return_value={"version": "1.2.3", "httpSdk": "sdk-9"}):
            payload = server_version_payload([])
        self.assertIn("Server version", payload["text"])
        self.assertIn("1.2.3", payload["text"])
        self.assertIn("sdk-9", payload["text"])

    def test_events_navigation_uses_short_callbacks(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = callback_payload([], 1800, "ev:feed:0")
        self.assertEqual(len(payload["cards"]), 3)
        event_buttons = payload["buttons"][:-1]
        self.assertTrue(event_buttons)
        for row in event_buttons:
            for button in row:
                self.assertLessEqual(len(button["callback_data"]), 64)
                self.assertTrue(button["callback_data"].startswith("ev:cam:"))
                self.assertNotIn("hosts/", button["callback_data"])

    def test_events_camera_detector_open_flow_keeps_contextual_back(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            feed = callback_payload([], 1800, "ev:feed:0")
            cam_cb = feed["buttons"][0][0]["callback_data"]
            detectors = callback_payload([], 1800, cam_cb)
            det_cb = detectors["buttons"][0][0]["callback_data"]
            events = callback_payload([], 1800, det_cb)
            open_cb = events["buttons"][0][0]["callback_data"]
            opened = callback_payload([], 1800, open_cb)
        parts = det_cb.split(":")
        expected_back = f"ev:list:{parts[2]}:{parts[3]}:0"
        self.assertEqual(opened["buttons"][-1][0]["callback_data"], expected_back)
        self.assertIn("2.Gate", detectors["text"])
        self.assertIn("License plate recognition RR", events["text"])
        self.assertLessEqual(len(open_cb), 64)

    def test_home_payload_uses_alert_buttons_and_dashboard_mix(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = callback_payload([], 1800, "home")
        self.assertIn("Choose what you want to do", payload["text"])
        self.assertIn("Recent alerts: 3 in the last hour", payload["text"])
        self.assertIn("Recent mix: LPR 1 · Motion 3", payload["text"])
        self.assertNotIn("Operator Console", payload["text"])
        self.assertNotIn("Investigate: Search ->", payload["text"])
        self.assertTrue(payload["buttons"][0][0]["callback_data"].startswith("al:open:"))
        self.assertTrue(payload["buttons"][1][0]["callback_data"].startswith("al:open:"))
        self.assertIn("P2 active", payload["buttons"][0][0]["text"])
        self.assertIn("Alarm initiated by macro", payload["buttons"][0][0]["text"])
        callbacks = {button["callback_data"] for row in payload["buttons"] for button in row}
        self.assertIn("sea:menu", callbacks)
        self.assertIn("arch:menu", callbacks)

    def test_home_payload_shows_admin_shortcut_only_for_admin_viewers(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            operator_payload = callback_payload([], 1800, "home")
            admin_payload = callback_payload([], 1800, "home", admin=True)
        operator_callbacks = {button["callback_data"] for row in operator_payload["buttons"] for button in row}
        admin_callbacks = {button["callback_data"] for row in admin_payload["buttons"] for button in row}
        self.assertNotIn("adm:menu", operator_callbacks)
        self.assertIn("adm:menu", admin_callbacks)

    def test_alert_feed_buttons_use_operator_labels(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = callback_payload([], 1800, "al:feed:0")
        self.assertIn("P2 active", payload["buttons"][0][0]["text"])
        self.assertNotIn("Open alert", payload["buttons"][0][0]["text"])
        self.assertEqual(payload["buttons"][-1][0]["text"], "🚨 Events")
        self.assertEqual(payload["buttons"][-1][0]["callback_data"], "ev:feed:0")

    def test_detector_list_buttons_add_event_preview_when_available(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            feed = callback_payload([], 1800, "ev:feed:0")
            cam_cb = feed["buttons"][0][0]["callback_data"]
            detectors = callback_payload([], 1800, cam_cb)
        self.assertIn("Recognized LP", detectors["buttons"][0][0]["text"])
        self.assertIn("License plate recognition RR", detectors["buttons"][0][0]["text"])

    def test_detector_event_buttons_prefer_human_label_over_raw_event_type(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            feed = callback_payload([], 1800, "ev:feed:0")
            cam_cb = feed["buttons"][0][0]["callback_data"]
            detectors = callback_payload([], 1800, cam_cb)
            payload = callback_payload([], 1800, detectors["buttons"][0][0]["callback_data"])
        self.assertIn("Recognized LP", payload["buttons"][0][0]["text"])
        self.assertNotIn("vehicleAppeared", payload["buttons"][0][0]["text"])

    def test_alert_open_uses_full_alert_window(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api) as mocked:
            payload = callback_payload([], 1800, f"al:open:{ALERT_CARDS[0]['id']}")
        self.assertIn("Alert card", payload["text"])
        telegram_calls = [call.args[0] for call in mocked.call_args_list if call.args and call.args[0][0] == "telegram-cards"]
        self.assertTrue(any("--seconds" in call and call[call.index("--seconds") + 1] == "3600" for call in telegram_calls))

    def test_event_search_payload_shows_help_when_terms_missing(self):
        payload = event_search_payload([], [])
        self.assertIn("Advanced typed search", payload["text"])
        self.assertNotIn("Use explicit key=value terms", payload["text"])
        self.assertEqual(payload["buttons"][0][0]["callback_data"], "arch:menu")

    def test_search_menu_exposes_event_plate_face_entry_points(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            menu = callback_payload([], 1800, "sea:menu")
            event_help = callback_payload([], 1800, "sea:event")
            plate_help = callback_payload([], 1800, "sea:plate")
            face_help = callback_payload([], 1800, "sea:face")
        callbacks = {button["callback_data"] for row in menu["buttons"] for button in row}
        self.assertIn("sea:event", callbacks)
        self.assertIn("sea:plate", callbacks)
        self.assertIn("sea:face", callbacks)
        self.assertIn("arch:menu", callbacks)
        self.assertIn("Choose what you want to search", menu["text"])
        self.assertNotIn("fake button workflows", menu["text"])
        self.assertIn("upload a Telegram photo", menu["text"])
        self.assertEqual(event_help["buttons"][0][0]["callback_data"], "sea:menu")
        self.assertIn("Advanced typed search", event_help["text"])
        self.assertEqual(plate_help["buttons"][0][0]["callback_data"], "sea:menu")
        self.assertIn("Recent matches:", plate_help["text"])
        self.assertEqual(face_help["buttons"][0][0]["callback_data"], "sea:menu")
        self.assertIn("Upload a Telegram photo", face_help["text"])
        self.assertIn("Accepted image format: JPEG.", face_help["text"])

    def test_event_search_list_payload_formats_results(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = event_search_payload(
                [],
                [
                    "from=20260308T220000",
                    "to=20260308T230000",
                    "camera=2.Gate",
                    "category=lpr",
                    "mode=list",
                    "page=1",
                ],
            )
        self.assertIn("Window: 08-03-2026 22:00:00 UTC -> 08-03-2026 23:00:00 UTC", payload["text"])
        self.assertIn("Page: 1/1", payload["text"])
        self.assertIn("Recognized LP", payload["text"])
        self.assertIn("No further pages", payload["text"])

    def test_plate_search_payload_shows_help_when_terms_missing(self):
        payload = plate_search_payload([], [])
        self.assertIn("Use plate=..., contains=..., or mask=...", payload["text"])
        self.assertEqual(payload["buttons"][0][0]["callback_data"], "arch:menu")

    def test_plate_search_payload_formats_results(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = plate_search_payload(
                [],
                [
                    "mask=*9922",
                    "camera=2.Gate",
                ],
            )
        self.assertIn("License plate search", payload["text"])
        self.assertIn("Match: mask: *9922", payload["text"])
        self.assertIn("BE59922", payload["text"])
        self.assertIn("99%", payload["text"])
        self.assertIn("Audi / A4 / Black", payload["text"])

    def test_face_search_payload_formats_results(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = face_search_payload(
                [],
                "/tmp/reference.jpg",
                [
                    "camera=1.Lobby",
                    "accuracy=0.82",
                ],
            )
        self.assertIn("Face search", payload["text"])
        self.assertIn("Threshold: 82%", payload["text"])
        self.assertIn("Scope: camera: 1.Lobby", payload["text"])
        self.assertIn("Results: 1 match(es)", payload["text"])
        self.assertIn("Face detectors: 1 VaFaceDetector instance(s) across 1 camera(s)", payload["text"])
        self.assertIn("Top hit: 1.Lobby", payload["text"])

    def test_face_search_payload_shows_upload_help_without_image(self):
        payload = face_search_payload([], "", [])
        self.assertIn("Upload a Telegram photo", payload["text"])
        self.assertIn("Accepted image format: JPEG.", payload["text"])
        self.assertNotIn("--image", payload["text"])

    def test_archive_jump_payload_formats_context_and_media(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = archive_jump_payload(
                [],
                [
                    "camera=2.Gate",
                    "at=20260308T224313.914000",
                ],
            )
        self.assertEqual(payload["media_path"], "/tmp/archive-preview.jpg")
        self.assertIn("Archive jump", payload["text"])
        self.assertIn("Requested: 08-03-2026 22:43:13 UTC", payload["text"])
        self.assertIn("Using: 08-03-2026 22:43:13 UTC", payload["text"])
        self.assertIn("Preview: ready (media)", payload["text"])

    def test_single_camera_export_payload_formats_ready_clip(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = single_camera_export_payload(
                [],
                [
                    "from=20260308T224000",
                    "to=20260308T224500",
                    "camera=2.Gate",
                ],
            )
        self.assertEqual(payload["media_path"], "/tmp/export-clip.mp4")
        self.assertIn("Single-camera export", payload["text"])
        self.assertIn("Camera: 2.Gate", payload["text"])
        self.assertIn("Result: clip ready.", payload["text"])
        self.assertIn("639.0 KB", payload["text"])

    def test_archive_menu_exposes_jump_and_export_help(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            menu = callback_payload([], 1800, "arch:menu")
            jump_help = callback_payload([], 1800, "arch:jump")
            export_help = callback_payload([], 1800, "arch:export")
        callbacks = {button["callback_data"] for row in menu["buttons"] for button in row}
        self.assertIn("arch:jump", callbacks)
        self.assertIn("arch:export", callbacks)
        self.assertIn("sea:menu", callbacks)
        self.assertIn("Choose Jump for a quick archive preview", menu["text"])
        self.assertNotIn("Both flows require typed terms", menu["text"])
        self.assertEqual(jump_help["buttons"][0][0]["callback_data"], "arch:menu")
        self.assertIn("Start with one camera and one moment in time", jump_help["text"])
        self.assertEqual(export_help["buttons"][0][0]["callback_data"], "arch:menu")
        self.assertIn("Start with one camera and a clear start/end time", export_help["text"])

    def test_macro_execution_preview_payload_formats_guardrails(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = macro_execution_payload(
                [],
                ["id=11111111-1111-1111-1111-111111111111"],
                execution_enabled=True,
                admin=True,
                allow_ids=["11111111-1111-1111-1111-111111111111"],
            )
        self.assertIn("Macro execution preview", payload["text"])
        self.assertIn("Manual Alert Test", payload["text"])
        self.assertIn("Actions: raise_alert", payload["text"])
        self.assertTrue(payload["meta"]["allowed"])

    def test_ptz_control_preview_payload_formats_guardrails(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = ptz_control_payload(
                [],
                ["camera=2.Gate", "PTZ", "preset=Home", "Position"],
                control_enabled=True,
                admin=True,
                allow_camera_aps=["hosts/ServerA/DeviceIpint.2/SourceEndpoint.video:0:0"],
            )
        self.assertIn("PTZ preset preview", payload["text"])
        self.assertIn("2.Gate PTZ", payload["text"])
        self.assertIn("Home Position", payload["text"])
        self.assertIn("Presets: Home Position (12)", payload["text"])
        self.assertTrue(payload["meta"]["allowed"])

    def test_admin_view_payload_formats_read_only_sections(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            overview = callback_payload([], 1800, "adm:menu", admin=True)
            access = callback_payload([], 1800, "adm:access", admin=True)
            caps = callback_payload([], 1800, "adm:caps", admin=True)
        self.assertIn("Admin foundation", overview["text"])
        self.assertIn("Write plane: disabled", overview["text"])
        self.assertEqual(overview["buttons"][0][0]["callback_data"], "adm:menu")
        self.assertIn("Role / access summary", access["text"])
        self.assertIn("Administrators", access["text"])
        self.assertIn("Admin capability surface", caps["text"])
        self.assertIn("Macro execution: enabled", caps["text"])

    def test_admin_view_payload_requires_admin_flag(self):
        with patch("tg_admin_ui.run_api") as mocked:
            payload = callback_payload([], 1800, "adm:menu", admin=False)
        mocked.assert_not_called()
        self.assertIn("restricted to configured Telegram admins", payload["text"])
        self.assertEqual(payload["buttons"], [[{"text": "🏠 Main", "callback_data": "home"}]])

    def test_server_and_status_payloads_use_short_truthful_navigation_labels(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            server = callback_payload([], 1800, "srv:menu")
            status = callback_payload([], 1800, "sys:health")
            lpr = callback_payload([], 1800, "lpr:menu")
        self.assertEqual(server["buttons"][0][1]["text"], "🌐 Domain")
        self.assertEqual(server["buttons"][1][1]["text"], "📈 Stats")
        self.assertEqual(status["buttons"][0][0]["text"], "🔄 Refresh")
        self.assertEqual(status["buttons"][0][0]["callback_data"], "sys:health")
        self.assertEqual(lpr["buttons"][0][0]["text"], "🔎 Search")
        self.assertEqual(lpr["buttons"][0][0]["callback_data"], "sea:menu")

    def test_event_open_adds_archive_button_and_archive_callback_keeps_open_card_back(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            payload = callback_payload([], 1800, f"ev:open:{EVENT_CARDS[3]['id']}")
            self.assertEqual(payload["buttons"][1][0]["callback_data"], f"ev:arch:{EVENT_CARDS[3]['id']}")
            archive_payload = callback_payload([], 1800, f"ev:arch:{EVENT_CARDS[3]['id']}")
        self.assertEqual(archive_payload["buttons"][0][0]["callback_data"], f"ev:open:{EVENT_CARDS[3]['id']}")
        self.assertEqual(archive_payload["media_path"], "/tmp/archive-preview.jpg")

    def test_detector_context_archive_callback_preserves_contextual_open_card(self):
        with patch("axxon_tg_ui.run_api", side_effect=self._fake_run_api):
            feed = callback_payload([], 1800, "ev:feed:0")
            cam_cb = feed["buttons"][0][0]["callback_data"]
            detectors = callback_payload([], 1800, cam_cb)
            det_cb = detectors["buttons"][0][0]["callback_data"]
            events = callback_payload([], 1800, det_cb)
            open_cb = events["buttons"][0][0]["callback_data"]
            opened = callback_payload([], 1800, open_cb)
            archive_cb = opened["buttons"][1][0]["callback_data"]
            archive_payload = callback_payload([], 1800, archive_cb)
        self.assertEqual(archive_payload["buttons"][0][0]["callback_data"], open_cb)


if __name__ == "__main__":
    unittest.main()
