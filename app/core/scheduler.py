"""
Background task scheduler using APScheduler.
"""
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """Wrapper for APScheduler to manage background tasks."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._started = False

    def start(self) -> None:
        """Start the scheduler."""
        if not self._started:
            self.scheduler.start()
            self._started = True
            logger.info("scheduler_started")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            logger.info("scheduler_shutdown")

    def add_job(
        self,
        func: Callable,
        trigger: str,
        **trigger_args
    ) -> None:
        """
        Add a job to the scheduler.

        Args:
            func: Function to execute
            trigger: Trigger type ('interval', 'cron', 'date')
            **trigger_args: Arguments for the trigger
        """
        try:
            self.scheduler.add_job(func, trigger, **trigger_args)
            logger.info(
                "job_added",
                function=func.__name__,
                trigger=trigger,
                args=trigger_args
            )
        except Exception as e:
            logger.error(
                "job_add_failed",
                function=func.__name__,
                error=str(e)
            )

    def add_interval_job(
        self,
        func: Callable,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        **kwargs
    ) -> None:
        """Add a job that runs at regular intervals."""
        self.add_job(
            func,
            trigger="interval",
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            **kwargs
        )

    def add_cron_job(
        self,
        func: Callable,
        hour: int = 0,
        minute: int = 0,
        **kwargs
    ) -> None:
        """Add a job that runs at specific time daily."""
        self.add_job(
            func,
            trigger="cron",
            hour=hour,
            minute=minute,
            **kwargs
        )

    def add_daily_job(
        self,
        func: Callable,
        time_str: str = "03:00",
        **kwargs
    ) -> None:
        """
        Add a job that runs daily at specific time.

        Args:
            func: Function to execute
            time_str: Time in HH:MM format (default 03:00)
        """
        hour, minute = map(int, time_str.split(":"))
        self.add_cron_job(func, hour=hour, minute=minute, **kwargs)


# Global scheduler instance
scheduler = TaskScheduler()
