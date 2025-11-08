"""
System models for configuration and logging.
"""
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import BigInteger, String, Text, Boolean, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class AIModel(Base, BaseModel, TimestampMixin):
    """AI Model configuration."""

    __tablename__ = "ai_models"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Model details
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="System name (e.g., 'gpt-4')"
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Display name for users"
    )

    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: text, image, video, audio"
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Provider: openai, anthropic, google, etc."
    )

    # API configuration
    api_endpoint: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="API endpoint URL"
    )

    # Pricing
    tokens_per_request: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=1000,
        comment="Token cost per request"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # Rate limiting
    rate_limit_per_minute: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Rate limit per minute"
    )

    # Additional settings
    settings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Model-specific settings"
    )


class AICache(Base, BaseModel, TimestampMixin):
    """AI response cache for optimization."""

    __tablename__ = "ai_cache"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Cache keys
    request_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA256 hash of request"
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    prompt_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Hash of the prompt"
    )

    # Cached data
    response_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Cached response"
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Path to cached file if applicable"
    )

    # Usage tracking
    access_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times this cache was used"
    )

    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Cache expiration time"
    )

    @property
    def is_expired(self) -> bool:
        """Check if cache has expired."""
        return self.expires_at < datetime.utcnow()


class SystemSetting(Base, BaseModel, TimestampMixin):
    """System-wide settings."""

    __tablename__ = "system_settings"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Setting details
    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Setting key"
    )

    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Setting value (as string)"
    )

    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="string",
        comment="Type: string, int, bool, json"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Setting description"
    )


class AdminLog(Base, BaseModel, TimestampMixin):
    """Admin action logging."""

    __tablename__ = "admin_logs"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Admin user
    admin_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Action details
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed"
    )

    target_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Type of target: user, payment, etc."
    )

    target_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="ID of affected entity"
    )

    details: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional action details"
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Admin IP address"
    )
