"""
Payment model for tracking all payment operations.
"""
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import BigInteger, String, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.subscription import Subscription


class Payment(Base, BaseModel, TimestampMixin):
    """Payment model for all financial transactions."""

    __tablename__ = "payments"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    subscription_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Payment details
    payment_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Internal payment ID"
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Status: pending, success, failed, refunded"
    )

    payment_method: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Payment method used"
    )

    # YooKassa integration
    yukassa_payment_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="YooKassa payment ID"
    )

    yukassa_response: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Full YooKassa response"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")

    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription",
        back_populates="payment"
    )

    @property
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == "success"

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == "pending"

    @property
    def is_refunded(self) -> bool:
        """Check if payment was refunded."""
        return self.status == "refunded"
