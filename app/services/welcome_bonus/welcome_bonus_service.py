"""
Service for managing welcome bonus links for advertising campaigns.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.database.models.welcome_bonus import WelcomeBonus, WelcomeBonusUse
from app.database.models.subscription import Subscription
from app.database.models.payment import Payment
from app.services.subscription.subscription_service import SubscriptionService

logger = get_logger(__name__)


class WelcomeBonusService:
    """Service for welcome bonus operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bonus(
        self,
        bonus_tokens: int,
        name: Optional[str] = None,
        max_uses: Optional[int] = None,
        expires_at: Optional[datetime] = None,
    ) -> WelcomeBonus:
        """Create a new welcome bonus link."""
        invite_code = WelcomeBonus.generate_code()

        bonus = WelcomeBonus(
            invite_code=invite_code,
            bonus_tokens=bonus_tokens,
            name=name,
            max_uses=max_uses,
            current_uses=0,
            is_active=True,
            expires_at=expires_at,
        )
        self.session.add(bonus)
        await self.session.commit()
        await self.session.refresh(bonus)

        logger.info(
            "welcome_bonus_created",
            bonus_id=bonus.id,
            invite_code=invite_code,
            bonus_tokens=bonus_tokens,
            max_uses=max_uses,
        )
        return bonus

    async def get_bonus_by_code(self, invite_code: str) -> Optional[WelcomeBonus]:
        """Get welcome bonus by invite code."""
        result = await self.session.execute(
            select(WelcomeBonus).where(WelcomeBonus.invite_code == invite_code)
        )
        return result.scalar_one_or_none()

    async def get_bonus_by_id(self, bonus_id: int) -> Optional[WelcomeBonus]:
        """Get welcome bonus by ID."""
        result = await self.session.execute(
            select(WelcomeBonus).where(WelcomeBonus.id == bonus_id)
        )
        return result.scalar_one_or_none()

    async def get_all_bonuses(self) -> list[WelcomeBonus]:
        """Get all welcome bonuses ordered by creation date."""
        result = await self.session.execute(
            select(WelcomeBonus).order_by(WelcomeBonus.created_at.desc())
        )
        return list(result.scalars().all())

    async def has_used_bonus(self, user_id: int, bonus_id: int) -> bool:
        """Check if user already used this bonus link."""
        result = await self.session.execute(
            select(WelcomeBonusUse).where(
                and_(
                    WelcomeBonusUse.user_id == user_id,
                    WelcomeBonusUse.welcome_bonus_id == bonus_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def activate_bonus(
        self,
        user_id: int,
        bonus: WelcomeBonus,
    ) -> Optional[WelcomeBonusUse]:
        """
        Activate welcome bonus for a user - award tokens and track usage.

        Returns:
            WelcomeBonusUse record, or None if activation failed
        """
        if not bonus.is_valid:
            return None

        if await self.has_used_bonus(user_id, bonus.id):
            return None

        # Award tokens
        sub_service = SubscriptionService(self.session)
        subscription = await sub_service.add_eternal_tokens(
            user_id=user_id,
            tokens=bonus.bonus_tokens,
            subscription_type="welcome_bonus",
        )

        # Track usage
        use = WelcomeBonusUse(
            welcome_bonus_id=bonus.id,
            user_id=user_id,
            tokens_awarded=bonus.bonus_tokens,
            subscription_id=subscription.id,
            has_purchased=False,
        )
        self.session.add(use)

        # Increment counter
        bonus.current_uses += 1

        await self.session.commit()

        logger.info(
            "welcome_bonus_activated",
            user_id=user_id,
            bonus_id=bonus.id,
            tokens_awarded=bonus.bonus_tokens,
        )
        return use

    async def mark_purchase(
        self,
        user_id: int,
        purchase_amount: float,
    ) -> bool:
        """
        Mark that a user who received a welcome bonus made a paid purchase.
        Called from payment webhook.

        Returns:
            True if a welcome bonus use was found and updated
        """
        result = await self.session.execute(
            select(WelcomeBonusUse).where(
                and_(
                    WelcomeBonusUse.user_id == user_id,
                    WelcomeBonusUse.has_purchased == False,
                )
            )
        )
        use = result.scalar_one_or_none()

        if not use:
            return False

        use.has_purchased = True
        use.first_purchase_at = datetime.now(timezone.utc)
        use.first_purchase_amount = purchase_amount
        await self.session.commit()

        logger.info(
            "welcome_bonus_purchase_tracked",
            user_id=user_id,
            bonus_id=use.welcome_bonus_id,
            purchase_amount=purchase_amount,
        )
        return True

    async def toggle_bonus(self, bonus_id: int) -> Optional[bool]:
        """Toggle bonus active/inactive. Returns new state."""
        bonus = await self.get_bonus_by_id(bonus_id)
        if not bonus:
            return None

        bonus.is_active = not bonus.is_active
        await self.session.commit()
        return bonus.is_active

    async def get_bonus_stats(self, bonus_id: int) -> dict:
        """Get detailed statistics for a welcome bonus campaign."""
        bonus = await self.get_bonus_by_id(bonus_id)
        if not bonus:
            return {}

        # Total uses
        total_uses = bonus.current_uses

        # Conversion stats
        result = await self.session.execute(
            select(
                func.count(WelcomeBonusUse.id),
                func.count(WelcomeBonusUse.id).filter(WelcomeBonusUse.has_purchased == True),
                func.coalesce(func.sum(WelcomeBonusUse.tokens_awarded), 0),
                func.coalesce(
                    func.sum(WelcomeBonusUse.first_purchase_amount).filter(
                        WelcomeBonusUse.has_purchased == True
                    ),
                    0,
                ),
            ).where(WelcomeBonusUse.welcome_bonus_id == bonus_id)
        )
        row = result.one()

        total_activated = row[0]
        total_purchased = row[1]
        total_tokens_given = row[2]
        total_revenue = row[3]

        conversion_rate = (total_purchased / total_activated * 100) if total_activated > 0 else 0

        return {
            "bonus": bonus,
            "total_uses": total_uses,
            "total_activated": total_activated,
            "total_purchased": total_purchased,
            "conversion_rate": round(conversion_rate, 1),
            "total_tokens_given": total_tokens_given,
            "total_revenue": round(float(total_revenue), 2),
        }

    async def get_overall_stats(self) -> dict:
        """Get aggregated statistics across all welcome bonus campaigns."""
        # Total campaigns
        total_campaigns = await self.session.scalar(
            select(func.count(WelcomeBonus.id))
        )

        active_campaigns = await self.session.scalar(
            select(func.count(WelcomeBonus.id)).where(WelcomeBonus.is_active == True)
        )

        # Overall usage stats
        result = await self.session.execute(
            select(
                func.count(WelcomeBonusUse.id),
                func.count(WelcomeBonusUse.id).filter(WelcomeBonusUse.has_purchased == True),
                func.coalesce(func.sum(WelcomeBonusUse.tokens_awarded), 0),
                func.coalesce(
                    func.sum(WelcomeBonusUse.first_purchase_amount).filter(
                        WelcomeBonusUse.has_purchased == True
                    ),
                    0,
                ),
            )
        )
        row = result.one()

        total_activated = row[0]
        total_purchased = row[1]
        total_tokens_given = row[2]
        total_revenue = row[3]

        conversion_rate = (total_purchased / total_activated * 100) if total_activated > 0 else 0

        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_activated": total_activated,
            "total_purchased": total_purchased,
            "conversion_rate": round(conversion_rate, 1),
            "total_tokens_given": total_tokens_given,
            "total_revenue": round(float(total_revenue), 2),
        }
