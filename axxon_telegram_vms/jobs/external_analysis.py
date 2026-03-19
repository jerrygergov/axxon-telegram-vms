"""Pure external-analysis job records for future async provider runners."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

from axxon_telegram_vms.models import RequestEnvelope


EXTERNAL_ANALYSIS_JOB_STATES = (
    "planned",
    "dry_run",
    "queued",
    "submitted",
    "running",
    "succeeded",
    "failed",
)


def _text(value: object) -> str:
    return str(value or "").strip()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ExternalAnalysisJobRecord:
    request_id: str
    provider_id: str
    requested_surface: str
    requested_by: str | None = None
    artifact_count: int = 0
    state: str = "planned"
    audit_required: bool = True
    dry_run: bool = False
    created_at: str | None = None
    submitted_at: str | None = None
    finished_at: str | None = None
    provider_job_id: str | None = None
    summary: str | None = None
    error: str | None = None
    job_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        request_id = _text(self.request_id)
        provider_id = _text(self.provider_id)
        state = _text(self.state) or "planned"
        if not request_id:
            raise ValueError("request_id is required")
        if not provider_id:
            raise ValueError("provider_id is required")
        if state not in EXTERNAL_ANALYSIS_JOB_STATES:
            raise ValueError(f"Unsupported external analysis job state: {self.state}")
        if int(self.artifact_count) < 0:
            raise ValueError("artifact_count must be zero or greater")
        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "requested_surface", _text(self.requested_surface) or "telegram_bot")
        object.__setattr__(self, "requested_by", _text(self.requested_by) or None)
        object.__setattr__(self, "artifact_count", int(self.artifact_count))
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "created_at", _text(self.created_at) or None)
        object.__setattr__(self, "submitted_at", _text(self.submitted_at) or None)
        object.__setattr__(self, "finished_at", _text(self.finished_at) or None)
        object.__setattr__(self, "provider_job_id", _text(self.provider_job_id) or None)
        object.__setattr__(self, "summary", _text(self.summary) or None)
        object.__setattr__(self, "error", _text(self.error) or None)

    @property
    def terminal(self) -> bool:
        return self.state in {"dry_run", "succeeded", "failed"}


def build_external_analysis_job_record(
    *,
    envelope: RequestEnvelope,
    provider_id: object,
    artifact_count: int,
    state: str = "planned",
    provider_job_id: object = None,
    summary: object = None,
    error: object = None,
    now_provider: Callable[[], datetime] = _utc_now,
) -> ExternalAnalysisJobRecord:
    if not isinstance(envelope, RequestEnvelope):
        raise ValueError("envelope must be a RequestEnvelope")
    timestamp = now_provider().isoformat()
    submitted_at = timestamp if state in {"submitted", "running", "succeeded", "failed"} else None
    finished_at = timestamp if state in {"dry_run", "succeeded", "failed"} else None
    return ExternalAnalysisJobRecord(
        request_id=envelope.request_id,
        provider_id=_text(provider_id),
        requested_surface=envelope.surface,
        requested_by=envelope.actor.display_name,
        artifact_count=artifact_count,
        state=state,
        audit_required=envelope.audit.audit_required,
        dry_run=envelope.audit.dry_run,
        created_at=timestamp,
        submitted_at=submitted_at,
        finished_at=finished_at,
        provider_job_id=_text(provider_job_id) or None,
        summary=_text(summary) or None,
        error=_text(error) or None,
    )


def external_analysis_job_to_payload(record: ExternalAnalysisJobRecord) -> dict[str, Any]:
    return {
        "job_id": record.job_id,
        "request_id": record.request_id,
        "provider_id": record.provider_id,
        "requested_surface": record.requested_surface,
        "requested_by": record.requested_by,
        "artifact_count": record.artifact_count,
        "state": record.state,
        "audit_required": record.audit_required,
        "dry_run": record.dry_run,
        "created_at": record.created_at,
        "submitted_at": record.submitted_at,
        "finished_at": record.finished_at,
        "provider_job_id": record.provider_job_id,
        "summary": record.summary,
        "error": record.error,
        "terminal": record.terminal,
    }


__all__ = [
    "EXTERNAL_ANALYSIS_JOB_STATES",
    "ExternalAnalysisJobRecord",
    "build_external_analysis_job_record",
    "external_analysis_job_to_payload",
]
