#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
DEFAULT_PORT = int(os.environ.get("AXXON_RELAY_PORT", "8099"))
DEFAULT_HOST = os.environ.get("AXXON_RELAY_HOST", "0.0.0.0")
PUBLIC_BASE = os.environ.get("AXXON_RELAY_PUBLIC_BASE", f"http://127.0.0.1:{DEFAULT_PORT}")
STATE_DIR = ROOT / ".runtime"
SECRET_FILE = STATE_DIR / "relay_secret.txt"
HLS_DIR = STATE_DIR / "relay_hls"
FFMPEG_BIN = shutil.which("ffmpeg") or "ffmpeg"
HLS_SESSIONS: dict[str, dict] = {}


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_secret() -> bytes:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    env_secret = os.environ.get("AXXON_RELAY_SECRET", "").strip()
    if env_secret:
        return env_secret.encode("utf-8")
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip().encode("utf-8")
    secret = secrets.token_urlsafe(32)
    SECRET_FILE.write_text(secret, encoding="utf-8")
    return secret.encode("utf-8")


load_dotenv(ENV_PATH)
SECRET = get_secret()


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_dec(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def sign_payload(payload: dict) -> str:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac.new(SECRET, body, hashlib.sha256).digest()
    return f"{_b64u(body)}.{_b64u(sig)}"


def verify_token(token: str) -> dict:
    body_b64, sig_b64 = token.split(".", 1)
    body = _b64u_dec(body_b64)
    sig = _b64u_dec(sig_b64)
    expected = hmac.new(SECRET, body, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("bad signature")
    payload = json.loads(body.decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return payload


def axxon_conn() -> dict[str, str]:
    host = os.environ.get("AXXON_HOST", "").strip()
    if not host:
        raise RuntimeError("AXXON_HOST is not set")
    return {
        "host": host,
        "port": os.environ.get("AXXON_PORT", "80").strip() or "80",
        "user": os.environ.get("AXXON_USER", "root").strip() or "root",
        "password": os.environ.get("AXXON_PASS", "").strip(),
    }


def archive_mjpeg_url(payload: dict) -> str:
    conn = axxon_conn()
    video_id_q = quote(str(payload["video_id"]), safe="/:")
    ts = str(payload["ts"])
    params = {
        "format": "mjpeg",
        "w": str(payload.get("w", 1280)),
        "h": str(payload.get("h", 720)),
        "speed": str(payload.get("speed", 1)),
        "fr": str(payload.get("fr", 3)),
    }
    return f"http://{conn['host']}:{conn['port']}/archive/media/{video_id_q}/{ts}?{urlencode(params)}"


def _basic_auth_header() -> str:
    conn = axxon_conn()
    return "Basic " + base64.b64encode(f"{conn['user']}:{conn['password']}".encode("utf-8")).decode("ascii")


def ensure_hls_session(payload: dict) -> str:
    key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    info = HLS_SESSIONS.get(key)
    if info and info.get("proc") and info["proc"].poll() is None:
        return key
    sess_dir = HLS_DIR / key
    sess_dir.mkdir(parents=True, exist_ok=True)
    playlist = sess_dir / "playlist.m3u8"
    for old in sess_dir.glob("*"):
        try:
            old.unlink()
        except IsADirectoryError:
            pass
    cmd = [
        FFMPEG_BIN,
        "-hide_banner",
        "-loglevel",
        "error",
        "-fflags",
        "+genpts",
        "-headers",
        f"Authorization: {_basic_auth_header()}\r\nUser-Agent: AxxonRelay/0.1\r\n",
        "-i",
        archive_mjpeg_url(payload),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-tune",
        "zerolatency",
        "-pix_fmt",
        "yuv420p",
        "-g",
        "25",
        "-sc_threshold",
        "0",
        "-f",
        "hls",
        "-hls_time",
        "2",
        "-hls_list_size",
        "6",
        "-hls_flags",
        "delete_segments+append_list+omit_endlist",
        "-hls_segment_filename",
        str(sess_dir / "seg_%03d.ts"),
        str(playlist),
    ]
    log_path = sess_dir / "ffmpeg.log"
    with open(log_path, "ab") as logf:
        proc = subprocess.Popen(cmd, stdout=logf, stderr=logf)
    HLS_SESSIONS[key] = {"proc": proc, "dir": sess_dir, "started": time.time()}
    return key


class RelayHandler(BaseHTTPRequestHandler):
    server_version = "AxxonRelay/0.1"

    def log_message(self, fmt: str, *args) -> None:
        return

    def _write_text(self, code: int, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        token = (params.get("token") or [""])[0]
        if not token and parsed.path.startswith("/stream/"):
            token = parsed.path.removeprefix("/stream/")
        try:
            if parsed.path == "/healthz":
                self._write_text(200, "ok\n")
                return
            if parsed.path == "/hls/init":
                if not token:
                    self._write_text(400, "missing token\n")
                    return
                payload = verify_token(token)
                self._serve_hls_init(payload)
                return
            if parsed.path.startswith("/hls/"):
                self._serve_hls_file(parsed.path)
                return
            if not token:
                self._write_text(400, "missing token\n")
                return
            payload = verify_token(token)
            if parsed.path == "/watch":
                self._serve_watch(payload, token)
                return
            if parsed.path == "/watch_hls":
                self._serve_watch_hls(payload, token)
                return
            if parsed.path == "/stream" or parsed.path.startswith("/stream/"):
                self._serve_stream(payload)
                return
            if parsed.path == "/hls/init":
                self._serve_hls_init(payload)
                return
            self._write_text(404, "not found\n")
        except ValueError as exc:
            self._write_text(403, f"forbidden: {exc}\n")
        except HTTPError as exc:
            self._write_text(exc.code, f"upstream http error: {exc}\n")
        except URLError as exc:
            self._write_text(502, f"upstream url error: {exc}\n")
        except BrokenPipeError:
            return
        except Exception as exc:
            self._write_text(500, f"server error: {exc}\n")

    def _serve_watch(self, payload: dict, token: str) -> None:
        title = str(payload.get("camera_name") or payload.get("video_id") or "Archive stream")
        ts = str(payload.get("ts"))
        stream_src = f"/stream?token={quote(token, safe='._-')}"
        html = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background:#0b1220; color:#e5eefc; margin:0; padding:16px; }}
    .card {{ max-width: 1100px; margin:0 auto; }}
    .meta {{ opacity:.8; margin-bottom:12px; }}
    img {{ width:100%; height:auto; background:#000; border-radius:12px; border:1px solid #24324d; }}
    .note {{ margin-top:12px; font-size:14px; opacity:.75; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h2>🎬 {title}</h2>
    <div class=\"meta\">Archive stream starting from <b>{ts}</b> UTC · signed temporary link</div>
    <img src=\"{stream_src}\" alt=\"archive stream\" />
    <div class=\"note\">If the browser stalls, reopen the link. For production safety put this behind HTTPS.</div>
  </div>
</body>
</html>"""
        self._write_text(200, html, content_type="text/html; charset=utf-8")

    def _serve_watch_hls(self, payload: dict, token: str) -> None:
        title = str(payload.get("camera_name") or payload.get("video_id") or "Archive stream")
        ts = str(payload.get("ts"))
        init_src = f"/hls/init?token={quote(token, safe='._-')}"
        html = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background:#0b1220; color:#e5eefc; margin:0; padding:16px; }}
    .card {{ max-width: 1100px; margin:0 auto; }}
    .meta {{ opacity:.8; margin-bottom:12px; }}
    video {{ width:100%; height:auto; background:#000; border-radius:12px; border:1px solid #24324d; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h2>🎬 {title}</h2>
    <div class=\"meta\">Archive HLS stream starting from <b>{ts}</b> UTC</div>
    <video controls autoplay playsinline muted src=\"{init_src}\"></video>
  </div>
</body>
</html>"""
        self._write_text(200, html, content_type="text/html; charset=utf-8")

    def _serve_stream(self, payload: dict) -> None:
        url = archive_mjpeg_url(payload)
        req = Request(url, headers={"Authorization": _basic_auth_header(), "User-Agent": "AxxonRelay/0.1"})
        with urlopen(req, timeout=30) as upstream:
            self.send_response(200)
            self.send_header("Content-Type", upstream.headers.get("Content-Type", "multipart/x-mixed-replace"))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            while True:
                chunk = upstream.read(64 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()

    def _serve_hls_init(self, payload: dict) -> None:
        session = ensure_hls_session(payload)
        playlist = HLS_DIR / session / "playlist.m3u8"
        deadline = time.time() + 20
        while time.time() < deadline:
            if playlist.exists() and playlist.stat().st_size > 0:
                break
            time.sleep(0.5)
        if not playlist.exists():
            self._write_text(504, "hls startup timeout\n")
            return
        playlist_url = f"/hls/{session}/playlist.m3u8"
        self.send_response(302)
        self.send_header("Location", playlist_url)
        self.end_headers()

    def _serve_hls_file(self, path: str) -> None:
        rel = path.removeprefix("/hls/")
        file_path = (HLS_DIR / rel).resolve()
        if HLS_DIR.resolve() not in file_path.parents and file_path != HLS_DIR.resolve():
            self._write_text(403, "forbidden\n")
            return
        if not file_path.exists() or not file_path.is_file():
            self._write_text(404, "not found\n")
            return
        ctype = "application/vnd.apple.mpegurl" if file_path.suffix == ".m3u8" else "video/mp2t"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_link(video_id: str, ts: str, camera_name: str = "", ttl_sec: int = 900, w: int = 1280, h: int = 720, speed: int = 1, fr: int = 3, mode: str = "mjpeg") -> str:
    payload = {
        "video_id": video_id,
        "camera_name": camera_name,
        "ts": ts,
        "w": w,
        "h": h,
        "speed": speed,
        "fr": fr,
        "exp": int(time.time()) + ttl_sec,
    }
    token = sign_payload(payload)
    if mode == "hls":
        route = "/hls/init"
        return f"{PUBLIC_BASE.rstrip('/')}{route}?token={token}"
    return f"{PUBLIC_BASE.rstrip('/')}/stream/{token}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--video-id")
    parser.add_argument("--camera-name", default="")
    parser.add_argument("--ts")
    parser.add_argument("--ttl-sec", type=int, default=900)
    parser.add_argument("--w", type=int, default=1280)
    parser.add_argument("--h", type=int, default=720)
    parser.add_argument("--speed", type=int, default=1)
    parser.add_argument("--fr", type=int, default=3)
    parser.add_argument("--mode", choices=["mjpeg", "hls"], default="mjpeg")
    args = parser.parse_args()

    if args.serve:
        server = ThreadingHTTPServer((args.host, args.port), RelayHandler)
        print(f"relay listening on http://{args.host}:{args.port}")
        server.serve_forever()
        return

    if not args.video_id or not args.ts:
        raise SystemExit("--video-id and --ts are required unless --serve is used")
    print(make_link(args.video_id, args.ts, camera_name=args.camera_name, ttl_sec=args.ttl_sec, w=args.w, h=args.h, speed=args.speed, fr=args.fr, mode=args.mode))


if __name__ == "__main__":
    main()
