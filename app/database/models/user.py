"""
User model for storing Telegram user data.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Boolean, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.subscription import Subscription
    from app.database.models.payment import Payment
    from app.database.models.ai_request import AIRequest
    from app.database.models.dialog import Dialog
    from app.database.models.referral import Referral
    from app.database.models.file import File
    from app.database.models.video_job import VideoGenerationJob


class User(Base, BaseModel, TimestampMixin):
    """User model representing Telegram bot users."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Telegram data
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="ru")

    # Status
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    ban_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Activity tracking
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        lazy="selectin"
    )

    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        lazy="selectin"
    )

    ai_requests: Mapped[List["AIRequest"]] = relationship(
        "AIRequest",
        back_populates="user",
        lazy="selectin"
    )

    dialogs: Mapped[List["Dialog"]] = relationship(
        "Dialog",
        back_populates="user",
        lazy="selectin"
    )

    # Referrals where this user is the referrer
    referrals_given: Mapped[List["Referral"]] = relationship(
        "Referral",
        foreign_keys="Referral.referrer_id",
        back_populates="referrer",
        lazy="selectin"
    )

    # Referral where this user was referred
    referral_received: Mapped[Optional["Referral"]] = relationship(
        "Referral",
        foreign_keys="Referral.referred_id",
        back_populates="referred",
        uselist=False,
        lazy="selectin"
    )

    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="user",
        lazy="selectin"
    )

    video_jobs: Mapped[List["VideoGenerationJob"]] = relationship(
        "VideoGenerationJob",
        back_populates="user",
        lazy="selectin"
    )

    def get_active_subscription(self) -> Optional["Subscription"]:
        """Get currently active subscription if exists."""
        for sub in self.subscriptions:
            if sub.is_active and (sub.expires_at is None or sub.expires_at > datetime.now(timezone.utc)):
                return sub
        return None

    def get_total_tokens(self) -> int:
        """Get total available tokens across all subscriptions."""
        total = 0
        for sub in self.subscriptions:
            if sub.is_active and not sub.is_expired:
                remaining = sub.tokens_amount - sub.tokens_used
                if remaining > 0:
                    total += remaining
        return total

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else f"User {self.telegram_id}"

    @property
    def mention(self) -> str:
        """Get user mention for Telegram."""
        name = self.full_name
        return f"[{name}](tg://user?id={self.telegram_id})"
