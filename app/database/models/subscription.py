"""
Subscription model for managing user subscriptions and tokens.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.payment import Payment


class Subscription(Base, BaseModel, TimestampMixin):
    """Subscription model for user token packages."""

    __tablename__ = "subscriptions"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key to user
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Subscription details
    subscription_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: 7days, 14days, 21days, 30days, unlimited_1day, eternal"
    )

    tokens_amount: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    tokens_used: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, index=True)

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Time range
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="NULL for eternal subscriptions"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment",
        back_populates="subscription",
        uselist=False
    )

    @property
    def tokens_remaining(self) -> int:
        """Get remaining tokens."""
        return max(0, self.tokens_amount - self.tokens_used)

    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        if self.expires_at is None:
            return False  # Eternal subscription
        return self.expires_at < datetime.utcnow()

    @property
    def is_unlimited(self) -> bool:
        """Check if subscription is unlimited (1 day unlimited)."""
        return self.subscription_type == "unlimited_1day"

    @property
    def is_eternal(self) -> bool:
        """Check if subscription is eternal."""
        return self.subscription_type == "eternal"

    def can_use_tokens(self, amount: int) -> bool:
        """Check if subscription has enough tokens."""
        if not self.is_active or self.is_expired:
            return False

        if self.is_unlimited:
            return True

        return self.tokens_remaining >= amount

    def use_tokens(self, amount: int) -> bool:
        """
        Use tokens from subscription.

        Returns:
            True if tokens were successfully used
        """
        if not self.can_use_tokens(amount):
            return False

        if not self.is_unlimited:
            self.tokens_used += amount

        return True
