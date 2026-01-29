"""
Scheduled tasks for reporting.

This module provides functions to register scheduled tasks
with the application's scheduler.
"""
from app.core.scheduler import scheduler
from app.core.logger import get_logger
from app.services.reporting.reporting_service import send_daily_business_report

logger = get_logger(__name__)


def register_reporting_tasks():
    """
    Register reporting scheduled tasks.

    This function should be called during application startup,
    after the scheduler is started.

    Tasks:
    - Daily business report at 09:00 MSK (06:00 UTC)
    """
    # Daily business report at 06:00 UTC (09:00 MSK)
    scheduler.add_cron_job(
        send_daily_business_report,
        hour=6,
        minute=0,
    )

    logger.info(
        "reporting_tasks_registered",
        tasks=["daily_business_report"],
        schedule="06:00 UTC (09:00 MSK)"
    )
