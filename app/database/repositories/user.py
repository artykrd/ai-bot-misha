"""
User repository for database operations.
"""
from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_from_telegram(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = "ru"
    ) -> User:
        """Create user from Telegram data."""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            last_activity=datetime.utcnow()
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_last_activity(self, user_id: int) -> None:
        """Update user's last activity timestamp."""
        await self.update(user_id, last_activity=datetime.utcnow())

    async def ban_user(self, user_id: int, reason: str) -> Optional[User]:
        """Ban a user."""
        return await self.update(user_id, is_banned=True, ban_reason=reason)

    async def unban_user(self, user_id: int) -> Optional[User]:
        """Unban a user."""
        return await self.update(user_id, is_banned=False, ban_reason=None)

    async def get_or_create(
        self,
        telegram_id: int,
        **user_data
    ) -> tuple[User, bool]:
        """
        Get existing user or create new one.

        Returns:
            Tuple of (user, created) where created is True if user was created
        """
        user = await self.get_by_telegram_id(telegram_id)

        if user:
            # Update last activity
            await self.update_last_activity(user.id)
            return user, False

        # Create new user
        user = await self.create_from_telegram(telegram_id, **user_data)
        return user, True
