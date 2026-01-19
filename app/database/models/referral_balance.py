"""
Referral balance model for storing separate money/token balances.
"""
from decimal import Decimal

from sqlalchemy import BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin


class ReferralBalance(Base, BaseModel, TimestampMixin):
    """Referral balance for a user."""

    __tablename__ = "referral_balances"
    # TODO: migration

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    tokens_balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    money_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    user = relationship("User", lazy="selectin")
