from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def scheduler_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی اصلی زمان‌بندی"""
    keyboard = [
        ['⚙️ تنظیم زمان‌بندی', '📋 لیست زمان‌بندی‌ها'],
        ['✏️ ویرایش زمان‌بندی', '❌ حذف زمان‌بندی'],
        ['▶️ شروع زمان‌بندی', '⏹ توقف زمان‌بندی'],
        ['🔙 بازگشت به منو']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "⏰ مدیریت زمان‌بندی\n"
        "👈 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )
