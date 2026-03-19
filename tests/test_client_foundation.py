import os
import unittest
from unittest.mock import patch

from axxon_telegram_vms.client import (
    TTLCache,
    build_live_media_url,
    build_server_info_payload,
    load_axxon_config,
    parse_grpc_response,
)


class _ServerInfoClient:
    def server_usage(self, domain: bool = False):
        return {"domain": domain, "servers": 1}

    def server_version(self):
        raise RuntimeError("missing version")

    def server_statistics(self):
        return {"requests": 12}


class ClientFoundationTests(unittest.TestCase):
    def test_load_axxon_config_from_package_seam(self):
        with patch.dict(
            os.environ,
            {
                "AXXON_HOST": "vms.local",
                "AXXON_USER": "operator",
                "AXXON_PASS": "secret",
                "AXXON_PORT": "8080",
                "AXXON_LOG_FILE": "/tmp/client-foundation.log",
            },
            clear=False,
        ):
            cfg = load_axxon_config()

        self.assertEqual(cfg.host, "vms.local")
        self.assertEqual(cfg.user, "operator")
        self.assertEqual(cfg.password, "secret")
        self.assertEqual(cfg.port, 8080)
        self.assertEqual(
            cfg.as_cli,
            ["--host", "vms.local", "--user", "operator", "--password", "secret", "--port", "8080"],
        )

    def test_parse_grpc_response_handles_sse_multipart_and_plain_json(self):
        sse = '\n'.join(['data: {"result": true}', 'data: {"items": [1, 2]}'])
        self.assertEqual(len(parse_grpc_response(sse)), 2)

        multipart = "\r\n".join(
            [
                "--ngpboundary",
                "Content-Type: application/json; charset=utf-8",
                "Content-Length: 16",
                "",
                '{"result": true}',
                "--ngpboundary",
                "Content-Type: application/json; charset=utf-8",
                "Content-Length: 25",
                "",
                '{"items": [{"id": "1"}]}',
                "--ngpboundary--",
            ]
        )
        self.assertEqual(
            parse_grpc_response(multipart),
            [{"result": True}, {"items": [{"id": "1"}]}],
        )

        plain = parse_grpc_response('{"result": true, "id": "abc"}')
        self.assertEqual(plain, [{"result": True, "id": "abc"}])

    def test_build_server_info_payload_collects_partial_errors(self):
        payload = build_server_info_payload(_ServerInfoClient(), domain=True)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["usage"], {"domain": True, "servers": 1})
        self.assertEqual(payload["statistics"], {"requests": 12})
        self.assertIsNone(payload["version"])
        self.assertEqual(payload["errors"][0]["section"], "version")

    def test_live_media_url_builder_keeps_query_shape(self):
        live_url = build_live_media_url(
            "http://example:80",
            "cam/1",
            width=1280,
            height=720,
            crop={"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4},
            cache_bust_token=42,
        )
        self.assertEqual(
            live_url,
            "http://example:80/live/media/cam/1?w=1280&h=720&crop_x=0.1&crop_y=0.2&crop_width=0.3&crop_height=0.4&_ts=42",
        )

    def test_ttl_cache_get_or_set_and_expiry(self):
        now = [100.0]
        cache = TTLCache(default_ttl_sec=5, clock=lambda: now[0])
        loads: list[str] = []

        def _load() -> str:
            loads.append("x")
            return f"value-{len(loads)}"

        self.assertEqual(cache.get_or_set("cameras", _load), "value-1")
        self.assertEqual(cache.get_or_set("cameras", _load), "value-1")
        self.assertEqual(len(loads), 1)

        now[0] = 106.0
        self.assertEqual(cache.get_or_set("cameras", _load), "value-2")
        self.assertEqual(len(loads), 2)

    def test_ttl_cache_invalidate(self):
        cache = TTLCache(default_ttl_sec=5, clock=lambda: 10.0)
        cache.set("hosts", {"count": 3})
        cache.invalidate("hosts")
        self.assertIsNone(cache.get("hosts"))


if __name__ == "__main__":
    unittest.main()
