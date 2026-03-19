import unittest
from types import SimpleNamespace

from axxon_telegram_vms.ui.telegram_face_search import (
    build_face_search_wizard_period_buttons,
    build_face_search_wizard_terms,
    build_face_search_wizard_threshold_buttons,
    face_reference_attachment,
    face_search_terms_support_wizard,
    format_face_search_wizard_period_label,
    parse_face_command_terms,
    parse_face_search_wizard_callback,
    should_start_face_search_from_upload,
)


class TelegramFaceSearchHelperTests(unittest.TestCase):
    def test_parse_face_command_terms_accepts_bot_suffix_and_multiline_terms(self):
        self.assertEqual(
            parse_face_command_terms("/face@TestBot camera=1.Lobby\nlast=7200"),
            ["camera=1.Lobby", "last=7200"],
        )

    def test_parse_face_command_terms_rejects_other_commands(self):
        self.assertIsNone(parse_face_command_terms("/search camera=1.Lobby"))

    def test_face_reference_attachment_uses_photo_or_reply_photo(self):
        reply = SimpleNamespace(photo=[SimpleNamespace(file_id="reply-photo")], document=None)
        message = SimpleNamespace(photo=[], document=None, reply_to_message=reply)
        self.assertEqual(face_reference_attachment(message), ("reply-photo", ".jpg"))

    def test_should_start_face_search_from_upload_for_plain_photo(self):
        message = SimpleNamespace(
            photo=[SimpleNamespace(file_id="photo-1")],
            document=None,
            caption="",
            reply_to_message=None,
        )
        self.assertEqual(should_start_face_search_from_upload(message), (True, []))

    def test_should_start_face_search_from_upload_for_face_caption(self):
        message = SimpleNamespace(
            photo=[],
            document=SimpleNamespace(file_id="doc-1", mime_type="image/jpeg", file_name="reference.jpg"),
            caption="/face camera=1.Lobby last=7200",
            reply_to_message=None,
        )
        self.assertEqual(
            should_start_face_search_from_upload(message),
            (True, ["camera=1.Lobby", "last=7200"]),
        )

    def test_should_not_start_face_search_for_non_face_caption(self):
        message = SimpleNamespace(
            photo=[SimpleNamespace(file_id="photo-1")],
            document=None,
            caption="evidence image",
            reply_to_message=None,
        )
        self.assertEqual(should_start_face_search_from_upload(message), (False, []))

    def test_face_search_terms_support_wizard_only_for_scope_terms(self):
        self.assertTrue(face_search_terms_support_wizard([]))
        self.assertTrue(face_search_terms_support_wizard(["camera=1.Lobby", "detector=Face"]))
        self.assertFalse(face_search_terms_support_wizard(["accuracy=0.82"]))
        self.assertFalse(face_search_terms_support_wizard(["last=7200"]))
        self.assertFalse(face_search_terms_support_wizard(["from=20260310T080000", "to=20260310T090000"]))

    def test_build_face_search_wizard_terms_keeps_scope_and_adds_presets(self):
        self.assertEqual(
            build_face_search_wizard_terms(
                ["camera=1.Lobby", "detector=Face", "last=7200"],
                accuracy_percent=85,
                period_seconds=3600,
            ),
            ["camera=1.Lobby", "detector=Face", "accuracy=0.85", "last=3600"],
        )

    def test_face_search_wizard_buttons_stay_short_and_parse_callbacks(self):
        threshold_buttons = build_face_search_wizard_threshold_buttons("7")
        period_buttons = build_face_search_wizard_period_buttons("7")
        acc_callback = parse_face_search_wizard_callback("facewiz:acc:7:85")
        period_callback = parse_face_search_wizard_callback("facewiz:last:7:3600")

        self.assertEqual([button["text"] for button in threshold_buttons[0]], ["90%", "85%"])
        self.assertEqual([button["text"] for button in period_buttons[-1]], ["⬅ Back", "✖ Cancel"])
        self.assertIsNotNone(acc_callback)
        self.assertEqual((acc_callback.action, acc_callback.draft_id, acc_callback.value), ("acc", "7", "85"))
        self.assertIsNotNone(period_callback)
        self.assertEqual((period_callback.action, period_callback.draft_id, period_callback.value), ("last", "7", "3600"))
        self.assertEqual(format_face_search_wizard_period_label(21600), "6h")


if __name__ == "__main__":
    unittest.main()
