=========================================================== test session starts ===========================================================
platform win32 -- Python 3.12.6, pytest-7.4.4, pluggy-1.5.0 -- C:\Users\KPC\Desktop\reposterbot\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\KPC\Desktop\reposterbot
configfile: pytest.ini
plugins: anyio-4.8.0, asyncio-0.23.3, cov-4.1.0
asyncio: mode=Mode.AUTO
collected 3 items

tests/test_integration.py::test_complete_ad_workflow PASSED                                                                          [ 33%]
tests/test_integration.py::test_multiple_users_isolation PASSED                                                                      [ 66%]
tests/test_integration.py::test_comprehensive_workflow FAILED                                                                        [100%]

================================================================ FAILURES ================================================================= 
_______________________________________________________ test_comprehensive_workflow _______________________________________________________ 

test_db = <sqlalchemy.orm.session.Session object at 0x000002476AF0FFE0>

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
>       with pytest.raises(Exception):
E       Failed: DID NOT RAISE <class 'Exception'>

tests\test_integration.py:200: Failed
========================================================= short test summary info ========================================================= 
FAILED tests/test_integration.py::test_comprehensive_workflow - Failed: DID NOT RAISE <class 'Exception'>
======================================================= 1 failed, 2 passed in 1.93s ======================================================= 