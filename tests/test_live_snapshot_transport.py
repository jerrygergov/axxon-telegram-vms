import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import AxxonClient, _append_cache_bust, _ffmpeg_auth_headers


class _FakeResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class LiveSnapshotTransportTests(unittest.TestCase):
    def test_append_cache_bust_preserves_existing_query(self):
        url = _append_cache_bust("http://example/live/media/cam?w=1280")
        self.assertIn("w=1280", url)
        self.assertIn("_ts=", url)

    def test_ffmpeg_auth_headers_renders_basic_auth(self):
        rendered = _ffmpeg_auth_headers({"Authorization": "Basic abc123"})
        self.assertEqual(rendered, "Authorization: Basic abc123\r\n")

    def test_live_snapshot_prefers_authenticated_live_media_ffmpeg(self):
        client = AxxonClient("example.local", "root", "secret", port=80)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "snap.jpg"
            ffmpeg_calls = []

            def _fake_run(cmd, **kwargs):
                ffmpeg_calls.append(cmd)
                out.write_bytes(b"jpg")
                return Mock(returncode=0)

            with patch("axxon_web_api.subprocess.run", side_effect=_fake_run):
                result = client.live_snapshot("cam/1", out, width=1280, height=720)

            self.assertEqual(result, str(out))
            self.assertTrue(ffmpeg_calls)
            cmd = ffmpeg_calls[0]
            self.assertIn("-headers", cmd)
            self.assertIn("Authorization: Basic", cmd[cmd.index("-headers") + 1])
            self.assertIn("_ts=", cmd[cmd.index("-i") + 1])
            self.assertIn("w=1280", cmd[cmd.index("-i") + 1])
            self.assertIn("h=720", cmd[cmd.index("-i") + 1])

    def test_live_snapshot_fallback_snapshot_is_cache_busted(self):
        client = AxxonClient("example.local", "root", "secret", port=80)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "snap.jpg"
            with patch("axxon_web_api.subprocess.run", side_effect=RuntimeError("ffmpeg failed")):
                with patch.object(client, "_request", return_value=_FakeResponse(b"jpg")) as request_mock:
                    result = client.live_snapshot("cam/1", out, width=640, height=360)

            self.assertEqual(result, str(out))
            args = request_mock.call_args[0]
            self.assertEqual(args[0], "GET")
            self.assertIn("/live/media/snapshot/cam/1", args[1])
            self.assertIn("w=640", args[1])
            self.assertIn("h=360", args[1])
            self.assertIn("_ts=", args[1])


if __name__ == "__main__":
    unittest.main()
