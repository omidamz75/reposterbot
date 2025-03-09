from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config import DATABASE_URL, DEFAULT_TIMEZONE

class BotScheduler:
    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(url=DATABASE_URL)
        }
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            timezone=DEFAULT_TIMEZONE
        )

    def start(self):
        self.scheduler.start()

    def add_job(self, func, trigger, **kwargs):
        return self.scheduler.add_job(func, trigger, **kwargs)

scheduler = BotScheduler()
