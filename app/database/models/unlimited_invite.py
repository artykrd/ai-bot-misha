"""
Unlimited invite link model for admin-created unlimited access links.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import secrets

from sqlalchemy import BigInteger, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class UnlimitedInviteLink(Base, BaseModel, TimestampMixin):
    """Unlimited invite link for admin-generated referral links with unlimited tokens."""

    __tablename__ = "unlimited_invite_links"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Invite details
    invite_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique invite code"
    )

    # Duration in days for unlimited access
    duration_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Duration in days (e.g., 7, 14)"
    )

    # Limitations
    max_uses: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Maximum number of uses (NULL = unlimited)"
    )

    current_uses: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Current number of uses"
    )

    # Validity
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Link expiration date (NULL = never expires)"
    )

    # Optional description
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Optional description for admin reference"
    )

    # Relationships
    uses: Mapped[List["UnlimitedInviteUse"]] = relationship(
        "UnlimitedInviteUse",
        back_populates="invite_link",
        lazy="selectin"
    )

    @property
    def is_valid(self) -> bool:
        """Check if invite link is valid."""
        if not self.is_active:
            return False

        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            return False

        if self.max_uses and self.current_uses >= self.max_uses:
            return False

        return True

    @property
    def uses_remaining(self) -> Optional[int]:
        """Get remaining uses."""
        if self.max_uses is None:
            return None
        return max(0, self.max_uses - self.current_uses)

    @staticmethod
    def generate_code() -> str:
        """Generate a random invite code."""
        return f"unlimited_{secrets.token_urlsafe(16)}"


class UnlimitedInviteUse(Base, BaseModel, TimestampMixin):
    """Track usage of unlimited invite links by users."""

    __tablename__ = "unlimited_invite_uses"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign keys
    invite_link_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("unlimited_invite_links.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the invite link"
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
        comment="User who used the link (one use per user)"
    )

    # Subscription details
    subscription_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID of created subscription"
    )

    # Relationships
    invite_link: Mapped["UnlimitedInviteLink"] = relationship(
        "UnlimitedInviteLink",
        back_populates="uses"
    )
