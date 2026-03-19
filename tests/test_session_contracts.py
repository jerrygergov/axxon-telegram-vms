import unittest

from axxon_telegram_vms.client import (
    build_web_session_context,
    build_web_session_contract,
    session_bearer_headers,
    session_storage_snapshot,
    session_token_bundle_from_payload,
    shape_web_session_summary,
)


class SessionContractTests(unittest.TestCase):
    def test_contract_uses_documented_session_endpoints(self):
        contract = build_web_session_contract(host="vms.local", port=8080)

        self.assertEqual(
            contract.endpoint_url("authenticate"),
            "http://vms.local:8080/v1/authentication/authenticate_ex2",
        )
        self.assertEqual(
            contract.endpoint_url("host_detail", host="NODE1"),
            "http://vms.local:8080/hosts/NODE1",
        )
        self.assertEqual(
            contract.endpoint_url("websocket", token="abc123"),
            "http://vms.local:8080/ws?authToken=abc123",
        )

    def test_context_shapes_headers_storage_snapshot_and_safe_summary(self):
        context = build_web_session_context(
            host="vms.local",
            surface="future_web_app",
            token_payload={
                "accessToken": "access-1",
                "refreshToken": "refresh-1",
                "expiredDate": "2026-03-10T12:00:00Z",
            },
            current_user="root",
            domain_id="domain-1",
            storage_scope="browser_storage",
        )

        self.assertEqual(session_bearer_headers(context), {"Authorization": "Bearer access-1"})
        self.assertEqual(session_storage_snapshot(context)["host"], "vms.local")

        summary = shape_web_session_summary(context)
        self.assertTrue(summary["has_bearer_auth"])
        self.assertIn("accessToken", summary["token_keys_present"])
        self.assertNotIn("access-1", str(summary))

    def test_token_bundle_parses_observed_key_variants(self):
        bundle = session_token_bundle_from_payload(
            {
                "access_token": "access-2",
                "refresh_token": "refresh-2",
                "cloudToken": "cloud-2",
                "expiresAt": "2026-03-10T13:00:00Z",
            }
        )
        self.assertEqual(bundle.preferred_bearer, "access-2")
        self.assertTrue(bundle.renewable)
        self.assertIn("cloudToken", bundle.present_keys)


if __name__ == "__main__":
    unittest.main()
