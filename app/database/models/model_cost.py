"""
Model cost configuration for calculating real API costs.
All pricing data is stored in the database, not hardcoded.
"""
from decimal import Decimal
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, String, Text, Integer, Boolean, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.base import BaseModel, TimestampMixin


class OperationCategory(Base, BaseModel, TimestampMixin):
    """Operation category for grouping AI operations."""

    __tablename__ = "operation_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Category code: text, image_gen, video_gen, etc."
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Maps to ai_requests.request_type: text, image, video, audio"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ModelCost(Base, BaseModel, TimestampMixin):
    """
    Model cost configuration.

    Stores all pricing information in the database,
    allowing updates without code changes.
    """

    __tablename__ = "model_costs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Model identification
    model_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Model identifier used in code"
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Provider: openai, anthropic, google, kling, suno, etc."
    )

    category_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="FK to operation_categories.code"
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="User-facing name"
    )

    # Cost configuration
    cost_usd_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        nullable=False,
        comment="Cost in USD per unit"
    )

    cost_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unit type: request, token, minute, character, second"
    )

    tokens_per_unit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Internal tokens charged per unit"
    )

    # Optional multipliers for variable costs (resolution, duration, etc.)
    unit_multipliers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Multipliers for different configurations"
    )

    # Unlimited subscription limits
    unlimited_daily_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Max requests per day for unlimited subscription"
    )

    unlimited_budget_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Token budget for unlimited subscription"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def calculate_cost_usd(self, units: float = 1.0) -> Decimal:
        """
        Calculate USD cost for given units.

        Args:
            units: Number of units (requests, tokens, minutes, etc.)

        Returns:
            Cost in USD
        """
        return self.cost_usd_per_unit * Decimal(str(units))

    def calculate_tokens(self, units: float = 1.0) -> int:
        """
        Calculate internal token cost for given units.

        Args:
            units: Number of units

        Returns:
            Token cost
        """
        return int(self.tokens_per_unit * units)

    def get_multiplier(self, key: str, default: float = 1.0) -> float:
        """
        Get unit multiplier for a specific configuration.

        Args:
            key: Multiplier key (e.g., "1080p", "10s", "hd")
            default: Default value if not found

        Returns:
            Multiplier value
        """
        if not self.unit_multipliers:
            return default
        return self.unit_multipliers.get(key, default)
