from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
)
from telegram.ext import (
    CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, Application
)
from . import instagram, memory
import logging
logger = logging.getLogger(__name__)

CHECK, STORY = "CHECK", "STORY"   # CallbackData / user_data mode keys

def build_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📸 查看近况", callback_data=CHECK),
        InlineKeyboardButton("🖼 讲述我的回忆", callback_data=STORY)
    ]])
    await update.message.reply_text("请选择功能：", reply_markup=kb)

async def menu_click(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    ctx.user_data["mode"] = data
    await update.callback_query.answer()
    prompt = "请输入 Instagram 用户名（含 @）：" if data == CHECK else "请描述一段回忆："
    await update.callback_query.edit_message_text(prompt)

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    mode = ctx.user_data.get("mode")
    text = update.message.text.strip()

    if mode == CHECK and text.startswith("@"):
        summary = instagram.summarize(text)
        if summary:
            await update.message.reply_text(summary)
        else:
            await update.message.reply_text("⚠️ 暂无公开动态（假数据）。")
        return

    # 默认为 STORY
    img_path = memory.generate_image_path(text)
    logger.info(f"Generated image path: {img_path}")
    with open(img_path, 'rb') as photo:
        await update.message.reply_photo(
            photo=InputFile(photo),
            caption="示例图（假数据）"
        )
