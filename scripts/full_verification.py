#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from axxon_web_api import AxxonClient
from camera_catalog import normalize_video_id


def _env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    raw = _env_str(name, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _env_str(name, "1" if default else "0").lower()
    return raw in {"1", "true", "yes", "on", "y"}


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _ts_compact(value: dt.datetime) -> str:
    return value.strftime("%Y%m%dT%H%M%S.000")


def _text(value: object) -> str:
    return str(value or "").strip()


def _ptz_error_text(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    error_code = _text(payload.get("error_code"))
    if error_code and error_code != "NotError":
        return error_code
    if payload.get("result") is False:
        return "result=false"
    return None


class SkipCheck(RuntimeError):
    pass


@dataclass(frozen=True)
class VerificationConfig:
    host: str
    user: str = "root"
    password: str = ""
    port: int = 80
    scheme: str = "http"
    window_sec: int = 3600
    output_path: Path = Path("full_verification_results.json")
    verify_video_id: str = ""
    verify_frame_ts: str = ""
    ptz_enabled: bool = False
    ptz_camera_ap: str = ""
    ptz_preset_position: int | None = None
    ptz_speed: int = 1

    @property
    def ready(self) -> bool:
        return bool(self.host and self.password)


def load_config_from_env(*, output_path: Path | None = None) -> VerificationConfig:
    ptz_enabled = _env_bool("AXXON_VERIFY_PTZ", False)
    ptz_preset_position_raw = _env_str("AXXON_VERIFY_PTZ_PRESET_POSITION")
    return VerificationConfig(
        host=_env_str("AXXON_HOST"),
        user=_env_str("AXXON_USER", "root"),
        password=_env_str("AXXON_PASS"),
        port=_env_int("AXXON_PORT", 80),
        scheme=_env_str("AXXON_SCHEME", "http") or "http",
        window_sec=max(60, _env_int("AXXON_VERIFY_WINDOW_SEC", 3600)),
        output_path=Path(output_path or "full_verification_results.json"),
        verify_video_id=_env_str("AXXON_VERIFY_VIDEO_ID"),
        verify_frame_ts=_env_str("AXXON_VERIFY_FRAME_TS"),
        ptz_enabled=ptz_enabled,
        ptz_camera_ap=_env_str("AXXON_VERIFY_PTZ_CAMERA_AP"),
        ptz_preset_position=int(ptz_preset_position_raw) if ptz_preset_position_raw else None,
        ptz_speed=max(1, _env_int("AXXON_VERIFY_PTZ_SPEED", 1)),
    )


def _candidate_frame_target(rows: list[dict[str, Any]], *, source: str) -> tuple[str, str, str] | None:
    for row in rows:
        camera_access_point = _text(row.get("camera_access_point"))
        frame_ts = _text(row.get("best_frame_timestamp") or row.get("timestamp"))
        if camera_access_point and frame_ts:
            return normalize_video_id(camera_access_point), frame_ts, source
    return None


def select_frame_target(
    config: VerificationConfig,
    *,
    events: list[dict[str, Any]],
    lpr_events: list[dict[str, Any]],
) -> tuple[str, str, str]:
    explicit_video_id = normalize_video_id(config.verify_video_id)
    explicit_frame_ts = _text(config.verify_frame_ts)
    if explicit_video_id and explicit_frame_ts:
        return explicit_video_id, explicit_frame_ts, "explicit_config"
    if explicit_video_id:
        for source_name, rows in (("recent_events", events), ("recent_lpr_events", lpr_events)):
            candidate = _candidate_frame_target(rows, source=source_name)
            if candidate:
                return explicit_video_id, candidate[1], f"explicit_video_id+{source_name}"
        raise SkipCheck(
            "archive frame export skipped: set AXXON_VERIFY_FRAME_TS or ensure recent events expose a timestamp"
        )
    for source_name, rows in (("recent_events", events), ("recent_lpr_events", lpr_events)):
        candidate = _candidate_frame_target(rows, source=source_name)
        if candidate:
            return candidate
    raise SkipCheck(
        "archive frame export skipped: no recent event exposed both camera_access_point and timestamp"
    )


def _check_result(status: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"status": status}
    payload.update(kwargs)
    return payload


def _run_check(name: str, fn) -> tuple[dict[str, Any], Any]:
    try:
        details = fn()
        if not isinstance(details, dict):
            details = {"result": details}
        return _check_result("PASS", **details), details
    except SkipCheck as exc:
        return _check_result("SKIP", reason=str(exc)), None
    except Exception as exc:
        return _check_result("FAIL", error=str(exc)), None


def run_live_verification(client: Any, config: VerificationConfig) -> dict[str, Any]:
    end = _utc_now()
    begin = end - dt.timedelta(seconds=config.window_sec)
    begin_ts = _ts_compact(begin)
    end_ts = _ts_compact(end)

    results: dict[str, Any] = {
        "metadata": {
            "validated_at_utc": end.isoformat(),
            "python_executable": sys.executable,
            "window_sec": config.window_sec,
            "host": config.host,
            "port": config.port,
            "scheme": config.scheme,
            "live_verification_ran": True,
        },
        "checks": {},
    }

    events: list[dict[str, Any]] = []
    lpr_events: list[dict[str, Any]] = []

    def _events_check() -> dict[str, Any]:
        nonlocal events
        events = list(client.read_events(begin=begin_ts, end=end_ts, limit=5))
        sample = events[0] if events else {}
        return {
            "count": len(events),
            "sample_event_id": _text(sample.get("id") or sample.get("guid")),
            "sample_camera_access_point": _text(sample.get("camera_access_point")),
        }

    def _lpr_check() -> dict[str, Any]:
        nonlocal lpr_events
        lpr_events = list(client.read_lpr_events(begin=begin_ts, end=end_ts, limit=5))
        sample = lpr_events[0] if lpr_events else {}
        return {
            "count": len(lpr_events),
            "sample_event_id": _text(sample.get("id") or sample.get("guid")),
            "sample_camera_access_point": _text(sample.get("camera_access_point")),
        }

    def _archive_check() -> dict[str, Any]:
        video_id, frame_ts, source = select_frame_target(
            config,
            events=events,
            lpr_events=lpr_events,
        )
        with TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "verification-frame.jpg"
            result_path = Path(client.media_frame(video_id, frame_ts, out_path))
            size_bytes = result_path.stat().st_size if result_path.exists() else 0
        return {
            "video_id": video_id,
            "frame_ts": frame_ts,
            "source": source,
            "size_bytes": size_bytes,
        }

    def _ptz_check() -> dict[str, Any]:
        if not config.ptz_enabled:
            raise SkipCheck("PTZ live verification not enabled (set AXXON_VERIFY_PTZ=1)")
        if not config.ptz_camera_ap or config.ptz_preset_position is None:
            raise SkipCheck(
                "PTZ live verification requires AXXON_VERIFY_PTZ_CAMERA_AP and AXXON_VERIFY_PTZ_PRESET_POSITION"
            )

        position_info = client.ptz_position_info(config.ptz_camera_ap)
        session_payload = client.ptz_acquire_session(config.ptz_camera_ap)
        session_error = _ptz_error_text(session_payload)
        if session_error:
            raise RuntimeError(f"AcquireSessionId failed: {session_error}")
        session_id = None
        if isinstance(session_payload, dict):
            session_id = session_payload.get("session_id")
        if session_id in {None, ""}:
            raise RuntimeError(f"AcquireSessionId returned no session_id: {session_payload}")

        go_payload = None
        release_payload = None
        release_error = None
        try:
            go_payload = client.ptz_go_preset(
                config.ptz_camera_ap,
                session_id,
                config.ptz_preset_position,
                config.ptz_speed,
            )
            go_error = _ptz_error_text(go_payload)
            if go_error:
                raise RuntimeError(f"GoPreset failed: {go_error}")
        finally:
            try:
                release_payload = client.ptz_release_session(session_id, config.ptz_camera_ap)
                release_error = _ptz_error_text(release_payload)
            except Exception as exc:
                release_error = str(exc)
        if release_error:
            raise RuntimeError(f"ReleaseSessionId failed: {release_error}")
        return {
            "camera_access_point": config.ptz_camera_ap,
            "position": config.ptz_preset_position,
            "speed": config.ptz_speed,
            "session_id": session_id,
            "position_info_keys": sorted(position_info.keys()) if isinstance(position_info, dict) else [],
            "go_preset": go_payload,
            "release": release_payload,
        }

    for name, fn in (
        ("read_events_recent", _events_check),
        ("read_lpr_events_recent", _lpr_check),
        ("archive_frame_export", _archive_check),
        ("ptz_session_lifecycle", _ptz_check),
    ):
        result, _ = _run_check(name, fn)
        results["checks"][name] = result

    return results


def write_results(path: Path, results: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run env-gated Axxon One live verification checks.")
    parser.add_argument("--output", default="full_verification_results.json")
    args = parser.parse_args(argv)

    config = load_config_from_env(output_path=Path(args.output))
    if not config.ready:
        results = {
            "metadata": {
                "validated_at_utc": _utc_now().isoformat(),
                "python_executable": sys.executable,
                "live_verification_ran": False,
                "skip_reason": "AXXON_HOST/AXXON_PASS not set",
            },
            "checks": {},
        }
        write_results(config.output_path, results)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    client = AxxonClient(
        config.host,
        config.user,
        config.password,
        port=config.port,
        scheme=config.scheme,
    )
    results = run_live_verification(client, config)
    write_results(config.output_path, results)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    failed = any(check.get("status") == "FAIL" for check in results.get("checks", {}).values())
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
