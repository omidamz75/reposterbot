from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, time
from core.database import SessionLocal
from ..services import SchedulerService
from .states import SETTING_INTERVAL, SETTING_START_TIME, SETTING_END_TIME

async def add_schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند تنظیم زمان‌بندی"""
    await update.message.reply_text(
        "⏱ لطفاً فاصله زمانی بین ارسال‌ها را به دقیقه وارد کنید:\n"
        "مثال: 30"
    )
    return SETTING_INTERVAL

async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم فاصله زمانی"""
    try:
        interval = int(update.message.text)
        if interval < 1:
            raise ValueError("Invalid interval")
        
        context.user_data['interval'] = interval
        await update.message.reply_text(
            "🕐 لطفاً ساعت شروع را به فرمت HH:MM وارد کنید:\n"
            "مثال: 09:00"
        )
        return SETTING_START_TIME
    
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
        return SETTING_INTERVAL

async def set_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم ساعت شروع"""
    try:
        start_time = datetime.strptime(update.message.text, "%H:%M").time()
        context.user_data['start_time'] = start_time
        
        await update.message.reply_text(
            "🕐 لطفاً ساعت پایان را به فرمت HH:MM وارد کنید:\n"
            "مثال: 18:00"
        )
        return SETTING_END_TIME
    
    except ValueError:
        await update.message.reply_text("❌ لطفاً زمان را به فرمت صحیح وارد کنید!")
        return SETTING_START_TIME

async def set_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم ساعت پایان و ذخیره زمان‌بندی"""
    try:
        end_time = datetime.strptime(update.message.text, "%H:%M").time()
        
        db = SessionLocal()
        try:
            schedule = await SchedulerService.create_schedule(
                db=db,
                owner_id=update.effective_user.id,
                interval_minutes=context.user_data['interval'],
                start_time=context.user_data['start_time'],
                end_time=end_time
            )
            
            await update.message.reply_text(
                "✅ زمان‌بندی با موفقیت تنظیم شد!\n\n"
                f"⏱ فاصله ارسال: هر {schedule.interval_minutes} دقیقه\n"
                f"🕐 ساعت شروع: {schedule.start_time.strftime('%H:%M')}\n"
                f"🕐 ساعت پایان: {schedule.end_time.strftime('%H:%M')}"
            )
            
        finally:
            db.close()
            context.user_data.clear()
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً زمان را به فرمت صحیح وارد کنید!")
        return SETTING_END_TIME
