import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from core.database import SessionLocal
from modules.channels import services

logger = logging.getLogger(__name__)

# States
ADDING_CHANNEL = 1

async def add_channel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "لطفاً ربات را ادمین کانال کرده و سپس آیدی کانال را به صورت @username یا لینک فوروارد پیام از کانال ارسال کنید."
    )
    return ADDING_CHANNEL

async def add_channel_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        channel_id = update.message.forward_from_chat.id if update.message.forward_from_chat \
            else update.message.text

        # Check if bot is admin
        is_admin = await services.ChannelService.check_bot_admin(context.bot, channel_id)
        if not is_admin:
            await update.message.reply_text("❌ لطفاً ابتدا ربات را ادمین کانال کنید!")
            return ConversationHandler.END

        with SessionLocal() as db:
            channel = await services.ChannelService.add_channel(
                db=db,
                channel_id=str(channel_id),
                title=update.message.forward_from_chat.title if update.message.forward_from_chat else channel_id,
                username=update.message.text,
                owner_id=update.effective_user.id
            )
        
        success_message = (
            "✅ کانال با موفقیت اضافه شد!\n"
            f"🔑 کد کانال شما: {channel.channel_code}\n"
            "این کد را برای حذف کانال نگه دارید."
        )
        await update.message.reply_text(success_message)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error adding channel: {str(e)}")
        await update.message.reply_text("❌ خطا در افزودن کانال. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END
