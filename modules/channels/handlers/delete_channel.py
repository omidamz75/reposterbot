import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.database import SessionLocal
from modules.channels import services

logger = logging.getLogger(__name__)

# States
DELETING_CHANNEL = 1

async def delete_channel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with SessionLocal() as db:
            channels = await services.ChannelService.get_user_channels(
                db=db,
                owner_id=update.effective_user.id
            )
        
        if not channels:
            await update.message.reply_text("شما هیچ کانال فعالی ندارید.")
            return ConversationHandler.END

        response = "برای حذف کانال، کد مربوط به آن را وارد کنید:\n\n"
        for channel in channels:
            response += f"📺 {channel.title}\n"
            response += f"🔑 کد: {channel.channel_code}\n"
            response += "➖➖➖➖➖➖➖➖\n"
        
        await update.message.reply_text(response)
        return DELETING_CHANNEL

    except Exception as e:
        logger.error(f"Error in delete channel start: {str(e)}")
        await update.message.reply_text("خطایی رخ داد. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END

async def delete_channel_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        try:
            permanent_id = int(update.message.text.strip())
        except ValueError:
            await update.message.reply_text("❌ لطفاً یک شناسه معتبر وارد کنید!")
            return ConversationHandler.END

        with SessionLocal() as db:
            success = await services.ChannelService.remove_channel_by_id(
                db=db,
                permanent_id=permanent_id,
                owner_id=update.effective_user.id
            )
        
        if success:
            await update.message.reply_text("✅ کانال با موفقیت حذف شد!")
        else:
            await update.message.reply_text("❌ کانال مورد نظر یافت نشد!")
        
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in delete channel: {str(e)}")
        await update.message.reply_text("❌ خطا در حذف کانال. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END
