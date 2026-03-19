"""Future-facing external analysis contracts for exported media."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from axxon_telegram_vms.models import RequestEnvelope, build_request_envelope


DEFAULT_EXTERNAL_ANALYSIS_PRIVACY_PROFILE = "minimum_necessary"
DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_FIELDS = (
    "summary",
    "findings",
    "confidence",
)
DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_STYLE = "operator_brief"
EXTERNAL_ANALYSIS_MEDIA_KINDS = (
    "clip",
    "image",
)


def _text(value: object) -> str:
    return str(value or "").strip()


def _split_csv_values(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    values = raw.split(",") if isinstance(raw, str) else raw
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _text(value)
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return tuple(out)


def _mapping_list(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _coerce_non_negative_int(value: object, field_name: str) -> int | None:
    if value in (None, ""):
        return None
    try:
        out = int(str(value).strip())
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a non-negative integer") from exc
    if out < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return out


def _coerce_confidence(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip())
    except (AttributeError, TypeError, ValueError):
        return None


@dataclass(frozen=True)
class ExternalAnalysisArtifact:
    path: str
    media_kind: str
    file_name: str | None = None
    content_type: str | None = None
    camera_name: str | None = None
    camera_access_point: str | None = None
    captured_at: str | None = None
    export_origin: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None

    def __post_init__(self) -> None:
        path = _text(self.path)
        if not path:
            raise ValueError("artifact path is required")
        media_kind = _text(self.media_kind).lower()
        if media_kind not in EXTERNAL_ANALYSIS_MEDIA_KINDS:
            raise ValueError(f"Unsupported media kind: {self.media_kind}")
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "media_kind", media_kind)
        object.__setattr__(self, "file_name", _text(self.file_name) or Path(path).name or None)
        object.__setattr__(self, "content_type", _text(self.content_type) or None)
        object.__setattr__(self, "camera_name", _text(self.camera_name) or None)
        object.__setattr__(self, "camera_access_point", _text(self.camera_access_point) or None)
        object.__setattr__(self, "captured_at", _text(self.captured_at) or None)
        object.__setattr__(self, "export_origin", _text(self.export_origin) or None)
        object.__setattr__(self, "size_bytes", _coerce_non_negative_int(self.size_bytes, "size_bytes"))
        object.__setattr__(self, "sha256", _text(self.sha256) or None)


@dataclass(frozen=True)
class ExternalAnalysisPromptPreset:
    prompt_id: str
    title: str
    instruction: str
    summary_style: str = DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_STYLE
    target_media_kinds: tuple[str, ...] = EXTERNAL_ANALYSIS_MEDIA_KINDS

    def __post_init__(self) -> None:
        prompt_id = _text(self.prompt_id)
        instruction = _text(self.instruction)
        if not prompt_id:
            raise ValueError("prompt_id is required")
        if not instruction:
            raise ValueError("instruction is required")
        target_media_kinds = tuple(
            kind for kind in _split_csv_values(self.target_media_kinds)
            if kind in EXTERNAL_ANALYSIS_MEDIA_KINDS
        )
        if not target_media_kinds:
            raise ValueError("target_media_kinds must include at least one supported media kind")
        object.__setattr__(self, "prompt_id", prompt_id)
        object.__setattr__(self, "title", _text(self.title) or prompt_id)
        object.__setattr__(self, "instruction", instruction)
        object.__setattr__(self, "summary_style", _text(self.summary_style) or DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_STYLE)
        object.__setattr__(self, "target_media_kinds", target_media_kinds)


@dataclass(frozen=True)
class ExternalAnalysisProviderCapability:
    provider_id: str
    display_name: str
    supported_media_kinds: tuple[str, ...] = EXTERNAL_ANALYSIS_MEDIA_KINDS
    supports_async_jobs: bool = True
    supports_dry_run: bool = True
    supports_prompt_presets: bool = True
    supports_audit_labels: bool = True

    def __post_init__(self) -> None:
        provider_id = _text(self.provider_id)
        if not provider_id:
            raise ValueError("provider_id is required")
        kinds = tuple(
            kind for kind in _split_csv_values(self.supported_media_kinds)
            if kind in EXTERNAL_ANALYSIS_MEDIA_KINDS
        )
        if not kinds:
            raise ValueError("supported_media_kinds must include at least one supported media kind")
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "display_name", _text(self.display_name) or provider_id)
        object.__setattr__(self, "supported_media_kinds", kinds)


@dataclass(frozen=True)
class ExternalAnalysisRequest:
    provider_id: str
    artifacts: tuple[ExternalAnalysisArtifact, ...]
    prompt_preset: ExternalAnalysisPromptPreset
    envelope: RequestEnvelope
    operator_note: str | None = None
    async_required: bool = True
    privacy_profile: str = DEFAULT_EXTERNAL_ANALYSIS_PRIVACY_PROFILE
    result_summary_fields: tuple[str, ...] = DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_FIELDS

    def __post_init__(self) -> None:
        provider_id = _text(self.provider_id)
        if not provider_id:
            raise ValueError("provider_id is required")
        artifacts = tuple(self.artifacts or ())
        if not artifacts:
            raise ValueError("external analysis requires at least one artifact")
        if not isinstance(self.prompt_preset, ExternalAnalysisPromptPreset):
            raise ValueError("prompt_preset must be an ExternalAnalysisPromptPreset")
        if not isinstance(self.envelope, RequestEnvelope):
            raise ValueError("envelope must be a RequestEnvelope")
        if any(not isinstance(item, ExternalAnalysisArtifact) for item in artifacts):
            raise ValueError("artifacts must be ExternalAnalysisArtifact values")
        unsupported = {
            item.media_kind
            for item in artifacts
            if item.media_kind not in self.prompt_preset.target_media_kinds
        }
        if unsupported:
            raise ValueError(
                "prompt preset does not cover media kinds: "
                + ", ".join(sorted(unsupported))
            )
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "artifacts", artifacts)
        object.__setattr__(self, "operator_note", _text(self.operator_note) or None)
        object.__setattr__(self, "privacy_profile", _text(self.privacy_profile) or DEFAULT_EXTERNAL_ANALYSIS_PRIVACY_PROFILE)
        object.__setattr__(self, "result_summary_fields", _split_csv_values(self.result_summary_fields))

    @property
    def media_kinds(self) -> tuple[str, ...]:
        return tuple(sorted({artifact.media_kind for artifact in self.artifacts}))


@dataclass(frozen=True)
class ExternalAnalysisSubmissionDecision:
    accepted: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


class ExternalAnalysisProviderAdapter(Protocol):
    capability: ExternalAnalysisProviderCapability

    def submit(self, request: ExternalAnalysisRequest) -> Mapping[str, Any]:
        """Build or execute a provider submission request."""

    def summarize(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        """Normalize provider output into a small summary payload."""


def build_external_analysis_artifact(
    *,
    path: object,
    media_kind: object,
    file_name: object = None,
    content_type: object = None,
    camera_name: object = None,
    camera_access_point: object = None,
    captured_at: object = None,
    export_origin: object = None,
    size_bytes: object = None,
    sha256: object = None,
) -> ExternalAnalysisArtifact:
    return ExternalAnalysisArtifact(
        path=_text(path),
        media_kind=_text(media_kind).lower(),
        file_name=_text(file_name) or None,
        content_type=_text(content_type) or None,
        camera_name=_text(camera_name) or None,
        camera_access_point=_text(camera_access_point) or None,
        captured_at=_text(captured_at) or None,
        export_origin=_text(export_origin) or None,
        size_bytes=size_bytes,
        sha256=_text(sha256) or None,
    )


def build_external_analysis_prompt_preset(
    *,
    prompt_id: object,
    title: object,
    instruction: object,
    summary_style: object = DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_STYLE,
    target_media_kinds: Iterable[object] = EXTERNAL_ANALYSIS_MEDIA_KINDS,
) -> ExternalAnalysisPromptPreset:
    return ExternalAnalysisPromptPreset(
        prompt_id=_text(prompt_id),
        title=_text(title),
        instruction=_text(instruction),
        summary_style=_text(summary_style) or DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_STYLE,
        target_media_kinds=_split_csv_values(target_media_kinds),
    )


def build_external_analysis_provider_capability(
    *,
    provider_id: object,
    display_name: object,
    supported_media_kinds: Iterable[object] = EXTERNAL_ANALYSIS_MEDIA_KINDS,
    supports_async_jobs: bool = True,
    supports_dry_run: bool = True,
    supports_prompt_presets: bool = True,
    supports_audit_labels: bool = True,
) -> ExternalAnalysisProviderCapability:
    return ExternalAnalysisProviderCapability(
        provider_id=_text(provider_id),
        display_name=_text(display_name),
        supported_media_kinds=_split_csv_values(supported_media_kinds),
        supports_async_jobs=bool(supports_async_jobs),
        supports_dry_run=bool(supports_dry_run),
        supports_prompt_presets=bool(supports_prompt_presets),
        supports_audit_labels=bool(supports_audit_labels),
    )


def build_external_analysis_request(
    *,
    provider_id: object,
    artifacts: Iterable[ExternalAnalysisArtifact | Mapping[str, Any]],
    prompt_preset: ExternalAnalysisPromptPreset | Mapping[str, Any],
    envelope: RequestEnvelope | None = None,
    operator_note: object = None,
    async_required: bool = True,
    privacy_profile: object = DEFAULT_EXTERNAL_ANALYSIS_PRIVACY_PROFILE,
    result_summary_fields: Iterable[object] = DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_FIELDS,
) -> ExternalAnalysisRequest:
    normalized_artifacts: list[ExternalAnalysisArtifact] = []
    for item in artifacts or ():
        if isinstance(item, ExternalAnalysisArtifact):
            normalized_artifacts.append(item)
            continue
        if isinstance(item, Mapping):
            normalized_artifacts.append(
                build_external_analysis_artifact(
                    path=item.get("path"),
                    media_kind=item.get("media_kind"),
                    file_name=item.get("file_name"),
                    content_type=item.get("content_type"),
                    camera_name=item.get("camera_name"),
                    camera_access_point=item.get("camera_access_point"),
                    captured_at=item.get("captured_at"),
                    export_origin=item.get("export_origin"),
                    size_bytes=item.get("size_bytes"),
                    sha256=item.get("sha256"),
                )
            )
    if isinstance(prompt_preset, ExternalAnalysisPromptPreset):
        normalized_prompt = prompt_preset
    elif isinstance(prompt_preset, Mapping):
        normalized_prompt = build_external_analysis_prompt_preset(
            prompt_id=prompt_preset.get("prompt_id"),
            title=prompt_preset.get("title"),
            instruction=prompt_preset.get("instruction"),
            summary_style=prompt_preset.get("summary_style"),
            target_media_kinds=prompt_preset.get("target_media_kinds") or EXTERNAL_ANALYSIS_MEDIA_KINDS,
        )
    else:
        raise ValueError("prompt_preset must be an ExternalAnalysisPromptPreset or mapping")

    return ExternalAnalysisRequest(
        provider_id=_text(provider_id),
        artifacts=tuple(normalized_artifacts),
        prompt_preset=normalized_prompt,
        envelope=envelope or build_request_envelope(action="analysis"),
        operator_note=_text(operator_note) or None,
        async_required=bool(async_required),
        privacy_profile=_text(privacy_profile) or DEFAULT_EXTERNAL_ANALYSIS_PRIVACY_PROFILE,
        result_summary_fields=_split_csv_values(result_summary_fields),
    )


def evaluate_external_analysis_submission(
    request: ExternalAnalysisRequest,
    provider: ExternalAnalysisProviderCapability,
) -> ExternalAnalysisSubmissionDecision:
    reasons: list[str] = []
    warnings: list[str] = []
    if request.provider_id != provider.provider_id:
        reasons.append("provider_id does not match the selected provider capability")
    unsupported_media = sorted(
        kind for kind in request.media_kinds
        if kind not in provider.supported_media_kinds
    )
    if unsupported_media:
        reasons.append(
            "provider does not advertise support for media kinds: "
            + ", ".join(unsupported_media)
        )
    if request.async_required and not provider.supports_async_jobs:
        reasons.append("provider does not advertise async job handling")
    if request.envelope.audit.dry_run and not provider.supports_dry_run:
        reasons.append("provider does not advertise dry-run support")
    if request.prompt_preset.prompt_id and not provider.supports_prompt_presets:
        reasons.append("provider does not advertise prompt preset support")
    if request.envelope.audit.audit_required and not provider.supports_audit_labels:
        warnings.append("provider does not advertise audit label support")
    if not request.envelope.audit.audit_required:
        warnings.append("audit trail is disabled for this external analysis request")
    return ExternalAnalysisSubmissionDecision(
        accepted=not reasons,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
    )


def summarize_external_analysis_findings(
    findings: object,
    *,
    max_items: int = 3,
) -> dict[str, Any]:
    if isinstance(findings, Mapping):
        items = _mapping_list(findings.get("findings"))
        if not items:
            items = _mapping_list(findings.get("items"))
    else:
        items = _mapping_list(findings)

    if not items:
        return {
            "finding_count": 0,
            "top_labels": [],
            "max_confidence": None,
            "text": "No findings returned",
        }

    label_counts: Counter[str] = Counter()
    confidences: list[float] = []
    for item in items:
        label = _text(
            item.get("label")
            or item.get("name")
            or item.get("category")
            or item.get("text")
        ) or "unlabeled"
        label_counts[label] += 1
        confidence = _coerce_confidence(item.get("confidence") or item.get("score"))
        if confidence is not None:
            confidences.append(confidence)

    top_labels = [
        {"label": label, "count": count}
        for label, count in label_counts.most_common(max(1, int(max_items)))
    ]
    parts = [f"{len(items)} finding(s)"]
    if top_labels:
        parts.append(", ".join(f"{row['label']} x{row['count']}" for row in top_labels))
    max_confidence = max(confidences) if confidences else None
    if max_confidence is not None:
        parts.append(f"max confidence {max_confidence:.2f}")
    return {
        "finding_count": len(items),
        "top_labels": top_labels,
        "max_confidence": max_confidence,
        "text": " · ".join(parts),
    }


def shape_external_analysis_submission(
    request: ExternalAnalysisRequest,
    provider: ExternalAnalysisProviderCapability,
    *,
    decision: ExternalAnalysisSubmissionDecision | None = None,
    provider_job_id: object = None,
    provider_payload: Mapping[str, Any] | None = None,
    status: str = "planned",
    error: object = None,
) -> dict[str, Any]:
    active_decision = decision or evaluate_external_analysis_submission(request, provider)
    effective_status = "dry_run" if request.envelope.audit.dry_run and status == "planned" else _text(status) or "planned"
    return {
        "request": {
            "provider_id": request.provider_id,
            "media_kinds": list(request.media_kinds),
            "artifact_count": len(request.artifacts),
            "async_required": request.async_required,
            "privacy_profile": request.privacy_profile,
            "result_summary_fields": list(request.result_summary_fields),
            "operator_note": request.operator_note,
            "prompt_preset": {
                "prompt_id": request.prompt_preset.prompt_id,
                "title": request.prompt_preset.title,
                "summary_style": request.prompt_preset.summary_style,
                "target_media_kinds": list(request.prompt_preset.target_media_kinds),
            },
        },
        "artifacts": [
            {
                "path": artifact.path,
                "file_name": artifact.file_name,
                "media_kind": artifact.media_kind,
                "content_type": artifact.content_type,
                "camera_name": artifact.camera_name,
                "camera_access_point": artifact.camera_access_point,
                "captured_at": artifact.captured_at,
                "export_origin": artifact.export_origin,
                "size_bytes": artifact.size_bytes,
                "sha256": artifact.sha256,
            }
            for artifact in request.artifacts
        ],
        "provider": {
            "provider_id": provider.provider_id,
            "display_name": provider.display_name,
            "supported_media_kinds": list(provider.supported_media_kinds),
            "supports_async_jobs": provider.supports_async_jobs,
            "supports_dry_run": provider.supports_dry_run,
            "supports_prompt_presets": provider.supports_prompt_presets,
            "supports_audit_labels": provider.supports_audit_labels,
        },
        "envelope": request.envelope.as_log_context(),
        "decision": {
            "accepted": active_decision.accepted,
            "reasons": list(active_decision.reasons),
            "warnings": list(active_decision.warnings),
        },
        "job": {
            "status": effective_status,
            "provider_job_id": _text(provider_job_id) or None,
            "error": _text(error) or None,
            "dry_run": request.envelope.audit.dry_run,
        },
        "summary": summarize_external_analysis_findings(provider_payload or {}),
    }


__all__ = [
    "DEFAULT_EXTERNAL_ANALYSIS_PRIVACY_PROFILE",
    "DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_FIELDS",
    "DEFAULT_EXTERNAL_ANALYSIS_SUMMARY_STYLE",
    "EXTERNAL_ANALYSIS_MEDIA_KINDS",
    "ExternalAnalysisArtifact",
    "ExternalAnalysisPromptPreset",
    "ExternalAnalysisProviderAdapter",
    "ExternalAnalysisProviderCapability",
    "ExternalAnalysisRequest",
    "ExternalAnalysisSubmissionDecision",
    "build_external_analysis_artifact",
    "build_external_analysis_prompt_preset",
    "build_external_analysis_provider_capability",
    "build_external_analysis_request",
    "evaluate_external_analysis_submission",
    "shape_external_analysis_submission",
    "summarize_external_analysis_findings",
]
