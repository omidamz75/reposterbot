import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.database import SessionLocal
from ..services import AdvertisementService
from .states import WAITING_FOR_AD_ID, EDITING_CONTENT, EDITING_MEDIA

logger = logging.getLogger(__name__)

async def edit_ad_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند ویرایش تبلیغ"""
    await update.message.reply_text(
        "✏️ برای ویرایش تبلیغ، شناسه آن را وارد کنید:\n"
        "💡 می‌توانید از دستور /list برای دیدن لیست تبلیغات استفاده کنید."
    )
    return WAITING_FOR_AD_ID

async def edit_ad_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت شناسه تبلیغ و نمایش محتوای فعلی"""
    try:
        ad_id = int(update.message.text)
        db = SessionLocal()
        try:
            ad = await AdvertisementService.get_advertisement_by_id(
                db=db,
                ad_id=ad_id,
                owner_id=update.effective_user.id
            )
            
            if not ad:
                await update.message.reply_text("❌ تبلیغ مورد نظر یافت نشد!")
                return ConversationHandler.END
            
            context.user_data['editing_ad_id'] = ad_id
            
            # نمایش محتوای فعلی تبلیغ
            await update.message.reply_text(
                f"📝 محتوای فعلی تبلیغ:\n\n{ad.content}\n\n"
                "✏️ محتوای جدید را وارد کنید:"
            )
            
            # نمایش رسانه فعلی اگر وجود دارد
            if ad.media_id:
                if ad.type == 'photo':
                    await update.message.reply_photo(ad.media_id, caption="🖼 تصویر فعلی تبلیغ")
                elif ad.type == 'video':
                    await update.message.reply_video(ad.media_id, caption="🎥 ویدیوی فعلی تبلیغ")
                elif ad.type == 'animation':
                    await update.message.reply_animation(ad.media_id, caption="🎞 انیمیشن فعلی تبلیغ")
            
            return EDITING_CONTENT
            
        finally:
            db.close()
            
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک شناسه معتبر وارد کنید!")
        return WAITING_FOR_AD_ID
    except Exception as e:
        logger.error(f"Error in edit_ad_get_content: {str(e)}")
        await update.message.reply_text("❌ خطا در دریافت اطلاعات تبلیغ. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END

async def edit_ad_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره محتوای جدید و درخواست رسانه"""
    context.user_data['new_content'] = update.message.text
    await update.message.reply_text(
        "🖼 اگر می‌خواهید رسانه تبلیغ را تغییر دهید، آن را ارسال کنید.\n"
        "یا برای حفظ رسانه فعلی، /skip را بزنید."
    )
    return EDITING_MEDIA

async def edit_ad_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره نهایی تغییرات تبلیغ"""
    try:
        ad_id = context.user_data.get('editing_ad_id')
        new_content = context.user_data.get('new_content')
        
        media_id = None
        ad_type = None
        
        if update.message.photo:
            media_id = update.message.photo[-1].file_id
            ad_type = 'photo'
        elif update.message.video:
            media_id = update.message.video.file_id
            ad_type = 'video'
        elif update.message.animation:
            media_id = update.message.animation.file_id
            ad_type = 'animation'
        
        db = SessionLocal()
        try:
            updated_ad = await AdvertisementService.update_advertisement(
                db=db,
                ad_id=ad_id,
                owner_id=update.effective_user.id,
                content=new_content,
                ad_type=ad_type if media_id else None,
                media_id=media_id
            )
            
            if updated_ad:
                await update.message.reply_text("✅ تبلیغ با موفقیت ویرایش شد!")
            else:
                await update.message.reply_text("❌ خطا در ویرایش تبلیغ!")
        finally:
            db.close()
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in edit_ad_media: {str(e)}")
        await update.message.reply_text("❌ خطا در ویرایش تبلیغ. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END
