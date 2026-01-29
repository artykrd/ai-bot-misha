"""
Video job service for async video generation management.
"""
import asyncio
from typing import Optional
from datetime import datetime, timezone, timedelta

from aiogram import Bot

from app.database.database import async_session_maker
from app.database.repositories.video_job import VideoJobRepository
from app.database.models.video_job import VideoGenerationJob
from app.services.video import KlingService, SoraService, VeoService, LumaService, HailuoService
from app.services.logging import log_ai_operation_background
from app.core.logger import get_logger

logger = get_logger(__name__)


class VideoJobService:
    """Service for managing async video generation jobs."""

    def __init__(self, session):
        self.session = session
        self.repository = VideoJobRepository(session)

    async def create_job(
        self,
        user_id: int,
        provider: str,
        model_id: str,
        prompt: str,
        input_data: dict,
        chat_id: int,
        tokens_cost: int,
        progress_message_id: Optional[int] = None,
        ai_request_id: Optional[int] = None
    ) -> VideoGenerationJob:
        """Create a new video generation job."""
        return await self.repository.create_job(
            user_id=user_id,
            provider=provider,
            model_id=model_id,
            prompt=prompt,
            input_data=input_data,
            chat_id=chat_id,
            tokens_cost=tokens_cost,
            progress_message_id=progress_message_id,
            ai_request_id=ai_request_id,
            expiration_hours=24
        )

    async def get_job(self, job_id: int) -> Optional[VideoGenerationJob]:
        """Get job by ID."""
        return await self.repository.get_by_id(job_id)

    async def update_job_status(
        self,
        job_id: int,
        status: str,
        **kwargs
    ) -> Optional[VideoGenerationJob]:
        """Update job status."""
        return await self.repository.update_job_status(job_id, status, **kwargs)

    def _get_video_service(self, provider: str):
        """Get video service instance by provider."""
        providers = {
            "kling": KlingService,
            "sora": SoraService,
            "veo": VeoService,
            "luma": LumaService,
            "hailuo": HailuoService,
        }

        service_class = providers.get(provider)
        if not service_class:
            raise ValueError(f"Unknown provider: {provider}")

        return service_class()

    async def process_job(self, job: VideoGenerationJob, bot: Bot) -> bool:
        """
        Process a single video generation job.

        Returns:
            True if job completed successfully, False otherwise
        """
        logger.info("processing_video_job", job_id=job.id, provider=job.provider, user_id=job.user_id)

        try:
            # Update status to processing
            await self.repository.update_job_status(
                job.id,
                "processing",
                started_processing_at=datetime.now(timezone.utc)
            )

            # Get video service
            service = self._get_video_service(job.provider)

            # Extract generation parameters
            input_data = job.input_data
            images = input_data.get("images", [])
            duration = input_data.get("duration", 5)
            aspect_ratio = input_data.get("aspect_ratio", "1:1")
            version = input_data.get("version", "2.5")

            # Attempt generation with 10-minute timeout
            try:
                result = await asyncio.wait_for(
                    service.generate_video(
                        prompt=job.prompt,
                        model=job.model_id,
                        images=images,
                        duration=duration,
                        aspect_ratio=aspect_ratio,
                        version=version
                    ),
                    timeout=600  # 10 minutes
                )
            except asyncio.TimeoutError:
                # Timeout - mark as timeout_waiting for later re-check
                logger.info("video_job_timeout", job_id=job.id, provider=job.provider)

                await self.repository.update_job_status(
                    job.id,
                    "timeout_waiting",
                    error_message="Initial generation timed out, will retry"
                )
                await self.repository.increment_attempt(job.id)

                # Send user message about waiting
                if job.progress_message_id:
                    try:
                        await bot.edit_message_text(
                            chat_id=job.chat_id,
                            message_id=job.progress_message_id,
                            text="⏳ Видео всё ещё генерируется... Мы отправим его вам, когда оно будет готово!"
                        )
                    except Exception as e:
                        logger.warning("failed_to_update_progress_message", error=str(e))

                return False

            # Check result
            if result.success:
                # Update job as completed
                await self.repository.update_job_status(
                    job.id,
                    "completed",
                    video_path=result.video_path,
                    task_id=result.metadata.get("task_id") if result.metadata else None
                )

                # Send video to user
                from aiogram.types import FSInputFile
                video_file = FSInputFile(result.video_path)
                await bot.send_video(
                    chat_id=job.chat_id,
                    video=video_file,
                    caption=f"✅ Ваше видео готово!\n\n📝 Промпт: {job.prompt[:100]}..."
                )

                # Delete progress message
                if job.progress_message_id:
                    try:
                        await bot.delete_message(chat_id=job.chat_id, message_id=job.progress_message_id)
                    except Exception:
                        pass

                logger.info("video_job_completed", job_id=job.id, provider=job.provider)
                return True

            else:
                # Failed
                error_msg = result.error or "Unknown error"
                await self.repository.update_job_status(
                    job.id,
                    "failed",
                    error_message=error_msg
                )

                # Notify user
                if job.progress_message_id:
                    try:
                        await bot.edit_message_text(
                            chat_id=job.chat_id,
                            message_id=job.progress_message_id,
                            text=f"❌ Ошибка генерации видео:\n{error_msg}"
                        )
                    except Exception:
                        pass

                logger.error("video_job_failed", job_id=job.id, provider=job.provider, error=error_msg)
                return False

        except Exception as e:
            logger.error("video_job_processing_exception", job_id=job.id, error=str(e))

            await self.repository.update_job_status(
                job.id,
                "failed",
                error_message=str(e)
            )

            # Notify user
            if job.progress_message_id:
                try:
                    await bot.edit_message_text(
                        chat_id=job.chat_id,
                        message_id=job.progress_message_id,
                        text=f"❌ Ошибка обработки задачи:\n{str(e)[:200]}"
                    )
                except Exception:
                    pass

            return False

    async def get_pending_jobs(self, limit: int = 10) -> list[VideoGenerationJob]:
        """Get pending jobs for processing."""
        return await self.repository.get_pending_jobs(limit=limit)

    async def get_timeout_waiting_jobs(self, limit: int = 10) -> list[VideoGenerationJob]:
        """Get timeout_waiting jobs for re-polling."""
        return await self.repository.get_timeout_waiting_jobs(limit=limit)

    async def cleanup_expired_jobs(self) -> int:
        """Mark expired jobs as failed."""
        expired_jobs = await self.repository.get_expired_jobs(limit=100)
        count = 0

        for job in expired_jobs:
            await self.repository.update_job_status(
                job.id,
                "failed",
                error_message="Job expired before completion"
            )
            count += 1

        if count > 0:
            logger.info("expired_jobs_cleaned", count=count)

        return count
