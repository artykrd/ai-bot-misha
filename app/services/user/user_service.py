"""
User service for business logic.
"""
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.repositories.user import UserRepository
from app.core.logger import get_logger
from app.core.exceptions import UserNotFoundError, UserBannedError

logger = get_logger(__name__)


class UserService:
    """Service for user-related business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = "ru"
    ) -> Tuple[User, bool]:
        """
        Get or create user from Telegram data.

        Returns:
            Tuple of (user, created)

        Raises:
            UserBannedError: If user is banned
        """
        user, created = await self.repository.get_or_create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code
        )

        if user.is_banned:
            logger.warning("banned_user_access_attempt", user_id=user.id)
            raise UserBannedError(
                f"User {user.telegram_id} is banned",
                {"reason": user.ban_reason}
            )

        if created:
            logger.info("user_created", user_id=user.id, telegram_id=telegram_id)

        return user, created

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """
        Get user by Telegram ID.

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = await self.repository.get_by_telegram_id(telegram_id)

        if not user:
            raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")

        return user

    async def update_activity(self, telegram_id: int) -> None:
        """Update user's last activity."""
        user = await self.get_user_by_telegram_id(telegram_id)
        await self.repository.update_last_activity(user.id)

    async def ban_user(
        self,
        telegram_id: int,
        reason: str,
        admin_id: Optional[int] = None
    ) -> User:
        """Ban a user."""
        user = await self.get_user_by_telegram_id(telegram_id)
        result = await self.repository.ban_user(user.id, reason)

        logger.warning(
            "user_banned",
            user_id=user.id,
            admin_id=admin_id,
            reason=reason
        )

        return result

    async def unban_user(
        self,
        telegram_id: int,
        admin_id: Optional[int] = None
    ) -> User:
        """Unban a user."""
        user = await self.get_user_by_telegram_id(telegram_id)
        result = await self.repository.unban_user(user.id)

        logger.info(
            "user_unbanned",
            user_id=user.id,
            admin_id=admin_id
        )

        return result

    async def get_user_stats(self, telegram_id: int) -> dict:
        """Get user statistics."""
        user = await self.get_user_by_telegram_id(telegram_id)
        from app.services.subscription.subscription_service import SubscriptionService

        sub_service = SubscriptionService(self.session)
        total_tokens = await sub_service.get_available_tokens(user.id)
        active_sub = user.get_active_subscription()

        return {
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "total_tokens": total_tokens,
            "has_active_subscription": active_sub is not None,
            "subscription_type": active_sub.subscription_type if active_sub else None,
            "subscription_expires_at": active_sub.expires_at if active_sub else None,
            "is_banned": user.is_banned,
            "created_at": user.created_at,
            "last_activity": user.last_activity
        }
