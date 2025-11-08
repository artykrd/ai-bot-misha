"""
Dialog models for managing AI conversations.
"""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class Dialog(Base, BaseModel, TimestampMixin):
    """Dialog model for AI conversations."""

    __tablename__ = "dialogs"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Dialog details
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    ai_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="AI model for this dialog"
    )

    system_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="System prompt/role for the AI"
    )

    is_history_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether to keep conversation history"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="dialogs")

    messages: Mapped[List["DialogMessage"]] = relationship(
        "DialogMessage",
        back_populates="dialog",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def get_history(self, limit: Optional[int] = None) -> List["DialogMessage"]:
        """Get dialog message history."""
        messages = sorted(self.messages, key=lambda m: m.created_at)
        if limit:
            return messages[-limit:]
        return messages


class DialogMessage(Base, BaseModel, TimestampMixin):
    """Dialog message model for storing conversation history."""

    __tablename__ = "dialog_messages"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key
    dialog_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("dialogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Message details
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Role: user, assistant, system"
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    tokens_used: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Tokens used for this message"
    )

    # Relationships
    dialog: Mapped["Dialog"] = relationship("Dialog", back_populates="messages")

    def to_openai_format(self) -> dict:
        """Convert to OpenAI message format."""
        return {
            "role": self.role,
            "content": self.content
        }
