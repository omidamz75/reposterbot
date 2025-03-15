from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import time, datetime
from . import models

class SchedulerService:
    @staticmethod
    async def create_schedule(
        db: Session,
        owner_id: int,
        interval_minutes: int,
        start_time: time,
        end_time: time
    ):
        """ایجاد یک زمان‌بندی جدید"""
        schedule = models.Schedule(
            owner_id=owner_id,
            interval_minutes=interval_minutes,
            start_time=start_time,
            end_time=end_time
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    @staticmethod
    async def get_user_schedules(db: Session, owner_id: int):
        """دریافت تمام زمان‌بندی‌های فعال کاربر"""
        return db.query(models.Schedule)\
            .filter(
                models.Schedule.owner_id == owner_id,
                models.Schedule.is_active == True
            )\
            .order_by(models.Schedule.created_at.desc())\
            .all()

    @staticmethod
    async def update_schedule(
        db: Session,
        schedule_id: int,
        owner_id: int,
        interval_minutes: int = None,
        start_time: time = None,
        end_time: time = None,
        is_active: bool = None
    ):
        """بروزرسانی زمان‌بندی"""
        schedule = db.query(models.Schedule)\
            .filter(
                models.Schedule.id == schedule_id,
                models.Schedule.owner_id == owner_id,
                models.Schedule.is_active == True
            ).first()

        if not schedule:
            return None

        if interval_minutes is not None:
            schedule.interval_minutes = interval_minutes
        if start_time is not None:
            schedule.start_time = start_time
        if end_time is not None:
            schedule.end_time = end_time
        if is_active is not None:
            schedule.is_active = is_active

        db.commit()
        db.refresh(schedule)
        return schedule

    @staticmethod
    async def delete_schedule(db: Session, schedule_id: int, owner_id: int):
        """حذف زمان‌بندی (غیرفعال کردن)"""
        schedule = db.query(models.Schedule)\
            .filter(
                models.Schedule.id == schedule_id,
                models.Schedule.owner_id == owner_id,
                models.Schedule.is_active == True
            ).first()

        if schedule:
            schedule.is_active = False
            db.commit()
            return True
        return False
