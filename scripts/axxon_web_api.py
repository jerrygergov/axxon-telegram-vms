#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import socket
import time
import urllib.parse
import urllib.request
import subprocess
import re
from collections.abc import Mapping
from pathlib import Path
import sys
from typing import Any
from camera_catalog import friendly_label, normalize_camera_rows, normalize_video_id
from config_loader import load_axxon_config, load_secure_profile_config, load_tg_bot_config
from media_utils import extract_raw_rectangle_candidates, rectangle_candidate_to_pixel_crop
from secure_profile_storage import SecureProfileStore

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from axxon_telegram_vms.client import (
    append_cache_bust as _append_cache_bust,
    build_live_media_url,
    build_server_info_payload,
    ffmpeg_auth_headers as _ffmpeg_auth_headers,
    parse_grpc_response as _parse_grpc_response,
)
from axxon_telegram_vms.models import classify_raw_event_category, normalize_event_card
from axxon_telegram_vms.services import (
    AdminViewPolicy,
    DEFAULT_ARCHIVE_CONTEXT_WINDOW_SEC,
    DEFAULT_ARCHIVE_PREVIEW_HEIGHT,
    DEFAULT_ARCHIVE_PREVIEW_THRESHOLD_MS,
    DEFAULT_ARCHIVE_PREVIEW_WIDTH,
    DEFAULT_ARCHIVE_SCAN_LIMIT,
    DEFAULT_ALLOWED_MACRO_MODE_KINDS,
    DEFAULT_DENIED_MACRO_ACTION_FAMILIES,
    DEFAULT_FACE_SEARCH_ACCURACY,
    DEFAULT_FACE_SEARCH_MAX_CAMERAS,
    DEFAULT_FACE_SEARCH_PAGE_SIZE,
    DEFAULT_FACE_SEARCH_SCAN_LIMIT,
    DEFAULT_FACE_SEARCH_WINDOW_SEC,
    DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE,
    DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT,
    DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC,
    DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS,
    DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
    DEFAULT_PTZ_CONTROL_SPEED,
    DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS,
    EventSearchRequest,
    build_admin_view_policy,
    build_archive_jump_request,
    build_event_search_backend_request,
    build_event_search_request,
    build_face_search_backend_request,
    build_face_search_request,
    build_license_plate_search_backend_request,
    build_license_plate_search_request,
    build_macro_execution_policy,
    build_macro_execution_request,
    build_multi_camera_export_request,
    build_ptz_control_policy,
    build_ptz_control_request,
    build_ptz_goto_preset_backend_request,
    build_single_camera_export_request,
    load_face_search_reference_image,
    derive_archive_jump_selection,
    evaluate_macro_execution_guardrails,
    evaluate_ptz_control_guardrails,
    resolve_face_search_selection,
    select_macro_inventory_record,
    select_ptz_camera_record,
    select_ptz_preset_record,
    resolve_scope_subjects,
    shape_license_plate_search_results,
    shape_face_search_results,
    shape_macro_execution_preview,
    shape_macro_execution_result,
    resolve_multi_camera_export_selection,
    shape_ptz_control_preview,
    shape_ptz_control_result,
    resolve_single_camera_export_selection,
    shape_archive_jump_result,
    shape_admin_view_result,
    shape_event_search_results,
    shape_multi_camera_export_result,
    shape_single_camera_export_result,
    summarize_ptz_preset_row,
)


