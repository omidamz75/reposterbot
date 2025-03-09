from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from .menu import channels_menu
from .add_channel import add_channel_start, add_channel_finish, ADDING_CHANNEL
from .delete_channel import delete_channel_start, delete_channel_finish, DELETING_CHANNEL
from .list_channels import list_channels

def get_channel_handlers(start_command):
    """Get channel handlers with start command dependency"""
    add_channel_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^➕ افزودن کانال$'), add_channel_start)],
        states={
            ADDING_CHANNEL: [MessageHandler(filters.TEXT | filters.FORWARDED, add_channel_finish)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), channels_menu)]
    )

    delete_channel_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^❌ حذف کانال$'), delete_channel_start)],
        states={
            DELETING_CHANNEL: [MessageHandler(filters.TEXT, delete_channel_finish)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), channels_menu)]
    )

    return [
        CommandHandler('channels', channels_menu),
        MessageHandler(filters.Regex('^📈 مدیریت کانال‌ها$'), channels_menu),
        MessageHandler(filters.Regex('^📋 لیست کانال‌ها$'), list_channels),
        MessageHandler(filters.Regex('^🔙 بازگشت$'), start_command),
        add_channel_handler,
        delete_channel_handler
    ]
