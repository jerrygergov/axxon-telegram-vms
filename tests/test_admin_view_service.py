import unittest

from axxon_telegram_vms.services import (
    admin_view_policy_to_api_args,
    build_admin_view_policy,
    shape_admin_view_result,
)


HOSTS = ["NODE1", "NODE2"]
HOST_DETAILS = {
    "NODE1": {
        "nodeName": "NODE1",
        "domainInfo": {
            "domainName": "domain-1",
            "domainFriendlyName": "Default",
        },
        "platformInfo": {
            "hostName": "SERVER1",
            "machine": "x64 6",
            "os": "Win32",
        },
        "licenseStatus": "OK",
        "timeZone": 240,
        "nodes": ["NODE1", "NODE2"],
    },
    "NODE2": {
        "nodeName": "NODE2",
        "domainInfo": {
            "domainName": "domain-1",
            "domainFriendlyName": "Default",
        },
        "platformInfo": {
            "hostName": "SERVER1",
            "machine": "x64 6",
            "os": "Win32",
        },
        "licenseStatus": "OK",
        "timeZone": 240,
        "nodes": ["NODE1", "NODE2"],
    },
}
CURRENT_USER = {"currentuser": "root"}
SECURITY_CONFIG = {
    "roles": [
        {"index": "role-admin", "name": "Administrators", "comment": "Full access"},
        {"index": "role-op", "name": "Operators", "comment": "Monitoring"},
    ],
    "users": [
        {
            "index": "user-root",
            "login": "root",
            "name": "Root",
            "enabled": True,
            "restrictions": {"web_count": 5, "mobile_count": 2},
        },
        {
            "index": "user-ops",
            "login": "operator",
            "name": "Operator",
            "enabled": False,
            "restrictions": {"web_count": 1, "mobile_count": 0},
        },
    ],
    "user_assignments": [
        {"user_id": "user-root", "role_id": "role-admin"},
        {"user_id": "user-root", "role_id": "role-op"},
        {"user_id": "user-ops", "role_id": "role-op"},
    ],
    "ldap_servers": [{"index": "ldap-1"}],
    "pwd_policy": [{"minimum_password_length": "12", "password_must_meet_complexity_requirements": True}],
    "ip_filters": [{"index": "filter-1"}],
    "trusted_ip_list": ["10.0.0.1", "10.0.0.2"],
}
GLOBAL_PERMISSIONS = {
    "permissions": {
        "role-admin": {
            "feature_access": [
                "FEATURE_ACCESS_USERS_RIGHTS_SETUP",
                "FEATURE_ACCESS_DOMAIN_MANAGING_OPS",
                "FEATURE_ACCESS_EXPORT",
                "FEATURE_ACCESS_SEARCH",
                "FEATURE_ACCESS_WEB_UI_LOGIN",
            ],
            "alert_access": "ALERT_ACCESS_FULL",
            "maps_access": "MAP_ACCESS_FULL",
            "unrestricted_access": "UNRESTRICTED_ACCESS_NO",
            "default_camera_access": "CAMERA_ACCESS_FULL",
            "default_archive_access": "ARCHIVE_ACCESS_FULL",
            "default_macros_access": "MACROS_ACCESS_FULL",
            "default_telemetry_priority": "TELEMETRY_PRIORITY_HIGH",
        },
        "role-op": {
            "feature_access": [
                "FEATURE_ACCESS_EXPORT",
                "FEATURE_ACCESS_SEARCH",
                "FEATURE_ACCESS_WEB_UI_LOGIN",
            ],
            "alert_access": "ALERT_ACCESS_VIEW_ONLY",
            "maps_access": "MAP_ACCESS_VIEW_ONLY",
            "unrestricted_access": "UNRESTRICTED_ACCESS_NO",
        },
    }
}
SERVER_INFO = {
    "usage": [{"name": "NODE1", "totalCPU": "10"}],
    "version": {"version": "Axxon One 2.0", "httpSdk": "sdk-9"},
    "statistics": {"requests": 3},
    "errors": [],
}
RUNTIME_CAPABILITIES = {
    "telegram_admin_user_count": 1,
    "macro_execution": {
        "enabled": True,
        "admin_only": True,
        "allowlist_configured": True,
        "audited": True,
        "confirm_ttl_sec": 300,
    },
    "ptz_control": {
        "enabled": False,
        "admin_only": True,
        "allowlist_configured": False,
        "audited": True,
        "confirm_ttl_sec": 300,
    },
}


class AdminViewServiceTests(unittest.TestCase):
    def test_policy_to_api_args_marks_admin_viewer(self):
        policy = build_admin_view_policy(admin=True)
        self.assertEqual(admin_view_policy_to_api_args(policy), ["--admin"])

    def test_shape_admin_view_result_summarizes_host_access_and_capabilities(self):
        result = shape_admin_view_result(
            hosts=HOSTS,
            host_details=HOST_DETAILS,
            current_user=CURRENT_USER,
            security_config=SECURITY_CONFIG,
            global_permissions=GLOBAL_PERMISSIONS,
            server_info=SERVER_INFO,
            policy=build_admin_view_policy(admin=True),
            runtime_capabilities=RUNTIME_CAPABILITIES,
            errors=[{"section": "statistics"}],
        )

        self.assertTrue(result["policy"]["admin"])
        self.assertEqual(result["hosts"]["summary"]["node_count"], 2)
        self.assertEqual(result["hosts"]["summary"]["domain_count"], 1)
        self.assertEqual(result["access"]["summary"]["role_count"], 2)
        self.assertEqual(result["access"]["summary"]["user_count"], 2)
        self.assertEqual(result["viewer"]["axxon_user"], "root")
        self.assertEqual(result["access"]["current_user"]["role_names"], ["Administrators", "Operators"])
        self.assertEqual(result["access"]["roles"][0]["name"], "Administrators")
        self.assertTrue(result["access"]["roles"][0]["privileges"]["domain_ops"])
        self.assertFalse(result["capabilities"]["future_write_plane"]["enabled"])
        self.assertTrue(result["capabilities"]["guarded_actions"][0]["enabled"])
        self.assertEqual(result["capabilities"]["server"]["backend_version"], "Axxon One 2.0")
        self.assertEqual(result["errors"][0]["section"], "statistics")

    def test_shape_admin_view_result_handles_missing_inputs_truthfully(self):
        result = shape_admin_view_result(
            policy=build_admin_view_policy(admin=False),
            server_info={"usage": None, "version": None, "statistics": None, "errors": [{"section": "usage"}]},
        )

        self.assertEqual(result["summary"]["node_count"], 0)
        self.assertEqual(result["summary"]["role_count"], 0)
        self.assertFalse(result["viewer"]["telegram_admin"])
        self.assertFalse(result["capabilities"]["read_surfaces"][0]["available"])
        self.assertFalse(result["capabilities"]["read_surfaces"][1]["available"])


if __name__ == "__main__":
    unittest.main()