ALERT_SEVERITY_BY_FLAG = {
    "confirmed": "SV_ALARM",
    "suspicious": "SV_WARNING",
    "false": "SV_FALSE",
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def ts_compact(d: dt.datetime) -> str:
    return d.strftime("%Y%m%dT%H%M%S.000000")


def ts_to_export(ts: str) -> str:
    return str(ts or "").strip()


def ts_parse(s: str) -> dt.datetime:
    if "." in s:
        return dt.datetime.strptime(s, "%Y%m%dT%H%M%S.%f").replace(tzinfo=dt.timezone.utc)
    return dt.datetime.strptime(s, "%Y%m%dT%H%M%S").replace(tzinfo=dt.timezone.utc)


def log_line(path: str, msg: str):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(f"[{dt.datetime.now(dt.timezone.utc).isoformat()}] {msg}\n")


class AxxonClient:
    def __init__(self, host: str, user: str, password: str, port: int = 80, scheme: str = "http"):
        self.base = f"{scheme}://{host}:{port}"
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self.auth_header = {"Authorization": f"Basic {token}"}

    def _request(self, method: str, url: str, data=None, headers=None, timeout=30):
        h = {**self.auth_header}
        if headers:
            h.update(headers)
        body = None
        if data is not None:
            body = data if isinstance(data, (bytes, bytearray)) else data.encode()
        req = urllib.request.Request(url=url, method=method, data=body, headers=h)
        return urllib.request.urlopen(req, timeout=timeout)

    def grpc_call(self, method_name: str, data: dict, timeout: int = 60):
        payload = json.dumps({"method": method_name, "data": data}).encode()
        with self._request("POST", f"{self.base}/grpc", data=payload, headers={"Content-Type": "application/json"}, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
        return _parse_grpc_response(raw)

    def grpc_stream_packets(
        self,
        method_name: str,
        data: dict,
        *,
        timeout: int = 60,
        stop_event: object | None = None,
    ):
        payload = json.dumps({"method": method_name, "data": data}).encode()
        response = self._request(
            "POST",
            f"{self.base}/grpc",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        content_type = str(response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        try:
            if content_type == "text/event-stream":
                while True:
                    if stop_event is not None and getattr(stop_event, "is_set", lambda: False)():
                        break
                    try:
                        line = response.readline()
                    except socket.timeout:
                        continue
                    if not line:
                        break
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if not decoded.startswith("data: "):
                        continue
                    try:
                        parsed = json.loads(decoded[6:].strip())
                    except json.JSONDecodeError:
                        continue
                    if isinstance(parsed, dict):
                        yield parsed
                return

            raw = response.read().decode("utf-8", errors="replace")
            for packet in _parse_grpc_response(raw):
                if stop_event is not None and getattr(stop_event, "is_set", lambda: False)():
                    break
                yield packet
        finally:
            response.close()

    def _grpc_payload(self, method_name: str, data: dict, timeout: int = 60) -> dict:
        packets = self.grpc_call(method_name, data, timeout=timeout)
        merged: dict[str, Any] = {}
        for packet in packets:
            payload = packet.get("data") if isinstance(packet.get("data"), dict) else packet
            if not isinstance(payload, dict):
                continue
            for key, value in payload.items():
                if key == "result" and len(payload) == 1:
                    continue
                current = merged.get(key)
                if isinstance(current, list) and isinstance(value, list):
                    current.extend(value)
                elif isinstance(current, dict) and isinstance(value, dict):
                    current.update(value)
                else:
                    merged[key] = value
        return merged

    def list_cameras(self, view: str = None, filter_prefix: str = None):
        data = {}
        if view:
            data["view"] = view
        if filter_prefix:
            data["filter"] = filter_prefix
        objs = self.grpc_call("axxonsoft.bl.domain.DomainService.ListCameras", data)
        out = []
        for o in objs:
            out.extend(o.get("items", []))
        return out

    def read_events(
        self,
        begin: str,
        end: str,
        subject: str = None,
        event_type: str = None,
        values: str = None,
        limit: int = 100,
        offset: int = 0,
        descending: bool = True,
    ):
        filt = {}
        if event_type:
            filt["type"] = event_type
        if subject:
            filt["subjects"] = subject
        if values:
            filt["values"] = values
        data = {
            "range": {"begin_time": begin, "end_time": end},
            "limit": limit,
            "offset": max(0, int(offset)),
            "descending": descending,
        }
        if filt:
            data["filters"] = {"filters": [filt]}
        objs = self.grpc_call("axxonsoft.bl.events.EventHistoryService.ReadEvents", data)
        items = []
        for o in objs:
            items.extend(o.get("items", []))
        return items

    def read_lpr_events(
        self,
        begin: str,
        end: str,
        subject: str = None,
        plate: str = None,
        search_predicate: str = None,
        limit: int = 100,
        offset: int = 0,
        descending: bool = True,
    ):
        filt = {}
        if subject:
            filt["subjects"] = subject
        if plate:
            filt["values"] = plate
        data = {
            "range": {"begin_time": begin, "end_time": end},
            "limit": limit,
            "offset": max(0, int(offset)),
            "descending": descending,
        }
        if filt:
            data["filters"] = {"filters": [filt]}
        if search_predicate:
            data["search_predicate"] = search_predicate
        objs = self.grpc_call("axxonsoft.bl.events.EventHistoryService.ReadLprEvents", data)
        items = []
        for o in objs:
            items.extend(o.get("items", []))
        return items

    def find_similar_objects(
        self,
        *,
        begin: str,
        end: str,
        origin_ids: list[str],
        jpeg_image: str,
        minimal_score: float,
        limit: int,
        offset: int = 0,
        is_face: bool = True,
    ) -> dict:
        data = {
            "session": 0,
            "is_face": bool(is_face),
            "minimal_score": float(minimal_score),
            "jpeg_image": jpeg_image,
            "range": {"begin_time": begin, "end_time": end},
            "origin_ids": list(origin_ids),
            "limit": max(1, int(limit)),
            "offset": max(0, int(offset)),
        }
        packets = self.grpc_call("axxonsoft.bl.events.EventHistoryService.FindSimilarObjects", data)
        items = []
        saw_terminal_packet = False
        for packet in packets:
            packet_items = packet.get("items") if isinstance(packet.get("items"), list) else None
            if packet_items is None:
                inner = packet.get("data") if isinstance(packet.get("data"), dict) else {}
                packet_items = inner.get("items") if isinstance(inner.get("items"), list) else None
            if packet_items:
                items.extend(packet_items)
            elif packet_items == []:
                saw_terminal_packet = True
        return {
            "items": items,
            "packets": len(packets),
            "complete": saw_terminal_packet or len(items) < max(1, int(limit)),
        }

    def _start_archive_export(
        self,
        video_id: str,
        begin_ts: str,
        end_ts: str,
        *,
        export_format: str,
        waittimeout: int,
        archive: str | None = None,
    ) -> str:
        begin = ts_to_export(begin_ts)
        end = ts_to_export(end_ts)
        params = {"waittimeout": int(waittimeout)}
        if archive:
            params["archive"] = archive
        query = urllib.parse.urlencode(params)
        start_url = f"{self.base}/export/archive/{video_id}/{begin}/{end}?{query}"
        with self._request(
            "POST",
            start_url,
            data=json.dumps({"format": export_format}),
            headers={"Content-Type": "application/json"},
        ) as r:
            location = r.headers.get("Location")
        if not location:
            raise RuntimeError("No Location header from export start")
        return location.rstrip("/").split("/")[-1]

    def _wait_export_status(self, export_id: str, *, attempts: int, sleep_sec: float) -> dict:
        status = {}
        for _ in range(max(1, int(attempts))):
            with self._request("GET", f"{self.base}/export/{export_id}/status") as r:
                status = json.loads(r.read().decode())
            if status.get("state") == 2:
                break
            time.sleep(max(0.0, float(sleep_sec)))
        return status

    def _download_export_file(self, export_id: str, out_path: Path, status: dict, fallback_name: str) -> tuple[str, str]:
        file_names = status.get("files") if isinstance(status.get("files"), list) else []
        file_name = str(next((value for value in file_names if str(value or "").strip()), fallback_name))
        q = urllib.parse.urlencode({"name": file_name})
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with self._request("GET", f"{self.base}/export/{export_id}/file?{q}") as r:
            out_path.write_bytes(r.read())
        return str(out_path), file_name

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
        export_id = self._start_archive_export(
            video_id,
            begin_ts,
            end_ts,
            export_format=export_format,
            waittimeout=waittimeout,
            archive=archive,
        )
        try:
            status = self._wait_export_status(export_id, attempts=attempts, sleep_sec=sleep_sec)
            if status.get("state") != 2:
                raise RuntimeError(f"Export not ready: {status}")
            downloaded_path, downloaded_name = self._download_export_file(
                export_id,
                out_path,
                status,
                fallback_name,
            )
        finally:
            try:
                self._request("DELETE", f"{self.base}/export/{export_id}").read()
            except Exception:
                pass
        return {
            "export_id": export_id,
            "status": status,
            "path": downloaded_path,
            "download_name": downloaded_name,
        }

    def export_frame(self, video_id: str, frame_ts: str, out_path: Path, waittimeout: int = 30000):
        result = self.export_archive(
            video_id,
            frame_ts,
            frame_ts,
            out_path=out_path,
            export_format="jpg",
            waittimeout=waittimeout,
            attempts=30,
            sleep_sec=1.0,
            fallback_name="file.jpg",
        )
        return result["path"]

    def export_clip(self, video_id: str, begin_ts: str, end_ts: str, out_path: Path, waittimeout: int = 60000):
        result = self.export_archive(
            video_id,
            begin_ts,
            end_ts,
            out_path=out_path,
            export_format="mp4",
            waittimeout=waittimeout,
            attempts=90,
            sleep_sec=1.0,
            fallback_name="file.mp4",
        )
        return result["path"]

    def media_frame(self, video_id: str, frame_ts: str, out_path: Path, threshold_ms: int = 1000, crop: dict = None, width: int = None, height: int = None):
        out_path = Path(out_path)
        filters: list[str] = []
        if crop:
            crop_x = float(crop.get("x", 0) or 0)
            crop_y = float(crop.get("y", 0) or 0)
            crop_w = float(crop.get("w", 0) or 0)
            crop_h = float(crop.get("h", 0) or 0)
            filters.append(f"crop=iw*{crop_w}:ih*{crop_h}:iw*{crop_x}:ih*{crop_y}")
        scale_w = int(width) if width else -1
        scale_h = int(height) if height else -1
        if width or height:
            filters.append(f"scale={scale_w}:{scale_h}")

        export_path = out_path
        if filters:
            export_path = out_path.with_name(f"{out_path.stem}.source{out_path.suffix}")

        result = self.export_archive(
            video_id,
            frame_ts,
            frame_ts,
            out_path=export_path,
            export_format="jpg",
            waittimeout=max(30000, int(threshold_ms or 0)),
            attempts=30,
            sleep_sec=1.0,
            fallback_name="file.jpg",
        )
        if filters:
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-i",
                        str(export_path),
                        "-vf",
                        ",".join(filters),
                        str(out_path),
                    ],
                    check=True,
                    timeout=15,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            finally:
                if export_path != out_path:
                    export_path.unlink(missing_ok=True)
        else:
            out_path = Path(result["path"])
        return str(out_path)

    def live_snapshot(self, video_id: str, out_path: Path, width: int = None, height: int = None, crop: dict = None):
        # Prefer grabbing a frame from /live/media stream because
        # /live/media/snapshot may be cached by server timeout settings.
        stream_url = build_live_media_url(
            self.base,
            video_id,
            width=width,
            height=height,
            crop=crop,
        )
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-headers", _ffmpeg_auth_headers(self.auth_header),
                    "-i", stream_url,
                    "-frames:v", "1",
                    str(out_path),
                ],
                check=True,
                timeout=8,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if out_path.exists() and out_path.stat().st_size > 0:
                return str(out_path)
        except Exception:
            pass

        # Fallback to snapshot endpoint.
        url = build_live_media_url(
            self.base,
            video_id,
            width=width,
            height=height,
            crop=crop,
            snapshot=True,
        )
        with self._request("GET", url) as r:
            out_path.write_bytes(r.read())
        return str(out_path)

    def server_usage(self, domain: bool = False):
        # Docs: /statistics/hardware and /statistics/hardware/domain
        # Historical alias in older support/docs/tests: /info/usage
        url = f"{self.base}/statistics/hardware/domain" if domain else f"{self.base}/statistics/hardware"
        with self._request("GET", url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def list_hosts(self):
        with self._request("GET", f"{self.base}/hosts", timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def host_info(self, node_name: str):
        quoted = urllib.parse.quote(node_name, safe="")
        with self._request("GET", f"{self.base}/hosts/{quoted}", timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def current_web_user(self):
        with self._request("GET", f"{self.base}/currentuser", timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def server_version(self):
        # Docs: /product/version
        # Historical alias in older support/docs/tests: /info/version
        with self._request("GET", f"{self.base}/product/version", timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def server_statistics(self):
        # Docs: /statistics/webserver
        # Historical alias in older support/docs/tests: /statistics/server
        with self._request("GET", f"{self.base}/statistics/webserver", timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def security_list_config(self):
        return self._grpc_payload(
            "axxonsoft.bl.security.SecurityService.ListConfig",
            {},
            timeout=60,
        )

    def security_list_global_permissions(self, role_ids: list[str]):
        permissions: dict[str, Any] = {}
        seen: set[str] = set()
        for role_id in role_ids:
            value = str(role_id or "").strip()
            if not value or value.casefold() in seen:
                continue
            seen.add(value.casefold())
            payload = self._grpc_payload(
                "axxonsoft.bl.security.SecurityService.ListGlobalPermissions",
                {"role_ids": value},
                timeout=60,
            )
            current = payload.get("permissions") if isinstance(payload.get("permissions"), dict) else {}
            permissions.update(current)
        return {"permissions": permissions}

    def archive_list(self, video_id: str):
        with self._request("GET", f"{self.base}/archive/list/{video_id}", timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def archive_intervals(
        self,
        video_id: str,
        *,
        end: str,
        begin: str,
        limit: int = 5,
        scale: int | None = None,
        archive: str | None = None,
    ):
        params = {"limit": int(limit)}
        if scale is not None:
            params["scale"] = int(scale)
        if archive:
            params["archive"] = archive
        query = urllib.parse.urlencode(params)
        url = f"{self.base}/archive/contents/intervals/{video_id}/{end}/{begin}"
        if query:
            url = f"{url}?{query}"
        with self._request("GET", url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def archive_depth(
        self,
        video_id: str,
        *,
        archive: str | None = None,
        threshold: int | None = None,
    ):
        params = {}
        if archive:
            params["archive"] = archive
        if threshold is not None:
            params["threshold"] = int(threshold)
        query = urllib.parse.urlencode(params)
        url = f"{self.base}/archive/statistics/depth/{video_id}"
        if query:
            url = f"{url}?{query}"
        with self._request("GET", url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))

    def list_macros(self, view: str = "VIEW_MODE_FULL"):
        data = {"view": view}
        errors: list[str] = []
        for method_name in (
            "axxonsoft.bl.logic.LogicService.ListMacrosV2",
            "axxonsoft.bl.logic.LogicService.ListMacros",
        ):
            try:
                packets = self.grpc_call(method_name, data)
            except Exception as ex:
                errors.append(f"{method_name}: {ex}")
                continue

            items: list[dict] = []
            for packet in packets:
                if isinstance(packet.get("items"), list):
                    items.extend(packet.get("items") or [])
                    continue
                inner = packet.get("data") if isinstance(packet.get("data"), dict) else {}
                if isinstance(inner.get("items"), list):
                    items.extend(inner.get("items") or [])
            if items:
                return items

        http_errors = list(errors)
        for url in (
            f"{self.base}/v1/logic_service/macros",
            f"{self.base}/logic_service/macros",
        ):
            try:
                with self._request("GET", url, timeout=30) as r:
                    payload = json.loads(r.read().decode("utf-8", errors="replace"))
                if isinstance(payload, list):
                    return [item for item in payload if isinstance(item, dict)]
            except Exception as ex:
                http_errors.append(f"{url}: {ex}")

        raise RuntimeError("Macro inventory read failed: " + "; ".join(http_errors))

    def launch_macro(self, macro_id: str):
        macro_id = urllib.parse.quote(str(macro_id or "").strip(), safe="")
        if not macro_id:
            raise ValueError("macro_id is required")
        url = f"{self.base}/macro/execute/{macro_id}"
        with self._request("GET", url, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="replace")
        raw = raw.strip()
        if not raw:
            return {"transport": "http", "response": None}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return {"transport": "http", "response": parsed}

    def _grpc_first_packet_data(self, method_name: str, data: dict[str, Any]):
        packets = self.grpc_call(method_name, data)
        for packet in packets:
            if not isinstance(packet, dict):
                continue
            inner = packet.get("data")
            if isinstance(inner, dict):
                return inner
            return packet
        return {}

    def ptz_presets(self, access_point: str):
        access_point = str(access_point or "").strip()
        if not access_point:
            raise ValueError("access_point is required")
        query = urllib.parse.urlencode({"access_point": access_point})
        url = f"{self.base}/v1/telemetry/presets?{query}"
        with self._request("GET", url, timeout=30) as r:
            payload = json.loads(r.read().decode("utf-8", errors="replace"))
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            if isinstance(payload.get("preset_info"), list):
                return payload.get("preset_info") or []
            inner = payload.get("data") if isinstance(payload.get("data"), dict) else {}
            if isinstance(inner.get("preset_info"), list):
                return inner.get("preset_info") or []
        return []

    def ptz_position_info(self, access_point: str):
        access_point = str(access_point or "").strip()
        if not access_point:
            raise ValueError("access_point is required")
        return self._grpc_first_packet_data(
            "axxonsoft.bl.ptz.TelemetryService.GetPositionInformation",
            {"access_point": access_point},
        )

    def ptz_acquire_session(self, access_point: str):
        access_point = str(access_point or "").strip()
        if not access_point:
            raise ValueError("access_point is required")
        return self._grpc_first_packet_data(
            "axxonsoft.bl.ptz.TelemetryService.AcquireSessionId",
            {"access_point": access_point},
        )

    def ptz_keepalive(self, session_id: object, access_point: str):
        access_point = str(access_point or "").strip()
        if not access_point:
            raise ValueError("access_point is required")
        return self._grpc_first_packet_data(
            "axxonsoft.bl.ptz.TelemetryService.KeepAlive",
            {
                "session_id": session_id,
                "access_point": access_point,
            },
        )

    def ptz_release_session(self, session_id: object, access_point: str):
        access_point = str(access_point or "").strip()
        if not access_point:
            raise ValueError("access_point is required")
        return self._grpc_first_packet_data(
            "axxonsoft.bl.ptz.TelemetryService.ReleaseSessionId",
            {
                "session_id": session_id,
                "access_point": access_point,
            },
        )

    def ptz_go_preset(self, access_point: str, session_id: object, position: int, speed: int):
        access_point = str(access_point or "").strip()
        if not access_point:
            raise ValueError("access_point is required")
        return self._grpc_first_packet_data(
            "axxonsoft.bl.ptz.TelemetryService.GoPreset",
            {
                "access_point": access_point,
                "session_id": session_id,
                "position": int(position),
                "speed": int(speed),
            },
        )


def classify(items):
    buckets = {}
    for e in items:
        et = e.get("body", {}).get("event_type") or e.get("event_type") or "UNKNOWN"
        st = e.get("body", {}).get("state") or ""
        key = f"{et}:{st}" if st else et
        buckets[key] = buckets.get(key, 0) + 1
    return buckets


def _event_category(e: dict) -> str:
    return classify_raw_event_category(e)


def _first_text(*values: object, fallback: str = "") -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return fallback


def _event_camera_name(body: dict) -> str:
    origin_ext = body.get("origin_ext") or {}
    return _first_text(
        origin_ext.get("friendly_name"),
        origin_ext.get("display_name"),
        origin_ext.get("name"),
        body.get("origin_deprecated"),
        fallback="Camera",
    )


def _event_detector_name(body: dict) -> str:
    detector_ext = body.get("detector_ext") or {}
    return _first_text(
        detector_ext.get("friendly_name"),
        detector_ext.get("display_name"),
        detector_ext.get("name"),
        body.get("detector_deprecated"),
        body.get("event_type"),
        fallback="Detector",
    )


def _event_best_timestamp(body: dict, data: dict | None = None, ex: dict | None = None) -> str | None:
    data = data or {}
    ex = ex or {}
    hypotheses = data.get("Hypotheses") or []
    if hypotheses and isinstance(hypotheses[0], dict):
        value = hypotheses[0].get("TimeBest")
        if value:
            return str(value)
    if data.get("plate_appeared_time"):
        return str(data.get("plate_appeared_time"))
    ex_hypotheses = ex.get("hypotheses") or []
    if ex_hypotheses and isinstance(ex_hypotheses[0], dict):
        value = ex_hypotheses[0].get("timeBest")
        if value:
            return str(value)
    detector_ts = ((body.get("detector") or {}).get("timestamp"))
    if detector_ts:
        return str(detector_ts)
    state_ts = ((body.get("states") or [{}])[0].get("timestamp"))
    if state_ts:
        return str(state_ts)
    body_ts = body.get("timestamp")
    if body_ts:
        return str(body_ts)
    return None


def _alert_best_timestamp(body: dict) -> str | None:
    detector_body = body.get("detector") or {}
    detector_data = detector_body.get("data") or {}
    value = _event_best_timestamp(detector_body, detector_data, {})
    if value:
        return value
    state_ts = ((body.get("states") or [{}])[0].get("timestamp"))
    if state_ts:
        return str(state_ts)
    body_ts = body.get("timestamp")
    if body_ts:
        return str(body_ts)
    return None


def _extract_alert_compact(e: dict) -> dict:
    return normalize_event_card(e)


def _grpc_packets_ok(packets: list[dict]) -> bool:
    if not packets:
        return False
    for p in packets:
        if not isinstance(p, dict):
            continue
        if p.get("result") is False:
            return False
        code = str(p.get("error_code") or "").strip().upper()
        if code and code not in {"OK", "AUTHENTICATE_CODE_OK"}:
            return False
    return True


def _build_notifier_include_filters(
    *,
    event_type: str,
    subjects: list[str] | tuple[str, ...] | None = None,
    include_json: str = "",
) -> list[dict[str, str]]:
    default_event_type = str(event_type or "").strip() or "ET_DetectorEvent"
    seen: set[tuple[str, str]] = set()
    include: list[dict[str, str]] = []

    if str(include_json or "").strip():
        raw_include = json.loads(include_json)
        if not isinstance(raw_include, list):
            raise ValueError("--include-json must decode to a JSON list")
    else:
        raw_include = [
            {
                "event_type": default_event_type,
                "subject": subject,
            }
            for subject in (subjects or [])
        ] or [{"event_type": default_event_type}]

    for raw_entry in raw_include:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("Notifier include entries must be JSON objects")
        normalized_event_type = str(raw_entry.get("event_type") or default_event_type).strip() or default_event_type
        normalized_subject = str(raw_entry.get("subject") or "").strip()
        key = (normalized_event_type, normalized_subject)
        if key in seen:
            continue
        seen.add(key)
        entry = {"event_type": normalized_event_type}
        if normalized_subject:
            entry["subject"] = normalized_subject
        include.append(entry)

    return include or [{"event_type": default_event_type}]


def simplify_event_card(e: dict) -> dict:
    return normalize_event_card(e)


def _card_matches(card: dict, state: str = "", contains: str = "") -> bool:
    if state:
        if (card.get("state") or "").upper() != state.upper():
            return False
    if contains:
        hay = " ".join([
            str(card.get("event_type") or ""),
            str(card.get("camera") or ""),
            str(card.get("detector") or ""),
            str(card.get("text") or ""),
            str(card.get("plate") or ""),
        ]).lower()
        if contains.lower() not in hay:
            return False
    return True


def _event_search_rows(client: AxxonClient, request: EventSearchRequest, *, batch_size: int) -> tuple[list[dict], int, bool]:
    scanned = 0
    rows: list[dict] = []
    complete = True
    inventory_rows = client.list_cameras(view="VIEW_MODE_FULL")
    resolved_scope = resolve_scope_subjects(
        request.query.scope,
        inventory_rows,
        include_detectors=True,
    )
    subjects = resolved_scope.preferred_subjects or request.query.scope.subjects
    if not subjects:
        if request.query.scope.is_empty():
            subjects = (None,)
        else:
            return [], 0, True
    seen_ids: set[tuple[str, str]] = set()
    for subject in subjects:
        offset = 0
        while scanned < request.scan_limit:
            backend_request = build_event_search_backend_request(
                request,
                batch_size=batch_size,
                offset=offset,
                subject=subject,
            )
            items = client.read_events(
                begin=backend_request["begin"],
                end=backend_request["end"],
                subject=backend_request["subject"],
                event_type=backend_request["event_type"],
                limit=backend_request["limit"],
                offset=backend_request["offset"],
                descending=backend_request["descending"],
            )
            batch_count = len(items)
            scanned += batch_count
            for item in items:
                if all(key in item for key in ("timestamp", "camera", "event_type")):
                    card = dict(item)
                else:
                    card = simplify_event_card(item)
                row_key = (
                    str(card.get("id") or card.get("guid") or ""),
                    str(card.get("timestamp") or ""),
                )
                if row_key in seen_ids:
                    continue
                seen_ids.add(row_key)
                rows.append(card)
            if batch_count < backend_request["limit"]:
                break
            offset += batch_count
    if scanned >= request.scan_limit:
        complete = False
    return rows, scanned, complete


def _license_plate_search_rows(
    client: AxxonClient,
    request: "LicensePlateSearchRequest",
    *,
    batch_size: int,
) -> tuple[list[dict], int, bool]:
    scanned = 0
    rows: list[dict] = []
    complete = True
    inventory_rows = client.list_cameras(view="VIEW_MODE_FULL")
    resolved_scope = resolve_scope_subjects(
        request.query.scope,
        inventory_rows,
        include_detectors=True,
    )
    subjects = resolved_scope.preferred_subjects or request.query.scope.subjects
    if not subjects:
        if request.query.scope.is_empty():
            subjects = (None,)
        else:
            return [], 0, True
    seen_ids: set[tuple[str, str, str, str, str]] = set()
    for subject in subjects:
        offset = 0
        while scanned < request.scan_limit:
            backend_request = build_license_plate_search_backend_request(
                request,
                batch_size=batch_size,
                offset=offset,
                subject=subject,
            )
            items = client.read_lpr_events(
                begin=backend_request["begin"],
                end=backend_request["end"],
                subject=backend_request["subject"],
                plate=backend_request["plate"],
                search_predicate=backend_request["search_predicate"],
                limit=backend_request["limit"],
                offset=backend_request["offset"],
                descending=backend_request["descending"],
            )
            batch_count = len(items)
            scanned += batch_count
            for item in items:
                if all(key in item for key in ("timestamp", "camera", "event_type")):
                    card = dict(item)
                else:
                    card = normalize_lpr_event(item)
                row_key = (
                    str(card.get("id") or card.get("guid") or ""),
                    str(card.get("timestamp") or ""),
                    str(card.get("camera_access_point") or ""),
                    str(card.get("event_type") or ""),
                    str(card.get("plate") or ""),
                )
                if row_key in seen_ids:
                    continue
                seen_ids.add(row_key)
                rows.append(card)
            if batch_count < backend_request["limit"]:
                break
            offset += batch_count
    if scanned >= request.scan_limit:
        complete = False
    return rows, scanned, complete


def _plate_search_image_camera_access_point(
    row: Mapping[str, Any],
    request: "LicensePlateSearchRequest",
    *,
    explicit_subject: str = "",
) -> str:
    camera_access_point = str(row.get("camera_access_point") or "").strip()
    if camera_access_point:
        return camera_access_point
    scope_camera_access_points = request.query.scope.camera_access_points
    if len(scope_camera_access_points) == 1:
        return scope_camera_access_points[0]
    explicit_subject = str(explicit_subject or "").strip()
    if explicit_subject:
        return explicit_subject
    return ""


def _error_payload(section: str, ex: Exception) -> dict:
    return {
        "section": section,
        "message": str(ex),
        "status_code": getattr(ex, "code", None),
    }


def _safe_file_fragment(value: object, *, limit: int = 48) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip())
    text = text.strip("._") or "archive"
    return text[:limit]


def _macro_request_from_args(args) -> "MacroExecutionRequest":
    try:
        return build_macro_execution_request(
            macro_id=getattr(args, "macro_id", None),
            macro_name=getattr(args, "macro_name", None),
        )
    except ValueError as ex:
        raise SystemExit(str(ex)) from ex


def _macro_policy_from_args(args) -> "MacroExecutionPolicy":
    return build_macro_execution_policy(
        execution_enabled=bool(getattr(args, "execution_enabled", False)),
        admin=bool(getattr(args, "admin", False)),
        require_admin=not bool(getattr(args, "no_require_admin", False)),
        allowed_macro_ids=getattr(args, "allow_id", ()) or (),
        allowed_macro_names=getattr(args, "allow_name", ()) or (),
        allowed_mode_kinds=DEFAULT_ALLOWED_MACRO_MODE_KINDS,
        denied_action_families=DEFAULT_DENIED_MACRO_ACTION_FAMILIES,
        require_enabled=not bool(getattr(args, "allow_disabled", False)),
        require_add_to_menu=not bool(getattr(args, "allow_hidden", False)),
    )


def _ptz_request_from_args(args) -> "PtzControlRequest":
    try:
        return build_ptz_control_request(
            camera_name=getattr(args, "camera", None),
            camera_access_point=getattr(args, "camera_ap", None),
            preset_label=getattr(args, "preset", None),
            preset_position=getattr(args, "position", None),
            speed=getattr(args, "speed", DEFAULT_PTZ_CONTROL_SPEED),
        )
    except ValueError as ex:
        raise SystemExit(str(ex)) from ex


def _ptz_policy_from_args(args) -> "PtzControlPolicy":
    return build_ptz_control_policy(
        control_enabled=bool(getattr(args, "control_enabled", False)),
        admin=bool(getattr(args, "admin", False)),
        require_admin=not bool(getattr(args, "no_require_admin", False)),
        allowed_camera_access_points=getattr(args, "allow_camera_ap", ()) or (),
        allowed_camera_names=getattr(args, "allow_camera_name", ()) or (),
    )


def _admin_policy_from_args(args) -> AdminViewPolicy:
    return build_admin_view_policy(admin=bool(getattr(args, "admin", False)))


def _ptz_error_text(payload: Mapping[str, Any] | None) -> str | None:
    if not isinstance(payload, Mapping):
        return None
    error_code = str(payload.get("error_code") or "").strip()
    if error_code and error_code != "NotError":
        return error_code
    if payload.get("result") is False:
        return "result=false"
    return None


def run_ptz_execute_flow(
    client: AxxonClient,
    *,
    request: "PtzControlRequest",
    camera: "PtzCameraRecord",
    preset: "PtzPresetRecord | None",
    policy: "PtzControlPolicy",
    position_info: Mapping[str, Any] | None = None,
    presets: list["PtzPresetRecord"] | None = None,
    preview_error: str | None = None,
    log_file: str | None = None,
) -> dict[str, Any]:
    decision = evaluate_ptz_control_guardrails(
        request,
        camera,
        preset,
        policy,
        position_info=position_info,
        preview_error=preview_error,
    )
    execute_result: dict[str, Any] | None = None
    execute_error: str | None = None
    attempted = False
    ok = False

    if decision.allowed and preset is not None:
        attempted = True
        log_line(
            log_file,
            (
                "ptz_execute attempt "
                f"camera_ap={camera.camera_access_point} camera={camera.camera_name} "
                f"preset_position={preset.position} preset_label={preset.label} transport=grpc"
            ),
        )
        session = None
        command = None
        release = None
        release_error = None
        session_id = None
        try:
            session = client.ptz_acquire_session(camera.camera_access_point)
            session_error = _ptz_error_text(session)
            if session_error:
                raise RuntimeError(f"AcquireSessionId failed: {session_error}")
            session_id = session.get("session_id") if isinstance(session, Mapping) else None
            if session_id in (None, ""):
                raise RuntimeError("AcquireSessionId returned no session_id")
            backend_request = build_ptz_goto_preset_backend_request(
                request,
                camera,
                preset,
                session_id=session_id,
            )
            command = client.ptz_go_preset(**backend_request)
            command_error = _ptz_error_text(command)
            if command_error:
                raise RuntimeError(f"GoPreset failed: {command_error}")
            ok = True
        except Exception as ex:
            execute_error = str(ex)
        finally:
            if session_id not in (None, ""):
                try:
                    release = client.ptz_release_session(session_id, camera.camera_access_point)
                except Exception as ex:
                    release_error = str(ex)
                    ok = False
            execute_result = {
                "session": session,
                "command": command,
                "release": release,
                "release_error": release_error,
            }
        if ok:
            log_line(
                log_file,
                (
                    "ptz_execute success "
                    f"camera_ap={camera.camera_access_point} camera={camera.camera_name} "
                    f"preset_position={preset.position} preset_label={preset.label}"
                ),
            )
        else:
            error_text = execute_error or (f"ReleaseSessionId failed: {release_error}" if release_error else "unknown")
            log_line(
                log_file,
                (
                    "ptz_execute failure "
                    f"camera_ap={camera.camera_access_point} camera={camera.camera_name} "
                    f"preset_position={(preset.position if preset else None)} "
                    f"preset_label={(preset.label if preset else None)} error={error_text}"
                ),
            )

    return shape_ptz_control_result(
        request,
        camera,
        decision,
        policy=policy,
        position_info=position_info,
        presets=presets or [],
        preset=preset,
        preview_error=preview_error,
        attempted=attempted,
        ok=ok,
        transport="grpc" if attempted else None,
        response=execute_result,
        error=execute_error,
    )


def _detector_inventory_rows(cameras: list[dict]) -> list[dict]:
    rows = []
    for cam in cameras:
        camera_access_point = cam.get("access_point", "")
        camera_name = friendly_label(cam.get("display_name"), cam.get("display_id"), camera_access_point)
        for detector in cam.get("detectors", []) or []:
            rows.append({
                "camera_access_point": camera_access_point,
                "camera_name": camera_name,
                "camera_display_id": cam.get("display_id", ""),
                "detector_name": friendly_label(
                    detector.get("display_name"),
                    detector.get("display_id"),
                    detector.get("access_point", ""),
                ),
                "detector_display_id": detector.get("display_id", ""),
                "detector_access_point": detector.get("access_point", ""),
                "parent_detector": detector.get("parent_detector", ""),
                "detector_type": detector.get("type", ""),
                "detector_type_name": detector.get("type_name", ""),
                "is_activated": detector.get("is_activated", False),
                "events": [event.get("id") for event in (detector.get("events", []) or [])],
            })
    return rows


def build_dashboard(items: list[dict]) -> dict:
    by_cat = {"lpr": 0, "motion": 0, "traffic": 0, "meta": 0, "other": 0}
    for e in items:
        by_cat[_event_category(e)] += 1

    cards = [simplify_event_card(x) for x in items[:5]]
    return {
        "total": len(items),
        "by_category": by_cat,
        "quick_menu": [
            {"id": "cam:list", "title": "📷 Cameras"},
            {"id": "ev:feed", "title": "🚨 Events"},
            {"id": "lpr:search", "title": "🔎 LPR"},
            {"id": "archive:quick", "title": "🎬 Archive"},
            {"id": "sys:health", "title": "🛠 Status"},
        ],
        "recent_cards": cards,
    }


def _vehicle_class_to_name(val):
    m = {
        0: "Unknown",
        1: "Car",
        2: "Truck",
        3: "Bus",
        4: "Motorcycle",
        5: "Bicycle",
    }
    if isinstance(val, str):
        return val
    return m.get(val, str(val) if val is not None else None)


def _plate_crop_from_event(e: dict):
    data = (e.get("body", {}) or {}).get("data", {}) or {}
    # listed_lpr_detected shape (x1,y1,x2,y2)
    pr = data.get("PlateRectangle")
    if isinstance(pr, list) and len(pr) >= 4:
        x1, y1, x2, y2 = map(float, pr[:4])
        return {"x": x1, "y": y1, "w": max(0.0, x2 - x1), "h": max(0.0, y2 - y1)}

    # plateRecognized shape in hypotheses (x1,y1,x2,y2)
    hy = data.get("Hypotheses") or []
    if hy and isinstance(hy[0], dict):
        r = hy[0].get("PlateRectangle")
        if isinstance(r, list) and len(r) >= 4:
            x1, y1, x2, y2 = map(float, r[:4])
            return {"x": x1, "y": y1, "w": max(0.0, x2 - x1), "h": max(0.0, y2 - y1)}

    # fallback to auto_recognition_result_ex plateRectangle (x,y,w,h)
    auto_ex = data.get("auto_recognition_result_ex")
    if isinstance(auto_ex, str) and auto_ex.strip().startswith("{"):
        try:
            ex = json.loads(auto_ex)
            hy2 = ex.get("hypotheses") or []
            if hy2 and isinstance(hy2[0], dict):
                rr = hy2[0].get("plateRectangle") or {}
                if isinstance(rr, dict):
                    return {
                        "x": float(rr.get("x", 0)),
                        "y": float(rr.get("y", 0)),
                        "w": float(rr.get("w", 0)),
                        "h": float(rr.get("h", 0)),
                    }
        except json.JSONDecodeError:
            pass

    return None


def _mask_match(text: str, mask: str) -> bool:
    if not mask:
        return True
    # * wildcard, case-insensitive
    rx = "^" + re.escape(mask).replace("\\*", ".*") + "$"
    return re.match(rx, text or "", flags=re.IGNORECASE) is not None


def _plate_best_timestamp(body: dict, data: dict, ex: dict):
    # Prefer detector-provided best frame timestamps for LPR crop accuracy.
    # Fall back to the shared event timestamp chooser so states/detector/body stay aligned.
    return _event_best_timestamp(body, data, ex)


def _plate_confidence(data: dict, ex: dict):
    hypotheses = data.get("Hypotheses") or ex.get("hypotheses") or []
    if hypotheses and isinstance(hypotheses[0], dict):
        raw_value = (
            hypotheses[0].get("ocrQuality")
            if hypotheses[0].get("ocrQuality") is not None
            else hypotheses[0].get("ocr_quality")
        )
        try:
            confidence = float(raw_value)
        except (TypeError, ValueError):
            return None
        if confidence <= 1.0:
            confidence *= 100.0
        return round(confidence, 2)
    return None


def normalize_lpr_event(e: dict):
    body = e.get("body", {})
    data = body.get("data", {}) or {}
    auto_ex = data.get("auto_recognition_result_ex")
    ex = {}
    if isinstance(auto_ex, str) and auto_ex.strip().startswith("{"):
        try:
            ex = json.loads(auto_ex)
        except json.JSONDecodeError:
            ex = {}

    hypotheses = data.get("Hypotheses") or ex.get("hypotheses") or []
    plate = data.get("plate")
    if not plate and hypotheses and isinstance(hypotheses[0], dict):
        plate = hypotheses[0].get("PlateFull") or hypotheses[0].get("plateFull")

    brand = data.get("VehicleBrand")
    model = data.get("VehicleModel")
    color = data.get("VehicleColor")
    vclass = _vehicle_class_to_name(data.get("VehicleClass"))

    if ex:
        brand = brand or ((ex.get("vehicleBrand") or {}).get("value"))
        model = model or ((ex.get("vehicleModel") or {}).get("value"))
        color = color or ((ex.get("vehicleColor") or {}).get("value"))
        vclass = vclass or ((ex.get("vehicleClass") or {}).get("value"))

    listed_lpr_list = data.get("list_name")
    if listed_lpr_list == "":
        listed_lpr_list = None

    best_ts = _plate_best_timestamp(body, data, ex)
    out = normalize_event_card(e)
    out.update({
        "best_frame_timestamp": best_ts,
        "plate": plate,
        "confidence": _plate_confidence(data, ex),
        "detector.listedFace.list": None,
        "detector.listedLpr.list": listed_lpr_list,
        "detector.lpr.vehicle.brand": brand,
        "detector.lpr.vehicle.class": vclass,
        "detector.lpr.vehicle.color": color,
        "detector.lpr.vehicle.model": model,
        "detector.lpr.vehicle.speed": None,
        "plate_crop": _plate_crop_from_event(e),
        "raw_event": e,
    })
    vehicle = out.get("vehicle") if isinstance(out.get("vehicle"), dict) else {}
    if vehicle:
        if vehicle.get("brand") is None:
            vehicle["brand"] = brand
        if vehicle.get("model") is None:
            vehicle["model"] = model
        if vehicle.get("color") is None:
            vehicle["color"] = color
        out["vehicle"] = vehicle
    elif any(value for value in (brand, model, color)):
        out["vehicle"] = {"brand": brand, "model": model, "color": color}
    return out


def draw_boxes_ffmpeg(src: Path, dst: Path, event_obj: dict):
    wh = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(src)
    ]).decode().strip()
    w, h = map(int, wh.split("x"))

    rects = []
    for candidate in extract_raw_rectangle_candidates(event_obj):
        px = rectangle_candidate_to_pixel_crop(candidate, w, h)
        if px:
            rects.append(px)

    if not rects:
        dst.write_bytes(src.read_bytes())
        return 0

    parts = []
    for X, Y, WW, HH in rects:
        parts.append(f"drawbox=x={X}:y={Y}:w={WW}:h={HH}:color=red@1:t=4")

    vf = ",".join(parts)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-frames:v", "1", str(dst)])
    return len(rects)


def main():
    cfg = load_axxon_config()
    secure_cfg = load_secure_profile_config()
    bot_cfg = load_tg_bot_config()
    p = argparse.ArgumentParser(description="Axxon One Web /grpc helper")
    p.add_argument("--host", default=cfg.host)
    p.add_argument("--user", default=cfg.user)
    p.add_argument("--password", default=cfg.password)
    p.add_argument("--port", type=int, default=cfg.port)
    p.add_argument("--log-file", default=cfg.log_file)

    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("list-cameras")
    pc.add_argument("--view", default=None)
    pc.add_argument("--filter-prefix", default=None)

    ps = sub.add_parser("session-init")
    ps.add_argument("--profile", default="/tmp/axxon_profile.json")
    ps.add_argument("--profile-scope", choices=["user", "server"], default="server")
    ps.add_argument("--profile-id", default=secure_cfg.profile_name)

    pg = sub.add_parser("session-get")
    pg.add_argument("--profile-scope", choices=["user", "server"], default="server")
    pg.add_argument("--profile-id", default=secure_cfg.profile_name)

    pi = sub.add_parser("inventory-refresh")
    pi.add_argument("--out", default="/tmp/axxon_inventory.json")

    pd = sub.add_parser("list-detectors")
    pd.add_argument("--camera", help="camera access_point")
    pd.add_argument("--contains", help="substring in detector display_name")

    pe = sub.add_parser("events")
    pe.add_argument("--seconds", type=int, default=120)
    pe.add_argument("--subject")
    pe.add_argument("--event-type", default="ET_DetectorEvent")
    pe.add_argument("--values")
    pe.add_argument("--limit", type=int, default=100)
    pe.add_argument("--state")
    pe.add_argument("--contains")
    pe.add_argument("--classify", action="store_true")

    pp = sub.add_parser("plate-search")
    pp.add_argument("--seconds", type=int, default=DEFAULT_LICENSE_PLATE_SEARCH_WINDOW_SEC)
    pp.add_argument("--begin", help="UTC start YYYYMMDDTHHMMSS(.ffffff)")
    pp.add_argument("--end", help="UTC end YYYYMMDDTHHMMSS(.ffffff)")
    pp.add_argument("--page", type=int, default=1)
    pp.add_argument("--page-size", type=int, default=DEFAULT_LICENSE_PLATE_SEARCH_PAGE_SIZE)
    pp.add_argument("--scan-limit", type=int, default=DEFAULT_LICENSE_PLATE_SEARCH_SCAN_LIMIT)
    pp.add_argument("--limit", type=int, default=0, help="legacy alias for scan-limit")
    pp.add_argument("--scope-host", action="append", default=[])
    pp.add_argument("--domain", action="append", default=[])
    pp.add_argument("--camera", action="append", default=[])
    pp.add_argument("--camera-ap", action="append", default=[])
    pp.add_argument("--detector", action="append", default=[])
    pp.add_argument("--detector-ap", action="append", default=[])
    pp.add_argument("--subject", default="")
    pp.add_argument("--plate", default="", help="exact plate match")
    pp.add_argument("--contains", default="", help="substring plate match")
    pp.add_argument("--mask", default="", help="wildcard mask with *")
    pp.add_argument("--ascending", action="store_true")
    pp.add_argument("--with-images", action="store_true")
    pp.add_argument("--images-dir", default="/tmp/axxon_plate_search")
    pp.add_argument("--max-images", type=int, default=20)
    pp.add_argument("--thumb-threshold", type=int, default=10, help="use thumbnail size for full_frame when matches exceed this count")
    pp.add_argument("--thumb-w", type=int, default=320)
    pp.add_argument("--thumb-h", type=int, default=240)
    pp.add_argument("--cleanup-after", action="store_true", help="remove generated images after JSON is written")

    pface = sub.add_parser("face-search")
    pface.add_argument("--image", required=True, help="path to a JPEG reference image")
    pface.add_argument("--seconds", type=int, default=DEFAULT_FACE_SEARCH_WINDOW_SEC)
    pface.add_argument("--begin", help="UTC start YYYYMMDDTHHMMSS(.ffffff)")
    pface.add_argument("--end", help="UTC end YYYYMMDDTHHMMSS(.ffffff)")
    pface.add_argument("--page", type=int, default=1)
    pface.add_argument("--page-size", type=int, default=DEFAULT_FACE_SEARCH_PAGE_SIZE)
    pface.add_argument("--scan-limit", type=int, default=DEFAULT_FACE_SEARCH_SCAN_LIMIT)
    pface.add_argument("--scope-host", action="append", default=[])
    pface.add_argument("--domain", action="append", default=[])
    pface.add_argument("--camera", action="append", default=[])
    pface.add_argument("--camera-ap", action="append", default=[])
    pface.add_argument("--detector", action="append", default=[])
    pface.add_argument("--detector-ap", action="append", default=[])
    pface.add_argument("--accuracy", type=float, default=DEFAULT_FACE_SEARCH_ACCURACY)
    pface.add_argument("--max-cameras", type=int, default=DEFAULT_FACE_SEARCH_MAX_CAMERAS)

    pl = sub.add_parser("latest-event")
    pl.add_argument("--seconds", type=int, default=600)
    pl.add_argument("--subject", required=True)
    pl.add_argument("--values", default="moveInZone")
    pl.add_argument("--state", required=True)
    pl.add_argument("--contains", required=True)
    pl.add_argument("--out", required=True)

    pf = sub.add_parser("frame-from-event")
    pf.add_argument("--video-id", required=False)
    pf.add_argument("--event-json", required=True)
    pf.add_argument("--out", required=True)
    pf.add_argument("--mode", choices=["media", "export"], default="media")
    pf.add_argument("--threshold-ms", type=int, default=1000)
    pf.add_argument("--w", type=int, default=0)
    pf.add_argument("--h", type=int, default=0)

    pb = sub.add_parser("box-from-event")
    pb.add_argument("--event-json", required=True)
    pb.add_argument("--image", required=True)
    pb.add_argument("--out", required=True)

    pclip = sub.add_parser("clip-from-event")
    pclip.add_argument("--event-json", required=True)
    pclip.add_argument("--out", required=True)
    pclip.add_argument("--pre", type=int, default=15)
    pclip.add_argument("--post", type=int, default=15)

    pls = sub.add_parser("live-snapshot")
    pls.add_argument("--video-id", required=True)
    pls.add_argument("--out", required=True)
    pls.add_argument("--w", type=int, default=0)
    pls.add_argument("--h", type=int, default=0)

    pcu = sub.add_parser("cleanup")
    pcu.add_argument("--path", default="/tmp/axxon_plate_search")
    pcu.add_argument("--patterns", default="*.jpg,*.json")
    pcu.add_argument("--older-min", type=int, default=0)
    pcu.add_argument("--truncate-log", action="store_true")

    pds = sub.add_parser("dashboard")
    pds.add_argument("--seconds", type=int, default=3600)
    pds.add_argument("--subject")
    pds.add_argument("--limit", type=int, default=200)

    ptc = sub.add_parser("telegram-cards")
    ptc.add_argument("--seconds", type=int, default=1800)
    ptc.add_argument("--subject")
    ptc.add_argument("--event-type", default="ET_DetectorEvent")
    ptc.add_argument("--values")
    ptc.add_argument("--limit", type=int, default=20)
    ptc.add_argument("--state")
    ptc.add_argument("--contains")

    pse = sub.add_parser("search-events")
    pse.add_argument("--begin", required=True)
    pse.add_argument("--end", required=True)
    pse.add_argument("--scope-host", action="append", default=[])
    pse.add_argument("--domain", action="append", default=[])
    pse.add_argument("--camera", action="append", default=[])
    pse.add_argument("--camera-ap", action="append", default=[])
    pse.add_argument("--detector", action="append", default=[])
    pse.add_argument("--detector-ap", action="append", default=[])
    pse.add_argument("--category", action="append", default=[])
    pse.add_argument("--event-type", action="append", default=[])
    pse.add_argument("--state", action="append", default=[])
    pse.add_argument("--severity", action="append", default=[])
    pse.add_argument("--priority", action="append", default=[])
    pse.add_argument("--contains", default="")
    pse.add_argument("--mask", default="")
    pse.add_argument("--mode", choices=["summary", "list"], default="summary")
    pse.add_argument("--page", type=int, default=1)
    pse.add_argument("--page-size", type=int, default=5)
    pse.add_argument("--scan-limit", type=int, default=1200)
    pse.add_argument("--ascending", action="store_true")

    pad = sub.add_parser("archive-depth")
    pad.add_argument("--camera-ap", required=True)

    paj = sub.add_parser("archive-jump")
    paj.add_argument("--begin", required=True)
    paj.add_argument("--end", required=True)
    paj.add_argument("--at")
    paj.add_argument("--scope-host", action="append", default=[])
    paj.add_argument("--domain", action="append", default=[])
    paj.add_argument("--camera", action="append", default=[])
    paj.add_argument("--camera-ap", action="append", default=[])
    paj.add_argument("--detector", action="append", default=[])
    paj.add_argument("--detector-ap", action="append", default=[])
    paj.add_argument("--category", action="append", default=[])
    paj.add_argument("--event-type", action="append", default=[])
    paj.add_argument("--state", action="append", default=[])
    paj.add_argument("--severity", action="append", default=[])
    paj.add_argument("--priority", action="append", default=[])
    paj.add_argument("--contains", default="")
    paj.add_argument("--mask", default="")
    paj.add_argument("--scan-limit", type=int, default=DEFAULT_ARCHIVE_SCAN_LIMIT)
    paj.add_argument("--preview-width", type=int, default=DEFAULT_ARCHIVE_PREVIEW_WIDTH)
    paj.add_argument("--preview-height", type=int, default=DEFAULT_ARCHIVE_PREVIEW_HEIGHT)
    paj.add_argument("--preview-threshold-ms", type=int, default=DEFAULT_ARCHIVE_PREVIEW_THRESHOLD_MS)
    paj.add_argument("--context-window-sec", type=int, default=DEFAULT_ARCHIVE_CONTEXT_WINDOW_SEC)
    paj.add_argument("--out", default="")
    paj.add_argument("--ascending", action="store_true")

    pmce = sub.add_parser("multi-camera-export-plan")
    pmce.add_argument("--begin")
    pmce.add_argument("--end")
    pmce.add_argument("--at")
    pmce.add_argument("--camera", action="append", default=[])
    pmce.add_argument("--camera-ap", action="append", default=[])
    pmce.add_argument("--waittimeout-ms", type=int, default=DEFAULT_MULTI_CAMERA_EXPORT_WAIT_TIMEOUT_MS)
    pmce.add_argument("--archive", default="")
    pmce.add_argument("--max-cameras", type=int, default=DEFAULT_MULTI_CAMERA_EXPORT_MAX_CAMERAS)

    pce = sub.add_parser("single-camera-export")
    pce.add_argument("--begin", required=True)
    pce.add_argument("--end", required=True)
    pce.add_argument("--camera", action="append", default=[])
    pce.add_argument("--camera-ap", action="append", default=[])
    pce.add_argument("--waittimeout-ms", type=int, default=DEFAULT_SINGLE_CAMERA_EXPORT_WAIT_TIMEOUT_MS)
    pce.add_argument("--archive", default="")
    pce.add_argument("--out", default="")

    pmp = sub.add_parser("macro-preview")
    pmp.add_argument("--macro-id")
    pmp.add_argument("--macro-name")
    pmp.add_argument("--allow-id", action="append", default=[])
    pmp.add_argument("--allow-name", action="append", default=[])
    pmp.add_argument("--execution-enabled", action="store_true")
    pmp.add_argument("--admin", action="store_true")
    pmp.add_argument("--no-require-admin", action="store_true")
    pmp.add_argument("--allow-disabled", action="store_true")
    pmp.add_argument("--allow-hidden", action="store_true")

    pme = sub.add_parser("macro-execute")
    pme.add_argument("--macro-id")
    pme.add_argument("--macro-name")
    pme.add_argument("--allow-id", action="append", default=[])
    pme.add_argument("--allow-name", action="append", default=[])
    pme.add_argument("--execution-enabled", action="store_true")
    pme.add_argument("--admin", action="store_true")
    pme.add_argument("--no-require-admin", action="store_true")
    pme.add_argument("--allow-disabled", action="store_true")
    pme.add_argument("--allow-hidden", action="store_true")

    ppp = sub.add_parser("ptz-preview")
    ppp.add_argument("--camera")
    ppp.add_argument("--camera-ap")
    ppp.add_argument("--preset")
    ppp.add_argument("--position", type=int)
    ppp.add_argument("--speed", type=int, default=DEFAULT_PTZ_CONTROL_SPEED)
    ppp.add_argument("--allow-camera-ap", action="append", default=[])
    ppp.add_argument("--allow-camera-name", action="append", default=[])
    ppp.add_argument("--control-enabled", action="store_true")
    ppp.add_argument("--admin", action="store_true")
    ppp.add_argument("--no-require-admin", action="store_true")

    ppe = sub.add_parser("ptz-execute")
    ppe.add_argument("--camera")
    ppe.add_argument("--camera-ap")
    ppe.add_argument("--preset")
    ppe.add_argument("--position", type=int)
    ppe.add_argument("--speed", type=int, default=DEFAULT_PTZ_CONTROL_SPEED)
    ppe.add_argument("--allow-camera-ap", action="append", default=[])
    ppe.add_argument("--allow-camera-name", action="append", default=[])
    ppe.add_argument("--control-enabled", action="store_true")
    ppe.add_argument("--admin", action="store_true")
    ppe.add_argument("--no-require-admin", action="store_true")

    pnp = sub.add_parser("notifier-pull")
    pnp.add_argument("--subscription-id", required=True)
    pnp.add_argument("--event-type", default="ET_DetectorEvent")
    pnp.add_argument("--subject", action="append", default=[])
    pnp.add_argument("--state")
    pnp.add_argument("--contains")
    pnp.add_argument("--timeout-sec", type=int, default=25)

    pnd = sub.add_parser("notifier-disconnect")
    pnd.add_argument("--subscription-id", required=True)

    par = sub.add_parser("alert-review")
    par.add_argument("--camera-ap", required=True)
    par.add_argument("--alert-id", required=True)
    par.add_argument("--severity", choices=["SV_UNCLASSIFIED", "SV_FALSE", "SV_WARNING", "SV_ALARM"], required=True)

    psu = sub.add_parser("server-usage")
    psu.add_argument("--domain", action="store_true")

    psv = sub.add_parser("server-version")

    pss = sub.add_parser("server-statistics")

    psi = sub.add_parser("server-info")
    psi.add_argument("--domain", action="store_true")

    pav = sub.add_parser("admin-view")
    pav.add_argument("--admin", action="store_true")

    args = p.parse_args()

    secure_store = SecureProfileStore(
        enabled=secure_cfg.enabled,
        storage_dir=secure_cfg.storage_dir,
        master_key=secure_cfg.master_key,
    )

    if args.cmd == "session-init":
        if not (args.host and args.user and args.password):
            raise SystemExit("session-init requires --host --user --password (or env AXXON_HOST/AXXON_USER/AXXON_PASS)")
        profile = {
            "host": args.host,
            "port": args.port,
            "user": args.user,
            "password": args.password,
            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        if secure_store.enabled:
            try:
                path = secure_store.save_profile(args.profile_scope, args.profile_id, profile)
            except RuntimeError as ex:
                raise SystemExit(str(ex))
            print(json.dumps({
                "secure_profile_path": path,
                "profile_scope": args.profile_scope,
                "profile_id": args.profile_id,
            }, ensure_ascii=False))
            return

        Path(args.profile).write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        print(args.profile)
        return

    if args.cmd == "session-get":
        if not secure_store.enabled:
            raise SystemExit("Secure profile storage is disabled (set AXXON_SECURE_PROFILE_ENABLED=1)")
        try:
            profile = secure_store.load_profile(args.profile_scope, args.profile_id)
        except RuntimeError as ex:
            raise SystemExit(str(ex))
        if not profile:
            raise SystemExit("Secure profile not found")
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        return

    if args.cmd == "cleanup":
        base = Path(args.path)
        removed = []
        now = time.time()
        pats = [x.strip() for x in args.patterns.split(",") if x.strip()]
        if base.exists():
            for pat in pats:
                for f in base.rglob(pat):
                    try:
                        if args.older_min > 0:
                            age_min = (now - f.stat().st_mtime) / 60.0
                            if age_min < args.older_min:
                                continue
                        f.unlink(missing_ok=True)
                        removed.append(str(f))
                    except Exception:
                        pass
        if args.truncate_log and args.log_file:
            Path(args.log_file).write_text("", encoding="utf-8")
        print(json.dumps({"removed": len(removed), "path": args.path, "log_truncated": bool(args.truncate_log)}, ensure_ascii=False))
        return

    if not (args.host and args.user and args.password):
        raise SystemExit("Missing connection params. Set --host/--user/--password or env AXXON_HOST/AXXON_USER/AXXON_PASS")

    c = AxxonClient(args.host, args.user, args.password, args.port)
    log_line(args.log_file, f"cmd={args.cmd} host={args.host}:{args.port}")

    if args.cmd == "list-cameras":
        cams = c.list_cameras(view=args.view, filter_prefix=args.filter_prefix)
        print(json.dumps(cams, ensure_ascii=False, indent=2))
        return

    if args.cmd == "inventory-refresh":
        cams = c.list_cameras(view="VIEW_MODE_FULL")
        rows = []
        for cam in cams:
            rows.append({
                "camera_access_point": cam.get("access_point"),
                "camera_name": friendly_label(cam.get("display_name"), cam.get("display_id"), cam.get("access_point")),
                "camera_display_id": cam.get("display_id"),
                "detectors": [
                    {
                        "name": friendly_label(d.get("display_name"), d.get("display_id"), d.get("access_point")),
                        "display_id": d.get("display_id"),
                        "access_point": d.get("access_point"),
                        "parent_detector": d.get("parent_detector"),
                        "type": d.get("type"),
                        "type_name": d.get("type_name"),
                        "events": [e.get("id") for e in (d.get("events", []) or [])],
                    }
                    for d in (cam.get("detectors") or [])
                ],
            })
        payload = {
            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "host": args.host,
            "port": args.port,
            "items": rows,
        }
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(args.out)
        return

    if args.cmd == "list-detectors":
        cams = c.list_cameras(view="VIEW_MODE_FULL")
        rows = []
        for row in _detector_inventory_rows(cams):
            if args.camera and row.get("camera_access_point") != args.camera:
                continue
            if args.contains and args.contains.lower() not in str(row.get("detector_name") or "").lower():
                continue
            rows.append(row)
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    if args.cmd == "events":
        end = utc_now()
        begin = end - dt.timedelta(seconds=args.seconds)
        items = c.read_events(
            begin=ts_compact(begin),
            end=ts_compact(end),
            subject=args.subject,
            event_type=args.event_type,
            values=args.values,
            limit=args.limit,
            descending=True,
        )
        if args.state:
            items = [e for e in items if (e.get("body", {}).get("state") == args.state)]
        if args.contains:
            items = [e for e in items if args.contains in ((e.get("localization", {}) or {}).get("text", ""))]
        if args.classify:
            print(json.dumps(classify(items), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(items, ensure_ascii=False, indent=2))
        return

    if args.cmd == "dashboard":
        end = utc_now()
        begin = end - dt.timedelta(seconds=args.seconds)
        items = c.read_events(
            begin=ts_compact(begin),
            end=ts_compact(end),
            subject=args.subject,
            event_type="ET_DetectorEvent",
            values=None,
            limit=args.limit,
            descending=True,
        )
        print(json.dumps(build_dashboard(items), ensure_ascii=False, indent=2))
        return

    if args.cmd == "telegram-cards":
        end = utc_now()
        begin = end - dt.timedelta(seconds=args.seconds)
        items = c.read_events(
            begin=ts_compact(begin),
            end=ts_compact(end),
            subject=args.subject,
            event_type=args.event_type,
            values=args.values,
            limit=args.limit,
            descending=True,
        )
        cards = [simplify_event_card(e) for e in items]
        if args.state or args.contains:
            cards = [x for x in cards if _card_matches(x, state=(args.state or ""), contains=(args.contains or ""))]
        print(json.dumps(cards, ensure_ascii=False, indent=2))
        return

    if args.cmd == "search-events":
        request = build_event_search_request(
            begin=args.begin,
            end=args.end,
            hosts=args.scope_host,
            domains=args.domain,
            camera_names=args.camera,
            camera_access_points=args.camera_ap,
            detector_names=args.detector,
            detector_access_points=args.detector_ap,
            categories=args.category,
            event_types=args.event_type,
            states=args.state,
            severities=args.severity,
            priorities=args.priority,
            contains=args.contains,
            mask=args.mask,
            mode=args.mode,
            page=args.page,
            page_size=args.page_size,
            scan_limit=args.scan_limit,
            descending=not args.ascending,
        )
        batch_size = min(200, max(100, request.page_size * 6))
        rows, scanned, complete = _event_search_rows(c, request, batch_size=batch_size)
        result = shape_event_search_results(
            rows,
            request,
            scanned_count=scanned,
            complete=complete,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "face-search":
        try:
            request = build_face_search_request(
                begin=args.begin,
                end=args.end,
                last_sec=args.seconds,
                accuracy=args.accuracy,
                hosts=args.scope_host,
                domains=args.domain,
                camera_names=args.camera,
                camera_access_points=args.camera_ap,
                detector_names=args.detector,
                detector_access_points=args.detector_ap,
                page=args.page,
                page_size=args.page_size,
                scan_limit=args.scan_limit,
            )
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        detector_rows = _detector_inventory_rows(c.list_cameras(view="VIEW_MODE_FULL"))
        selection = resolve_face_search_selection(
            request,
            detector_rows,
            max_cameras=args.max_cameras,
        )

        reference_image = None
        load_error = None
        try:
            reference_image = load_face_search_reference_image(args.image)
        except ValueError as ex:
            load_error = str(ex)

        if reference_image is None or not selection.searchable:
            result = shape_face_search_results(
                [],
                request,
                selection,
                reference_image,
                scanned_count=0,
                complete=True,
                error=load_error,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        backend_request = build_face_search_backend_request(request, selection, reference_image)
        search_result = c.find_similar_objects(
            begin=backend_request["range"]["begin_time"],
            end=backend_request["range"]["end_time"],
            origin_ids=backend_request["origin_ids"],
            jpeg_image=backend_request["jpeg_image"],
            minimal_score=backend_request["minimal_score"],
            limit=backend_request["limit"],
            offset=backend_request["offset"],
            is_face=backend_request["is_face"],
        )
        result = shape_face_search_results(
            search_result["items"],
            request,
            selection,
            reference_image,
            scanned_count=len(search_result["items"]),
            complete=bool(search_result.get("complete")),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "archive-depth":
        video_id = normalize_video_id(args.camera_ap)
        try:
            depth_payload = c.archive_depth(video_id)
        except Exception as ex:
            raise SystemExit(str(ex)) from ex
        print(json.dumps(depth_payload if isinstance(depth_payload, dict) else {}, ensure_ascii=False, indent=2))
        return

    if args.cmd == "archive-jump":
        try:
            request = build_archive_jump_request(
                begin=args.begin,
                end=args.end,
                at=args.at,
                hosts=args.scope_host,
                domains=args.domain,
                camera_names=args.camera,
                camera_access_points=args.camera_ap,
                detector_names=args.detector,
                detector_access_points=args.detector_ap,
                categories=args.category,
                event_types=args.event_type,
                states=args.state,
                severities=args.severity,
                priorities=args.priority,
                contains=args.contains,
                mask=args.mask,
                scan_limit=args.scan_limit,
                preview_width=args.preview_width,
                preview_height=args.preview_height,
                preview_threshold_ms=args.preview_threshold_ms,
                context_window_sec=args.context_window_sec,
                descending=not args.ascending,
            )
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        search_request = EventSearchRequest(
            query=request.query,
            mode="list",
            page=1,
            page_size=1,
            scan_limit=request.scan_limit,
        )
        rows, _scanned, _complete = _event_search_rows(
            c,
            search_request,
            batch_size=min(200, max(100, request.scan_limit)),
        )
        camera_rows = normalize_camera_rows(c.list_cameras(view="VIEW_MODE_FULL"))
        try:
            selection = derive_archive_jump_selection(request, rows, camera_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        video_id = normalize_video_id(selection.camera_access_point)
        metadata_errors: list[dict] = []
        archives_payload: dict = {"archives": []}
        depth_payload: dict | None = None
        intervals_payload: dict = {"intervals": [], "more": False}

        try:
            archives_payload = c.archive_list(video_id)
        except Exception as ex:
            metadata_errors.append(_error_payload("archive_list", ex))

        try:
            depth_payload = c.archive_depth(video_id)
        except Exception as ex:
            metadata_errors.append(_error_payload("archive_depth", ex))

        try:
            intervals_payload = c.archive_intervals(
                video_id,
                end=selection.context_end,
                begin=selection.context_begin,
                limit=5,
            )
        except Exception as ex:
            metadata_errors.append(_error_payload("archive_intervals", ex))

        interval_rows = ((intervals_payload or {}) if isinstance(intervals_payload, dict) else {}).get("intervals") or []
        effective_ts = selection.target_timestamp
        target_dt = ts_parse(selection.target_timestamp)
        nearest_dt = None
        for row in interval_rows:
            if not isinstance(row, Mapping):
                continue
            begin_raw = row.get("begin")
            end_raw = row.get("end")
            try:
                begin_dt = ts_parse(begin_raw)
                end_dt = ts_parse(end_raw)
            except Exception:
                continue
            if begin_dt <= target_dt <= end_dt:
                nearest_dt = target_dt
                break
            candidates = [begin_dt, end_dt]
            best_local = min(candidates, key=lambda value: abs((value - target_dt).total_seconds()))
            if nearest_dt is None or abs((best_local - target_dt).total_seconds()) < abs((nearest_dt - target_dt).total_seconds()):
                nearest_dt = best_local
        if nearest_dt is None and isinstance(depth_payload, Mapping):
            try:
                depth_start = ts_parse(depth_payload.get("start"))
                depth_end = ts_parse(depth_payload.get("end"))
                if target_dt < depth_start:
                    nearest_dt = depth_start
                elif target_dt > depth_end:
                    nearest_dt = depth_end
            except Exception:
                pass
        if nearest_dt is not None:
            effective_ts = ts_compact(nearest_dt)

        preview_path = None
        preview_error = None
        preview_mode = ""
        out_path = Path(args.out) if args.out else Path(
            f"/tmp/axxon_tg_archive_jump_{_safe_file_fragment(selection.camera)}_{_safe_file_fragment(effective_ts)}.jpg"
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            preview_path = c.media_frame(
                video_id,
                effective_ts,
                out_path,
                threshold_ms=request.preview_threshold_ms,
                width=request.preview_width,
                height=request.preview_height,
            )
            preview_mode = "media"
        except Exception as media_ex:
            try:
                preview_path = c.export_frame(video_id, effective_ts, out_path)
                preview_mode = "export"
            except Exception as export_ex:
                preview_error = f"media: {media_ex}; export: {export_ex}"

        result = shape_archive_jump_result(
            request,
            selection,
            preview_path=preview_path,
            preview_error=preview_error,
            preview_mode=preview_mode,
            archives=((archives_payload or {}) if isinstance(archives_payload, dict) else {}).get("archives") or [],
            depth=depth_payload if isinstance(depth_payload, dict) else None,
            intervals=((intervals_payload or {}) if isinstance(intervals_payload, dict) else {}).get("intervals") or [],
            intervals_more=bool(((intervals_payload or {}) if isinstance(intervals_payload, dict) else {}).get("more")),
            errors=metadata_errors,
        )
        if effective_ts != selection.target_timestamp:
            result_selection = result.get("selection") if isinstance(result.get("selection"), dict) else None
            result_archive = result.get("archive") if isinstance(result.get("archive"), dict) else None
            if result_selection is not None:
                result_selection["effective_timestamp"] = effective_ts
            if result_archive is not None:
                context_handle = result_archive.get("context_handle") if isinstance(result_archive.get("context_handle"), dict) else None
                if context_handle is not None:
                    context_handle["timestamp"] = effective_ts
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "single-camera-export":
        try:
            request = build_single_camera_export_request(
                begin=args.begin,
                end=args.end,
                camera_names=args.camera,
                camera_access_points=args.camera_ap,
                waittimeout_ms=args.waittimeout_ms,
                archive_name=args.archive,
            )
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        camera_rows = normalize_camera_rows(c.list_cameras(view="VIEW_MODE_FULL"))
        try:
            selection = resolve_single_camera_export_selection(request, camera_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        out_path = Path(args.out) if args.out else Path(
            f"/tmp/axxon_tg_single_camera_export_{_safe_file_fragment(selection.camera)}_{_safe_file_fragment(selection.request_begin)}_{_safe_file_fragment(selection.request_end)}.mp4"
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)

        export_result = None
        export_error = None
        try:
            export_result = c.export_archive(
                normalize_video_id(selection.camera_access_point),
                selection.request_begin,
                selection.request_end,
                out_path=out_path,
                export_format=request.export_format,
                waittimeout=request.waittimeout_ms,
                archive=request.archive_name,
                attempts=90,
                sleep_sec=1.0,
                fallback_name="file.mp4",
            )
        except Exception as ex:
            export_error = str(ex)

        artifact_path = str((export_result or {}).get("path") or "").strip()
        artifact_size_bytes = None
        if artifact_path and Path(artifact_path).exists():
            artifact_size_bytes = Path(artifact_path).stat().st_size

        result = shape_single_camera_export_result(
            request,
            selection,
            artifact_path=artifact_path or None,
            artifact_size_bytes=artifact_size_bytes,
            export_status=((export_result or {}).get("status") if isinstance(export_result, dict) else None),
            error=export_error,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "macro-preview":
        request = _macro_request_from_args(args)
        policy = _macro_policy_from_args(args)
        try:
            macro_rows = c.list_macros(view="VIEW_MODE_FULL")
            record = select_macro_inventory_record(request, macro_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex
        decision = evaluate_macro_execution_guardrails(record, policy)
        result = shape_macro_execution_preview(
            request,
            record,
            decision,
            policy=policy,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "macro-execute":
        request = _macro_request_from_args(args)
        policy = _macro_policy_from_args(args)
        try:
            macro_rows = c.list_macros(view="VIEW_MODE_FULL")
            record = select_macro_inventory_record(request, macro_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex
        decision = evaluate_macro_execution_guardrails(record, policy)
        launch_result = None
        launch_error = None
        attempted = False
        ok = False

        if decision.allowed:
            attempted = True
            log_line(
                cfg.log_file,
                f"macro_execute attempt macro_id={record.macro_id} name={record.name} transport=http",
            )
            try:
                launch_result = c.launch_macro(record.macro_id)
                ok = True
                log_line(
                    cfg.log_file,
                    f"macro_execute success macro_id={record.macro_id} name={record.name} transport={launch_result.get('transport')}",
                )
            except Exception as ex:
                launch_error = str(ex)
                log_line(
                    cfg.log_file,
                    f"macro_execute failure macro_id={record.macro_id} name={record.name} error={launch_error}",
                )

        result = shape_macro_execution_result(
            request,
            record,
            decision,
            policy=policy,
            attempted=attempted,
            ok=ok,
            transport=((launch_result or {}).get("transport") if isinstance(launch_result, dict) else None),
            response=((launch_result or {}).get("response") if isinstance(launch_result, dict) else launch_result),
            error=launch_error,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "ptz-preview":
        request = _ptz_request_from_args(args)
        policy = _ptz_policy_from_args(args)
        try:
            camera_rows = c.list_cameras(view="VIEW_MODE_FULL")
            camera = select_ptz_camera_record(request, camera_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        position_info = None
        presets: list[dict] = []
        preview_errors: list[str] = []
        if camera.ptz_count > 0:
            try:
                position_info = c.ptz_position_info(camera.camera_access_point)
            except Exception as ex:
                preview_errors.append(f"position info: {ex}")
            try:
                presets = c.ptz_presets(camera.camera_access_point)
            except Exception as ex:
                preview_errors.append(f"preset inventory: {ex}")
        preview_error = "; ".join(preview_errors) or None
        preset_records = []
        for row in presets:
            try:
                preset_records.append(summarize_ptz_preset_row(row))
            except ValueError:
                continue

        preset = None
        if request.has_action and preset_records:
            try:
                preset = select_ptz_preset_record(request, presets)
            except ValueError as ex:
                raise SystemExit(str(ex)) from ex

        decision = evaluate_ptz_control_guardrails(
            request,
            camera,
            preset,
            policy,
            position_info=position_info,
            preview_error=preview_error,
        )
        result = shape_ptz_control_preview(
            request,
            camera,
            decision,
            policy=policy,
            position_info=position_info,
            presets=preset_records,
            preset=preset,
            preview_error=preview_error,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "ptz-execute":
        request = _ptz_request_from_args(args)
        policy = _ptz_policy_from_args(args)
        try:
            camera_rows = c.list_cameras(view="VIEW_MODE_FULL")
            camera = select_ptz_camera_record(request, camera_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        position_info = None
        presets: list[dict] = []
        preview_errors: list[str] = []
        if camera.ptz_count > 0:
            try:
                position_info = c.ptz_position_info(camera.camera_access_point)
            except Exception as ex:
                preview_errors.append(f"position info: {ex}")
            try:
                presets = c.ptz_presets(camera.camera_access_point)
            except Exception as ex:
                preview_errors.append(f"preset inventory: {ex}")
        preview_error = "; ".join(preview_errors) or None
        preset_records = []
        for row in presets:
            try:
                preset_records.append(summarize_ptz_preset_row(row))
            except ValueError:
                continue

        try:
            preset = select_ptz_preset_record(request, presets) if request.has_action and preset_records else None
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        result = run_ptz_execute_flow(
            c,
            request=request,
            camera=camera,
            preset=preset,
            policy=policy,
            position_info=position_info,
            presets=preset_records,
            preview_error=preview_error,
            log_file=cfg.log_file,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "multi-camera-export-plan":
        try:
            request = build_multi_camera_export_request(
                begin=args.begin,
                end=args.end,
                at=args.at,
                camera_names=() if args.camera_ap else args.camera,
                camera_access_points=args.camera_ap,
                waittimeout_ms=args.waittimeout_ms,
                archive_name=args.archive,
                max_cameras=args.max_cameras,
            )
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        camera_rows = normalize_camera_rows(c.list_cameras(view="VIEW_MODE_FULL"))
        try:
            selection = resolve_multi_camera_export_selection(request, camera_rows)
        except ValueError as ex:
            raise SystemExit(str(ex)) from ex

        result = shape_multi_camera_export_result(request, selection)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "notifier-pull":
        include: list[dict[str, str]] = []
        subjects = [str(value).strip() for value in (args.subject or []) if str(value).strip()]
        if subjects:
            include.extend(
                {
                    "event_type": args.event_type,
                    "subject": subject,
                }
                for subject in subjects
            )
        else:
            include.append({"event_type": args.event_type})
        payload = {
            "subscription_id": args.subscription_id,
            "filters": {"include": include},
        }
        packets = c.grpc_call(
            "axxonsoft.bl.events.DomainNotifier.PullEvents",
            payload,
            timeout=max(1, args.timeout_sec + 5),
        )
        items = []
        for p in packets:
            if isinstance(p.get("items"), list):
                items.extend(p.get("items") or [])
                continue
            data = p.get("data") or {}
            if isinstance(data, dict) and isinstance(data.get("items"), list):
                items.extend(data.get("items") or [])

        cards = [simplify_event_card(e) for e in items]
        if args.state or args.contains:
            cards = [x for x in cards if _card_matches(x, state=(args.state or ""), contains=(args.contains or ""))]
        print(json.dumps({
            "subscription_id": args.subscription_id,
            "packets": len(packets),
            "items": len(items),
            "cards": cards,
        }, ensure_ascii=False, indent=2))
        return

    if args.cmd == "notifier-disconnect":
        packets = c.grpc_call(
            "axxonsoft.bl.events.DomainNotifier.DisconnectEventChannel",
            {"subscription_id": args.subscription_id},
            timeout=30,
        )
        result = True
        for p in packets:
            if isinstance(p, dict) and p.get("result") is False:
                result = False
        print(json.dumps({
            "subscription_id": args.subscription_id,
            "disconnected": result,
            "packets": len(packets),
        }, ensure_ascii=False, indent=2))
        return

    if args.cmd == "alert-review":
        begin_packets = c.grpc_call(
            "axxonsoft.bl.logic.LogicService.BeginAlertReview",
            {"camera_ap": args.camera_ap, "alert_id": args.alert_id},
            timeout=30,
        )
        begin_ok = _grpc_packets_ok(begin_packets)

        continue_packets = []
        continue_ok = False
        if not begin_ok:
            continue_packets = c.grpc_call(
                "axxonsoft.bl.logic.LogicService.ContinueAlertReview",
                {"camera_ap": args.camera_ap, "alert_id": args.alert_id},
                timeout=30,
            )
            continue_ok = _grpc_packets_ok(continue_packets)

        can_complete = begin_ok or continue_ok
        complete_packets = []
        complete_ok = False
        if can_complete:
            complete_packets = c.grpc_call(
                "axxonsoft.bl.logic.LogicService.CompleteAlertReview",
                {
                    "severity": args.severity,
                    "bookmark": {},
                    "camera_ap": args.camera_ap,
                    "alert_id": args.alert_id,
                },
                timeout=30,
            )
            complete_ok = _grpc_packets_ok(complete_packets)

        # best-effort status lookup for better diagnostics
        current_state = None
        current_severity = None
        try:
            end = utc_now()
            begin = end - dt.timedelta(hours=24)
            items = c.read_events(
                begin=ts_compact(begin),
                end=ts_compact(end),
                subject=None,
                event_type="ET_Alert",
                values=None,
                limit=500,
                descending=True,
            )
            for e in items:
                b = e.get("body", {}) or {}
                aid = ((b.get("states") or [{}])[0].get("alert_id")) or b.get("guid")
                if aid == args.alert_id:
                    st = (b.get("states") or [{}])[0]
                    current_state = st.get("state")
                    current_severity = st.get("severity")
                    break
        except Exception:
            pass

        limitation = None
        if not complete_ok:
            if current_state and current_state != "ST_WANT_REACTION":
                limitation = f"Alert is not in ST_WANT_REACTION (current: {current_state}, severity: {current_severity})."
            else:
                limitation = "Alert review failed (state/permissions/session guard in LogicService)."

        print(json.dumps({
            "ok": complete_ok,
            "camera_ap": args.camera_ap,
            "alert_id": args.alert_id,
            "severity": args.severity,
            "begin_ok": begin_ok,
            "continue_ok": continue_ok,
            "complete_ok": complete_ok,
            "limitation": limitation,
            "current_state": current_state,
            "current_severity": current_severity,
            "raw": {
                "begin": begin_packets,
                "continue": continue_packets,
                "complete": complete_packets,
            },
        }, ensure_ascii=False, indent=2))
        return

    if args.cmd == "server-usage":
        print(json.dumps(c.server_usage(domain=bool(args.domain)), ensure_ascii=False, indent=2))
        return

    if args.cmd == "server-version":
        print(json.dumps(c.server_version(), ensure_ascii=False, indent=2))
        return

    if args.cmd == "server-statistics":
        print(json.dumps(c.server_statistics(), ensure_ascii=False, indent=2))
        return

    if args.cmd == "server-info":
        print(json.dumps(build_server_info_payload(c, domain=bool(args.domain)), ensure_ascii=False, indent=2))
        return

    if args.cmd == "admin-view":
        policy = _admin_policy_from_args(args)
        errors: list[dict[str, Any]] = []
        hosts: list[str] = []
        host_details: dict[str, dict[str, Any]] = {}
        current_user: dict[str, Any] = {}
        security_config: dict[str, Any] = {}
        global_permissions: dict[str, Any] = {}
        server_info = build_server_info_payload(c, domain=True)
        for item in (server_info.get("errors") or []):
            if isinstance(item, dict):
                errors.append(item)

        try:
            host_rows = c.list_hosts()
            if isinstance(host_rows, list):
                hosts = [str(value) for value in host_rows if str(value or "").strip()]
        except Exception as ex:
            errors.append(_error_payload("hosts", ex))

        for host in hosts:
            try:
                detail = c.host_info(host)
                if isinstance(detail, dict):
                    host_details[host] = detail
            except Exception as ex:
                errors.append(_error_payload(f"host:{host}", ex))

        try:
            current_payload = c.current_web_user()
            if isinstance(current_payload, dict):
                current_user = current_payload
        except Exception as ex:
            errors.append(_error_payload("currentuser", ex))

        try:
            config_payload = c.security_list_config()
            if isinstance(config_payload, dict):
                security_config = config_payload
        except Exception as ex:
            errors.append(_error_payload("SecurityService.ListConfig", ex))

        role_ids = [
            str((role or {}).get("index") or "").strip()
            for role in (security_config.get("roles") or [])
            if isinstance(role, dict) and str((role or {}).get("index") or "").strip()
        ]
        if role_ids:
            try:
                permissions_payload = c.security_list_global_permissions(role_ids)
                if isinstance(permissions_payload, dict):
                    global_permissions = permissions_payload
            except Exception as ex:
                errors.append(_error_payload("SecurityService.ListGlobalPermissions", ex))

        result = shape_admin_view_result(
            hosts=hosts,
            host_details=host_details,
            current_user=current_user,
            security_config=security_config,
            global_permissions=global_permissions,
            server_info=server_info,
            policy=policy,
            runtime_capabilities={
                "telegram_admin_user_count": len(bot_cfg.admin_users),
                "macro_execution": {
                    "enabled": bot_cfg.macro_execution_enabled,
                    "admin_only": True,
                    "allowlist_configured": bool(bot_cfg.macro_allowed_ids or bot_cfg.macro_allowed_names),
                    "audited": True,
                    "confirm_ttl_sec": bot_cfg.macro_confirm_ttl_sec,
                },
                "ptz_control": {
                    "enabled": bot_cfg.ptz_control_enabled,
                    "admin_only": True,
                    "allowlist_configured": bool(bot_cfg.ptz_allowed_camera_aps or bot_cfg.ptz_allowed_camera_names),
                    "audited": True,
                    "confirm_ttl_sec": bot_cfg.ptz_confirm_ttl_sec,
                },
            },
            errors=errors,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "plate-search":
        legacy_scan_limit = int(args.limit) if int(args.limit or 0) > 0 else 0
        request = build_license_plate_search_request(
            plate=args.plate,
            contains=args.contains,
            mask=args.mask,
            begin=args.begin,
            end=args.end,
            last_sec=args.seconds,
            hosts=args.scope_host,
            domains=args.domain,
            camera_names=args.camera,
            camera_access_points=[*args.camera_ap, *([args.subject] if args.subject else [])],
            detector_names=args.detector,
            detector_access_points=args.detector_ap,
            page=args.page,
            page_size=args.page_size,
            scan_limit=max(args.scan_limit, legacy_scan_limit),
            descending=not args.ascending,
        )
        rows, scanned, complete = _license_plate_search_rows(
            c,
            request,
            batch_size=request.scan_limit,
        )
        result = shape_license_plate_search_results(
            rows,
            request,
            scanned_count=scanned,
            complete=complete,
        )

        img_dir = Path(args.images_dir)
        page_items = result.get("items") if isinstance(result.get("items"), list) else []
        if args.with_images:
            img_dir.mkdir(parents=True, exist_ok=True)
            use_thumb = len(page_items) > args.thumb_threshold
            img_count = 0
            for n in page_items:
                if not isinstance(n, dict):
                    continue
                if img_count >= args.max_images:
                    break
                ts = n.get("best_frame_timestamp") or n.get("timestamp")
                cam_ap = _plate_search_image_camera_access_point(
                    n,
                    request,
                    explicit_subject=args.subject,
                )
                if not cam_ap:
                    n["full_frame"] = None
                    n["full_frame_error"] = "missing camera_access_point"
                    n["plate_crop_image"] = None
                    img_count += 1
                    continue
                video_id = normalize_video_id(cam_ap)
                full_path = img_dir / f"plate_{img_count+1}_{ts}_full.jpg"
                try:
                    if use_thumb:
                        c.media_frame(video_id, ts, full_path, width=args.thumb_w, height=args.thumb_h)
                    else:
                        c.media_frame(video_id, ts, full_path)
                    n["full_frame"] = str(full_path)
                    n["full_frame_thumb"] = use_thumb
                except Exception as ex:
                    n["full_frame"] = None
                    n["full_frame_error"] = str(ex)

                crop = n.get("plate_crop")
                if crop and n.get("full_frame"):
                    crop_path = img_dir / f"plate_{img_count+1}_{ts}_crop.jpg"
                    try:
                        c.media_frame(video_id, ts, crop_path, crop=crop)
                        n["plate_crop_image"] = str(crop_path)
                    except Exception as ex:
                        n["plate_crop_image"] = None
                        n["plate_crop_error"] = str(ex)
                else:
                    n["plate_crop_image"] = None
                img_count += 1

        if args.cleanup_after and args.with_images:
            for n in page_items:
                if not isinstance(n, dict):
                    continue
                for k in ("full_frame", "plate_crop_image"):
                    pth = n.get(k)
                    if pth:
                        try:
                            Path(pth).unlink(missing_ok=True)
                        except Exception:
                            pass
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "latest-event":
        end = utc_now()
        begin = end - dt.timedelta(seconds=args.seconds)
        items = c.read_events(
            begin=ts_compact(begin),
            end=ts_compact(end),
            subject=args.subject,
            event_type="ET_DetectorEvent",
            values=args.values,
            limit=500,
            descending=True,
        )
        for e in items:
            if e.get("body", {}).get("state") != args.state:
                continue
            txt = ((e.get("localization", {}) or {}).get("text", ""))
            if args.contains not in txt:
                continue
            Path(args.out).write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")
            print(args.out)
            return
        raise SystemExit("No matching event")

    if args.cmd == "live-snapshot":
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        print(c.live_snapshot(
            video_id=args.video_id,
            out_path=out,
            width=(args.w if args.w > 0 else None),
            height=(args.h if args.h > 0 else None),
        ))
        return

    if args.cmd == "frame-from-event":
        ev = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
        b = ev.get("body", {})
        if str(ev.get("event_type") or "").strip() == "ET_Alert":
            detector_body = b.get("detector") or {}
            ts = _alert_best_timestamp(b)
            if not ts:
                raise SystemExit("event_json has no timestamp")
        else:
            detector_body = {}
            ts = _event_best_timestamp(b, b.get("data") or {}, {})
            if not ts:
                raise SystemExit("event_json has no timestamp")

        video_id = args.video_id
        if not video_id:
            ap = ((b.get("origin_ext") or {}).get("access_point")
                  or (b.get("data", {}).get("origin_id"))
                  or (b.get("camera", {}).get("access_point"))
                  or ((detector_body.get("origin_ext") or {}).get("access_point"))
                  or ((detector_body.get("data") or {}).get("origin_id"))
                  or "")
            video_id = ap.replace("hosts/", "") if ap else ""
        if not video_id:
            raise SystemExit("video-id missing and cannot be resolved from event_json")

        if args.mode == "media":
            out = c.media_frame(
                video_id,
                ts,
                Path(args.out),
                threshold_ms=args.threshold_ms,
                width=(args.w or None),
                height=(args.h or None),
            )
        else:
            out = c.export_frame(video_id, ts, Path(args.out))
        print(out)
        return

    if args.cmd == "box-from-event":
        ev = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
        n = draw_boxes_ffmpeg(Path(args.image), Path(args.out), ev)
        print(json.dumps({"out": args.out, "boxes": n}, ensure_ascii=False))
        return

    if args.cmd == "clip-from-event":
        ev = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
        b = ev.get("body", {})
        ts = _event_best_timestamp(b, b.get("data") or {}, {})
        if not ts:
            raise SystemExit("event_json has no timestamp")
        t0 = ts_parse(ts)
        begin = t0 - dt.timedelta(seconds=args.pre)
        end = t0 + dt.timedelta(seconds=args.post)
        ap = ((b.get("origin_ext") or {}).get("access_point")
              or (b.get("data", {}).get("origin_id"))
              or (b.get("camera", {}).get("access_point"))
              or "")
        video_id = ap.replace("hosts/", "") if ap else ""
        if not video_id:
            raise SystemExit("cannot resolve video_id from event")
        out = c.export_clip(video_id, ts_compact(begin), ts_compact(end), Path(args.out))
        print(out)
        return


if __name__ == "__main__":
    main()
eturn


if __name__ == "__main__":
    main()
