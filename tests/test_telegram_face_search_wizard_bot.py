import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import sys
import types
from pathlib import Path


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


class _FakeChat:
    def __init__(self):
        self.id = 77
        self.messages: list[dict[str, object]] = []

    async def send_message(self, text: str, reply_markup=None):
        self.messages.append({"text": text, "reply_markup": reply_markup})
        return SimpleNamespace(message_id=len(self.messages))


class _FakeCallbackQuery:
    def __init__(self, data: str):
        self.data = data
        self.message = SimpleNamespace(chat_id=77, message_id=701, photo=None, video=None)
        self.answers: list[dict[str, object]] = []
        self.edits: list[dict[str, object]] = []

    async def answer(self, text: str | None = None, show_alert: bool = False):
        self.answers.append({"text": text, "show_alert": show_alert})

    async def edit_message_text(self, text: str, reply_markup=None):
        self.edits.append({"text": text, "reply_markup": reply_markup})


class TelegramFaceSearchWizardBotTests(unittest.IsolatedAsyncioTestCase):
    async def test_cmd_face_enters_pending_mode_and_prompts_for_upload(self):
        chat = _FakeChat()
        update = SimpleNamespace(
            effective_message=SimpleNamespace(photo=[], document=None, caption="", reply_to_message=None),
            effective_chat=chat,
            effective_user=SimpleNamespace(id=42),
        )
        context = SimpleNamespace(user_data={}, bot=SimpleNamespace(), args=[])

        with patch.object(axxon_tg_bot, "_guard", AsyncMock(return_value=True)):
            await axxon_tg_bot.cmd_face(update, context)

        self.assertIn(axxon_tg_bot.FACE_SEARCH_PENDING_KEY, context.user_data)
        self.assertIn("Upload a face photo.", chat.messages[-1]["text"])
        self.assertIn("Requirements:", chat.messages[-1]["text"])

    async def test_msg_face_upload_starts_wizard_for_pending_plain_photo(self):
        chat = _FakeChat()
        update = SimpleNamespace(
            effective_message=SimpleNamespace(
                photo=[SimpleNamespace(file_id="photo-1")],
                document=None,
                caption="",
                reply_to_message=None,
            ),
            effective_chat=chat,
            effective_user=SimpleNamespace(id=42),
        )
        context = SimpleNamespace(user_data={axxon_tg_bot.FACE_SEARCH_PENDING_KEY: {"terms": []}}, bot=SimpleNamespace())

        with patch.object(axxon_tg_bot, "_guard", AsyncMock(return_value=True)):
            await axxon_tg_bot.msg_face_upload(update, context)

        wizard = context.user_data[axxon_tg_bot.FACE_SEARCH_WIZARD_KEY]
        self.assertEqual(wizard["file_id"], "photo-1")
        self.assertEqual(wizard["terms"], [])
        self.assertNotIn(axxon_tg_bot.FACE_SEARCH_PENDING_KEY, context.user_data)
        self.assertEqual(len(chat.messages), 1)
        self.assertIn("Choose similarity.", chat.messages[0]["text"])
        keyboard = chat.messages[0]["reply_markup"].inline_keyboard
        self.assertEqual([button.text for button in keyboard[0]], ["90%", "85%"])
        self.assertEqual([button.text for button in keyboard[1]], ["80%", "✖ Cancel"])

    async def test_face_search_callback_moves_to_period_step(self):
        query = _FakeCallbackQuery("facewiz:acc:3:85")
        context = SimpleNamespace(
            user_data={
                axxon_tg_bot.FACE_SEARCH_WIZARD_KEY: {
                    "draft_id": "3",
                    "file_id": "photo-1",
                    "suffix": ".jpg",
                    "terms": ["camera=1.Lobby"],
                }
            },
            bot=SimpleNamespace(),
        )
        update = SimpleNamespace(
            callback_query=query,
            effective_chat=_FakeChat(),
            effective_user=SimpleNamespace(id=42),
        )

        handled = await axxon_tg_bot._handle_face_search_callback(update, context, query.data)

        self.assertTrue(handled)
        self.assertEqual(
            context.user_data[axxon_tg_bot.FACE_SEARCH_WIZARD_KEY]["accuracy_percent"],
            85,
        )
        self.assertIn("Choose period.", query.edits[-1]["text"])
        keyboard = query.edits[-1]["reply_markup"].inline_keyboard
        self.assertEqual([button.text for button in keyboard[0]], ["15m", "1h"])
        self.assertEqual([button.text for button in keyboard[-1]], ["⬅ Back", "✖ Cancel"])

    async def test_face_search_callback_back_returns_to_similarity_step(self):
        query = _FakeCallbackQuery("facewiz:back:3")
        context = SimpleNamespace(
            user_data={
                axxon_tg_bot.FACE_SEARCH_WIZARD_KEY: {
                    "draft_id": "3",
                    "file_id": "photo-1",
                    "suffix": ".jpg",
                    "terms": ["camera=1.Lobby"],
                    "accuracy_percent": 85,
                }
            },
            bot=SimpleNamespace(),
        )
        update = SimpleNamespace(
            callback_query=query,
            effective_chat=_FakeChat(),
            effective_user=SimpleNamespace(id=42),
        )

        handled = await axxon_tg_bot._handle_face_search_callback(update, context, query.data)

        self.assertTrue(handled)
        self.assertNotIn(
            "accuracy_percent",
            context.user_data[axxon_tg_bot.FACE_SEARCH_WIZARD_KEY],
        )
        self.assertIn("Choose similarity.", query.edits[-1]["text"])

    async def test_face_search_callback_runs_search_with_selected_presets(self):
        query = _FakeCallbackQuery("facewiz:last:3:3600")
        context = SimpleNamespace(
            user_data={
                axxon_tg_bot.FACE_SEARCH_WIZARD_KEY: {
                    "draft_id": "3",
                    "file_id": "photo-1",
                    "suffix": ".jpg",
                    "terms": ["camera=1.Lobby"],
                    "accuracy_percent": 85,
                }
            },
            bot=SimpleNamespace(),
        )
        update = SimpleNamespace(
            callback_query=query,
            effective_chat=_FakeChat(),
            effective_user=SimpleNamespace(id=42),
        )

        with patch.object(axxon_tg_bot, "_run_face_search", AsyncMock()) as run_face_search:
            handled = await axxon_tg_bot._handle_face_search_callback(update, context, query.data)

        self.assertTrue(handled)
        self.assertNotIn(axxon_tg_bot.FACE_SEARCH_WIZARD_KEY, context.user_data)
        self.assertIn("Running search...", query.edits[0]["text"])
        run_face_search.assert_awaited_once()
        kwargs = run_face_search.await_args.kwargs
        self.assertEqual(kwargs["terms"], ["camera=1.Lobby", "accuracy=0.85", "last=3600"])
        self.assertEqual(kwargs["reference_file_id"], "photo-1")
        self.assertEqual(kwargs["reference_suffix"], ".jpg")
        self.assertTrue(kwargs["edit"])

    async def test_face_search_callback_cancel_clears_pending_state(self):
        query = _FakeCallbackQuery("facewiz:cancel:3")
        context = SimpleNamespace(
            user_data={
                axxon_tg_bot.FACE_SEARCH_WIZARD_KEY: {
                    "draft_id": "3",
                    "file_id": "photo-1",
                    "suffix": ".jpg",
                    "terms": [],
                }
            },
            bot=SimpleNamespace(),
        )
        update = SimpleNamespace(
            callback_query=query,
            effective_chat=_FakeChat(),
            effective_user=SimpleNamespace(id=42),
        )

        handled = await axxon_tg_bot._handle_face_search_callback(update, context, query.data)

        self.assertTrue(handled)
        self.assertNotIn(axxon_tg_bot.FACE_SEARCH_WIZARD_KEY, context.user_data)
        self.assertEqual(query.edits[-1]["text"], "🙂 Face search canceled.")

    async def test_manual_threshold_text_moves_wizard_to_period_step(self):
        chat = _FakeChat()
        update = SimpleNamespace(
            effective_message=SimpleNamespace(text="87%"),
            effective_chat=chat,
            effective_user=SimpleNamespace(id=42),
        )
        context = SimpleNamespace(
            user_data={
                axxon_tg_bot.FACE_SEARCH_WIZARD_KEY: {
                    "draft_id": "5",
                    "file_id": "photo-1",
                    "suffix": ".jpg",
                    "terms": ["camera=1.Lobby"],
                }
            },
            bot=SimpleNamespace(),
        )

        await axxon_tg_bot.msg_text_shortcut(update, context)

        self.assertEqual(context.user_data[axxon_tg_bot.FACE_SEARCH_WIZARD_KEY]["accuracy_percent"], 87)
        self.assertIn("Choose period.", chat.messages[-1]["text"])

    async def test_manual_threshold_text_reprompts_on_invalid_value(self):
        chat = _FakeChat()
        update = SimpleNamespace(
            effective_message=SimpleNamespace(text="banana"),
            effective_chat=chat,
            effective_user=SimpleNamespace(id=42),
        )
        context = SimpleNamespace(
            user_data={
                axxon_tg_bot.FACE_SEARCH_WIZARD_KEY: {
                    "draft_id": "5",
                    "file_id": "photo-1",
                    "suffix": ".jpg",
                    "terms": [],
                }
            },
            bot=SimpleNamespace(),
        )

        await axxon_tg_bot.msg_text_shortcut(update, context)

        self.assertIn("Enter similarity as 90, 87, 0.87, or 87%.", chat.messages[-1]["text"])


if __name__ == "__main__":
    unittest.main()
