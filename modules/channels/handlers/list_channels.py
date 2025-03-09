import logging
from telegram import Update
from telegram.ext import ContextTypes
from core.database import SessionLocal
from modules.channels import services

logger = logging.getLogger(__name__)

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with SessionLocal() as db:
            channels = await services.ChannelService.get_user_channels(
                db=db,
                owner_id=update.effective_user.id
            )
            
        if not channels:
            await update.message.reply_text("شما هنوز کانالی اضافه نکرده‌اید.")
            return

        response = "📋 لیست کانال‌های شما:\n\n"
        for channel in channels:
            response += f"🆔 شناسه: {channel.permanent_id}\n"
            response += f"📺 عنوان: {channel.title}\n"
            response += f"🔗 لینک: {channel.username}\n"
            response += "➖➖➖➖➖➖➖➖\n"
        
        response += "\n💡 برای حذف کانال، شناسه آن را وارد کنید."
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error listing channels: {str(e)}")
        await update.message.reply_text("❌ خطا در نمایش لیست کانال‌ها")
