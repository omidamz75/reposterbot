============================================ test session starts =============================================
platform win32 -- Python 3.12.6, pytest-7.4.3, pluggy-1.5.0 -- C:\Users\KPC\Desktop\reposter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\KPC\Desktop\reposter
configfile: pytest.ini
plugins: anyio-4.8.0, asyncio-0.23.2
asyncio: mode=Mode.AUTO
collected 7 items

tests/test_channels.py::test_add_channel PASSED                                                         [ 14%]
tests/test_channels.py::test_get_user_channels PASSED                                                   [ 28%]
tests/test_channels.py::test_remove_channel PASSED                                                      [ 42%]
tests/test_channels.py::test_duplicate_channel PASSED                                                   [ 57%]
tests/test_channels.py::test_multiple_users_channels PASSED                                             [ 71%]
tests/test_channels.py::test_remove_nonexistent_channel PASSED                                          [ 85%]
tests/test_channels.py::test_channel_numbering_after_multiple_operations FAILED                         [100%]

================================================== FAILURES ================================================== 
______________________________ test_channel_numbering_after_multiple_operations ______________________________ 

test_db = <sqlalchemy.orm.session.Session object at 0x000002D6BB249E80>

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

        # Remove channels 2 and 4
        await ChannelService.remove_channel_by_number(db=test_db, number=2, owner_id=12345)
        await ChannelService.remove_channel_by_number(db=test_db, number=4, owner_id=12345)

        # Add two new channels
        await ChannelService.add_channel(
            db=test_db,
            channel_id="@channel_new1",
            title="New Channel 1",
            username="@channel_new1",
            owner_id=12345
        )
        await ChannelService.add_channel(
            db=test_db,
            channel_id="@channel_new2",
            title="New Channel 2",
            username="@channel_new2",
            owner_id=12345
        )

        # Check final channel list
        channels = await ChannelService.get_user_channels(db=test_db, owner_id=12345)
        assert len(channels) == 5

        # Verify channel order by channel_id
        channel_ids = [ch.channel_id for ch in channels]
>       assert channel_ids == ["@channel0", "@channel1", "@channel3", "@channel_new1", "@channel_new2"]        
E       AssertionError: assert ['@channel0',...channel_new2'] == ['@channel0',...channel_new2']
E         At index 1 diff: '@channel2' != '@channel1'
E         Full diff:
E         - ['@channel0', '@channel1', '@channel3', '@channel_new1', '@channel_new2']
E         ?                        ^
E         + ['@channel0', '@channel2', '@channel3', '@channel_new1', '@channel_new2']
E         ?                        ^

tests\test_channels.py:196: AssertionError
========================================== short test summary info =========================================== 
FAILED tests/test_channels.py::test_channel_numbering_after_multiple_operations - AssertionError: assert ['@channel0',...channel_new2'] == ['@channel0',...channel_new2']
======================================== 1 failed, 6 passed in 2.18s ========================================= 