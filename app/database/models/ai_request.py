"""
AI Request model for logging all AI service requests.
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class AIRequest(Base, BaseModel, TimestampMixin):
    """AI Request model for tracking all AI API calls."""

    __tablename__ = "ai_requests"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Request details
    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: text, image, video, audio"
    )

    ai_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="AI model name"
    )

    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cost and status
    tokens_cost: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Status: pending, completed, failed"
    )

    # Response
    response_file_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Path to generated file"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if failed"
    )

    processing_time_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Processing time in seconds"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_requests")

    @property
    def is_completed(self) -> bool:
        """Check if request completed successfully."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if request failed."""
        return self.status == "failed"

    @property
    def is_pending(self) -> bool:
        """Check if request is still pending."""
        return self.status == "pending"
