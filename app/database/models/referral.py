"""
Referral model for managing referral program.
"""
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import BigInteger, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class Referral(Base, BaseModel, TimestampMixin):
    """Referral model for tracking referral relationships."""

    __tablename__ = "referrals"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign keys
    referrer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who referred"
    )

    referred_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
        comment="User who was referred"
    )

    # Referral details
    referral_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Referral code used"
    )

    referral_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
        comment="Type: user (50% tokens) or partner (10% money)"
    )

    # Earnings
    tokens_earned: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Total tokens earned (for user referrals)"
    )

    money_earned: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Total money earned (for partner referrals)"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # Relationships
    referrer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[referrer_id],
        back_populates="referrals_given"
    )

    referred: Mapped["User"] = relationship(
        "User",
        foreign_keys=[referred_id],
        back_populates="referral_received"
    )

    @property
    def is_partner(self) -> bool:
        """Check if this is a partner referral."""
        return self.referral_type == "partner"

    @property
    def is_user_referral(self) -> bool:
        """Check if this is a user referral."""
        return self.referral_type == "user"
