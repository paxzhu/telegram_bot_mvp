#!/usr/bin/env python
import logging, os
from dotenv import load_dotenv
from telegram.ext import Application
from bot.handlers import build_handlers

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing BOT_TOKEN in .env")

    app = Application.builder().token(token).build()
    build_handlers(app)          
    
    logger = logging.getLogger(__name__)
    logger.info("Bot is starting...")
    logger.info("Using Telegram API for long polling")
    
    app.run_polling()            

if __name__ == "__main__":
    main()
