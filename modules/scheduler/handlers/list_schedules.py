from telegram import Update
from telegram.ext import ContextTypes
from core.database import SessionLocal
from ..services import SchedulerService

async def list_schedules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست زمان‌بندی‌های فعال"""
    db = SessionLocal()
    try:
        schedules = await SchedulerService.get_user_schedules(
            db=db,
            owner_id=update.effective_user.id
        )
        
        if not schedules:
            await update.message.reply_text("❌ شما هیچ زمان‌بندی فعالی ندارید!")
            return
            
        response = "📋 لیست زمان‌بندی‌های فعال:\n\n"
        for schedule in schedules:
            response += f"🆔 شناسه: {schedule.id}\n"
            response += f"⏱ فاصله ارسال: هر {schedule.interval_minutes} دقیقه\n"
            response += f"🕐 از ساعت: {schedule.start_time.strftime('%H:%M')}\n"
            response += f"🕐 تا ساعت: {schedule.end_time.strftime('%H:%M')}\n"
            response += "➖➖➖➖➖➖➖➖\n"
            
        await update.message.reply_text(response)
        
    finally:
        db.close()
