from aiogram import Router
from aiogram.filters.command import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards import build_main_menu
from tg_bot.i18n import tr

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        tr("welcome", message.from_user.language_code),
        reply_markup=build_main_menu(message.from_user.language_code),
    )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        tr("cancel_ok", message.from_user.language_code),
        reply_markup=build_main_menu(message.from_user.language_code),
    )
