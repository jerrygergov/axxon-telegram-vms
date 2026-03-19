import unittest
from pathlib import Path


class TelegramCommandsMenuTests(unittest.TestCase):
    def test_menu_registration_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("BotCommand(", src)
        self.assertIn("set_my_commands", src)
        self.assertIn("post_init(_register_telegram_commands)", src)
        self.assertIn("MessageHandler(filters.TEXT & ~filters.COMMAND, msg_text_shortcut)", src)

    def test_text_shortcuts_tolerate_spaced_slash_commands(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn('re.sub(r"^/\\s+", "/", raw)', src)
        self.assertIn('"/start": "cmd_start"', src)
        self.assertIn('"start": "cmd_start"', src)
        self.assertNotIn('"/home": "cmd_home"', src)

    def test_fast_home_mode_toggle_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn('UI_MODE_KEY = "ui_mode"', src)
        self.assertIn('"callback_data": f"mode:{next_mode}"', src)
        self.assertIn('if q.data.startswith("mode:")', src)
        self.assertIn('payload = _fallback_home_payload(mode=_get_ui_mode(context))', src)

    def test_stop_command_described(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn('BotCommand("stop", "stop all subscriptions or /stop <id>")', src)
        self.assertNotIn('BotCommand("stopall", "stop all subscriptions")', src)
        self.assertNotIn('BotCommand("cancel", "stop all subscriptions")', src)

    def test_search_command_present(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn('BotCommand("search", "time-range event search")', src)
        self.assertIn('CommandHandler("search", cmd_search)', src)
        self.assertIn('BotCommand("face", "upload photo or reply /face")', src)
        self.assertIn('CommandHandler("face", cmd_face)', src)
        self.assertIn('MessageHandler(filters.PHOTO | filters.Document.IMAGE, msg_face_upload)', src)
        self.assertIn('BotCommand("plate", "license plate search")', src)
        self.assertIn('CommandHandler("plate", cmd_plate)', src)
        self.assertIn('BotCommand("archive", "archive jump and preview")', src)
        self.assertIn('CommandHandler("archive", cmd_archive)', src)
        self.assertIn('BotCommand("export", "single-camera clip export")', src)
        self.assertIn('CommandHandler("export", cmd_export)', src)
        self.assertIn('CommandHandler("admin", cmd_admin)', src)
        self.assertIn('CommandHandler("macro", cmd_macro)', src)
        self.assertIn('CommandHandler("ptz", cmd_ptz)', src)

    def test_help_text_is_grouped_and_plain(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn("Monitor", src)
        self.assertIn("Search and archive", src)
        self.assertIn("Subscriptions", src)
        self.assertIn("Admin tools", src)
        self.assertIn("Settings", src)
        self.assertIn("/admin - read-only admin overview", src)
        self.assertIn("/face - face search for an uploaded photo or a replied photo", src)
        self.assertIn("(upload photo) send a Telegram photo", src)
        self.assertNotIn("entry/help surfaces", src)

    def test_removed_alias_handlers_absent(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertNotIn('CommandHandler("home", cmd_home)', src)
        self.assertNotIn('CommandHandler("stopall", cmd_stop_all)', src)
        self.assertNotIn('CommandHandler(["server", "serverinfo"], cmd_server)', src)
        self.assertNotIn('CommandHandler(["stats", "stat"], cmd_stats)', src)
        self.assertNotIn('CommandHandler("counterwatch", cmd_counterwatch)', src)
        self.assertNotIn('CommandHandler("counterstop", cmd_counterstop)', src)


if __name__ == "__main__":
    unittest.main()
