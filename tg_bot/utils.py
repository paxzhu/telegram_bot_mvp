import re
import logging
from functools import wraps
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger("tg-bot")

_HANDLE_RE = re.compile(r"@?([A-Za-z0-9._]+)")

def extract_handle(text: str) -> str | None:
    """从文本中提取 Instagram handle（无 @）。"""
    m = _HANDLE_RE.search(text)
    return m.group(1) if m else None

def guard_errors(func):
    """捕获异常并回复用户，不让 bot 崩溃。"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception("handler error: %s", e)
            obj = args[0]
            target = obj.message if isinstance(obj, CallbackQuery) else obj  # type: ignore
            await target.answer("⚠️ 系统繁忙，请稍后再试")
    return wrapper

__all__ = ["extract_handle", "guard_errors"]