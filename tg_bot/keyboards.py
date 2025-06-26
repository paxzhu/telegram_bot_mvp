from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tg_bot.i18n import tr


def build_main_menu(lang_code: str | None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr("view_recent", lang_code), callback_data="recent")],
            [InlineKeyboardButton(text=tr("tell_memory", lang_code), callback_data="memory")],
        ]
    )

# 主菜单按钮翻译：注册到全局表
from tg_bot.i18n import _TRANSLATIONS  # type: ignore
_TRANSLATIONS["view_recent"] = ("🔎 查看近况", "🔎 近況を見る", "🔎 View recent")
_TRANSLATIONS["tell_memory"] = ("🖼️ 讲述回忆", "🖼️ 思い出を語る", "🖼️ Tell a memory")

__all__ = ["build_main_menu"]
