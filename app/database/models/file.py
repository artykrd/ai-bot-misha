"""
File model for managing uploaded and generated files.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.ai_request import AIRequest


class File(Base, BaseModel, TimestampMixin):
    """File model for uploaded and generated files."""

    __tablename__ = "files"

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
        index=True
    )

    # File details
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: image, video, audio, document"
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Path to file in storage"
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type"
    )

    # Compression
    is_compressed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    original_file_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Path to original file before compression"
    )

    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When the file will be deleted"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="files")

    @property
    def is_expired(self) -> bool:
        """Check if file has expired."""
        return self.expires_at < datetime.now(timezone.utc)
