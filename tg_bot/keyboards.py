
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔎 查看近况", callback_data="recent")],
        [InlineKeyboardButton(text="🖼️ 讲述回忆", callback_data="memory")],
    ]
)

__all__ = ["main_menu"]