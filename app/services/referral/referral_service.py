"""
Referral service for managing referral program logic.
Handles referral rewards, statistics, and notifications.
"""
from typing import Optional, Tuple
from datetime import datetime, timezone
from decimal import Decimal

from asyncpg.exceptions import UndefinedTableError
from sqlalchemy import select, func
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.referral import Referral
from app.database.models.referral_balance import ReferralBalance
from app.database.models.user import User
from app.database.models.subscription import Subscription
from app.core.logger import get_logger

logger = get_logger(__name__)


class ReferralService:
    """Service for managing referral program operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_or_create_balance(self, user_id: int) -> ReferralBalance:
        result = await self.session.execute(
            select(ReferralBalance).where(ReferralBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()
        if balance:
            return balance
        balance = ReferralBalance(
            user_id=user_id,
            tokens_balance=0,
            money_balance=Decimal("0.00")
        )
        self.session.add(balance)
        await self.session.flush()
        return balance

    async def exchange_money_to_tokens(
        self,
        user_id: int,
        money_amount: Decimal,
        tokens_per_ruble: int
    ) -> Optional[int]:
        """Exchange referral money balance to tokens."""
        try:
            balance = await self._get_or_create_balance(user_id)
            if money_amount <= 0 or balance.money_balance < money_amount:
                return None

            tokens_to_add = int(money_amount * Decimal(tokens_per_ruble))
            if tokens_to_add <= 0:
                return None

            balance.money_balance -= money_amount
            balance.tokens_balance += tokens_to_add

            reward_subscription = Subscription(
                user_id=user_id,
                subscription_type="referral_money_exchange",
                tokens_amount=tokens_to_add,
                tokens_used=0,
                price=Decimal("0.00"),
                is_active=True,
                started_at=datetime.now(timezone.utc),
                expires_at=None
            )
            self.session.add(reward_subscription)
            await self.session.commit()

            return tokens_to_add
        except Exception as e:
            logger.error(
                "referral_exchange_failed",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            await self.session.rollback()
            return None

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

            # Award 10% money for any referral purchase
            money_awarded = money_paid * Decimal("0.1")
            referral.money_earned += money_awarded
            balance = await self._get_or_create_balance(referral.referrer_id)
            balance.money_balance += money_awarded

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

    async def give_signup_bonus(
        self,
        referrer_id: int,
        referred_id: int,
        bonus_tokens: int = 50
    ) -> bool:
        """
        Give signup bonus tokens to referrer and referred user (once).

        Args:
            referrer_id: ID of user who invited
            referred_id: ID of user who was invited
            bonus_tokens: Number of bonus tokens (default: 50)

        Returns:
            True if successful, False otherwise
        """
        try:
            referral_result = await self.session.execute(
                select(Referral).where(
                    Referral.referred_id == referred_id,
                    Referral.referrer_id == referrer_id,
                    Referral.is_active == True
                )
            )
            referral = referral_result.scalar_one_or_none()
            if not referral:
                return False

            if referral.tokens_earned >= bonus_tokens:
                return False

            # Create subscriptions with bonus tokens
            referred_subscription = Subscription(
                user_id=referred_id,
                subscription_type="referral_signup_bonus",
                tokens_amount=bonus_tokens,
                tokens_used=0,
                price=Decimal("0.00"),
                is_active=True,
                started_at=datetime.now(timezone.utc),
                expires_at=None  # Eternal tokens
            )
            referrer_subscription = Subscription(
                user_id=referrer_id,
                subscription_type="referral_signup_bonus_referrer",
                tokens_amount=bonus_tokens,
                tokens_used=0,
                price=Decimal("0.00"),
                is_active=True,
                started_at=datetime.now(timezone.utc),
                expires_at=None  # Eternal tokens
            )
            self.session.add(referred_subscription)
            self.session.add(referrer_subscription)

            referral.tokens_earned += bonus_tokens
            balance = await self._get_or_create_balance(referrer_id)
            balance.tokens_balance += bonus_tokens

            await self.session.commit()

            logger.info(
                "referral_signup_bonus_given",
                referrer_id=referrer_id,
                referred_id=referred_id,
                bonus_tokens=bonus_tokens
            )

            return True

        except Exception as e:
            logger.error(
                "referral_signup_bonus_failed",
                error=str(e),
                referrer_id=referrer_id,
                referred_id=referred_id,
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

            balance = None
            try:
                balance_result = await self.session.execute(
                    select(ReferralBalance).where(ReferralBalance.user_id == user_id)
                )
                balance = balance_result.scalar_one_or_none()
            except ProgrammingError as exc:
                if isinstance(getattr(exc, "orig", None), UndefinedTableError):
                    logger.warning(
                        "referral_balance_table_missing",
                        user_id=user_id
                    )
                else:
                    raise

            return {
                "referral_count": referral_count,
                "tokens_earned": tokens_earned,
                "money_earned": money_earned,
                "tokens_balance": int(balance.tokens_balance) if balance else 0,
                "money_balance": float(balance.money_balance) if balance else 0.0
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
                "money_earned": 0.0,
                "tokens_balance": 0,
                "money_balance": 0.0
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
