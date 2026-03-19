import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


if "telegram" not in sys.modules:
    telegram = types.ModuleType("telegram")
    telegram_ext = types.ModuleType("telegram.ext")

    class BotCommand:
        def __init__(self, command, description):
            self.command = command
            self.description = description

    class InlineKeyboardButton:
        def __init__(self, text, callback_data=None, url=None):
            self.text = text
            self.callback_data = callback_data
            self.url = url

    class InlineKeyboardMarkup:
        def __init__(self, inline_keyboard):
            self.inline_keyboard = inline_keyboard

    class InputMediaPhoto:
        def __init__(self, media=None, caption=None):
            self.media = media
            self.caption = caption

    class Update:
        pass

    class _ContextTypes:
        DEFAULT_TYPE = object

    class _DummyHandler:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    telegram.BotCommand = BotCommand
    telegram.InlineKeyboardButton = InlineKeyboardButton
    telegram.InlineKeyboardMarkup = InlineKeyboardMarkup
    telegram.InputMediaPhoto = InputMediaPhoto
    telegram.Update = Update
    telegram_ext.Application = object
    telegram_ext.CallbackQueryHandler = _DummyHandler
    telegram_ext.CommandHandler = _DummyHandler
    telegram_ext.ContextTypes = _ContextTypes
    telegram_ext.MessageHandler = _DummyHandler
    telegram_ext.filters = SimpleNamespace(PHOTO=object(), Document=SimpleNamespace(IMAGE=object()))
    sys.modules["telegram"] = telegram
    sys.modules["telegram.ext"] = telegram_ext

import scripts.axxon_tg_bot as axxon_tg_bot
from scripts.process_bridge import CommandExecutionError


class BotFailurePayloadTests(unittest.TestCase):
    def test_ui_error_payload_keeps_section_and_home_buttons(self):
        payload = axxon_tg_bot._ui_error_payload("server")
        callbacks = [button["callback_data"] for row in payload["buttons"] for button in row]
        self.assertIn("srv:menu", callbacks)
        self.assertIn("home", callbacks)
        self.assertIn("Server", payload["text"])

    def test_run_ui_payload_or_error_returns_recoverable_payload(self):
        with patch.object(
            axxon_tg_bot,
            "run_ui",
            side_effect=CommandExecutionError("backend unavailable", command=["tool"], timeout_sec=25),
        ):
            payload = axxon_tg_bot._run_ui_payload_or_error(
                "callback",
                "--seconds",
                "1800",
                "--data",
                "ev:feed:0",
                tz="UTC",
                section="events",
            )

        callbacks = [button["callback_data"] for row in payload["buttons"] for button in row]
        self.assertIn("ev:feed:0", callbacks)
        self.assertIn("home", callbacks)
        self.assertIn("Events", payload["text"])


if __name__ == "__main__":
    unittest.main()
