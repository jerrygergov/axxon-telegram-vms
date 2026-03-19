import unittest

from axxon_telegram_vms.models import build_request_envelope
from axxon_telegram_vms.services import (
    build_external_analysis_artifact,
    build_external_analysis_prompt_preset,
    build_external_analysis_provider_capability,
    build_external_analysis_request,
    evaluate_external_analysis_submission,
    shape_external_analysis_submission,
    summarize_external_analysis_findings,
)


class ExternalAnalysisServiceTests(unittest.TestCase):
    def test_request_and_submission_shape_cover_dry_run_audit_and_summary(self):
        request = build_external_analysis_request(
            provider_id="demo-vlm",
            artifacts=[
                build_external_analysis_artifact(
                    path="/tmp/export-clip.mp4",
                    media_kind="clip",
                    camera_name="1.Gate",
                    camera_access_point="hosts/A/DeviceIpint.1/SourceEndpoint.video:0:0",
                    export_origin="single_camera_export",
                    size_bytes=4096,
                )
            ],
            prompt_preset=build_external_analysis_prompt_preset(
                prompt_id="operator_incident_summary",
                title="Incident summary",
                instruction="Summarize operator-visible activity in the clip.",
                target_media_kinds=["clip"],
            ),
            envelope=build_request_envelope(
                action="analysis",
                actor_id="7",
                username="operator",
                dry_run=True,
                tags=["export", "vlm"],
            ),
            operator_note="Focus on ingress activity",
        )
        provider = build_external_analysis_provider_capability(
            provider_id="demo-vlm",
            display_name="Demo VLM",
            supported_media_kinds=["clip"],
            supports_async_jobs=True,
            supports_dry_run=True,
        )

        decision = evaluate_external_analysis_submission(request, provider)
        shaped = shape_external_analysis_submission(
            request,
            provider,
            decision=decision,
            provider_job_id="job-55",
            provider_payload={
                "findings": [
                    {"label": "person", "confidence": 0.91},
                    {"label": "vehicle", "confidence": 0.62},
                ]
            },
        )

        self.assertTrue(decision.accepted)
        self.assertEqual(shaped["job"]["status"], "dry_run")
        self.assertEqual(shaped["request"]["artifact_count"], 1)
        self.assertEqual(shaped["summary"]["finding_count"], 2)
        self.assertIn("person", shaped["summary"]["text"])
        self.assertTrue(shaped["envelope"]["audit"]["dry_run"])

    def test_provider_rejection_is_truthful_for_unsupported_media_and_dry_run(self):
        request = build_external_analysis_request(
            provider_id="image-only",
            artifacts=[{"path": "/tmp/frame.jpg", "media_kind": "image"}],
            prompt_preset={
                "prompt_id": "frame_summary",
                "title": "Frame summary",
                "instruction": "Summarize visible entities.",
                "target_media_kinds": ["image"],
            },
            envelope=build_request_envelope(action="analysis", dry_run=True),
        )
        provider = build_external_analysis_provider_capability(
            provider_id="image-only",
            display_name="Image-only provider",
            supported_media_kinds=["image"],
            supports_async_jobs=False,
            supports_dry_run=False,
        )

        decision = evaluate_external_analysis_submission(request, provider)

        self.assertFalse(decision.accepted)
        self.assertIn("async job handling", decision.reasons[0])
        self.assertIn("dry-run support", decision.reasons[1])

    def test_findings_summary_handles_empty_payload(self):
        summary = summarize_external_analysis_findings({})
        self.assertEqual(summary["finding_count"], 0)
        self.assertEqual(summary["text"], "No findings returned")


if __name__ == "__main__":
    unittest.main()
