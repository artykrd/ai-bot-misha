"""
Promocode models for discount and bonus system.
"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class Promocode(Base, BaseModel, TimestampMixin):
    """Promocode model for bonuses and discounts."""

    __tablename__ = "promocodes"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Promocode details
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Promocode string"
    )

    bonus_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type: tokens, discount_percent, subscription"
    )

    bonus_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Bonus amount (tokens or discount percent)"
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
        comment="Expiration date (NULL = never expires)"
    )

    # Relationships
    uses: Mapped[List["PromocodeUse"]] = relationship(
        "PromocodeUse",
        back_populates="promocode",
        lazy="selectin"
    )

    @property
    def is_valid(self) -> bool:
        """Check if promocode is valid."""
        if not self.is_active:
            return False

        if self.expires_at and self.expires_at < datetime.utcnow():
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


class PromocodeUse(Base, BaseModel, TimestampMixin):
    """Track promocode usage by users."""

    __tablename__ = "promocode_uses"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign keys
    promocode_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("promocodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Usage details
    bonus_received: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Actual bonus received"
    )

    # Relationships
    promocode: Mapped["Promocode"] = relationship("Promocode", back_populates="uses")
