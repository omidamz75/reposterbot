import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.ads.services import AdvertisementService
from modules.channels.services import ChannelService

TEST_DATABASE_URL = "sqlite:///test_integration.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
async def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.mark.asyncio
async def test_complete_ad_workflow(test_db):
    """تست کامل چرخه تبلیغات از ثبت تا ارسال"""
    # 1. افزودن کانال
    channel = await ChannelService.add_channel(
        db=test_db,
        channel_id="@test_channel",
        title="Test Channel",
        username="@test_channel",
        owner_id=12345
    )
    assert channel is not None
    assert channel.is_active == True

    # 2. افزودن تبلیغ
    ad = await AdvertisementService.add_advertisement(
        db=test_db,
        content="Test Advertisement",
        ad_type="text",
        media_id=None,
        owner_id=12345
    )
    assert ad is not None
    assert ad.is_active == True

    # 3. ویرایش تبلیغ
    updated_ad = await AdvertisementService.update_advertisement(
        db=test_db,
        ad_id=ad.id,
        owner_id=12345,
        content="Updated Advertisement",
        ad_type="text",
        media_id=None
    )
    assert updated_ad.content == "Updated Advertisement"

    # 4. بررسی لیست تبلیغات
    ads = await AdvertisementService.get_user_advertisements(
        db=test_db,
        owner_id=12345
    )
    assert len(ads) == 1
    assert ads[0].content == "Updated Advertisement"

    # 5. بررسی لیست کانال‌ها
    channels = await ChannelService.get_user_channels(
        db=test_db,
        owner_id=12345
    )
    assert len(channels) == 1
    assert channels[0].channel_id == "@test_channel"

    # 6. حذف تبلیغ
    success = await AdvertisementService.remove_advertisement(
        db=test_db,
        ad_id=ad.id,
        owner_id=12345
    )
    assert success == True

    # 7. حذف کانال
    success = await ChannelService.remove_channel_by_number(
        db=test_db,
        number=1,
        owner_id=12345
    )
    assert success == True

@pytest.mark.asyncio
async def test_multiple_users_isolation(test_db):
    """تست جداسازی داده‌های کاربران مختلف"""
    # کاربر اول
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@user1_channel",
        title="User 1 Channel",
        username="@user1_channel",
        owner_id=11111
    )
    
    await AdvertisementService.add_advertisement(
        db=test_db,
        content="User 1 Ad",
        ad_type="text",
        media_id=None,
        owner_id=11111
    )

    # کاربر دوم
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@user2_channel",
        title="User 2 Channel",
        username="@user2_channel",
        owner_id=22222
    )
    
    await AdvertisementService.add_advertisement(
        db=test_db,
        content="User 2 Ad",
        ad_type="text",
        media_id=None,
        owner_id=22222
    )

    # بررسی داده‌های کاربر اول
    user1_channels = await ChannelService.get_user_channels(db=test_db, owner_id=11111)
    user1_ads = await AdvertisementService.get_user_advertisements(db=test_db, owner_id=11111)
    assert len(user1_channels) == 1
    assert len(user1_ads) == 1
    assert user1_channels[0].channel_id == "@user1_channel"
    assert user1_ads[0].content == "User 1 Ad"

    # بررسی داده‌های کاربر دوم
    user2_channels = await ChannelService.get_user_channels(db=test_db, owner_id=22222)
    user2_ads = await AdvertisementService.get_user_advertisements(db=test_db, owner_id=22222)
    assert len(user2_channels) == 1
    assert len(user2_ads) == 1
    assert user2_channels[0].channel_id == "@user2_channel"
    assert user2_ads[0].content == "User 2 Ad"

