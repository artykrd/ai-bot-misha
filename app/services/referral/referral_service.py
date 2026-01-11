"""
Referral service for managing referral program logic.
Handles referral rewards, statistics, and notifications.
"""
from typing import Optional, Tuple
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.referral import Referral
from app.database.models.user import User
from app.database.models.subscription import Subscription
from app.core.logger import get_logger

logger = get_logger(__name__)


class ReferralService:
    """Service for managing referral program operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_referral(
        self,
        referrer_id: int,
        referred_id: int,
        referral_code: str,
        referral_type: str = "user"
    ) -> Optional[Referral]:
        """
        Create a new referral relationship.

        Args:
            referrer_id: ID of user who invited
            referred_id: ID of user who was invited
            referral_code: Referral code used
            referral_type: Type of referral ("user" or "partner")

        Returns:
            Created Referral object or None if failed
        """
        try:
            # Check if referral already exists
            existing = await self.session.execute(
                select(Referral).where(Referral.referred_id == referred_id)
            )
            if existing.scalar_one_or_none():
                logger.warning(
                    "referral_already_exists",
                    referred_id=referred_id,
                    referrer_id=referrer_id
                )
                return None

            # Create new referral
            referral = Referral(
                referrer_id=referrer_id,
                referred_id=referred_id,
                referral_code=referral_code,
                referral_type=referral_type,
                tokens_earned=0,
                money_earned=Decimal('0.00'),
                is_active=True
            )

            self.session.add(referral)
            await self.session.commit()
            await self.session.refresh(referral)

            logger.info(
                "referral_created",
                referrer_id=referrer_id,
                referred_id=referred_id,
                referral_type=referral_type
            )

            return referral

        except Exception as e:
            logger.error("referral_creation_failed", error=str(e), exc_info=True)
            await self.session.rollback()
            return None

    async def award_referrer_for_purchase(
        self,
        referred_user_id: int,
        tokens_purchased: int,
        money_paid: Decimal
    ) -> Tuple[Optional[int], Optional[Decimal]]:
        """
        Award referrer when referred user makes a purchase.

        Args:
            referred_user_id: ID of user who made purchase
            tokens_purchased: Number of tokens purchased
            money_paid: Amount paid in rubles

        Returns:
            Tuple of (tokens_awarded, money_awarded) or (None, None) if no referral
        """
        try:
            # Find referral
            result = await self.session.execute(
                select(Referral).where(
                    Referral.referred_id == referred_user_id,
                    Referral.is_active == True
                )
            )
            referral = result.scalar_one_or_none()

            if not referral:
                return None, None

            tokens_awarded = None
            money_awarded = None

            if referral.referral_type == "user":
                # Award 50% tokens for user referrals
                tokens_awarded = int(tokens_purchased * 0.5)

                # Create subscription for referrer with reward tokens
                reward_subscription = Subscription(
                    user_id=referral.referrer_id,
                    subscription_type="referral_reward",
                    tokens_amount=tokens_awarded,
                    tokens_used=0,
                    price=Decimal('0.00'),
                    is_active=True,
                    started_at=datetime.now(timezone.utc),
                    expires_at=None  # Eternal tokens
                )
                self.session.add(reward_subscription)

                # Update referral stats
                referral.tokens_earned += tokens_awarded

                logger.info(
                    "referral_tokens_awarded",
                    referrer_id=referral.referrer_id,
                    referred_id=referred_user_id,
                    tokens=tokens_awarded
                )

            elif referral.referral_type == "partner":
                # Award 10% money for partner referrals
                money_awarded = money_paid * Decimal('0.1')

                # Update referral stats
                referral.money_earned += money_awarded

                logger.info(
                    "referral_money_awarded",
                    referrer_id=referral.referrer_id,
                    referred_id=referred_user_id,
                    money=float(money_awarded)
                )

            await self.session.commit()

            return tokens_awarded, money_awarded

        except Exception as e:
            logger.error(
                "referral_award_failed",
                error=str(e),
                referred_user_id=referred_user_id,
                exc_info=True
            )
            await self.session.rollback()
            return None, None

    async def give_signup_bonus(self, user_id: int, bonus_tokens: int = 100) -> bool:
        """
        Give signup bonus tokens to new referred user.

        Args:
            user_id: ID of user to give bonus to
            bonus_tokens: Number of bonus tokens (default: 100)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create subscription with bonus tokens
            bonus_subscription = Subscription(
                user_id=user_id,
                subscription_type="referral_signup_bonus",
                tokens_amount=bonus_tokens,
                tokens_used=0,
                price=Decimal('0.00'),
                is_active=True,
                started_at=datetime.now(timezone.utc),
                expires_at=None  # Eternal tokens
            )
            self.session.add(bonus_subscription)
            await self.session.commit()

            logger.info(
                "referral_signup_bonus_given",
                user_id=user_id,
                bonus_tokens=bonus_tokens
            )

            return True

        except Exception as e:
            logger.error(
                "referral_signup_bonus_failed",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            await self.session.rollback()
            return False

    async def get_referral_stats(self, user_id: int) -> dict:
        """
        Get referral statistics for a user.

        Args:
            user_id: ID of user

        Returns:
            Dictionary with referral stats
        """
        try:
            # Count total referrals
            referral_count_result = await self.session.execute(
                select(func.count(Referral.id)).where(
                    Referral.referrer_id == user_id,
                    Referral.is_active == True
                )
            )
            referral_count = referral_count_result.scalar() or 0

            # Sum tokens earned
            tokens_earned_result = await self.session.execute(
                select(func.sum(Referral.tokens_earned)).where(
                    Referral.referrer_id == user_id,
                    Referral.is_active == True
                )
            )
            tokens_earned = int(tokens_earned_result.scalar() or 0)

            # Sum money earned
            money_earned_result = await self.session.execute(
                select(func.sum(Referral.money_earned)).where(
                    Referral.referrer_id == user_id,
                    Referral.is_active == True
                )
            )
            money_earned = float(money_earned_result.scalar() or 0)

            return {
                "referral_count": referral_count,
                "tokens_earned": tokens_earned,
                "money_earned": money_earned
            }

        except Exception as e:
            logger.error(
                "referral_stats_failed",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            return {
                "referral_count": 0,
                "tokens_earned": 0,
                "money_earned": 0.0
            }

    async def get_referrer(self, user_id: int) -> Optional[User]:
        """
        Get the referrer (who invited) for a user.

        Args:
            user_id: ID of referred user

        Returns:
            User object of referrer or None
        """
        try:
            result = await self.session.execute(
                select(Referral).where(
                    Referral.referred_id == user_id,
                    Referral.is_active == True
                )
            )
            referral = result.scalar_one_or_none()

            if not referral:
                return None

            # Get referrer user
            referrer_result = await self.session.execute(
                select(User).where(User.id == referral.referrer_id)
            )
            return referrer_result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                "get_referrer_failed",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            return None
