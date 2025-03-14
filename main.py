import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from modules.channels.handlers import get_channel_handlers
from modules.ads.handlers import get_ads_handlers  # اضافه کردن import جدید
from core.database import create_database

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

class SingleInstanceBot:
    def __init__(self):
        self.lockfile = "bot.lock"
        
    def check_instance(self):
        """Check if another instance is running"""
        if os.path.exists(self.lockfile):
            try:
                with open(self.lockfile, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    # Check if process is still running
                    os.kill(pid, 0)
                    logger.error(f"Bot is already running with PID {pid}")
                    return False
                except OSError:
                    # Process not found, safe to continue
                    pass
            except Exception as e:
                logger.error(f"Error checking lockfile: {e}")
                
        # Create lockfile with current PID
        with open(self.lockfile, 'w') as f:
            f.write(str(os.getpid()))
        return True
        
    def cleanup(self):
        """Remove lockfile on exit"""
        try:
            if os.path.exists(self.lockfile):
                os.remove(self.lockfile)
        except Exception as e:
            logger.error(f"Error removing lockfile: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    try:
        user = update.effective_user
        logger.info(f"New user interaction - ID: {user.id}, Username: {user.username}")
        
        keyboard = [
            ['📊 مدیریت تبلیغات', '📈 مدیریت کانال‌ها'],
            ['⚙️ تنظیمات', '📋 راهنما']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # فقط در اولین اجرا پیام خوش‌آمدگویی نمایش داده شود
        if not context.user_data.get('welcomed'):
            welcome_text = (
                f"👋 سلام {user.first_name} عزیز!\n\n"
                "🤖 به ربات مدیریت تبلیغات و ریپوست خوش آمدید.\n"
                "📌 لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید."
            )
            context.user_data['welcomed'] = True
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        else:
            # در دفعات بعدی فقط منو نمایش داده شود
            await update.message.reply_text("📌 لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید.", 
                                         reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text("متأسفانه مشکلی پیش آمده. لطفاً دوباره تلاش کنید.")

def main():
    try:
        # Single instance check
        instance = SingleInstanceBot()
        if not instance.check_instance():
            sys.exit(1)

        # Create database tables if they don't exist
        logger.info("Checking database...")
        create_database()

        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("No token found! Make sure you set BOT_TOKEN in .env file")
            return

        logger.info("Bot is starting...")
        application = Application.builder().token(token).build()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start_command))
        application.add_error_handler(error_handler)
        
        # Add channel handlers
        application.add_handlers(get_channel_handlers(start_command))
        
        # Add advertisement handlers - اضافه کردن هندلرهای تبلیغات
        application.add_handlers(get_ads_handlers(start_command))
        
        # Cleanup on shutdown
        try:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                close_loop=False  # Don't close the event loop on shutdown
            )
        finally:
            instance.cleanup()
            
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        instance.cleanup()

if __name__ == '__main__':
    main()
