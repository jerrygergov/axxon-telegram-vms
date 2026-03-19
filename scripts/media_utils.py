#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import Any


def _to_float(val: Any) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _clamp01(val: float) -> float:
    return max(0.0, min(1.0, val))


def _is_normalized_rect_values(*values: float) -> bool:
    return all(0.0 <= value <= 1.0 for value in values)


def _looks_like_normalized_xywh(x: float, y: float, w: float, h: float) -> bool:
    return _is_normalized_rect_values(x, y, w, h)


def _rect_xywh_candidate(x: Any, y: Any, w: Any, h: Any, *, source: str) -> dict[str, Any] | None:
    xf = _to_float(x)
    yf = _to_float(y)
    wf = _to_float(w)
    hf = _to_float(h)
    if xf is None or yf is None or wf is None or hf is None:
        return None
    if wf <= 0 or hf <= 0:
        return None
    return {"mode": "xywh", "x": xf, "y": yf, "w": wf, "h": hf, "source": source}


def _rect_xyxy_candidate(x1: Any, y1: Any, x2: Any, y2: Any, *, source: str) -> dict[str, Any] | None:
    x1f = _to_float(x1)
    y1f = _to_float(y1)
    x2f = _to_float(x2)
    y2f = _to_float(y2)
    if x1f is None or y1f is None or x2f is None or y2f is None:
        return None
    left = min(x1f, x2f)
    right = max(x1f, x2f)
    top = min(y1f, y2f)
    bottom = max(y1f, y2f)
    return _rect_xywh_candidate(left, top, right - left, bottom - top, source=source)


