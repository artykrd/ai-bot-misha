"""
Channel subscription bonus models.
Tracks channel bonus configurations and user claims.
"""
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import BigInteger, String, Text, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class ChannelSubscriptionBonus(Base, BaseModel, TimestampMixin):
    """Configuration for channel subscription bonuses."""

    __tablename__ = "channel_subscription_bonuses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Channel info
    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Telegram channel/chat numeric ID"
    )

    channel_username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Channel @username (without @) for display"
    )

    channel_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Channel display title"
    )

    # Bonus settings
    bonus_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        comment="Number of tokens to award for subscription"
    )

    welcome_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Custom message shown when bonus is awarded"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether this bonus is currently active"
    )

    # Claims relationship
    claims: Mapped[list["ChannelBonusClaim"]] = relationship(
        "ChannelBonusClaim",
        back_populates="bonus",
        lazy="selectin"
    )


class ChannelBonusClaim(Base, BaseModel, TimestampMixin):
    """Tracks which users have claimed channel subscription bonuses."""

    __tablename__ = "channel_bonus_claims"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who claimed the bonus"
    )

    bonus_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("channel_subscription_bonuses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the bonus configuration"
    )

    tokens_awarded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Actual tokens awarded at the time of claim"
    )

    # Relationships
    bonus: Mapped["ChannelSubscriptionBonus"] = relationship(
        "ChannelSubscriptionBonus",
        back_populates="claims"
    )

    __table_args__ = (
        Index('idx_channel_bonus_claims_user_bonus', 'user_id', 'bonus_id', unique=True),
    )
