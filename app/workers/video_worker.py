"""
Background worker for processing video generation jobs.

This worker:
- Polls pending jobs from database
- Processes them asynchronously
- Retries timeout_waiting jobs
- Sends results to users via bot
- Cleans up expired jobs
"""
import asyncio
from typing import Optional

from aiogram import Bot

from app.database.database import async_session_maker
from app.services.video_job_service import VideoJobService
from app.database.models.system import SystemSetting
from app.core.logger import get_logger
from sqlalchemy import select

logger = get_logger(__name__)


class VideoWorker:
    """Background worker for async video generation."""

    def __init__(self, bot: Bot, poll_interval: int = 30):
        """
        Initialize video worker.

        Args:
            bot: Telegram bot instance
            poll_interval: Seconds between polling cycles
        """
        self.bot = bot
        self.poll_interval = poll_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def is_feature_enabled(self) -> bool:
        """Check if async video is enabled via feature flag."""
        try:
            async with async_session_maker() as session:
                result = await session.execute(
                    select(SystemSetting).where(SystemSetting.key == "async_video_enabled")
                )
                setting = result.scalar_one_or_none()
                if not setting:
                    return True  # Enabled by default
                return setting.value.lower() in ("true", "1", "yes")
        except Exception as e:
            logger.warning("failed_to_check_async_video_flag", error=str(e))
            return True  # Default to enabled

    async def process_pending_jobs(self):
        """Process pending video jobs."""
        try:
            async with async_session_maker() as session:
                service = VideoJobService(session)

                # Get pending jobs
                pending_jobs = await service.get_pending_jobs(limit=10)

                if not pending_jobs:
                    logger.debug("no_pending_video_jobs")
                    return

                logger.info("processing_pending_video_jobs", count=len(pending_jobs))

                # Process jobs concurrently (max 5 at a time to avoid overload)
                tasks = []
                for job in pending_jobs[:5]:  # Process max 5 simultaneously
                    task = asyncio.create_task(service.process_job(job, self.bot))
                    tasks.append(task)

                # Wait for all to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                success_count = sum(1 for r in results if r is True)
                logger.info("video_jobs_processed", total=len(tasks), success=success_count)

        except Exception as e:
            logger.error("process_pending_jobs_failed", error=str(e))

    async def retry_timeout_waiting_jobs(self):
        """Retry jobs that timed out initially."""
        try:
            async with async_session_maker() as session:
                service = VideoJobService(session)

                # Get timeout_waiting jobs
                timeout_jobs = await service.get_timeout_waiting_jobs(limit=10)

                if not timeout_jobs:
                    return

                logger.info("retrying_timeout_waiting_jobs", count=len(timeout_jobs))

                # Process jobs (fewer concurrently since these already took long)
                tasks = []
                for job in timeout_jobs[:3]:  # Max 3 retries simultaneously
                    # Only retry if not exceeded max attempts
                    if job.can_retry:
                        task = asyncio.create_task(service.process_job(job, self.bot))
                        tasks.append(task)
                    else:
                        # Mark as failed if max attempts exceeded
                        await service.update_job_status(
                            job.id,
                            "failed",
                            error_message="Maximum retry attempts exceeded"
                        )

                        # Notify user
                        if job.progress_message_id:
                            try:
                                await self.bot.edit_message_text(
                                    chat_id=job.chat_id,
                                    message_id=job.progress_message_id,
                                    text="❌ Не удалось сгенерировать видео после нескольких попыток."
                                )
                            except Exception:
                                pass

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error("retry_timeout_jobs_failed", error=str(e))

    async def cleanup_expired_jobs(self):
        """Clean up expired jobs."""
        try:
            async with async_session_maker() as session:
                service = VideoJobService(session)
                count = await service.cleanup_expired_jobs()

                if count > 0:
                    logger.info("expired_jobs_cleaned_up", count=count)

        except Exception as e:
            logger.error("cleanup_expired_jobs_failed", error=str(e))

    async def _run_loop(self):
        """Main worker loop."""
        logger.info("video_worker_started", poll_interval=self.poll_interval)

        while self._running:
            try:
                # Check if feature is enabled
                if not await self.is_feature_enabled():
                    logger.debug("async_video_disabled_skipping")
                    await asyncio.sleep(self.poll_interval)
                    continue

                # Process pending jobs
                await self.process_pending_jobs()

                # Retry timeout jobs (less frequently - every 3rd cycle)
                if hasattr(self, '_cycle_count'):
                    self._cycle_count += 1
                else:
                    self._cycle_count = 0

                if self._cycle_count % 3 == 0:
                    await self.retry_timeout_waiting_jobs()

                # Cleanup expired jobs (every 10th cycle)
                if self._cycle_count % 10 == 0:
                    await self.cleanup_expired_jobs()

            except Exception as e:
                logger.error("video_worker_cycle_error", error=str(e))

            # Wait before next cycle
            await asyncio.sleep(self.poll_interval)

        logger.info("video_worker_stopped")

    def start(self):
        """Start the worker."""
        if self._running:
            logger.warning("video_worker_already_running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("video_worker_task_created")

    async def stop(self):
        """Stop the worker gracefully."""
        if not self._running:
            return

        logger.info("stopping_video_worker")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("video_worker_stopped")
