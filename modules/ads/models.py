from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from core.database import Base

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # محتوای تبلیغ
    type = Column(String)  # نوع تبلیغ (متن، عکس، ویدیو و...)
    media_id = Column(String, nullable=True)  # شناسه فایل در تلگرام
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, index=True)  # کاربر ایجاد کننده
