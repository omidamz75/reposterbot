from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import logging

async def ads_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show advertisement management menu"""
    try:
        keyboard = [
            ['📝 افزودن تبلیغ', '📋 لیست تبلیغات'],
            ['✏️ ویرایش تبلیغ', '❌ حذف تبلیغ'],
            ['🔙 بازگشت به منو']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "🎯 مدیریت تبلیغات\n"
            "👈 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error in ads_menu: {str(e)}")
        await update.message.reply_text("خطایی رخ داد. لطفا دوباره تلاش کنید.")
