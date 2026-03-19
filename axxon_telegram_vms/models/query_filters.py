"""Shared query/filter models for event and archive workflows."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any


_AXXON_TS_FORMATS = (
    "%Y%m%dT%H%M%S.%f",
    "%Y%m%dT%H%M%S",
    "%H:%M:%S %d-%m-%Y",
    "%H:%M %d-%m-%Y",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y %H:%M",
)
_HOST_PATH_RE = re.compile(r"(?:^|/)hosts/([^/]+)", flags=re.IGNORECASE)
_DOMAIN_PATH_RE = re.compile(r"(?:^|/)domains/([^/]+)", flags=re.IGNORECASE)
_SPACE_RE = re.compile(r"\s+")


def _text(value: object) -> str:
    return _SPACE_RE.sub(" ", str(value or "").strip())


def _normalized_key(value: object) -> str:
    return _text(value).casefold()


def _iter_values(raw: object) -> Iterable[object]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        return (raw,)
    if isinstance(raw, Mapping):
        return tuple(raw.values())
    if isinstance(raw, Iterable):
        return raw
    return (raw,)


def _string_tuple(
    raw: object,
    *,
    normalize: Callable[[str], str] | None = None,
) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for item in _iter_values(raw):
        value = _text(item)
        if not value:
            continue
        if normalize is not None:
            value = normalize(value)
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return tuple(out)


def _coerce_bool(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = _text(value).casefold()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _coerce_int(value: object, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return default
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def parse_query_datetime(value: object) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = _text(value)
        if not text:
            return None
        dt = None
        for fmt in _AXXON_TS_FORMATS:
            try:
                dt = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"Unsupported datetime value: {text}") from exc
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_query_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    dt = parse_query_datetime(value)
    if dt is None:
        return None
    if dt.microsecond:
        return dt.strftime("%Y%m%dT%H%M%S.%f")
    return dt.strftime("%Y%m%dT%H%M%S")


def _extract_path_match(pattern: re.Pattern[str], value: object) -> str:
    match = pattern.search(_text(value))
    return _text(match.group(1)) if match else ""


def _card_subject_candidates(card: Mapping[str, Any]) -> tuple[str, ...]:
    return _string_tuple(
        (
            card.get("subject"),
            card.get("access_point"),
            card.get("camera_access_point"),
            card.get("detector_access_point"),
        )
    )


def _card_host_candidates(card: Mapping[str, Any]) -> tuple[str, ...]:
    explicit = _string_tuple((card.get("host"), card.get("hostname"), card.get("server")))
    derived = _string_tuple(_extract_path_match(_HOST_PATH_RE, item) for item in _card_subject_candidates(card))
    return _string_tuple((*explicit, *derived))


def _card_domain_candidates(card: Mapping[str, Any]) -> tuple[str, ...]:
    explicit = _string_tuple((card.get("domain"), card.get("domain_name"), card.get("domain_id")))
    derived = _string_tuple(_extract_path_match(_DOMAIN_PATH_RE, item) for item in _card_subject_candidates(card))
    return _string_tuple((*explicit, *derived))


def _candidate_texts(card: Mapping[str, Any]) -> tuple[str, ...]:
    return _string_tuple(
        (
            card.get("text"),
            card.get("localization_text"),
            card.get("label_primary"),
            card.get("label_secondary"),
            card.get("camera"),
            card.get("detector"),
            card.get("plate"),
            card.get("event_type"),
            card.get("category"),
        )
    )


def _contains_text(candidates: Iterable[str], value: str) -> bool:
    needle = _normalized_key(value)
    return bool(needle) and any(needle in _normalized_key(candidate) for candidate in candidates)


def _mask_match(text: str, mask: str) -> bool:
    if not mask:
        return True
    regex = "^" + re.escape(mask).replace("\\*", ".*") + "$"
    return re.match(regex, text or "", flags=re.IGNORECASE) is not None


def _subject_matches(card_subject: str, query_subject: str) -> bool:
    card_key = _normalized_key(card_subject)
    query_key = _normalized_key(query_subject)
    if not card_key or not query_key:
        return False
    return (
        card_key == query_key
        or card_key.startswith(f"{query_key}/")
        or query_key.startswith(f"{card_key}/")
    )


def _detector_name_matches(card: Mapping[str, Any], detector_names: tuple[str, ...]) -> bool:
    detector_name = _text(card.get("detector") or card.get("detector_name"))
    if not detector_name:
        return False
    variants = {
        _normalized_key(detector_name),
        _normalized_key(detector_name.split(".", 1)[-1]),
    }
    return any(_normalized_key(name) in variants for name in detector_names)


def _camera_name_matches(card: Mapping[str, Any], camera_names: tuple[str, ...]) -> bool:
    camera_name = _text(card.get("camera") or card.get("camera_name"))
    if not camera_name:
        return False
    variants = {
        _normalized_key(camera_name),
        _normalized_key(camera_name.split(".", 1)[-1]),
    }
    return any(_normalized_key(name) in variants for name in camera_names)


def _event_type_matches(card: Mapping[str, Any], event_types: tuple[str, ...]) -> bool:
    card_event_type = _normalized_key(card.get("event_type"))
    card_category = _normalized_key(card.get("category"))
    for event_type in event_types:
        expected = _normalized_key(event_type)
        if card_event_type == expected:
            return True
        if expected == "et_detectorevent" and card_category != "alert" and card_event_type != "et_alert":
            return True
        if expected == "et_alert" and (card_category == "alert" or card_event_type == "et_alert"):
            return True
    return False


@dataclass(frozen=True)
class EventTimeRange:
    begin: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        begin = parse_query_datetime(self.begin)
        end = parse_query_datetime(self.end)
        if begin and end and begin > end:
            raise ValueError("EventTimeRange begin must be before end")
        object.__setattr__(self, "begin", begin)
        object.__setattr__(self, "end", end)

    def is_bounded(self) -> bool:
        return self.begin is not None and self.end is not None

    def contains(self, value: object) -> bool:
        ts = parse_query_datetime(value)
        if ts is None:
            return False
        if self.begin and ts < self.begin:
            return False
        if self.end and ts > self.end:
            return False
        return True

    def as_axxon_range(self) -> dict[str, str]:
        out: dict[str, str] = {}
        begin = format_query_datetime(self.begin)
        end = format_query_datetime(self.end)
        if begin:
            out["begin_time"] = begin
        if end:
            out["end_time"] = end
        return out


@dataclass(frozen=True)
class EventScopeFilter:
    hosts: tuple[str, ...] = ()
    domains: tuple[str, ...] = ()
    subjects: tuple[str, ...] = ()
    camera_names: tuple[str, ...] = ()
    camera_access_points: tuple[str, ...] = ()
    detector_access_points: tuple[str, ...] = ()
    detector_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "hosts", _string_tuple(self.hosts))
        object.__setattr__(self, "domains", _string_tuple(self.domains))
        object.__setattr__(self, "subjects", _string_tuple(self.subjects))
        object.__setattr__(self, "camera_names", _string_tuple(self.camera_names))
        object.__setattr__(self, "camera_access_points", _string_tuple(self.camera_access_points))
        object.__setattr__(self, "detector_access_points", _string_tuple(self.detector_access_points))
        object.__setattr__(self, "detector_names", _string_tuple(self.detector_names))

    def all_subjects(self) -> tuple[str, ...]:
        return _string_tuple((*self.subjects, *self.camera_access_points, *self.detector_access_points))

    def is_empty(self) -> bool:
        return not any(
            (
                self.hosts,
                self.domains,
                self.subjects,
                self.camera_names,
                self.camera_access_points,
                self.detector_access_points,
                self.detector_names,
            )
        )

    def matches_card(self, card: Mapping[str, Any]) -> bool:
        if self.hosts and not any(
            _normalized_key(candidate) in {_normalized_key(value) for value in self.hosts}
            for candidate in _card_host_candidates(card)
        ):
            return False

        if self.domains and not any(
            _normalized_key(candidate) in {_normalized_key(value) for value in self.domains}
            for candidate in _card_domain_candidates(card)
        ):
            return False

        subjects = self.all_subjects()
        if subjects:
            card_subjects = _card_subject_candidates(card)
            if not any(_subject_matches(card_subject, query_subject) for card_subject in card_subjects for query_subject in subjects):
                return False

        if self.camera_names and not _camera_name_matches(card, self.camera_names):
            return False

        if self.camera_access_points:
            camera_ap = _text(card.get("camera_access_point"))
            if _normalized_key(camera_ap) not in {_normalized_key(value) for value in self.camera_access_points}:
                return False

        if self.detector_access_points:
            detector_ap = _text(card.get("detector_access_point"))
            if _normalized_key(detector_ap) not in {_normalized_key(value) for value in self.detector_access_points}:
                return False

        if self.detector_names and not _detector_name_matches(card, self.detector_names):
            return False

        return True


@dataclass(frozen=True)
class EventTaxonomyFilter:
    categories: tuple[str, ...] = ()
    event_types: tuple[str, ...] = ()
    states: tuple[str, ...] = ()
    severities: tuple[str, ...] = ()
    priorities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "categories", _string_tuple(self.categories, normalize=str.lower))
        object.__setattr__(self, "event_types", _string_tuple(self.event_types))
        object.__setattr__(self, "states", _string_tuple(self.states, normalize=str.upper))
        object.__setattr__(self, "severities", _string_tuple(self.severities, normalize=str.upper))
        object.__setattr__(self, "priorities", _string_tuple(self.priorities, normalize=str.upper))

    def is_empty(self) -> bool:
        return not any((self.categories, self.event_types, self.states, self.severities, self.priorities))

    def matches_card(self, card: Mapping[str, Any]) -> bool:
        if self.categories and _normalized_key(card.get("category")) not in {_normalized_key(value) for value in self.categories}:
            return False

        if self.event_types and not _event_type_matches(card, self.event_types):
            return False

        if self.states and _normalized_key(_text(card.get("state")).upper()) not in {_normalized_key(value) for value in self.states}:
            return False

        if self.severities:
            severity_candidates = _string_tuple((card.get("severity"), card.get("current_severity")))
            if not severity_candidates or not any(
                _normalized_key(candidate.upper()) in {_normalized_key(value) for value in self.severities}
                for candidate in severity_candidates
            ):
                return False

        if self.priorities:
            priority_candidates = _string_tuple((card.get("priority"), card.get("current_priority")))
            if not priority_candidates or not any(
                _normalized_key(candidate.upper()) in {_normalized_key(value) for value in self.priorities}
                for candidate in priority_candidates
            ):
                return False

        return True


@dataclass(frozen=True)
class EventTextFilter:
    text: str = ""
    contains: str = ""
    mask: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _text(self.text))
        object.__setattr__(self, "contains", _text(self.contains))
        object.__setattr__(self, "mask", _text(self.mask))

    def is_empty(self) -> bool:
        return not any((self.text, self.contains, self.mask))

    def matches_card(self, card: Mapping[str, Any]) -> bool:
        candidates = _candidate_texts(card)
        if self.text and not _contains_text(candidates, self.text):
            return False
        if self.contains and not _contains_text(candidates, self.contains):
            return False
        if self.mask and not any(_mask_match(candidate, self.mask) for candidate in candidates):
            return False
        return True


@dataclass(frozen=True)
class EventQuery:
    time_range: EventTimeRange | None = None
    scope: EventScopeFilter = field(default_factory=EventScopeFilter)
    taxonomy: EventTaxonomyFilter = field(default_factory=EventTaxonomyFilter)
    text: EventTextFilter = field(default_factory=EventTextFilter)
    limit: int | None = None
    offset: int = 0
    descending: bool = True

    def __post_init__(self) -> None:
        time_range = self.time_range
        if time_range is not None and not isinstance(time_range, EventTimeRange):
            if isinstance(time_range, Mapping):
                time_range = EventTimeRange(
                    begin=time_range.get("begin") or time_range.get("begin_time"),
                    end=time_range.get("end") or time_range.get("end_time"),
                )
            else:
                raise TypeError("EventQuery time_range must be EventTimeRange or mapping")
        limit = _coerce_int(self.limit, default=None)
        offset = _coerce_int(self.offset, default=0) or 0
        if limit is not None and limit <= 0:
            raise ValueError("EventQuery limit must be positive")
        if offset < 0:
            raise ValueError("EventQuery offset must be zero or positive")
        object.__setattr__(self, "time_range", time_range)
        object.__setattr__(self, "limit", limit)
        object.__setattr__(self, "offset", offset)
        object.__setattr__(self, "descending", _coerce_bool(self.descending, True))

    @classmethod
    def from_legacy_filters(
        cls,
        filters: Mapping[str, Any] | None,
        *,
        states: Iterable[object] | None = None,
        time_range: EventTimeRange | None = None,
    ) -> "EventQuery":
        raw = dict(filters or {})

        if time_range is None:
            range_payload = raw.get("range")
            if isinstance(range_payload, Mapping):
                time_range = EventTimeRange(
                    begin=range_payload.get("begin") or range_payload.get("begin_time"),
                    end=range_payload.get("end") or range_payload.get("end_time"),
                )
            elif raw.get("begin") or raw.get("begin_time") or raw.get("end") or raw.get("end_time"):
                time_range = EventTimeRange(
                    begin=raw.get("begin") or raw.get("begin_time"),
                    end=raw.get("end") or raw.get("end_time"),
                )

        event_types = list(_string_tuple(raw.get("event_types")))
        event_type = _text(raw.get("event_type"))
        if event_type:
            event_types.insert(0, event_type)

        subjects = list(_string_tuple(raw.get("subjects")))
        subject = _text(raw.get("subject"))
        if subject:
            subjects.insert(0, subject)

        categories = _string_tuple(raw.get("categories"), normalize=str.lower)
        states_values = _string_tuple((*_iter_values(raw.get("states")), *_iter_values(states)), normalize=str.upper)
        priorities = _string_tuple((*_iter_values(raw.get("priorities")), raw.get("priority")), normalize=str.upper)
        severities = _string_tuple((*_iter_values(raw.get("severities")), raw.get("severity")), normalize=str.upper)
        text_value = _text(raw.get("text") or raw.get("texts"))
        contains = _text(raw.get("contains"))
        mask = _text(raw.get("mask") or raw.get("search_predicate"))

        return cls(
            time_range=time_range,
            scope=EventScopeFilter(
                hosts=_string_tuple((*_iter_values(raw.get("hosts")), raw.get("host"))),
                domains=_string_tuple((*_iter_values(raw.get("domains")), raw.get("domain"))),
                subjects=_string_tuple(subjects),
                camera_names=_string_tuple(raw.get("camera_names") or raw.get("camera")),
                camera_access_points=_string_tuple(raw.get("camera_access_points") or raw.get("cameras")),
                detector_access_points=_string_tuple(raw.get("detector_access_points") or raw.get("detectors")),
                detector_names=_string_tuple(raw.get("detector_names")),
            ),
            taxonomy=EventTaxonomyFilter(
                categories=categories,
                event_types=_string_tuple(event_types),
                states=states_values,
                severities=severities,
                priorities=priorities,
            ),
            text=EventTextFilter(
                text=text_value,
                contains=contains,
                mask=mask,
            ),
            limit=_coerce_int(raw.get("limit"), default=None),
            offset=_coerce_int(raw.get("offset"), default=0) or 0,
            descending=_coerce_bool(raw.get("descending"), True),
        )

    def is_empty(self) -> bool:
        return not any(
            (
                self.time_range and (self.time_range.begin or self.time_range.end),
                not self.scope.is_empty(),
                not self.taxonomy.is_empty(),
                not self.text.is_empty(),
                self.limit is not None,
                self.offset,
                not self.descending,
            )
        )

    def matches_card(self, card: Mapping[str, Any] | None) -> bool:
        if not isinstance(card, Mapping):
            return False
        if self.time_range is not None:
            if not self.time_range.contains(card.get("timestamp")):
                return False
        return (
            self.scope.matches_card(card)
            and self.taxonomy.matches_card(card)
            and self.text.matches_card(card)
        )

    def to_legacy_filters(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.time_range is not None:
            range_payload = self.time_range.as_axxon_range()
            if range_payload:
                out["range"] = range_payload
        if self.scope.hosts:
            out["hosts"] = list(self.scope.hosts)
        if self.scope.domains:
            out["domains"] = list(self.scope.domains)
        if self.scope.subjects:
            if len(self.scope.subjects) == 1:
                out["subject"] = self.scope.subjects[0]
            else:
                out["subjects"] = list(self.scope.subjects)
        if self.scope.camera_names:
            out["camera_names"] = list(self.scope.camera_names)
        if self.scope.camera_access_points:
            out["camera_access_points"] = list(self.scope.camera_access_points)
        if self.scope.detector_access_points:
            out["detector_access_points"] = list(self.scope.detector_access_points)
        if self.scope.detector_names:
            out["detector_names"] = list(self.scope.detector_names)
        if self.taxonomy.categories:
            out["categories"] = list(self.taxonomy.categories)
        if self.taxonomy.event_types:
            if len(self.taxonomy.event_types) == 1:
                out["event_type"] = self.taxonomy.event_types[0]
            else:
                out["event_types"] = list(self.taxonomy.event_types)
        if self.taxonomy.states:
            out["states"] = list(self.taxonomy.states)
        if self.taxonomy.severities:
            out["severities"] = list(self.taxonomy.severities)
        if self.taxonomy.priorities:
            out["priorities"] = list(self.taxonomy.priorities)
        if self.text.text:
            out["text"] = self.text.text
        if self.text.contains:
            out["contains"] = self.text.contains
        if self.text.mask:
            out["mask"] = self.text.mask
        if self.limit is not None:
            out["limit"] = self.limit
        if self.offset:
            out["offset"] = self.offset
        if not self.descending:
            out["descending"] = False
        return out


def query_card_matches(card: Mapping[str, Any], query: EventQuery) -> bool:
    return query.matches_card(card)


__all__ = [
    "EventQuery",
    "EventScopeFilter",
    "EventTaxonomyFilter",
    "EventTextFilter",
    "EventTimeRange",
    "format_query_datetime",
    "parse_query_datetime",
    "query_card_matches",
]
