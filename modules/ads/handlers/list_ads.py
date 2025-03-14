import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from core.database import SessionLocal
from ..services import AdvertisementService
from .menu import ads_menu  # اضافه کردن import

logger = logging.getLogger(__name__)

# States
CHOOSING_DISPLAY_TYPE = 1

async def list_ads_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند نمایش لیست تبلیغات"""
    keyboard = [
        ['📝 پیام متنی', '📄 فایل تکست'],
        ['🔙 بازگشت']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "📋 لطفا نحوه نمایش لیست تبلیغات را انتخاب کنید:",
        reply_markup=reply_markup
    )
    return CHOOSING_DISPLAY_TYPE

async def list_ads_display(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست تبلیغات به صورت متنی یا فایل"""
    try:
        display_type = update.message.text
        
        db = SessionLocal()
        try:
            ads = await AdvertisementService.get_user_advertisements(
                db=db,
                owner_id=update.effective_user.id
            )

            if not ads:
                await update.message.reply_text("❌ شما هنوز تبلیغی ثبت نکرده‌اید!")
                await ads_menu(update, context)  # بازگشت به منوی تبلیغات
                return ConversationHandler.END

            if display_type == "📝 پیام متنی":
                # نمایش به صورت پیام متنی
                response = "📋 لیست تبلیغات شما:\n\n"
                for ad in ads:
                    response += f"🆔 شناسه: {ad.id}\n"
                    response += f"📝 متن: {ad.content[:100]}...\n"
                    response += f"📅 تاریخ ایجاد: {ad.created_at}\n"
                    response += "➖➖➖➖➖➖➖➖\n"
                
                await update.message.reply_text(response)

            elif display_type == "📄 فایل تکست":
                # ارسال به صورت فایل متنی
                content = "لیست تبلیغات\n\n"
                for ad in ads:
                    content += f"شناسه: {ad.id}\n"
                    content += f"متن تبلیغ: {ad.content}\n"
                    content += f"نوع: {ad.type}\n"
                    content += f"تاریخ ایجاد: {ad.created_at}\n"
                    content += "─────────────────\n"

                with open("ads_list.txt", "w", encoding="utf-8") as f:
                    f.write(content)

                await update.message.reply_document(
                    document=open("ads_list.txt", "rb"),
                    filename="ads_list.txt",
                    caption="📄 لیست کامل تبلیغات"
                )
                import os
                os.remove("ads_list.txt")

            # بازگشت به منوی تبلیغات بعد از نمایش
            await ads_menu(update, context)
            return ConversationHandler.END

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in list_ads_display: {str(e)}")
        await update.message.reply_text("❌ خطا در نمایش لیست تبلیغات")
        await ads_menu(update, context)  # بازگشت به منوی تبلیغات در صورت خطا
        return ConversationHandler.END
