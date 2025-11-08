"""
Subscription repository for database operations.
"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.subscription import Subscription
from app.database.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for Subscription model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_user_subscriptions(
        self,
        user_id: int,
        active_only: bool = False
    ) -> List[Subscription]:
        """Get all subscriptions for a user."""
        query = select(Subscription).where(Subscription.user_id == user_id)

        if active_only:
            query = query.where(
                Subscription.is_active == True,
                (Subscription.expires_at.is_(None)) |
                (Subscription.expires_at > datetime.utcnow())
            )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_subscription(
        self,
        user_id: int
    ) -> Optional[Subscription]:
        """Get user's active subscription."""
        subscriptions = await self.get_user_subscriptions(user_id, active_only=True)

        # Return first active subscription
        return subscriptions[0] if subscriptions else None

    async def create_subscription(
        self,
        user_id: int,
        subscription_type: str,
        tokens_amount: int,
        price: float,
        duration_days: Optional[int] = None
    ) -> Subscription:
        """Create new subscription."""
        started_at = datetime.utcnow()
        expires_at = None

        if duration_days:
            from datetime import timedelta
            expires_at = started_at + timedelta(days=duration_days)

        subscription = Subscription(
            user_id=user_id,
            subscription_type=subscription_type,
            tokens_amount=tokens_amount,
            tokens_used=0,
            price=price,
            is_active=True,
            started_at=started_at,
            expires_at=expires_at
        )

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def use_tokens(
        self,
        subscription_id: int,
        amount: int
    ) -> bool:
        """
        Use tokens from subscription.

        Returns:
            True if tokens were used successfully
        """
        subscription = await self.get(subscription_id)

        if not subscription or not subscription.can_use_tokens(amount):
            return False

        subscription.use_tokens(amount)
        await self.session.commit()
        return True

    async def deactivate_expired_subscriptions(self) -> int:
        """Deactivate all expired subscriptions."""
        from sqlalchemy import update

        result = await self.session.execute(
            update(Subscription)
            .where(
                Subscription.is_active == True,
                Subscription.expires_at.isnot(None),
                Subscription.expires_at < datetime.utcnow()
            )
            .values(is_active=False)
        )

        await self.session.commit()
        return result.rowcount
