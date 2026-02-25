"""
Service for managing channel subscription bonuses.
Handles checking channel membership and awarding token bonuses.
"""
from typing import Optional

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.database.models.channel_bonus import ChannelSubscriptionBonus, ChannelBonusClaim
from app.services.subscription.subscription_service import SubscriptionService

logger = get_logger(__name__)


class ChannelBonusService:
    """Service for channel subscription bonus operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bonus(
        self,
        channel_id: int,
        bonus_tokens: int = 1000,
        channel_username: Optional[str] = None,
        channel_title: Optional[str] = None,
        welcome_message: Optional[str] = None,
    ) -> ChannelSubscriptionBonus:
        """
        Create a new channel subscription bonus configuration.

        Args:
            channel_id: Telegram numeric channel ID
            bonus_tokens: Tokens to award (default: 1000)
            channel_username: Channel @username for display
            channel_title: Channel display name
            welcome_message: Custom message to show when bonus is awarded

        Returns:
            Created ChannelSubscriptionBonus instance
        """
        bonus = ChannelSubscriptionBonus(
            channel_id=channel_id,
            channel_username=channel_username,
            channel_title=channel_title,
            bonus_tokens=bonus_tokens,
            welcome_message=welcome_message,
            is_active=True,
        )
        self.session.add(bonus)
        await self.session.commit()
        await self.session.refresh(bonus)

        logger.info(
            "channel_bonus_created",
            bonus_id=bonus.id,
            channel_id=channel_id,
            bonus_tokens=bonus_tokens,
        )
        return bonus

    async def get_active_bonuses(self) -> list[ChannelSubscriptionBonus]:
        """Get all active channel bonuses."""
        result = await self.session.execute(
            select(ChannelSubscriptionBonus).where(
                ChannelSubscriptionBonus.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_bonus_by_id(self, bonus_id: int) -> Optional[ChannelSubscriptionBonus]:
        """Get a specific bonus by ID."""
        result = await self.session.execute(
            select(ChannelSubscriptionBonus).where(
                ChannelSubscriptionBonus.id == bonus_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_bonuses(self) -> list[ChannelSubscriptionBonus]:
        """Get all channel bonuses (active and inactive)."""
        result = await self.session.execute(
            select(ChannelSubscriptionBonus).order_by(
                ChannelSubscriptionBonus.created_at.desc()
            )
        )
        return list(result.scalars().all())

    async def toggle_bonus(self, bonus_id: int) -> Optional[bool]:
        """
        Toggle bonus active/inactive status.

        Returns:
            New is_active state, or None if bonus not found
        """
        bonus = await self.get_bonus_by_id(bonus_id)
        if not bonus:
            return None

        bonus.is_active = not bonus.is_active
        await self.session.commit()

        logger.info(
            "channel_bonus_toggled",
            bonus_id=bonus_id,
            is_active=bonus.is_active,
        )
        return bonus.is_active

    async def update_bonus_tokens(self, bonus_id: int, new_tokens: int) -> Optional[ChannelSubscriptionBonus]:
        """Update bonus token amount."""
        bonus = await self.get_bonus_by_id(bonus_id)
        if not bonus:
            return None

        bonus.bonus_tokens = new_tokens
        await self.session.commit()
        return bonus

    async def has_claimed(self, user_id: int, bonus_id: int) -> bool:
        """Check if user already claimed this bonus."""
        result = await self.session.execute(
            select(ChannelBonusClaim).where(
                and_(
                    ChannelBonusClaim.user_id == user_id,
                    ChannelBonusClaim.bonus_id == bonus_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def check_channel_membership(
        bot: Bot,
        user_telegram_id: int,
        channel_id: int,
    ) -> bool:
        """
        Check if user is a member of the specified channel/group.

        Args:
            bot: Bot instance (must be admin of the channel)
            user_telegram_id: Telegram user ID to check
            channel_id: Telegram channel/group numeric ID

        Returns:
            True if user is a member (member, admin, or creator)
        """
        try:
            member = await bot.get_chat_member(
                chat_id=channel_id,
                user_id=user_telegram_id,
            )
            # User is subscribed if they are member, admin, or creator
            return member.status in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            )
        except Exception as e:
            logger.error(
                "channel_membership_check_error",
                user_id=user_telegram_id,
                channel_id=channel_id,
                error=str(e),
            )
            return False

    async def claim_bonus(
        self,
        user_id: int,
        bonus_id: int,
    ) -> Optional[int]:
        """
        Award channel subscription bonus tokens to user.

        Args:
            user_id: Internal user ID
            bonus_id: Bonus configuration ID

        Returns:
            Number of tokens awarded, or None if claim failed
        """
        bonus = await self.get_bonus_by_id(bonus_id)
        if not bonus or not bonus.is_active:
            return None

        # Check if already claimed
        if await self.has_claimed(user_id, bonus_id):
            return None

        # Award tokens
        sub_service = SubscriptionService(self.session)
        await sub_service.add_eternal_tokens(
            user_id=user_id,
            tokens=bonus.bonus_tokens,
            subscription_type=f"channel_bonus_{bonus_id}",
        )

        # Record the claim
        claim = ChannelBonusClaim(
            user_id=user_id,
            bonus_id=bonus_id,
            tokens_awarded=bonus.bonus_tokens,
        )
        self.session.add(claim)
        await self.session.commit()

        logger.info(
            "channel_bonus_claimed",
            user_id=user_id,
            bonus_id=bonus_id,
            tokens=bonus.bonus_tokens,
        )
        return bonus.bonus_tokens

    async def get_bonus_stats(self, bonus_id: int) -> dict:
        """Get statistics for a bonus (total claims, total tokens)."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(
                func.count(ChannelBonusClaim.id),
                func.coalesce(func.sum(ChannelBonusClaim.tokens_awarded), 0),
            ).where(ChannelBonusClaim.bonus_id == bonus_id)
        )
        row = result.one()
        return {
            "total_claims": row[0],
            "total_tokens_awarded": row[1],
        }

    async def delete_bonus(self, bonus_id: int) -> bool:
        """Delete a bonus configuration and all its claims."""
        bonus = await self.get_bonus_by_id(bonus_id)
        if not bonus:
            return False

        await self.session.delete(bonus)
        await self.session.commit()

        logger.info("channel_bonus_deleted", bonus_id=bonus_id)
        return True
