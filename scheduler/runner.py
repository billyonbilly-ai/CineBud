from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler.jobs import poll_tmdb

scheduler = AsyncIOScheduler()

def start_scheduler(bot):
    scheduler.add_job(
        poll_tmdb,
        trigger="interval",
        hours=1,
        args=[bot],
        id="tmdb_poll",
        replace_existing=True
    )
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()