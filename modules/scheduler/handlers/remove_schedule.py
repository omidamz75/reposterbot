from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.database import SessionLocal
from ..services import SchedulerService
from .states import REMOVING_SCHEDULE

async def remove_schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرایند حذف زمان‌بندی"""
    db = SessionLocal()
    try:
        schedules = await SchedulerService.get_user_schedules(
            db=db,
            owner_id=update.effective_user.id
        )
        
        if not schedules:
            await update.message.reply_text("❌ شما هیچ زمان‌بندی فعالی ندارید!")
            return ConversationHandler.END
            
        response = "🗑 برای حذف، شناسه زمان‌بندی را وارد کنید:\n\n"
        for schedule in schedules:
            response += f"🆔 شناسه: {schedule.id}\n"
            response += f"⏱ فاصله: {schedule.interval_minutes} دقیقه\n"
            response += f"🕐 زمان: {schedule.start_time.strftime('%H:%M')} تا {schedule.end_time.strftime('%H:%M')}\n"
            response += "➖➖➖➖➖➖➖➖\n"
            
        await update.message.reply_text(response)
        return REMOVING_SCHEDULE
        
    finally:
        db.close()

async def remove_schedule_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف زمان‌بندی"""
    try:
        schedule_id = int(update.message.text)
        
        db = SessionLocal()
        try:
            success = await SchedulerService.delete_schedule(
                db=db,
                schedule_id=schedule_id,
                owner_id=update.effective_user.id
            )
            
            if success:
                await update.message.reply_text("✅ زمان‌بندی با موفقیت حذف شد!")
            else:
                await update.message.reply_text("❌ زمان‌بندی مورد نظر یافت نشد!")
                
        finally:
            db.close()
            
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک شناسه معتبر وارد کنید!")
        return REMOVING_SCHEDULE
