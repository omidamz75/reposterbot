from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from .menu import ads_menu
from .states import *  # Import states from separate file
from .add_ad import add_ad_start, add_ad_content, add_ad_media
from .list_ads import list_ads_start, list_ads_display, CHOOSING_DISPLAY_TYPE
from .remove_ad import remove_ad_start, remove_ad_finish
from .edit_ad import edit_ad_start, edit_ad_get_content, edit_ad_content, edit_ad_media

def get_ads_handlers(start_command):
    """Get all advertisement related handlers"""
    add_ad_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📝 افزودن تبلیغ$'), add_ad_start)],
        states={
            ADDING_CONTENT: [MessageHandler(filters.TEXT, add_ad_content)],
            ADDING_MEDIA: [MessageHandler(filters.ALL, add_ad_media)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), ads_menu)]
    )

    remove_ad_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^❌ حذف تبلیغ$'), remove_ad_start)],
        states={
            REMOVING_AD: [MessageHandler(filters.TEXT, remove_ad_finish)]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), ads_menu)]
    )

    edit_ad_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^✏️ ویرایش تبلیغ$'), edit_ad_start)],
        states={
            WAITING_FOR_AD_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_ad_get_content)],
            EDITING_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_ad_content)],
            EDITING_MEDIA: [
                MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Regex('^/skip$'), edit_ad_media)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), ads_menu)]
    )

    list_ads_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^📋 لیست تبلیغات$'), list_ads_start),
            CommandHandler('list', list_ads_start)
        ],
        states={
            CHOOSING_DISPLAY_TYPE: [
                MessageHandler(
                    filters.Regex('^(📝 پیام متنی|📄 فایل تکست)$'),
                    list_ads_display
                ),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), ads_menu)  # تغییر به ads_menu
            ]
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت$'), ads_menu)]  # تغییر به ads_menu
    )

    return [
        CommandHandler('ads', ads_menu),
        MessageHandler(filters.Regex('^📊 مدیریت تبلیغات$'), ads_menu),
        MessageHandler(filters.Regex('^🔙 بازگشت به منو$'), start_command),
        add_ad_handler,
        remove_ad_handler,
        edit_ad_handler,
        list_ads_handler
    ]
