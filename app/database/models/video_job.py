"""
Video generation job model for async video processing.

Jobs are created when user requests video generation and processed
by background worker.
"""
from typing import TYPE_CHECKING, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, Integer, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.ai_request import AIRequest


class VideoGenerationJob(Base, BaseModel, TimestampMixin):
    """Video generation job for async processing."""

    __tablename__ = "video_generation_jobs"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    ai_request_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("ai_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Linked AI request for tracking"
    )

    # Job details
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Provider: kling, sora, veo, luma, hailuo"
    )

    model_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Model identifier (e.g., kling-2.5)"
    )

    # Provider task ID for polling
    task_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Provider's task ID for status polling"
    )

    # Job status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Status: pending, processing, timeout_waiting, completed, failed"
    )

    # Input data
    prompt: Mapped[str] = mapped_column(Text, nullable=False)

    input_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Generation parameters (images, duration, aspect_ratio, etc.)"
    )

    # Output
    video_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Path to generated video file"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if failed"
    )

    # Telegram message info for sending result
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Telegram chat ID to send result to"
    )

    progress_message_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Telegram message ID for progress updates"
    )

    # Processing metadata
    tokens_cost: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Token cost for this job"
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of processing attempts"
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum number of retry attempts"
    )

    started_processing_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When worker started processing this job"
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="When job was completed or failed"
    )

    # For cleanup and timeout detection
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Job expiration time (for cleanup)"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="video_jobs")

    ai_request: Mapped[Optional["AIRequest"]] = relationship(
        "AIRequest",
        foreign_keys=[ai_request_id],
        lazy="selectin"
    )

    @property
    def is_pending(self) -> bool:
        """Check if job is pending."""
        return self.status == "pending"

    @property
    def is_processing(self) -> bool:
        """Check if job is processing."""
        return self.status == "processing"

    @property
    def is_timeout_waiting(self) -> bool:
        """Check if job is waiting for timeout result."""
        return self.status == "timeout_waiting"

    @property
    def is_completed(self) -> bool:
        """Check if job completed successfully."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == "failed"

    @property
    def is_finished(self) -> bool:
        """Check if job is in final state."""
        return self.status in ("completed", "failed")

    @property
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.attempt_count < self.max_attempts and not self.is_finished

    @property
    def is_expired(self) -> bool:
        """Check if job has expired."""
        return self.expires_at < datetime.now(timezone.utc)
