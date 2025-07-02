from aiogram import Router
from aiogram.filters.command import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from tg_bot.states import IntroFlow
from tg_bot.keyboards import build_main_menu
from tg_bot.i18n import tr

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "おはようございます。私は「るーちゃん」と申します。\n"
        "認知症の方や、将来の物忘れがご心配な方のお手伝いをするAIです。\n"
        "これから、どうぞよろしくお願いいたします。\n"
        "差し支えなければ、お名前を教えていただけますか？"
    )
    await state.set_state(IntroFlow.asking_name)

@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        tr("welcome", message.from_user.language_code),
        reply_markup=build_main_menu(message.from_user.language_code),
    )
