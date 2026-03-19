#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def friendly_label(name: object = "", display_id: object = "", fallback: object = "") -> str:
    text = str(name or "").strip()
    ident = str(display_id or "").strip()
    fb = str(fallback or "").strip()
    if ident and text and not text.startswith(f"{ident}."):
        return f"{ident}.{text}"
    return text or fb or ident or "—"


def normalize_video_id(access_point: str) -> str:
    ap = str(access_point or "").strip()
    if ap.startswith("hosts/"):
        return ap[len("hosts/"):]
    return ap


def normalize_camera_rows(cams: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for cam in cams or []:
        ap = str(cam.get("access_point") or "").strip()
        if not ap:
            continue
        out.append({
            "name": friendly_label(cam.get("display_name"), cam.get("display_id"), ap),
            "access_point": ap,
            "detectors": cam.get("detectors") or [],
        })
    return out
