from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from typing import Union

from tg_bot.states import Form
from tg_bot.core import memory_to_image
from tg_bot.utils import guard_errors
from tg_bot.keyboards import build_main_menu
from tg_bot.i18n import tr

router = Router()

@router.callback_query(F.data == "memory")
@guard_errors
async def memory_menu(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_memory)
    await call.message.answer(tr("ask_memory", call.from_user.language_code))
    await call.answer()

@router.message(Form.waiting_for_memory)
@guard_errors
async def process_memory(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer(tr("empty_memory_description", message.from_user.language_code))
        return
    
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_PHOTO,
    )

    try:
        img_path = await memory_to_image(text)
    except Exception:
        await message.answer(tr("image_generation_failed", message.from_user.language_code))
        await state.clear()
        return

    await message.answer_photo(
        FSInputFile(img_path),
        caption=tr("your_memory_img", message.from_user.language_code),
        reply_markup=build_main_menu(message.from_user.language_code),
    )
    await state.clear()