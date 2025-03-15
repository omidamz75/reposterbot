import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.channels.services import ChannelService

TEST_DATABASE_URL = "sqlite:///test_channels.db"
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
async def test_basic_channel_operations(test_db):
    """تست عملیات‌های پایه کانال"""
    # 1. افزودن کانال
    channel = await ChannelService.add_channel(
        db=test_db,
        channel_id="@test_channel",
        title="Test Channel",
        username="@test",
        owner_id=12345
    )
    assert channel.channel_id == "@test_channel"
    assert channel.is_active == True

    # 2. تست افزودن کانال تکراری
    with pytest.raises(ValueError):
        await ChannelService.add_channel(
            db=test_db,
            channel_id="@test_channel",
            title="Duplicate Channel",
            username="@test",
            owner_id=12345
        )

    # 3. دریافت لیست کانال‌ها
    channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    assert len(channels) == 1
    assert channels[0].channel_id == "@test_channel"

    # 4. حذف کانال
    success = await ChannelService.remove_channel(
        db=test_db,
        channel_id="@test_channel",
        owner_id=12345
    )
    assert success == True

    # 5. بررسی لیست بعد از حذف
    channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    assert len(channels) == 0
