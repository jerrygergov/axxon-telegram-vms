import unittest

from axxon_telegram_vms.models import build_request_envelope


class RequestEnvelopeTests(unittest.TestCase):
    def test_build_request_envelope_normalizes_actor_audit_tags_and_metadata(self):
        envelope = build_request_envelope(
            request_id="req-123",
            action="analysis",
            actor_id="42",
            username="operator",
            role="admin",
            session_id="sess-1",
            correlation_id="corr-1",
            dry_run=True,
            retention_hint="ephemeral",
            redact_fields=["face_crop", "face_crop"],
            tags=["export", "analysis", "Export"],
            metadata={"source": "single_camera_export", "nested": {"count": 2}},
        )

        self.assertEqual(envelope.request_id, "req-123")
        self.assertEqual(envelope.actor.display_name, "operator")
        self.assertEqual(envelope.audit.redact_fields, ("face_crop",))
        self.assertEqual(envelope.tags, ("export", "analysis"))

        context = envelope.as_log_context()
        self.assertEqual(context["actor"]["role"], "admin")
        self.assertTrue(context["audit"]["dry_run"])
        self.assertEqual(context["metadata"]["nested"]["count"], 2)

    def test_invalid_surface_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported request surface"):
            build_request_envelope(surface="desktop_app")


if __name__ == "__main__":
    unittest.main()
