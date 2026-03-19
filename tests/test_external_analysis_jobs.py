from datetime import datetime, timezone
import unittest

from axxon_telegram_vms.jobs import build_external_analysis_job_record, external_analysis_job_to_payload
from axxon_telegram_vms.models import build_request_envelope


class ExternalAnalysisJobTests(unittest.TestCase):
    def test_job_record_tracks_audit_and_terminal_state(self):
        envelope = build_request_envelope(
            action="analysis",
            surface="future_api_service",
            actor_id="svc-1",
            display_name="analysis-api",
            dry_run=True,
        )

        record = build_external_analysis_job_record(
            envelope=envelope,
            provider_id="demo-vlm",
            artifact_count=2,
            state="dry_run",
            now_provider=lambda: datetime(2026, 3, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        payload = external_analysis_job_to_payload(record)

        self.assertEqual(record.request_id, envelope.request_id)
        self.assertEqual(record.finished_at, "2026-03-10T12:00:00+00:00")
        self.assertTrue(record.terminal)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["requested_by"], "analysis-api")


if __name__ == "__main__":
    unittest.main()