@pytest.mark.asyncio
async def test_comprehensive_workflow(test_db):
    """تست جامع تمام قابلیت‌های سیستم"""
    # 1. تست افزودن چند کانال
    channels = []
    for i in range(3):
        channel = await ChannelService.add_channel(
            db=test_db,
            channel_id=f"@test_channel_{i}",
            title=f"Test Channel {i}",
            username=f"@test_channel_{i}",
            owner_id=12345
        )
        channels.append(channel)
        assert channel.is_active == True

    # 2. تست افزودن انواع مختلف تبلیغ
    ads = []
    ad_types = [
        ("text", "Text only ad", None),
        ("photo", "Photo ad", "photo123"),
        ("video", "Video ad", "video123"),
        ("animation", "GIF ad", "animation123")
    ]
    
    for ad_type, content, media_id in ad_types:
        ad = await AdvertisementService.add_advertisement(
            db=test_db,
            content=content,
            ad_type=ad_type,
            media_id=media_id,
            owner_id=12345
        )
        ads.append(ad)
        assert ad.type == ad_type
        assert ad.media_id == media_id

    # 3. تست ویرایش متوالی تبلیغ
    ad_to_edit = ads[0]
    edit_contents = ["First edit", "Second edit", "Final version"]
    
    for content in edit_contents:
        updated_ad = await AdvertisementService.update_advertisement(
            db=test_db,
            ad_id=ad_to_edit.id,
            owner_id=12345,
            content=content,
            ad_type="text"
        )
        assert updated_ad.content == content

    # 4. تست خطاهای امنیتی
    # تلاش برای دسترسی به تبلیغ کاربر دیگر
    with pytest.raises(Exception):
        await AdvertisementService.update_advertisement(
            db=test_db,
            ad_id=ads[0].id,
            owner_id=99999,  # کاربر نامعتبر
            content="Unauthorized edit",
            ad_type="text"
        )

    # 5. تست حذف و بازیابی
    # حذف کانال اول
    success = await ChannelService.remove_channel_by_number(
        db=test_db,
        number=1,
        owner_id=12345
    )
    assert success == True
    
    # بررسی تعداد کانال‌های فعال
    active_channels = await ChannelService.get_user_channels(
        db=test_db,
        owner_id=12345
    )
    assert len(active_channels) == 2

    # 6. تست محدودیت‌ها
    # تلاش برای افزودن کانال تکراری
    with pytest.raises(ValueError):
        await ChannelService.add_channel(
            db=test_db,
            channel_id=channels[1].channel_id,
            title="Duplicate Channel",
            username=channels[1].username,
            owner_id=12345
        )

    # 7. تست عملکرد چند کاربره
    # ایجاد داده برای کاربر دوم
    other_user_id = 67890
    other_channel = await ChannelService.add_channel(
        db=test_db,
        channel_id="@other_channel",
        title="Other User Channel",
        username="@other_channel",
        owner_id=other_user_id
    )
    
    other_ad = await AdvertisementService.add_advertisement(
        db=test_db,
        content="Other user ad",
        ad_type="text",
        media_id=None,
        owner_id=other_user_id
    )

    # بررسی جداسازی داده‌ها
    user1_ads = await AdvertisementService.get_user_advertisements(db=test_db, owner_id=12345)
    user2_ads = await AdvertisementService.get_user_advertisements(db=test_db, owner_id=other_user_id)
    assert len(user1_ads) == len(ads)
    assert len(user2_ads) == 1

    # 8. تست حذف همزمان
    # حذف همه تبلیغات کاربر اول
    for ad in ads:
        success = await AdvertisementService.remove_advertisement(
            db=test_db,
            ad_id=ad.id,
            owner_id=12345
        )
        assert success == True

    # بررسی عدم تأثیر بر داده‌های کاربر دوم
    other_user_ads = await AdvertisementService.get_user_advertisements(
        db=test_db,
        owner_id=other_user_id
    )
    assert len(other_user_ads) == 1
    assert other_user_ads[0].id == other_ad.id

    # 9. تست وضعیت نهایی سیستم
    final_user1_ads = await AdvertisementService.get_user_advertisements(db=test_db, owner_id=12345)
    final_user1_channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    assert len(final_user1_ads) == 0
    assert len(final_user1_channels) == 2
