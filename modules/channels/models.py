from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from core.database import Base

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, index=True)
    title = Column(String)
    username = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, index=True)

    @property
    def channel_code(self):
        """Return position in active channels list as channel code"""
        return str(self.id)

    __table_args__ = (
        UniqueConstraint('channel_id', 'owner_id', name='uix_channel_owner'),
    )
