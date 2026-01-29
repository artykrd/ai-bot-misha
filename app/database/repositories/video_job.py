"""
Video generation job repository.
"""
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.video_job import VideoGenerationJob
from app.database.repositories.base import BaseRepository


class VideoJobRepository(BaseRepository[VideoGenerationJob]):
    """Repository for video generation job operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(VideoGenerationJob, session)

    async def get_by_id(self, job_id: int) -> Optional[VideoGenerationJob]:
        """Get job by ID."""
        return await self.get(job_id)

    async def get_by_task_id(self, task_id: str) -> Optional[VideoGenerationJob]:
        """Get job by provider task ID."""
        result = await self.session.execute(
            select(VideoGenerationJob).where(VideoGenerationJob.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_jobs(self, limit: Optional[int] = 100) -> List[VideoGenerationJob]:
        """
        Get pending jobs ready for processing.

        Returns jobs with status 'pending' that haven't expired.
        """
        now = datetime.now(timezone.utc)
        query = select(VideoGenerationJob).where(
            VideoGenerationJob.status == "pending",
            VideoGenerationJob.expires_at > now
        ).order_by(VideoGenerationJob.created_at).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_timeout_waiting_jobs(self, limit: Optional[int] = 100) -> List[VideoGenerationJob]:
        """
        Get jobs waiting after timeout for re-polling.

        Returns jobs with status 'timeout_waiting' that can be retried.
        """
        now = datetime.now(timezone.utc)
        query = select(VideoGenerationJob).where(
            VideoGenerationJob.status == "timeout_waiting",
            VideoGenerationJob.expires_at > now
        ).order_by(VideoGenerationJob.created_at).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_processing_jobs(self, limit: Optional[int] = 100) -> List[VideoGenerationJob]:
        """
        Get jobs currently being processed.

        Returns jobs with status 'processing'.
        """
        now = datetime.now(timezone.utc)
        query = select(VideoGenerationJob).where(
            VideoGenerationJob.status == "processing",
            VideoGenerationJob.expires_at > now
        ).order_by(VideoGenerationJob.started_processing_at).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_jobs(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: Optional[int] = 50
    ) -> List[VideoGenerationJob]:
        """Get jobs for a user, optionally filtered by status."""
        query = select(VideoGenerationJob).where(VideoGenerationJob.user_id == user_id)

        if status:
            query = query.where(VideoGenerationJob.status == status)

        query = query.order_by(VideoGenerationJob.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_expired_jobs(self, limit: Optional[int] = 100) -> List[VideoGenerationJob]:
        """Get expired jobs for cleanup."""
        now = datetime.now(timezone.utc)
        query = select(VideoGenerationJob).where(
            VideoGenerationJob.expires_at <= now,
            or_(
                VideoGenerationJob.status == "pending",
                VideoGenerationJob.status == "processing",
                VideoGenerationJob.status == "timeout_waiting"
            )
        ).order_by(VideoGenerationJob.expires_at).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

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
        ai_request_id: Optional[int] = None,
        expiration_hours: int = 24
    ) -> VideoGenerationJob:
        """Create a new video generation job."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expiration_hours)

        job = VideoGenerationJob(
            user_id=user_id,
            ai_request_id=ai_request_id,
            provider=provider,
            model_id=model_id,
            prompt=prompt,
            input_data=input_data,
            chat_id=chat_id,
            progress_message_id=progress_message_id,
            tokens_cost=tokens_cost,
            status="pending",
            expires_at=expires_at
        )

        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)

        return job

    async def update_job_status(
        self,
        job_id: int,
        status: str,
        **kwargs
    ) -> Optional[VideoGenerationJob]:
        """
        Update job status and optional fields.

        Args:
            job_id: Job ID
            status: New status
            **kwargs: Optional fields (task_id, video_path, error_message, etc.)

        Returns:
            Updated job or None if not found
        """
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.status = status

        # Update optional fields
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        # Set completed_at if finished
        if status in ("completed", "failed") and not job.completed_at:
            job.completed_at = datetime.now(timezone.utc)

        # Set started_processing_at if processing
        if status == "processing" and not job.started_processing_at:
            job.started_processing_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(job)

        return job

    async def increment_attempt(self, job_id: int) -> Optional[VideoGenerationJob]:
        """Increment job attempt count."""
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.attempt_count += 1
        await self.session.commit()
        await self.session.refresh(job)

        return job

    async def cleanup_old_jobs(self, days_old: int = 7) -> int:
        """
        Delete completed/failed jobs older than specified days.

        Returns:
            Number of jobs deleted
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)

        result = await self.session.execute(
            select(VideoGenerationJob).where(
                VideoGenerationJob.completed_at < cutoff_date,
                or_(
                    VideoGenerationJob.status == "completed",
                    VideoGenerationJob.status == "failed"
                )
            )
        )

        jobs = result.scalars().all()
        count = len(jobs)

        for job in jobs:
            await self.session.delete(job)

        await self.session.commit()

        return count
