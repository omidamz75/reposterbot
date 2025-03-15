import pytest
from datetime import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.scheduler.models import Schedule

TEST_DATABASE_URL = "sqlite:///test_scheduler.db"
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
async def test_create_basic_schedule(test_db):
    """تست ایجاد یک زمان‌بندی ساده"""
    schedule = Schedule(
        owner_id=12345,
        interval_minutes=30,
        start_time=time(9, 0),  # 9:00 AM
        end_time=time(18, 0)    # 6:00 PM
    )
    
    test_db.add(schedule)
    test_db.commit()
    test_db.refresh(schedule)
    
    assert schedule.id is not None
    assert schedule.owner_id == 12345
    assert schedule.interval_minutes == 30
    assert schedule.start_time == time(9, 0)
    assert schedule.end_time == time(18, 0)
    assert schedule.is_active == True

@pytest.mark.asyncio
async def test_scheduler_service_operations(test_db):
    """تست عملیات سرویس زمان‌بندی"""
    from modules.scheduler.services import SchedulerService
    
    # 1. ایجاد زمان‌بندی
    schedule = await SchedulerService.create_schedule(
        db=test_db,
        owner_id=12345,
        interval_minutes=30,
        start_time=time(9, 0),
        end_time=time(18, 0)
    )
    assert schedule.interval_minutes == 30
    assert schedule.is_active == True

    # 2. بروزرسانی زمان‌بندی
    updated = await SchedulerService.update_schedule(
        db=test_db,
        schedule_id=schedule.id,
        owner_id=12345,
        interval_minutes=45,
        start_time=time(10, 0)
    )
    assert updated.interval_minutes == 45
    assert updated.start_time == time(10, 0)

    # 3. دریافت لیست زمان‌بندی‌ها
    schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=12345)
    assert len(schedules) == 1
    assert schedules[0].id == schedule.id

    # 4. حذف زمان‌بندی
    success = await SchedulerService.delete_schedule(
        db=test_db,
        schedule_id=schedule.id,
        owner_id=12345
    )
    assert success == True

    # 5. بررسی عدم نمایش زمان‌بندی حذف شده
    schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=12345)
    assert len(schedules) == 0

@pytest.mark.asyncio
async def test_multiple_users_schedules(test_db):
    """تست جداسازی زمان‌بندی کاربران مختلف"""
    from modules.scheduler.services import SchedulerService

    # ایجاد زمان‌بندی برای دو کاربر مختلف
    user1_schedule = await SchedulerService.create_schedule(
        db=test_db,
        owner_id=11111,
        interval_minutes=30,
        start_time=time(9, 0),
        end_time=time(18, 0)
    )

    user2_schedule = await SchedulerService.create_schedule(
        db=test_db,
        owner_id=22222,
        interval_minutes=60,
        start_time=time(10, 0),
        end_time=time(20, 0)
    )

    # بررسی جداسازی داده‌ها
    user1_schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=11111)
    user2_schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=22222)

    assert len(user1_schedules) == 1
    assert len(user2_schedules) == 1
    assert user1_schedules[0].interval_minutes == 30
    assert user2_schedules[0].interval_minutes == 60

