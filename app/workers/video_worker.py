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
from app.services.subscription.subscription_service import SubscriptionService
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

    async def _process_job_isolated(self, job_id: int) -> bool:
        """
        Process a single job inside its OWN database session.

        SQLAlchemy ``AsyncSession`` is not safe for concurrent use, so each
        job processed via ``asyncio.gather`` must own its session. Sharing one
        session across gathered tasks is what produced the recurring
        "This transaction is closed" / "_prepare_impl is already in progress"
        failures in production.
        """
        try:
            async with async_session_maker() as session:
                service = VideoJobService(session)
                job = await service.repository.get_by_id(job_id)
                if not job:
                    logger.warning("video_job_disappeared_before_processing", job_id=job_id)
                    return False
                return await service.process_job(job, self.bot)
        except Exception as e:
            logger.error("video_job_isolated_processing_failed", job_id=job_id, error=str(e))
            return False

    async def process_pending_jobs(self):
        """Process pending video jobs."""
        try:
            # Fetch the batch in a short-lived session, then release it before
            # spawning per-job tasks so each task gets an isolated session.
            async with async_session_maker() as session:
                service = VideoJobService(session)
                pending_jobs = await service.get_pending_jobs(limit=10)
                job_ids = [job.id for job in pending_jobs[:5]]  # Process max 5 simultaneously

            if not job_ids:
                logger.debug("no_pending_video_jobs")
                return

            logger.info("processing_pending_video_jobs", count=len(job_ids))

            # Each job runs in its own DB session (sessions are not concurrency-safe).
            tasks = [
                asyncio.create_task(self._process_job_isolated(job_id))
                for job_id in job_ids
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for r in results if r is True)
            logger.info("video_jobs_processed", total=len(tasks), success=success_count)

        except Exception as e:
            logger.error("process_pending_jobs_failed", error=str(e))

    async def _fail_timeout_job_isolated(self, job_id: int) -> None:
        """Mark a retry-exhausted job as failed, refund and notify — own session."""
        try:
            async with async_session_maker() as session:
                service = VideoJobService(session)
                job = await service.repository.get_by_id(job_id)
                if not job:
                    return

                await service.update_job_status(
                    job.id,
                    "failed",
                    error_message="Maximum retry attempts exceeded"
                )

                refund_note = ""
                if job.tokens_cost > 0:
                    try:
                        sub_service = SubscriptionService(session)
                        await sub_service.rollback_tokens(job.user_id, job.tokens_cost)
                        logger.info(
                            "timeout_job_tokens_refunded",
                            job_id=job.id,
                            user_id=job.user_id,
                            tokens=job.tokens_cost,
                        )
                        refund_note = "\n\nТокены возвращены на ваш счёт."
                    except Exception as refund_err:
                        logger.error(
                            "timeout_job_token_refund_failed",
                            job_id=job.id,
                            user_id=job.user_id,
                            error=str(refund_err),
                        )

                if job.progress_message_id:
                    try:
                        await self.bot.edit_message_text(
                            chat_id=job.chat_id,
                            message_id=job.progress_message_id,
                            text=f"❌ Не удалось сгенерировать видео после нескольких попыток.{refund_note}"
                        )
                    except Exception:
                        try:
                            await self.bot.send_message(
                                chat_id=job.chat_id,
                                text=f"❌ Не удалось сгенерировать видео после нескольких попыток.{refund_note}"
                            )
                        except Exception:
                            pass
        except Exception as e:
            logger.error("fail_timeout_job_isolated_failed", job_id=job_id, error=str(e))

    async def retry_timeout_waiting_jobs(self):
        """Retry jobs that timed out initially."""
        try:
            # Snapshot the batch in a short-lived session, then release it so
            # each job gets its own isolated session (see _process_job_isolated).
            async with async_session_maker() as session:
                service = VideoJobService(session)
                timeout_jobs = await service.get_timeout_waiting_jobs(limit=10)
                # Capture only the plain attributes we need before the session closes.
                retry_ids = [job.id for job in timeout_jobs[:3] if job.can_retry]
                exhausted_ids = [job.id for job in timeout_jobs[:3] if not job.can_retry]

            if not retry_ids and not exhausted_ids:
                return

            logger.info(
                "retrying_timeout_waiting_jobs",
                retry=len(retry_ids),
                exhausted=len(exhausted_ids),
            )

            tasks = [
                asyncio.create_task(self._process_job_isolated(job_id))
                for job_id in retry_ids
            ]
            tasks += [
                asyncio.create_task(self._fail_timeout_job_isolated(job_id))
                for job_id in exhausted_ids
            ]

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error("retry_timeout_jobs_failed", error=str(e))

    async def cleanup_expired_jobs(self):
        """Clean up expired jobs, refund tokens, and notify users."""
        try:
            async with async_session_maker() as session:
                service = VideoJobService(session)
                count = await service.cleanup_expired_jobs(bot=self.bot)

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
