import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from axxon_web_api import AxxonClient


class FakeArchiveClient(AxxonClient):
    def __init__(self):
        self.export_calls: list[dict[str, object]] = []

    def export_archive(
        self,
        video_id: str,
        begin_ts: str,
        end_ts: str,
        *,
        out_path: Path,
        export_format: str,
        waittimeout: int,
        archive: str | None = None,
        attempts: int = 90,
        sleep_sec: float = 1.0,
        fallback_name: str,
    ) -> dict:
        self.export_calls.append(
            {
                "video_id": video_id,
                "begin_ts": begin_ts,
                "end_ts": end_ts,
                "out_path": str(out_path),
                "export_format": export_format,
                "waittimeout": waittimeout,
                "archive": archive,
                "attempts": attempts,
                "sleep_sec": sleep_sec,
                "fallback_name": fallback_name,
            }
        )
        out_path.write_bytes(b"jpg")
        return {"path": str(out_path)}


class ArchiveFrameTests(unittest.TestCase):
    def test_media_frame_uses_export_archive_jpg_contract(self):
        client = FakeArchiveClient()
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "frame.jpg"
            result = client.media_frame(
                "ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
                "20260310T105500",
                out,
            )

        self.assertEqual(result, str(out))
        self.assertEqual(len(client.export_calls), 1)
        self.assertEqual(
            client.export_calls[0],
            {
                "video_id": "ServerA/DeviceIpint.1/SourceEndpoint.video:0:0",
                "begin_ts": "20260310T105500",
                "end_ts": "20260310T105500",
                "out_path": str(out),
                "export_format": "jpg",
                "waittimeout": 30000,
                "archive": None,
                "attempts": 30,
                "sleep_sec": 1.0,
                "fallback_name": "file.jpg",
            },
        )


if __name__ == "__main__":
    unittest.main()
