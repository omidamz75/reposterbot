import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.database import SessionLocal
from ..services import AdvertisementService
from .states import ADDING_CONTENT, ADDING_MEDIA

logger = logging.getLogger(__name__)

async def add_ad_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند اضافه کردن تبلیغ"""
    await update.message.reply_text(
        "📝 لطفاً متن تبلیغ خود را ارسال کنید:\n"
        "💡 برای لغو از دکمه 'بازگشت' استفاده کنید."
    )
    return ADDING_CONTENT

async def add_ad_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت متن تبلیغ"""
    context.user_data['ad_content'] = update.message.text
    await update.message.reply_text(
        "🖼 حالا می‌توانید فایل رسانه (عکس/ویدیو) را ارسال کنید.\n"
        "📝 یا اگر تبلیغ فقط متنی است، /skip را بزنید."
    )
    return ADDING_MEDIA

async def add_ad_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت رسانه تبلیغ و ذخیره نهایی"""
    try:
        content = context.user_data.get('ad_content', '')
        media_id = None
        ad_type = 'text'

        # تشخیص نوع رسانه
        if update.message.photo:
            media_id = update.message.photo[-1].file_id
            ad_type = 'photo'
        elif update.message.video:
            media_id = update.message.video.file_id
            ad_type = 'video'
        elif update.message.animation:
            media_id = update.message.animation.file_id
            ad_type = 'animation'
        elif update.message.text == '/skip':
            ad_type = 'text'

        # ذخیره تبلیغ با استفاده صحیح از session
        db = SessionLocal()
        try:
            ad = await AdvertisementService.add_advertisement(
                db=db,
                content=content,
                ad_type=ad_type,
                media_id=media_id,
                owner_id=update.effective_user.id
            )
            
            await update.message.reply_text(
                f"✅ تبلیغ با موفقیت ذخیره شد!\n"
                f"🆔 شناسه تبلیغ: {ad.id}\n"
                f"💡 از این شناسه برای ویرایش یا حذف تبلیغ استفاده کنید."
            )
        finally:
            db.close()

        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in add_ad_media: {str(e)}")
        await update.message.reply_text("❌ خطا در ذخیره تبلیغ. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END
