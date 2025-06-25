
from aiogram import Router
from aiogram.filters.command import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards import main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("你好！请选择功能：", reply_markup=main_menu)