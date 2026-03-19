"""Pure transport helpers for the staged client lane."""

from __future__ import annotations

import json
import time
import urllib.parse
from collections.abc import Mapping
from typing import Any


def _parse_grpc_json_dict(payload: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def _parse_grpc_multipart(raw: str) -> list[dict]:
    text = str(raw or "").lstrip()
    if not text.startswith("--"):
        return []
    first_line, _, remainder = text.partition("\n")
    boundary = first_line.strip().strip("\r")
    if len(boundary) <= 2:
        return []

    objs: list[dict] = []
    for chunk in (remainder if remainder else text[len(first_line):]).split(boundary):
        part = chunk.lstrip("\r\n")
        if not part:
            continue
        if part.startswith("--"):
            continue
        body = ""
        if "\r\n\r\n" in part:
            _headers, body = part.split("\r\n\r\n", 1)
        elif "\n\n" in part:
            _headers, body = part.split("\n\n", 1)
        if not body:
            continue
        payload = body.strip()
        if payload.endswith("--"):
            payload = payload[:-2].rstrip()
        parsed = _parse_grpc_json_dict(payload)
        if parsed is not None:
            objs.append(parsed)
    return objs


def parse_grpc_response(raw: str) -> list[dict]:
    objs: list[dict] = []
    saw_sse = False
    for line in raw.splitlines():
        if line.startswith("data: "):
            saw_sse = True
            payload = line[6:].strip()
            if not payload:
                continue
            parsed = _parse_grpc_json_dict(payload)
            if parsed is not None:
                objs.append(parsed)

    if saw_sse:
        return objs

    multipart = _parse_grpc_multipart(raw)
    if multipart:
        return multipart

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if isinstance(parsed, dict):
        return [parsed]
    return []


def build_server_info_error(section: str, ex: Exception) -> dict[str, Any]:
    return {
        "section": section,
        "message": str(ex),
        "status_code": getattr(ex, "code", None),
    }


def build_server_info_payload(client: object, domain: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "usage": None,
        "version": None,
        "statistics": None,
        "errors": [],
    }
    calls = [
        ("usage", lambda: client.server_usage(domain=bool(domain))),
        ("version", client.server_version),
        ("statistics", client.server_statistics),
    ]
    for section, call in calls:
        try:
            payload[section] = call()
        except Exception as ex:
            payload["ok"] = False
            payload["errors"].append(build_server_info_error(section, ex))
    return payload


def append_cache_bust(url: str, token: int | None = None) -> str:
    sep = "&" if "?" in url else "?"
    cache_token = time.time_ns() if token is None else int(token)
    return f"{url}{sep}_ts={cache_token}"


def ffmpeg_auth_headers(headers: Mapping[str, str] | None) -> str:
    lines = []
    for key, value in (headers or {}).items():
        lines.append(f"{key}: {value}\r\n")
    return "".join(lines)


def build_media_query_params(
    *,
    width: int | None = None,
    height: int | None = None,
    crop: Mapping[str, Any] | None = None,
    threshold_ms: int | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if threshold_ms is not None:
        params["threshold"] = int(threshold_ms)
    if width:
        params["w"] = int(width)
    if height:
        params["h"] = int(height)
    if crop:
        params.update(
            {
                "crop_x": crop.get("x", 0),
                "crop_y": crop.get("y", 0),
                "crop_width": crop.get("w", 0),
                "crop_height": crop.get("h", 0),
            }
        )
    return params


def build_archive_frame_url(
    base: str,
    video_id: str,
    frame_ts: str,
    *,
    threshold_ms: int = 1000,
    width: int | None = None,
    height: int | None = None,
    crop: Mapping[str, Any] | None = None,
) -> str:
    # Legacy archive-stream helper. Documented single-frame retrieval should use export/archive with format=jpg.
    query = urllib.parse.urlencode(
        build_media_query_params(
            threshold_ms=threshold_ms,
            width=width,
            height=height,
            crop=crop,
        )
    )
    return f"{base}/archive/media/{video_id}/{frame_ts}?{query}"


def build_live_media_url(
    base: str,
    video_id: str,
    *,
    width: int | None = None,
    height: int | None = None,
    crop: Mapping[str, Any] | None = None,
    snapshot: bool = False,
    cache_bust_token: int | None = None,
) -> str:
    endpoint = "snapshot" if snapshot else None
    url = f"{base}/live/media/{video_id}"
    if endpoint:
        url = f"{base}/live/media/{endpoint}/{video_id}"
    query = urllib.parse.urlencode(build_media_query_params(width=width, height=height, crop=crop))
    if query:
        url = f"{url}?{query}"
    return append_cache_bust(url, token=cache_bust_token)


__all__ = [
    "append_cache_bust",
    "build_archive_frame_url",
    "build_live_media_url",
    "build_media_query_params",
    "build_server_info_error",
    "build_server_info_payload",
    "ffmpeg_auth_headers",
    "parse_grpc_response",
]
