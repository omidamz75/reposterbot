from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Enum
from sqlalchemy.sql import func
from core.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)
    interval_minutes = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)  # ساعت شروع
    end_time = Column(Time, nullable=False)    # ساعت پایان
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
