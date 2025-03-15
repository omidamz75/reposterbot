from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from core.database import Base

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)
    title = Column(String)
    username = Column(String, nullable=True)
    owner_id = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Channel {self.channel_id}>"
