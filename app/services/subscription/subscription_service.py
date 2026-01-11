"""
Subscription service for managing user subscriptions.
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.subscription import Subscription
from app.database.repositories.subscription import SubscriptionRepository
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError, SubscriptionExpiredError

logger = get_logger(__name__)


# Subscription tariffs configuration
TARIFFS = {
    "7days": {"days": 7, "tokens": 150000, "price": 98},
    "14days": {"days": 14, "tokens": 250000, "price": 196},
    "21days": {"days": 21, "tokens": 500000, "price": 289},
    "30days_1m": {"days": 30, "tokens": 1000000, "price": 597},
    "30days_5m": {"days": 30, "tokens": 5000000, "price": 2790},
    "unlimited_1day": {"days": 1, "tokens": -1, "price": 649},  # -1 = unlimited
    "eternal_150k": {"days": None, "tokens": 150000, "price": 149},
    "eternal_250k": {"days": None, "tokens": 250000, "price": 279},
    "eternal_500k": {"days": None, "tokens": 500000, "price": 519},
    "eternal_1m": {"days": None, "tokens": 1000000, "price": 999},
}


class SubscriptionService:
    """Service for subscription management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SubscriptionRepository(session)

    async def create_subscription(
        self,
        user_id: int,
        subscription_type: str
    ) -> Subscription:
        """Create a new subscription for user."""
        if subscription_type not in TARIFFS:
            raise ValueError(f"Invalid subscription type: {subscription_type}")

        tariff = TARIFFS[subscription_type]

        subscription = await self.repository.create_subscription(
            user_id=user_id,
            subscription_type=subscription_type,
            tokens_amount=tariff["tokens"] if tariff["tokens"] != -1 else 999999999,
            price=tariff["price"],
            duration_days=tariff["days"]
        )

        logger.info(
            "subscription_created",
            user_id=user_id,
            subscription_id=subscription.id,
            type=subscription_type
        )

        return subscription

    async def get_active_subscription(
        self,
        user_id: int
    ) -> Optional[Subscription]:
        """Get user's active subscription."""
        return await self.repository.get_active_subscription(user_id)

    async def check_and_use_tokens(
        self,
        user_id: int,
        tokens_required: int
    ) -> Subscription:
        """
        Check if user has enough tokens and use them.

        Returns:
            Subscription that was used

        Raises:
            InsufficientTokensError: If user doesn't have enough tokens
            SubscriptionExpiredError: If subscription is expired
        """
        subscription = await self.get_active_subscription(user_id)

        if not subscription:
            raise InsufficientTokensError(
                "No active subscription found",
                {"required": tokens_required, "available": 0}
            )

        if subscription.is_expired:
            raise SubscriptionExpiredError(
                "Subscription has expired",
                {"expired_at": subscription.expires_at}
            )

        if not subscription.can_use_tokens(tokens_required):
            raise InsufficientTokensError(
                f"Insufficient tokens: need {tokens_required}, have {subscription.tokens_remaining}",
                {
                    "required": tokens_required,
                    "available": subscription.tokens_remaining
                }
            )

        # Use tokens
        success = await self.repository.use_tokens(subscription.id, tokens_required)

        if not success:
            raise InsufficientTokensError("Failed to use tokens")

        logger.info(
            "tokens_used",
            user_id=user_id,
            subscription_id=subscription.id,
            amount=tokens_required,
            remaining=subscription.tokens_remaining - tokens_required
        )

        return subscription

    async def get_user_total_tokens(self, user_id: int) -> int:
        """Get total available tokens for user."""
        subscriptions = await self.repository.get_user_subscriptions(
            user_id,
            active_only=True
        )

        total = 0
        for sub in subscriptions:
            if not sub.is_expired:
                total += sub.tokens_remaining

        return total

    async def deactivate_expired_subscriptions(self) -> int:
        """Deactivate all expired subscriptions (background task)."""
        count = await self.repository.deactivate_expired_subscriptions()

        if count > 0:
            logger.info("expired_subscriptions_deactivated", count=count)

        return count

    async def add_eternal_tokens(
        self,
        user_id: int,
        tokens: int,
        subscription_type: str = "eternal_purchase"
    ) -> Subscription:
        """
        Add eternal tokens to user (tokens that never expire).

        Args:
            user_id: User ID
            tokens: Number of tokens to add
            subscription_type: Type of subscription (default: "eternal_purchase")

        Returns:
            Created Subscription object
        """
        from datetime import datetime, timezone
        from decimal import Decimal

        subscription = Subscription(
            user_id=user_id,
            subscription_type=subscription_type,
            tokens_amount=tokens,
            tokens_used=0,
            price=Decimal('0.00'),  # Price already paid
            is_active=True,
            started_at=datetime.now(timezone.utc),
            expires_at=None  # Eternal - never expires
        )

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)

        logger.info(
            "eternal_tokens_added",
            user_id=user_id,
            tokens=tokens,
            subscription_type=subscription_type
        )

        return subscription

    async def add_subscription_tokens(
        self,
        user_id: int,
        tokens: int,
        days: int = 30,
        subscription_type: str = "premium_subscription"
    ) -> Subscription:
        """
        Add time-limited subscription tokens to user.

        Args:
            user_id: User ID
            tokens: Number of tokens to add
            days: Number of days subscription is valid
            subscription_type: Type of subscription (default: "premium_subscription")

        Returns:
            Created Subscription object
        """
        from datetime import datetime, timezone, timedelta
        from decimal import Decimal

        subscription = Subscription(
            user_id=user_id,
            subscription_type=subscription_type,
            tokens_amount=tokens,
            tokens_used=0,
            price=Decimal('0.00'),  # Price already paid
            is_active=True,
            started_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=days)
        )

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)

        logger.info(
            "subscription_tokens_added",
            user_id=user_id,
            tokens=tokens,
            days=days,
            subscription_type=subscription_type
        )

        return subscription