def extract_raw_rectangle_candidates(event_obj: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    body = event_obj.get("body") or {}
    detector_body = body.get("detector") or {}
    data = body.get("data") or {}
    detector_data = detector_body.get("data") or {}

    for d in (body.get("details") or []):
        r = d.get("rectangle")
        if isinstance(r, dict):
            rr = _rect_xywh_candidate(r.get("x"), r.get("y"), r.get("w"), r.get("h"), source="body.details.rectangle")
            if rr:
                out.append(rr)

    for d in (detector_body.get("details") or []):
        r = d.get("rectangle")
        if isinstance(r, dict):
            rr = _rect_xywh_candidate(r.get("x"), r.get("y"), r.get("w"), r.get("h"), source="body.detector.details.rectangle")
            if rr:
                out.append(rr)

    for rr in (data.get("rectangles") or []):
        if isinstance(rr, list) and len(rr) >= 4:
            norm = _rect_xyxy_candidate(rr[0], rr[1], rr[2], rr[3], source="body.data.rectangles")
            if norm:
                out.append(norm)

    for rr in (detector_data.get("rectangles") or []):
        if isinstance(rr, list) and len(rr) >= 4:
            norm = _rect_xyxy_candidate(rr[0], rr[1], rr[2], rr[3], source="body.detector.data.rectangles")
            if norm:
                out.append(norm)

    pr = data.get("PlateRectangle")
    if isinstance(pr, list) and len(pr) >= 4:
        norm = _rect_xyxy_candidate(pr[0], pr[1], pr[2], pr[3], source="body.data.PlateRectangle")
        if norm:
            out.append(norm)

    hy = data.get("Hypotheses") or []
    if hy and isinstance(hy[0], dict):
        p2 = hy[0].get("PlateRectangle")
        if isinstance(p2, list) and len(p2) >= 4:
            norm = _rect_xyxy_candidate(p2[0], p2[1], p2[2], p2[3], source="body.data.Hypotheses[0].PlateRectangle")
            if norm:
                out.append(norm)

    for d in (body.get("details") or []):
        ar = d.get("auto_recognition_result") or {}
        hh = ar.get("hypotheses") or []
        if hh and isinstance(hh[0], dict):
            p3 = hh[0].get("plate_rectangle")
            if isinstance(p3, dict):
                if all(k in p3 for k in ("left", "top", "right", "bottom")):
                    norm = _rect_xyxy_candidate(
                        p3.get("left"), p3.get("top"), p3.get("right"), p3.get("bottom"),
                        source="body.details.auto_recognition_result.hypotheses[0].plate_rectangle.xyxy",
                    )
                    if norm:
                        out.append(norm)
                else:
                    norm = _rect_xywh_candidate(
                        p3.get("x"), p3.get("y"), p3.get("w"), p3.get("h"),
                        source="body.details.auto_recognition_result.hypotheses[0].plate_rectangle.xywh",
                    )
                    if norm:
                        out.append(norm)

    auto_ex = data.get("auto_recognition_result_ex")
    ex_obj = None
    if isinstance(auto_ex, dict):
        ex_obj = auto_ex
    elif isinstance(auto_ex, str) and auto_ex.strip().startswith("{"):
        try:
            ex_obj = json.loads(auto_ex)
        except json.JSONDecodeError:
            ex_obj = None
    if isinstance(ex_obj, dict):
        hy2 = ex_obj.get("hypotheses") or []
        if hy2 and isinstance(hy2[0], dict):
            p4 = hy2[0].get("plateRectangle") or {}
            if isinstance(p4, dict):
                norm = _rect_xywh_candidate(
                    p4.get("x"), p4.get("y"), p4.get("w"), p4.get("h"),
                    source="body.data.auto_recognition_result_ex.hypotheses[0].plateRectangle",
                )
                if norm:
                    out.append(norm)
    return out


def _candidate_to_normalized(candidate: dict[str, Any]) -> dict[str, float] | None:
    x = _to_float(candidate.get("x"))
    y = _to_float(candidate.get("y"))
    w = _to_float(candidate.get("w"))
    h = _to_float(candidate.get("h"))
    if x is None or y is None or w is None or h is None or w <= 0 or h <= 0:
        return None
    if not _looks_like_normalized_xywh(x, y, w, h):
        return None
    x0 = _clamp01(x)
    y0 = _clamp01(y)
    x1 = _clamp01(x + w)
    y1 = _clamp01(y + h)
    if x1 <= x0 or y1 <= y0:
        return None
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def extract_candidate_rectangles(event_obj: dict[str, Any]) -> list[dict[str, float]]:
    out: list[dict[str, float]] = []
    for candidate in extract_raw_rectangle_candidates(event_obj):
        norm = _candidate_to_normalized(candidate)
        if norm:
            out.append(norm)
    return out


def _candidate_area(candidate: dict[str, Any]) -> float:
    w = _to_float(candidate.get("w")) or 0.0
    h = _to_float(candidate.get("h")) or 0.0
    return max(0.0, w) * max(0.0, h)


def _candidate_source_rank(source: object) -> int:
    text = str(source or "")
    order = [
        "body.details.rectangle",
        "body.detector.details.rectangle",
        "body.data.Hypotheses[0].PlateRectangle",
        "body.data.PlateRectangle",
        "body.details.auto_recognition_result.hypotheses[0].plate_rectangle.xyxy",
        "body.details.auto_recognition_result.hypotheses[0].plate_rectangle.xywh",
        "body.data.auto_recognition_result_ex.hypotheses[0].plateRectangle",
        "body.data.rectangles",
        "body.detector.data.rectangles",
    ]
    for idx, item in enumerate(order):
        if text == item:
            return idx
    return len(order)


def is_meaningful_rectangle_candidate(candidate: dict[str, Any], *, full_frame_threshold: float = 0.95) -> bool:
    x = _to_float(candidate.get("x"))
    y = _to_float(candidate.get("y"))
    w = _to_float(candidate.get("w"))
    h = _to_float(candidate.get("h"))
    if x is None or y is None or w is None or h is None:
        return False
    if w <= 0 or h <= 0:
        return False
    if _looks_like_normalized_xywh(x, y, w, h):
        return (w * h) < float(full_frame_threshold)
    return True


def pick_primary_rectangle_candidate(event_obj: dict[str, Any], *, prefer_meaningful: bool = True) -> dict[str, Any] | None:
    rows = extract_raw_rectangle_candidates(event_obj)
    if not rows:
        return None
    if prefer_meaningful:
        meaningful = [row for row in rows if is_meaningful_rectangle_candidate(row)]
        if meaningful:
            rows = meaningful
    rows = sorted(rows, key=lambda row: (_candidate_source_rank(row.get("source")), _candidate_area(row)))
    return rows[0] if rows else None


def pick_primary_rectangle(event_obj: dict[str, Any]) -> dict[str, float] | None:
    candidate = pick_primary_rectangle_candidate(event_obj)
    return _candidate_to_normalized(candidate) if candidate else None


def rectangle_candidate_to_pixel_crop(candidate: dict[str, Any], frame_width: int, frame_height: int) -> tuple[int, int, int, int] | None:
    if frame_width <= 1 or frame_height <= 1:
        return None
    x = _to_float(candidate.get("x"))
    y = _to_float(candidate.get("y"))
    w = _to_float(candidate.get("w"))
    h = _to_float(candidate.get("h"))
    if x is None or y is None or w is None or h is None or w <= 0 or h <= 0:
        return None

    if _looks_like_normalized_xywh(x, y, w, h):
        px = int(x * frame_width)
        py = int(y * frame_height)
        pw = int(w * frame_width)
        ph = int(h * frame_height)
    else:
        px = int(x)
        py = int(y)
        pw = int(w)
        ph = int(h)

    px = max(0, min(frame_width - 2, px))
    py = max(0, min(frame_height - 2, py))
    pw = max(2, min(frame_width - px, pw))
    ph = max(2, min(frame_height - py, ph))
    if pw <= 1 or ph <= 1:
        return None
    return px, py, pw, ph


def normalized_to_pixel_crop(rect: dict[str, float], frame_width: int, frame_height: int) -> tuple[int, int, int, int] | None:
    return rectangle_candidate_to_pixel_crop(rect, frame_width, frame_height)
