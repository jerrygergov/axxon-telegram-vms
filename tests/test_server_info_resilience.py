import unittest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import build_server_info_payload
from axxon_tg_ui import callback_payload, server_info_payload


class _FakeClient:
    def server_usage(self, domain: bool = False):
        return {"servers": [{"name": "Node-A", "activeUsers": 2}]}

    def server_version(self):
        raise RuntimeError("HTTP Error 404: Not Found")

    def server_statistics(self):
        raise RuntimeError("HTTP Error 404: Not Found")


class ServerInfoResilienceTests(unittest.TestCase):
    def test_build_server_info_payload_partial_data_and_errors(self):
        payload = build_server_info_payload(_FakeClient(), domain=False)
        self.assertFalse(payload["ok"])
        self.assertIsInstance(payload.get("usage"), dict)
        self.assertIsNone(payload.get("version"))
        self.assertIsNone(payload.get("statistics"))
        sections = [x.get("section") for x in (payload.get("errors") or [])]
        self.assertIn("version", sections)
        self.assertIn("statistics", sections)

    def test_server_info_payload_renders_missing_sections_friendly(self):
        with patch("axxon_tg_ui.run_api", return_value={
            "usage": {"servers": [{"name": "Node-A", "activeUsers": 2}]},
            "version": None,
            "statistics": None,
            "errors": [{"section": "version"}, {"section": "statistics"}],
        }):
            payload = server_info_payload([], domain=False)
        self.assertIn("Node-A", payload["text"])
        self.assertIn("Not available on this server version", payload["text"])
        self.assertIsInstance(payload.get("buttons"), list)
        self.assertTrue(payload["buttons"])

    def test_callback_payload_never_raises_and_returns_buttons(self):
        with patch("axxon_tg_ui._callback_payload_impl", side_effect=RuntimeError("boom")):
            payload = callback_payload([], 1800, "srv:menu")
        self.assertIn("Callback processing failed", payload["text"])
        self.assertIsInstance(payload.get("buttons"), list)
        self.assertTrue(payload["buttons"])
        self.assertEqual(payload["buttons"][0][0]["callback_data"], "srv:menu")


if __name__ == "__main__":
    unittest.main()
