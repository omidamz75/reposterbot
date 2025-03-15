from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
from core.database import SessionLocal
from ..services import SchedulerService
from .states import EDITING_SCHEDULE, SETTING_INTERVAL, SETTING_START_TIME, SETTING_END_TIME

async def edit_schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند ویرایش زمان‌بندی"""
    db = SessionLocal()
    try:
        schedules = await SchedulerService.get_user_schedules(
            db=db,
            owner_id=update.effective_user.id
        )
        
        if not schedules:
            await update.message.reply_text("❌ شما هیچ زمان‌بندی فعالی ندارید!")
            return ConversationHandler.END
            
        response = "🔄 برای ویرایش، شناسه زمان‌بندی را وارد کنید:\n\n"
        for schedule in schedules:
            response += f"🆔 شناسه: {schedule.id}\n"
            response += f"⏱ فاصله: {schedule.interval_minutes} دقیقه\n"
            response += f"🕐 از ساعت: {schedule.start_time.strftime('%H:%M')}\n"
            response += f"🕐 تا ساعت: {schedule.end_time.strftime('%H:%M')}\n"
            response += "➖➖➖➖➖➖➖➖\n"
            
        await update.message.reply_text(response)
        return EDITING_SCHEDULE
        
    finally:
        db.close()

async def edit_schedule_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب زمان‌بندی برای ویرایش"""
    try:
        schedule_id = int(update.message.text)
        context.user_data['editing_schedule_id'] = schedule_id
        
        await update.message.reply_text(
            "⏱ فاصله زمانی جدید بین ارسال‌ها را به دقیقه وارد کنید:\n"
            "مثال: 30"
        )
        return SETTING_INTERVAL
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک شناسه معتبر وارد کنید!")
        return EDITING_SCHEDULE

async def edit_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش فاصله زمانی"""
    try:
        interval = int(update.message.text)
        if interval < 1:
            raise ValueError("Invalid interval")
        
        context.user_data['new_interval'] = interval
        await update.message.reply_text(
            "🕐 ساعت شروع جدید را به فرمت HH:MM وارد کنید:\n"
            "مثال: 09:00"
        )
        return SETTING_START_TIME
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
        return SETTING_INTERVAL

async def edit_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش ساعت شروع"""
    try:
        start_time = datetime.strptime(update.message.text, "%H:%M").time()
        context.user_data['new_start_time'] = start_time
        
        await update.message.reply_text(
            "🕐 ساعت پایان جدید را به فرمت HH:MM وارد کنید:\n"
            "مثال: 18:00"
        )
        return SETTING_END_TIME
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً زمان را به فرمت صحیح وارد کنید!")
        return SETTING_START_TIME

async def edit_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش ساعت پایان و ذخیره تغییرات"""
    try:
        end_time = datetime.strptime(update.message.text, "%H:%M").time()
        
        db = SessionLocal()
        try:
            schedule = await SchedulerService.update_schedule(
                db=db,
                schedule_id=context.user_data['editing_schedule_id'],
                owner_id=update.effective_user.id,
                interval_minutes=context.user_data['new_interval'],
                start_time=context.user_data['new_start_time'],
                end_time=end_time
            )
            
            if schedule:
                await update.message.reply_text(
                    "✅ زمان‌بندی با موفقیت بروزرسانی شد!\n\n"
                    f"⏱ فاصله ارسال: هر {schedule.interval_minutes} دقیقه\n"
                    f"🕐 ساعت شروع: {schedule.start_time.strftime('%H:%M')}\n"
                    f"🕐 ساعت پایان: {schedule.end_time.strftime('%H:%M')}"
                )
            else:
                await update.message.reply_text("❌ زمان‌بندی مورد نظر یافت نشد!")
                
        finally:
            db.close()
            context.user_data.clear()
            
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً زمان را به فرمت صحیح وارد کنید!")
        return SETTING_END_TIME
