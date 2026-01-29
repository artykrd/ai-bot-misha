"""
Broadcast messaging models for admin notifications.
"""
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import BigInteger, String, Text, Integer, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class BroadcastMessage(Base, BaseModel, TimestampMixin):
    """Broadcast message tracking."""

    __tablename__ = "broadcast_messages"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Admin who sent the broadcast
    admin_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Admin user who created the broadcast"
    )

    # Message content
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Message text content"
    )

    image_file_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Telegram file_id for attached photo"
    )

    buttons: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="List of inline buttons: [{'text': '...', 'callback_data': '...'}]"
    )

    # Targeting
    filter_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Filter: all, subscribed, free"
    )

    # Delivery statistics
    sent_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of successfully sent messages"
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of failed deliveries"
    )

    # Timestamps (from TimestampMixin)
    # created_at, updated_at


class BroadcastClick(Base, BaseModel, TimestampMixin):
    """User clicks on broadcast buttons."""

    __tablename__ = "broadcast_clicks"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # References
    broadcast_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("broadcast_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to broadcast message"
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who clicked the button"
    )

    # Button details
    button_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="0-based index of button in buttons array"
    )

    button_text: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Button text for convenient querying"
    )

    button_callback_data: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Full callback_data"
    )

    # Timestamps (from TimestampMixin)
    # created_at, updated_at

    __table_args__ = (
        Index('idx_broadcast_clicks_broadcast_user', 'broadcast_id', 'user_id'),
        Index('idx_broadcast_clicks_created', 'created_at'),
    )
