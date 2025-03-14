from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

class AdvertisementService:
    @staticmethod
    async def add_advertisement(db: Session, content: str, ad_type: str, media_id: str, owner_id: int):
        """Add new advertisement"""
        try:
            ad = models.Advertisement(
                content=content,
                type=ad_type,
                media_id=media_id,
                owner_id=owner_id
            )
            db.add(ad)
            db.commit()
            db.refresh(ad)
            return ad
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    async def get_user_advertisements(db: Session, owner_id: int):
        """Get all active advertisements for a user"""
        return db.query(models.Advertisement)\
            .filter(
                models.Advertisement.owner_id == owner_id,
                models.Advertisement.is_active == True
            )\
            .group_by(models.Advertisement.id)\
            .order_by(models.Advertisement.created_at.desc())\
            .all()

    @staticmethod
    async def remove_advertisement(db: Session, ad_id: int, owner_id: int):
        """Remove an advertisement"""
        ad = db.query(models.Advertisement)\
            .filter(
                models.Advertisement.id == ad_id,
                models.Advertisement.owner_id == owner_id,
                models.Advertisement.is_active == True
            ).first()
        
        if ad:
            ad.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    async def get_advertisement_by_id(db: Session, ad_id: int, owner_id: int):
        """Get specific advertisement by ID"""
        return db.query(models.Advertisement)\
            .filter(
                models.Advertisement.id == ad_id,
                models.Advertisement.owner_id == owner_id,
                models.Advertisement.is_active == True
            ).first()

    @staticmethod
    async def update_advertisement(db: Session, ad_id: int, owner_id: int, content: str, ad_type: str = None, media_id: str = None):
        """Update existing advertisement"""
        ad = await AdvertisementService.get_advertisement_by_id(db, ad_id, owner_id)
        if ad:
            ad.content = content
            if ad_type:
                ad.type = ad_type
            if media_id:
                ad.media_id = media_id
            db.commit()
            db.refresh(ad)
            return ad
        return None
