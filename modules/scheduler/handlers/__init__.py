from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from .menu import scheduler_menu
from .states import *
from .add_schedule import add_schedule_start, set_interval, set_start_time, set_end_time
from .list_schedules import list_schedules

def get_scheduler_handlers(start_command):
    """Get all scheduler related handlers"""
    
    add_schedule_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^⚙️ تنظیم زمان‌بندی$'), add_schedule_start)],
        states={
            SETTING_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_interval)],
            SETTING_START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_start_time)],
            SETTING_END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_end_time)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), scheduler_menu)]
    )

    return [
        CommandHandler('schedule', scheduler_menu),
        MessageHandler(filters.Regex('^⏰ مدیریت زمان‌بندی$'), scheduler_menu),
        MessageHandler(filters.Regex('^📋 لیست زمان‌بندی‌ها$'), list_schedules),
        MessageHandler(filters.Regex('^🔙 بازگشت به منو$'), start_command),
        add_schedule_handler
    ]
