import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tg_bot import config
from tg_bot.handlers import start, recent, memory

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("tg-bot")

async def main() -> None:
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # 注册子路由
    dp.include_router(start.router)
    dp.include_router(recent.router)
    dp.include_router(memory.router)

    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")