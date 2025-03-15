import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from modules.channels.handlers import get_channel_handlers
from modules.ads.handlers import get_ads_handlers
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات"""
    keyboard = [
        ['📊 مدیریت تبلیغات', '📈 مدیریت کانال‌ها'],
        ['⚙️ تنظیمات', '📋 راهنما']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"👋 سلام {update.effective_user.first_name} عزیز!\n"
        "🤖 به ربات مدیریت تبلیغات خوش آمدید.",
        reply_markup=reply_markup
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"Error: {context.error} in update {update}")

def main():
    try:
        logger.info("Starting bot...")
        create_database()

        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("No bot token found in .env file!")
            return

        application = Application.builder().token(token).build()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start_command))
        application.add_handlers(get_channel_handlers(start_command))
        application.add_handlers(get_ads_handlers(start_command))
        application.add_error_handler(error_handler)

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")

if __name__ == '__main__':
    main()
