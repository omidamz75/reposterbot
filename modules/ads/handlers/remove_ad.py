import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.database import SessionLocal
from ..services import AdvertisementService
from .states import REMOVING_AD

logger = logging.getLogger(__name__)

async def remove_ad_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند حذف تبلیغ"""
    await update.message.reply_text(
        "🗑 برای حذف تبلیغ، شناسه آن را وارد کنید:\n"
        "💡 برای دیدن لیست تبلیغات و شناسه‌ها از دکمه 'لیست تبلیغات' استفاده کنید."
    )
    return REMOVING_AD

async def remove_ad_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف تبلیغ با شناسه"""
    try:
        ad_id = int(update.message.text)
        
        db = SessionLocal()
        try:
            success = await AdvertisementService.remove_advertisement(
                db=db,
                ad_id=ad_id,
                owner_id=update.effective_user.id
            )
            
            if success:
                await update.message.reply_text("✅ تبلیغ با موفقیت حذف شد!")
            else:
                await update.message.reply_text("❌ تبلیغ مورد نظر یافت نشد!")
            
            return ConversationHandler.END

        finally:
            db.close()

    except ValueError:
        await update.message.reply_text("❌ لطفاً یک شناسه معتبر وارد کنید!")
        return REMOVING_AD
    except Exception as e:
        logger.error(f"Error in remove_ad_finish: {str(e)}")
        await update.message.reply_text("❌ خطا در حذف تبلیغ. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END
