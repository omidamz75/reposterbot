import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.channels.models import Channel
from modules.channels.services import ChannelService

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio

# Test database configuration
TEST_DATABASE_URL = "sqlite:///test_database.db"
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

# Mark all test functions as async
@pytest.mark.asyncio
async def test_add_channel(test_db):
    """تست اضافه کردن کانال"""
    channel = await ChannelService.add_channel(
        db=test_db,
        channel_id="@test_channel",
        title="Test Channel",
        username="@test_channel",
        owner_id=12345
    )
    
    assert channel is not None
    assert channel.channel_id == "@test_channel"
    assert channel.is_active == True

@pytest.mark.asyncio
async def test_get_user_channels(test_db):
    """تست دریافت لیست کانال‌ها"""
    # Add two channels
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@channel1",
        title="Channel 1",
        username="@channel1",
        owner_id=12345
    )
    
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@channel2",
        title="Channel 2",
        username="@channel2",
        owner_id=12345
    )
    
    channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    assert len(channels) == 2
    assert channels[0].channel_id == "@channel1"
    assert channels[1].channel_id == "@channel2"

@pytest.mark.asyncio
async def test_remove_channel(test_db):
    """تست حذف کانال"""
    # Add channel
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@test_channel",
        title="Test Channel",
        username="@test_channel",
        owner_id=12345
    )
    
    # Remove by position
    success = await ChannelService.remove_channel_by_number(
        db=test_db,
        number=1,
        owner_id=12345
    )
    
    assert success == True
    channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    assert len(channels) == 0

@pytest.mark.asyncio
async def test_duplicate_channel(test_db):
    """تست اضافه کردن کانال تکراری"""
    # Add first channel
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@test_channel",
        title="Test Channel",
        username="@test_channel",
        owner_id=12345
    )
    
    # Try to add same channel
    with pytest.raises(ValueError):
        await ChannelService.add_channel(
            db=test_db,
            channel_id="@test_channel",
            title="Test Channel 2",
            username="@test_channel",
            owner_id=12345
        )

@pytest.mark.asyncio
async def test_multiple_users_channels(test_db):
    """تست جداسازی کانال‌های کاربران مختلف"""
    # Add channels for two different users
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@channel1",
        title="Channel 1",
        username="@channel1",
        owner_id=12345
    )
    
    await ChannelService.add_channel(
        db=test_db,
        channel_id="@channel2",
        title="Channel 2",
        username="@channel2",
        owner_id=67890
    )
    
    user1_channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    user2_channels = await ChannelService.get_user_channels(db=test_db, owner_id=67890)
    
    assert len(user1_channels) == 1
    assert len(user2_channels) == 1
    assert user1_channels[0].channel_id == "@channel1"
    assert user2_channels[0].channel_id == "@channel2"

@pytest.mark.asyncio
async def test_remove_nonexistent_channel(test_db):
    """تست حذف کانال غیرموجود"""
    success = await ChannelService.remove_channel_by_number(
        db=test_db,
        number=1,
        owner_id=12345
    )
    assert success == False

@pytest.mark.asyncio
async def test_channel_numbering_after_multiple_operations(test_db):
    """تست عملیات متوالی روی کانال‌ها"""
    # Add 5 channels
    for i in range(5):
        await ChannelService.add_channel(
            db=test_db,
            channel_id=f"@channel{i}",
            title=f"Channel {i}",
            username=f"@channel{i}",
            owner_id=12345
        )

    # Remove channels 2 and 4 (1-based indexing)
    await ChannelService.remove_channel_by_number(db=test_db, number=2, owner_id=12345)
    # After first removal, channel 4 becomes channel 3 in the list
    await ChannelService.remove_channel_by_number(db=test_db, number=3, owner_id=12345)

    # Add two new channels
    for i in range(2):
        await ChannelService.add_channel(
            db=test_db,
            channel_id=f"@channel_new{i+1}",
            title=f"New Channel {i+1}",
            username=f"@channel_new{i+1}",
            owner_id=12345
        )

    # Check final channel list
    channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
    assert len(channels) == 5
    expected_ids = ["@channel0", "@channel1", "@channel3", "@channel_new1", "@channel_new2"]
    actual_ids = [ch.channel_id for ch in channels]
    assert actual_ids == expected_ids

if __name__ == "__main__":
    pytest.main(["-v"])