@pytest.mark.asyncio
async def test_comprehensive_scheduler_workflow(test_db):
    """تست جامع سیستم زمان‌بندی"""
    from modules.scheduler.services import SchedulerService
    from datetime import time

    # 1. ایجاد چند زمان‌بندی مختلف
    schedules = []
    test_data = [
        (30, time(9, 0), time(18, 0)),  # زمان‌بندی روزانه
        (60, time(20, 0), time(23, 59)),  # زمان‌بندی شبانه
        (45, time(12, 0), time(15, 0))   # زمان‌بندی ظهر
    ]

    for interval, start, end in test_data:
        schedule = await SchedulerService.create_schedule(
            db=test_db,
            owner_id=12345,
            interval_minutes=interval,
            start_time=start,
            end_time=end
        )
        schedules.append(schedule)
        assert schedule.is_active == True

    # 2. بررسی تعداد زمان‌بندی‌های فعال
    active_schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=12345)
    assert len(active_schedules) == 3

    # 3. تست ویرایش متوالی یک زمان‌بندی
    test_schedule = schedules[0]
    updates = [
        {"interval_minutes": 40},
        {"start_time": time(10, 0)},
        {"end_time": time(19, 0)},
        {"interval_minutes": 35, "start_time": time(8, 0), "end_time": time(20, 0)}
    ]

    for update_data in updates:
        updated = await SchedulerService.update_schedule(
            db=test_db,
            schedule_id=test_schedule.id,
            owner_id=12345,
            **update_data
        )
        for key, value in update_data.items():
            assert getattr(updated, key) == value

    # 4. تست حذف و بررسی امنیت
    # حذف زمان‌بندی اول
    success = await SchedulerService.delete_schedule(
        db=test_db,
        schedule_id=schedules[0].id,
        owner_id=12345
    )
    assert success == True

    # تلاش برای حذف با کاربر نامعتبر
    success = await SchedulerService.delete_schedule(
        db=test_db,
        schedule_id=schedules[1].id,
        owner_id=99999  # کاربر نامعتبر
    )
    assert success == False

    # 5. تست محدودیت‌ها
    # تلاش برای آپدیت زمان‌بندی غیرفعال
    deleted_schedule = await SchedulerService.update_schedule(
        db=test_db,
        schedule_id=schedules[0].id,  # زمان‌بندی حذف شده
        owner_id=12345,
        interval_minutes=50
    )
    assert deleted_schedule is None

    # 6. تست عملکرد چند کاربره
    # ایجاد زمان‌بندی برای کاربر دیگر
    other_user_schedule = await SchedulerService.create_schedule(
        db=test_db,
        owner_id=67890,
        interval_minutes=25,
        start_time=time(10, 0),
        end_time=time(22, 0)
    )

    # بررسی جداسازی داده‌ها
    user1_schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=12345)
    user2_schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=67890)

    assert len(user1_schedules) == 2  # یکی حذف شده
    assert len(user2_schedules) == 1
    assert user2_schedules[0].interval_minutes == 25

    # 7. تست وضعیت نهایی
    final_schedules = await SchedulerService.get_user_schedules(db=test_db, owner_id=12345)
    assert len(final_schedules) == 2
    assert all(schedule.is_active for schedule in final_schedules)

@pytest.mark.asyncio
async def test_scheduler_handlers_workflow(test_db):
    """تست جریان کار هندلرهای زمان‌بندی"""
    from modules.scheduler.services import SchedulerService
    from modules.scheduler.handlers import edit_schedule, remove_schedule
    from datetime import time
    
    # 1. ایجاد یک زمان‌بندی اولیه
    initial_schedule = await SchedulerService.create_schedule(
        db=test_db,
        owner_id=12345,
        interval_minutes=30,
        start_time=time(9, 0),
        end_time=time(18, 0)
    )
    assert initial_schedule is not None
    
    # 2. تست ویرایش زمان‌بندی
    updated_schedule = await SchedulerService.update_schedule(
        db=test_db,
        schedule_id=initial_schedule.id,
        owner_id=12345,
        interval_minutes=45,
        start_time=time(10, 0),
        end_time=time(19, 0)
    )
    assert updated_schedule.interval_minutes == 45
    assert updated_schedule.start_time == time(10, 0)
    assert updated_schedule.end_time == time(19, 0)
    
    # 3. تست حذف زمان‌بندی
    success = await SchedulerService.delete_schedule(
        db=test_db,
        schedule_id=initial_schedule.id,
        owner_id=12345
    )
    assert success == True
    
    # 4. تست عدم امکان ویرایش زمان‌بندی حذف شده
    deleted_update = await SchedulerService.update_schedule(
        db=test_db,
        schedule_id=initial_schedule.id,
        owner_id=12345,
        interval_minutes=60
    )
    assert deleted_update is None
