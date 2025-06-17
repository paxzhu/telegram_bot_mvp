#!/usr/bin/env python
import logging, os
from dotenv import load_dotenv
from telegram.ext import Application
from bot.handlers import build_handlers

load_dotenv()
logging.basicConfig(level=logging.INFO)

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing BOT_TOKEN in .env")

    app = Application.builder().token(token).build()
    build_handlers(app)          # 注册所有路由
    app.run_polling()            # 长轮询最快捷

if __name__ == "__main__":
    main()
