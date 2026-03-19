import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


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


class _FakeQuery:
    def __init__(self, data: str):
        self.data = data
        self.message = SimpleNamespace(chat_id=77, message_id=88, photo=None, video=None)
        self.answers: list[dict[str, object]] = []
        self.edits: list[dict[str, object]] = []

    async def answer(self, text: str | None = None, show_alert: bool = False):
        self.answers.append({"text": text, "show_alert": show_alert})

    async def edit_message_text(self, text: str, reply_markup=None):
        self.edits.append({"text": text, "reply_markup": reply_markup})


class SubscriptionUserFeedbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_on_callback_empty_subscription_list_offers_next_step(self):
        query = _FakeQuery("sub:list")
        update = SimpleNamespace(
            callback_query=query,
            effective_user=SimpleNamespace(id=42),
            effective_chat=SimpleNamespace(id=77),
        )
        context = SimpleNamespace(user_data={})

        with patch.object(axxon_tg_bot, "_guard", AsyncMock(return_value=True)), \
             patch.object(axxon_tg_bot, "_handle_ptz_callback", AsyncMock(return_value=False)), \
             patch.object(axxon_tg_bot, "_handle_macro_callback", AsyncMock(return_value=False)), \
             patch.object(axxon_tg_bot, "_handle_face_search_callback", AsyncMock(return_value=False)), \
             patch.object(axxon_tg_bot, "_handle_subscription_callback", AsyncMock(return_value=False)), \
             patch.object(axxon_tg_bot, "_is_live_subscription_alert_callback", return_value=False), \
             patch.object(axxon_tg_bot, "_get_user_timezone", return_value="UTC"), \
             patch.object(axxon_tg_bot.SUBSCRIPTIONS, "list_subscriptions", return_value=[]):
            await axxon_tg_bot.on_callback(update, context)

        self.assertTrue(query.edits)
        self.assertIn("Use Subscribe to create one", query.edits[-1]["text"])
        self.assertEqual(query.edits[-1]["reply_markup"].inline_keyboard[0][0].text, "🔔 Create")


if __name__ == "__main__":
    unittest.main()
