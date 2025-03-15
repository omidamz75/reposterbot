from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
from telegram import Bot
from . import models

class ChannelService:
    @staticmethod
    async def get_next_id(db: Session) -> int:
        """Get next available permanent ID"""
        result = db.query(func.max(models.Channel.permanent_id)).scalar()
        return (result or 0) + 1

    @staticmethod
    async def get_next_sequence_id(db: Session, owner_id: int) -> int:
        """Get the next available sequence ID"""
        max_sequence = db.query(func.max(models.Channel.sequence_id)).scalar() or 0
        return max_sequence + 1

    @staticmethod
    async def get_highest_code(db: Session, owner_id: int) -> int:
        """Get highest used code for a user"""
        result = db.query(func.max(models.Channel.original_code))\
            .filter(models.Channel.owner_id == owner_id)\
            .scalar()
        return int(result) if result and result.isdigit() else 0

    @staticmethod
    async def get_available_channel_codes(db: Session, owner_id: int) -> set:
        """Get all currently used channel codes for a user"""
        channels = db.query(models.Channel.channel_code)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            ).all()
        return {int(ch.channel_code) for ch in channels}

    @staticmethod
    async def get_next_channel_code(db: Session, owner_id: int) -> str:
        """Find the next available channel code, including gaps"""
        used_codes = await ChannelService.get_available_channel_codes(db, owner_id)
        if not used_codes:
            return "1"
        
        # Find the first gap in sequence or next number after max
        all_numbers = set(range(1, max(used_codes) + 2))
        available_numbers = all_numbers - used_codes
        return str(min(available_numbers))

    @staticmethod
    async def check_duplicate_channel(db: Session, channel_id: str, owner_id: int) -> bool:
        """Check if channel already exists"""
        return db.query(models.Channel)\
            .filter(
                models.Channel.channel_id == channel_id,
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            ).first() is not None

    @staticmethod
    async def get_next_sequence_number(db: Session, owner_id: int) -> int:
        """Get next sequence number for ordering"""
        result = db.query(func.max(models.Channel.sequence_number))\
            .filter(models.Channel.owner_id == owner_id)\
            .scalar()
        return (result or 0) + 1

    @staticmethod
    async def reorder_display_numbers(db: Session, owner_id: int):
        """Update display numbers based on sequence"""
        channels = db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.sequence_number.asc())\
            .all()
        
        for i, channel in enumerate(channels, 1):
            channel.channel_code = str(i)
        
        db.commit()

    @staticmethod
    async def get_next_permanent_id(db: Session) -> int:
        """Get next available permanent ID"""
        max_id = db.query(func.max(models.Channel.permanent_id)).scalar()
        return (max_id or 0) + 1

    @staticmethod
    async def get_next_internal_id(db: Session) -> int:
        """Get next available internal ID"""
        result = db.query(func.max(models.Channel.internal_id)).scalar()
        return (result or 0) + 1

    @staticmethod
    async def update_display_numbers(db: Session, owner_id: int):
        """Update display numbers for sequential appearance"""
        active_channels = db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.real_id.asc())\
            .all()

        # Reset display numbers to be sequential
        last_number = 0
        for channel in active_channels:
            last_number += 1
            channel.display_id = last_number

        db.commit()

    @staticmethod
    async def get_max_sequence_id(db: Session, owner_id: int) -> int:
        """Get maximum sequence ID for active channels"""
        result = db.query(func.max(models.Channel.sequence_id))\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            ).scalar()
        return result or 0

    @staticmethod
    async def add_channel(db: Session, channel_id: str, title: str, username: str, owner_id: int):
        """افزودن کانال جدید"""
        # بررسی وجود کانال فعال با همین مشخصات
        existing = db.query(models.Channel).filter(
            and_(
                models.Channel.channel_id == channel_id,
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )
        ).first()

        if existing:
            raise ValueError(f"Channel {channel_id} already exists for this user")

        try:
            channel = models.Channel(
                channel_id=channel_id,
                title=title,
                username=username,
                owner_id=owner_id
            )
            db.add(channel)
            db.commit()
            db.refresh(channel)
            return channel

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    async def reorder_channel_codes(db: Session, owner_id: int):
        """Reorder channel codes after deletion"""
        channels = db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.channel_code.asc())\
            .all()
        
        for i, channel in enumerate(channels, 1):
            channel.channel_code = str(i)
        
        db.commit()

    @staticmethod
    async def get_user_channels(db: Session, owner_id: int):
        """دریافت کانال‌های فعال کاربر"""
        return db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.created_at.desc())\
            .all()

    @staticmethod
    async def remove_channel(db: Session, channel_id: str, owner_id: int):
        """حذف کانال"""
        channel = db.query(models.Channel).filter(
            models.Channel.channel_id == channel_id,
            models.Channel.owner_id == owner_id,
            models.Channel.is_active == True
        ).first()

        if channel:
            channel.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    async def remove_channel_by_id(db: Session, permanent_id: int, owner_id: int):
        """Remove channel using permanent ID"""
        channel = db.query(models.Channel).filter(
            models.Channel.permanent_id == permanent_id,
            models.Channel.owner_id == owner_id,
            models.Channel.is_active == True
        ).first()
        
        if channel:
            channel.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    async def remove_channel_by_number(db: Session, number: int, owner_id: int):
        """Remove channel by its position in the list"""
        channels = db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.sequence_number)\
            .all()

        if not channels or number < 1 or number > len(channels):
            return False

        try:
            channel = channels[number - 1]
            channel.is_active = False
            db.commit()
            
            # Reorder remaining channels
            await ChannelService.reorder_sequence_numbers(db, owner_id)
            return True
            
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    async def reorder_sequence_numbers(db: Session, owner_id: int):
        """Reorder sequence numbers for active channels"""
        channels = db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.sequence_number)\
            .all()

        for i, channel in enumerate(channels, 1):
            channel.sequence_number = i
        
        db.commit()

    @staticmethod
    async def check_bot_admin(bot: Bot, channel_id: str):
        """Check if bot is admin in channel"""
        try:
            bot_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
            return bot_member.status in ['administrator', 'creator']
        except Exception:
            return False

    @staticmethod
    async def get_all_user_channels(db: Session, owner_id: int, include_inactive=False):
        """Get all channels for a user, optionally including inactive ones"""
        query = db.query(models.Channel).filter(models.Channel.owner_id == owner_id)
        if not include_inactive:
            query = query.filter(models.Channel.is_active == True)
        return query.order_by(models.Channel.channel_code.asc()).all()

    @staticmethod
    async def reorder_channel_numbers(db: Session, owner_id: int):
        """Reorder channel numbers to be sequential"""
        channels = await ChannelService.get_all_user_channels(db, owner_id)
        expected_numbers = list(range(1, len(channels) + 1))
        
        for channel, new_number in zip(channels, expected_numbers):
            channel.channel_code = str(new_number)
        
        db.commit()

    @staticmethod
    async def update_display_orders(db: Session, owner_id: int):
        """Update display orders for all active channels"""
        active_channels = db.query(models.Channel)\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            )\
            .order_by(models.Channel.permanent_id.asc())\
            .all()
        
        current_max = db.query(func.max(models.Channel.display_order))\
            .filter(
                models.Channel.owner_id == owner_id,
                models.Channel.is_active == True
            ).scalar() or 0

        for idx, channel in enumerate(active_channels, 1):
            if channel.display_order is None:
                channel.display_order = current_max + idx

        db.commit()

    @staticmethod
    async def get_next_real_id(db: Session) -> int:
        """Get next available real ID"""
        result = db.query(func.max(models.Channel.real_id)).scalar()
        return (result or 0) + 1
