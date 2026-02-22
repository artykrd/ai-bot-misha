"""
Models for post-subscription-expiry notifications.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin


class ExpiryNotificationSettings(Base, BaseModel, TimestampMixin):
    """Settings for automatic post-expiry notifications."""

    __tablename__ = "expiry_notification_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # When to send (days after subscription expiry)
    delay_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=5,
        comment="Days after expiry to send notification"
    )

    # Notification content
    message_text: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Notification message text"
    )

    # Discount settings
    has_discount: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="Whether to include a discount"
    )
    discount_percent: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        comment="Discount percentage (0-100)"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True,
        comment="Whether this notification rule is active"
    )


class ExpiryNotificationLog(Base, BaseModel, TimestampMixin):
    """Log of sent expiry notifications to prevent duplicates."""

    __tablename__ = "expiry_notification_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="User who received the notification"
    )

    subscription_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="Expired subscription that triggered this notification"
    )

    settings_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("expiry_notification_settings.id", ondelete="CASCADE"),
        nullable=False,
        comment="Settings rule that triggered this notification"
    )

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="When the notification was sent"
    )

    delivered: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Whether the notification was successfully delivered"
    )
