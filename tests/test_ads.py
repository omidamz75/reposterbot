import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.ads.models import Advertisement
from modules.ads.services import AdvertisementService

# Test database configuration
TEST_DATABASE_URL = "sqlite:///test_ads.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
async def setup_database():
    """Setup and teardown the test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def test_db():
    """Provide a test database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
async def sample_ad(test_db):
    """Create a sample advertisement"""
    ad = await AdvertisementService.add_advertisement(
        db=test_db,
        content="Test Advertisement",
        ad_type="text",
        media_id=None,
        owner_id=12345
    )
    return ad

@pytest.mark.asyncio
async def test_add_text_advertisement(test_db):
    """تست اضافه کردن تبلیغ متنی"""
    ad = await AdvertisementService.add_advertisement(
        db=test_db,
        content="This is a test ad",
        ad_type="text",
        media_id=None,
        owner_id=12345
    )
    assert ad is not None
    assert ad.content == "This is a test ad"
    assert ad.type == "text"
    assert ad.is_active == True

@pytest.mark.asyncio
async def test_add_media_advertisement(test_db):
    """تست اضافه کردن تبلیغ با رسانه"""
    ad = await AdvertisementService.add_advertisement(
        db=test_db,
        content="Ad with media",
        ad_type="photo",
        media_id="test_photo_id",
        owner_id=12345
    )
    assert ad.media_id == "test_photo_id"
    assert ad.type == "photo"

@pytest.mark.asyncio
async def test_get_user_advertisements(test_db):
    """تست دریافت لیست تبلیغات کاربر"""
    # Add two ads
    await AdvertisementService.add_advertisement(
        db=test_db, content="Ad 1", ad_type="text", 
        media_id=None, owner_id=12345
    )
    await AdvertisementService.add_advertisement(
        db=test_db, content="Ad 2", ad_type="text", 
        media_id=None, owner_id=12345
    )
    
    ads = await AdvertisementService.get_user_advertisements(
        db=test_db, owner_id=12345
    )
    assert len(ads) == 2
    assert all(ad.owner_id == 12345 for ad in ads)

@pytest.mark.asyncio
async def test_remove_advertisement(test_db, sample_ad):
    """تست حذف تبلیغ"""
    success = await AdvertisementService.remove_advertisement(
        db=test_db,
        ad_id=sample_ad.id,
        owner_id=12345
    )
    assert success == True
    
    # Check if ad is actually removed (marked as inactive)
    ads = await AdvertisementService.get_user_advertisements(
        db=test_db, owner_id=12345
    )
    assert len(ads) == 0

@pytest.mark.asyncio
async def test_update_advertisement(test_db, sample_ad):
    """تست ویرایش تبلیغ"""
    updated_ad = await AdvertisementService.update_advertisement(
        db=test_db,
        ad_id=sample_ad.id,
        owner_id=12345,
        content="Updated content",
        ad_type="photo",
        media_id="new_photo_id"
    )
    assert updated_ad is not None
    assert updated_ad.content == "Updated content"
    assert updated_ad.type == "photo"
    assert updated_ad.media_id == "new_photo_id"

@pytest.mark.asyncio
async def test_get_nonexistent_advertisement(test_db):
    """تست دریافت تبلیغ غیرموجود"""
    ad = await AdvertisementService.get_advertisement_by_id(
        db=test_db,
        ad_id=999,
        owner_id=12345
    )
    assert ad is None

@pytest.mark.asyncio
async def test_multiple_users_advertisements(test_db):
    """تست جداسازی تبلیغات کاربران مختلف"""
    # Add ads for two different users
    await AdvertisementService.add_advertisement(
        db=test_db, content="User1 Ad", ad_type="text", 
        media_id=None, owner_id=12345
    )
    await AdvertisementService.add_advertisement(
        db=test_db, content="User2 Ad", ad_type="text", 
        media_id=None, owner_id=67890
    )
    
    user1_ads = await AdvertisementService.get_user_advertisements(
        db=test_db, owner_id=12345
    )
    user2_ads = await AdvertisementService.get_user_advertisements(
        db=test_db, owner_id=67890
    )
    
    assert len(user1_ads) == 1
    assert len(user2_ads) == 1
    assert user1_ads[0].content == "User1 Ad"
    assert user2_ads[0].content == "User2 Ad"

@pytest.mark.asyncio
async def test_remove_other_user_advertisement(test_db, sample_ad):
    """تست حذف تبلیغ توسط کاربر دیگر"""
    # Try to remove ad with different owner_id
    success = await AdvertisementService.remove_advertisement(
        db=test_db,
        ad_id=sample_ad.id,
        owner_id=99999  # Different user
    )
    assert success == False
    
    # Check if ad still exists
    ads = await AdvertisementService.get_user_advertisements(
        db=test_db, owner_id=12345
    )
    assert len(ads) == 1

if __name__ == "__main__":
    pytest.main(["-v", "test_ads.py"])
