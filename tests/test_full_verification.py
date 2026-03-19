import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from full_verification import VerificationConfig, load_config_from_env, run_live_verification


class FakeVerificationClient:
    def __init__(self):
        self.calls: list[tuple[str, object]] = []

    def read_events(self, *, begin: str, end: str, limit: int = 5):
        self.calls.append(("read_events", {"begin": begin, "end": end, "limit": limit}))
        return [
            {
                "id": "evt-1",
                "timestamp": "20260310T105500",
                "camera_access_point": "hosts/ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
            }
        ]

    def read_lpr_events(self, *, begin: str, end: str, limit: int = 5):
        self.calls.append(("read_lpr_events", {"begin": begin, "end": end, "limit": limit}))
        return []

    def media_frame(self, video_id: str, frame_ts: str, out_path: Path, **kwargs):
        self.calls.append(
            (
                "media_frame",
                {
                    "video_id": video_id,
                    "frame_ts": frame_ts,
                    "out_path": str(out_path),
                    "kwargs": kwargs,
                },
            )
        )
        Path(out_path).write_bytes(b"jpg")
        return str(out_path)


class FullVerificationTests(unittest.TestCase):
    def test_load_config_from_env_defaults_and_ptz_opt_in(self):
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "results.json"
            with patch.dict(
                os.environ,
                {
                    "AXXON_HOST": "vms.local",
                    "AXXON_USER": "operator",
                    "AXXON_PASS": "secret",
                    "AXXON_PORT": "8080",
                    "AXXON_SCHEME": "https",
                    "AXXON_VERIFY_WINDOW_SEC": "900",
                    "AXXON_VERIFY_PTZ": "1",
                    "AXXON_VERIFY_PTZ_CAMERA_AP": "hosts/A/cam1",
                    "AXXON_VERIFY_PTZ_PRESET_POSITION": "12",
                    "AXXON_VERIFY_PTZ_SPEED": "4",
                },
                clear=False,
            ):
                cfg = load_config_from_env(output_path=output_path)

        self.assertEqual(cfg.host, "vms.local")
        self.assertEqual(cfg.user, "operator")
        self.assertEqual(cfg.password, "secret")
        self.assertEqual(cfg.port, 8080)
        self.assertEqual(cfg.scheme, "https")
        self.assertEqual(cfg.window_sec, 900)
        self.assertTrue(cfg.ptz_enabled)
        self.assertEqual(cfg.ptz_camera_ap, "hosts/A/cam1")
        self.assertEqual(cfg.ptz_preset_position, 12)
        self.assertEqual(cfg.ptz_speed, 4)
        self.assertEqual(cfg.output_path, output_path)

    def test_run_live_verification_uses_event_camera_for_frame_and_skips_ptz_when_disabled(self):
        client = FakeVerificationClient()
        with TemporaryDirectory() as tmp:
            cfg = VerificationConfig(
                host="vms.local",
                user="root",
                password="secret",
                port=80,
                scheme="http",
                window_sec=600,
                output_path=Path(tmp) / "results.json",
            )
            results = run_live_verification(client, cfg)

        self.assertEqual(results["checks"]["read_events_recent"]["status"], "PASS")
        self.assertEqual(results["checks"]["read_lpr_events_recent"]["status"], "PASS")
        self.assertEqual(results["checks"]["archive_frame_export"]["status"], "PASS")
        self.assertEqual(results["checks"]["ptz_session_lifecycle"]["status"], "SKIP")
        self.assertEqual(
            client.calls[2],
            (
                "media_frame",
                {
                    "video_id": "ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "frame_ts": "20260310T105500",
                    "out_path": client.calls[2][1]["out_path"],
                    "kwargs": {},
                },
            ),
        )


if __name__ == "__main__":
    unittest.main()
