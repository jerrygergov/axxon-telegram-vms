"""Pure Telegram face-search UX helpers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FACE_SEARCH_WIZARD_CALLBACK_PREFIX = "facewiz"
FACE_SEARCH_WIZARD_ACCURACY_PRESETS: tuple[tuple[int, str], ...] = (
    (90, "90%"),
    (85, "85%"),
    (80, "80%"),
)
FACE_SEARCH_WIZARD_PERIOD_PRESETS: tuple[tuple[int, str], ...] = (
    (15 * 60, "15m"),
    (60 * 60, "1h"),
    (6 * 60 * 60, "6h"),
    (24 * 60 * 60, "24h"),
)
_FACE_SEARCH_WIZARD_TERM_ALIASES = {
    "from": "begin",
    "begin": "begin",
    "start": "begin",
    "to": "end",
    "end": "end",
    "last": "last_sec",
    "seconds": "last_sec",
    "window": "last_sec",
    "accuracy": "accuracy",
    "score": "accuracy",
    "similarity": "accuracy",
}
_FACE_SEARCH_WIZARD_CONTROL_KEYS = {"begin", "end", "last_sec", "accuracy"}


@dataclass(frozen=True)
class FaceSearchWizardCallback:
    action: str
    draft_id: str
    value: str = ""


def _face_button(text: str, callback_data: str) -> dict[str, str]:
    return {"text": text, "callback_data": callback_data}


def _face_search_wizard_term_key(term: object) -> str | None:
    text = str(term or "").strip()
    if not text or "=" not in text:
        return None
    raw_key = text.split("=", 1)[0].strip().lower()
    return _FACE_SEARCH_WIZARD_TERM_ALIASES.get(raw_key)


def face_search_terms_support_wizard(terms: Iterable[object]) -> bool:
    for term in terms or ():
        if _face_search_wizard_term_key(term) in _FACE_SEARCH_WIZARD_CONTROL_KEYS:
            return False
    return True


def build_face_search_wizard_terms(
    base_terms: Iterable[object],
    *,
    accuracy_percent: int,
    period_seconds: int,
) -> list[str]:
    terms: list[str] = []
    for term in base_terms or ():
        text = str(term or "").strip()
        if not text:
            continue
        if _face_search_wizard_term_key(text) in _FACE_SEARCH_WIZARD_CONTROL_KEYS:
            continue
        terms.append(text)
    accuracy = max(0, min(100, int(accuracy_percent)))
    period = max(1, int(period_seconds))
    terms.append(f"accuracy={accuracy / 100:.2f}")
    terms.append(f"last={period}")
    return terms


def build_face_search_wizard_threshold_buttons(draft_id: object) -> list[list[dict[str, str]]]:
    draft = str(draft_id or "").strip()
    return [
        [
            _face_button("90%", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:acc:{draft}:90"),
            _face_button("85%", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:acc:{draft}:85"),
        ],
        [
            _face_button("80%", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:acc:{draft}:80"),
            _face_button("✖ Cancel", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:cancel:{draft}"),
        ],
    ]


def build_face_search_wizard_period_buttons(draft_id: object) -> list[list[dict[str, str]]]:
    draft = str(draft_id or "").strip()
    return [
        [
            _face_button("15m", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:last:{draft}:900"),
            _face_button("1h", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:last:{draft}:3600"),
        ],
        [
            _face_button("6h", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:last:{draft}:21600"),
            _face_button("24h", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:last:{draft}:86400"),
        ],
        [
            _face_button("⬅ Back", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:back:{draft}"),
            _face_button("✖ Cancel", f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:cancel:{draft}"),
        ],
    ]


def parse_face_search_wizard_callback(data: object) -> FaceSearchWizardCallback | None:
    text = str(data or "").strip()
    if not text.startswith(f"{FACE_SEARCH_WIZARD_CALLBACK_PREFIX}:"):
        return None
    parts = text.split(":")
    if len(parts) < 3:
        return None
    action = parts[1]
    draft_id = parts[2].strip()
    if not draft_id:
        return None
    if action in {"acc", "last"} and len(parts) == 4 and parts[3].strip():
        return FaceSearchWizardCallback(action=action, draft_id=draft_id, value=parts[3].strip())
    if action in {"back", "cancel"} and len(parts) == 3:
        return FaceSearchWizardCallback(action=action, draft_id=draft_id)
    return None


def format_face_search_wizard_period_label(seconds: int) -> str:
    for preset_seconds, label in FACE_SEARCH_WIZARD_PERIOD_PRESETS:
        if seconds == preset_seconds:
            return label
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    if seconds % 60 == 0:
        return f"{seconds // 60}m"
    return f"{seconds}s"


def parse_face_command_terms(text: object, *, command: str = "face") -> list[str] | None:
    raw = str(text or "").strip()
    if not raw.startswith("/"):
        return None

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return None

    head_parts = lines[0].split(maxsplit=1)
    command_token = head_parts[0][1:]
    command_name = command_token.split("@", 1)[0].casefold()
    if command_name != command.casefold():
        return None

    extra_parts: list[str] = []
    if len(head_parts) > 1 and head_parts[1].strip():
        extra_parts.append(head_parts[1].strip())
    if len(lines) > 1:
        extra_parts.extend(line for line in lines[1:] if line)

    extra_text = " ".join(extra_parts).strip()
    return [part for part in extra_text.split() if part]


def face_reference_attachment(message: Any) -> tuple[str, str]:
    for candidate in (message, getattr(message, "reply_to_message", None)):
        if not candidate:
            continue
        photos = list(getattr(candidate, "photo", None) or [])
        if photos:
            file_id = str(getattr(photos[-1], "file_id", "") or "")
            if file_id:
                return file_id, ".jpg"
        document = getattr(candidate, "document", None)
        if document and str(getattr(document, "mime_type", "") or "").startswith("image/"):
            file_id = str(getattr(document, "file_id", "") or "")
            if not file_id:
                continue
            suffix = Path(str(getattr(document, "file_name", "") or "reference.jpg")).suffix or ".jpg"
            return file_id, suffix
    return "", ""


def should_start_face_search_from_upload(message: Any) -> tuple[bool, list[str]]:
    file_id, _suffix = face_reference_attachment(message)
    if not file_id:
        return False, []

    caption = str(getattr(message, "caption", "") or "").strip()
    if not caption:
        return True, []

    terms = parse_face_command_terms(caption)
    if terms is None:
        return False, []
    return True, terms


__all__ = [
    "FACE_SEARCH_WIZARD_ACCURACY_PRESETS",
    "FACE_SEARCH_WIZARD_CALLBACK_PREFIX",
    "FACE_SEARCH_WIZARD_PERIOD_PRESETS",
    "FaceSearchWizardCallback",
    "build_face_search_wizard_period_buttons",
    "build_face_search_wizard_terms",
    "build_face_search_wizard_threshold_buttons",
    "face_reference_attachment",
    "face_search_terms_support_wizard",
    "format_face_search_wizard_period_label",
    "parse_face_command_terms",
    "parse_face_search_wizard_callback",
    "should_start_face_search_from_upload",
]
