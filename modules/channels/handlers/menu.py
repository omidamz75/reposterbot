from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['➕ افزودن کانال', '📋 لیست کانال‌ها'],
        ['❌ حذف کانال', '🔙 بازگشت']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👈 لطفا یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )
