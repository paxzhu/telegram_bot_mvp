from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from tg_bot.states import Form
from tg_bot.keyboards import build_main_menu
from tg_bot.utils import extract_handle, guard_errors
from tg_bot.core import fetch_posts, summarize
from tg_bot.i18n import tr

router = Router()

@router.callback_query(F.data == "recent")
@guard_errors
async def recent_menu(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_instagram)
    await call.message.answer(
        tr("ask_instagram", call.from_user.language_code)
    )
    await call.answer()

@router.message(Form.waiting_for_instagram)
@guard_errors
async def process_instagram(message: Message, state: FSMContext):
    handle = extract_handle(message.text or "")
    if not handle:
        await message.answer(tr("no_caption", message.from_user.language_code))
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

    try:
        posts = await fetch_posts(handle, limit=3)
    except Exception:
        await message.answer(tr("private_or_none", message.from_user.language_code))
        await state.clear()
        return

    if not posts:
        await message.answer(tr("no_posts", message.from_user.language_code))
        await state.clear()
        return

    summary = await summarize(posts, message.from_user.language_code)
    await message.answer(
        f"<b>@{handle}</b> {summary}",
        reply_markup=build_main_menu(message.from_user.language_code),
    )
    await state.clear()