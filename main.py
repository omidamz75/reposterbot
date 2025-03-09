import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext

# تنظیم سطح لاگ به WARNING برای کاهش پیام‌های اضافی
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

# فقط لاگ‌های خودمون رو در سطح INFO نمایش میدیم
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    try:
        # لاگ برای شروع فرایند
        logger.info("Starting the start_command handler")
        
        if not update or not update.message:
            logger.error("Update or message is None")
            return

        user = update.effective_user
        logger.info(f"Processing start command for user {user.id}")

        # ساخت کیبورد
        keyboard = [
            ['📊 مدیریت تبلیغات', '📈 مدیریت کانال‌ها'],
            ['⚙️ تنظیمات', '📋 راهنما']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # ارسال پیام اصلی
        welcome_text = (
            f"👋 سلام {user.first_name} عزیز!\n\n"
            "🤖 به ربات مدیریت تبلیغات و ریپوست خوش آمدید.\n"
            "📌 لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید."
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        logger.info("Welcome message sent successfully")

    except Exception as e:
        logger.error(f"Error in start command: {str(e)}", exc_info=True)
        try:
            await update.message.reply_text("خطایی رخ داد. لطفا دوباره تلاش کنید.")
        except:
            logger.error("Could not send error message to user")

def main():
    try:
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("No token found! Make sure you set BOT_TOKEN in .env file")
            return

        logger.info("Bot is starting...")
        application = Application.builder().token(token).build()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start_command))
        application.add_error_handler(error_handler)
        
        logger.info("Starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)

if __name__ == '__main__':
    main()
