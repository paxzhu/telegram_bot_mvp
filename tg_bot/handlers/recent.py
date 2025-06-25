from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from tg_bot.states import Form
from tg_bot.keyboards import main_menu
from tg_bot.utils import extract_handle, guard_errors
from tg_bot.core import fetch_posts, summarize

router = Router()

@router.callback_query(F.data == "recent")
@guard_errors
async def recent_menu(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_instagram)
    await call.message.answer("请输入 Instagram 用户名或带 @ 的句子：")
    await call.answer()

@router.message(Form.waiting_for_instagram)
@guard_errors
async def process_instagram(message: Message, state: FSMContext):
    handle = extract_handle(message.text or "")
    if not handle:
        await message.answer("⚠️ 未识别用户名，请重新输入，例如：@natgeo")
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

    try:
        posts = await fetch_posts(handle, limit=3)
    except Exception:
        await message.answer("❌ 账号不存在或为私密账号。", reply_markup=main_menu)
        await state.clear()
        return

    if not posts:
        await message.answer("⚠️ 没获取到最近贴文，也许账号为空或受限。", reply_markup=main_menu)
        await state.clear()
        return

    summary = await summarize(posts)
    await message.answer(f"<b>@{handle}</b> 最近动态：\n{summary}", reply_markup=main_menu)
    await state.clear()