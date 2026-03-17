"""
Welcome bonus models for advertising campaign referral links.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import secrets

from sqlalchemy import BigInteger, String, Integer, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class WelcomeBonus(Base, BaseModel, TimestampMixin):
    """Welcome bonus link for advertising campaigns."""

    __tablename__ = "welcome_bonuses"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Link code
    invite_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique invite code for deep link"
    )

    # Bonus configuration
    bonus_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of tokens to award"
    )

    # Campaign name for tracking
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Campaign name for admin reference"
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

    # Relationships
    uses: Mapped[List["WelcomeBonusUse"]] = relationship(
        "WelcomeBonusUse",
        back_populates="welcome_bonus",
        lazy="selectin"
    )

    @property
    def is_valid(self) -> bool:
        """Check if welcome bonus link is valid."""
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
        return f"wb_{secrets.token_urlsafe(12)}"


class WelcomeBonusUse(Base, BaseModel, TimestampMixin):
    """Track usage of welcome bonus links by users."""

    __tablename__ = "welcome_bonus_uses"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign keys
    welcome_bonus_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("welcome_bonuses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the welcome bonus link"
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who used the link"
    )

    # Bonus details
    tokens_awarded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Actual tokens awarded at the time of use"
    )

    # Subscription tracking for conversion
    subscription_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID of created bonus subscription"
    )

    # Conversion tracking
    has_purchased: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user made a paid purchase after bonus"
    )

    first_purchase_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of first paid purchase after bonus"
    )

    first_purchase_amount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Amount of first paid purchase"
    )

    # Relationships
    welcome_bonus: Mapped["WelcomeBonus"] = relationship(
        "WelcomeBonus",
        back_populates="uses"
    )
