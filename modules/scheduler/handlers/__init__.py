from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from .menu import scheduler_menu
from .states import *
from .add_schedule import add_schedule_start, set_interval, set_start_time, set_end_time
from .list_schedules import list_schedules
from .edit_schedule import edit_schedule_start, edit_schedule_select, edit_interval, edit_start_time, edit_end_time
from .remove_schedule import remove_schedule_start, remove_schedule_finish

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

    edit_schedule_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^✏️ ویرایش زمان‌بندی$'), edit_schedule_start)],
        states={
            EDITING_SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_schedule_select)],
            SETTING_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_interval)],
            SETTING_START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_start_time)],
            SETTING_END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_end_time)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), scheduler_menu)]
    )

    remove_schedule_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^❌ حذف زمان‌بندی$'), remove_schedule_start)],
        states={
            REMOVING_SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_schedule_finish)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), scheduler_menu)]
    )

    return [
        CommandHandler('schedule', scheduler_menu),
        MessageHandler(filters.Regex('^⏰ مدیریت زمان‌بندی$'), scheduler_menu),
        MessageHandler(filters.Regex('^📋 لیست زمان‌بندی‌ها$'), list_schedules),
        MessageHandler(filters.Regex('^🔙 بازگشت به منو$'), start_command),
        add_schedule_handler,
        edit_schedule_handler,
        remove_schedule_handler
    ]
