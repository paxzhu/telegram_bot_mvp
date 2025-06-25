from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from typing import Union

from tg_bot.states import Form
from tg_bot.core import memory_to_image
from tg_bot.utils import guard_errors
from tg_bot.keyboards import main_menu

router = Router()

@router.callback_query(F.data == "memory")
@guard_errors
async def memory_menu(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_memory)
    await call.message.answer("请描述一段回忆，我会为你生成写实图像：")
    await call.answer()

@router.message(Form.waiting_for_memory)
@guard_errors
async def process_memory(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("⚠️ 描述不能为空，请重新输入。")
        return
    
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_PHOTO,
    )

    try:
        result: Union[bytes, str] = await memory_to_image(text)
    except Exception:
        await message.answer("❌ 图像生成失败，请稍后重试。", reply_markup=main_menu)
        await state.clear()
        return

    if isinstance(result, (bytes, bytearray)):
        photo = BufferedInputFile(result, filename="memory.jpg")
    else:
        photo = FSInputFile(result)

    await message.answer_photo(photo, caption="✨ 你的回忆图像已生成", reply_markup=main_menu)
    await state.clear()