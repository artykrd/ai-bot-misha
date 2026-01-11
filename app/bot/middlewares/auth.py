"""
Authentication middleware for user registration and ban check.
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.database.database import async_session_maker
from app.services.user.user_service import UserService
from app.core.logger import get_logger
from app.core.exceptions import UserBannedError

logger = get_logger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication and registration."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process update and register/check user."""

        # Get user from event
        if isinstance(event, Message):
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery):
            telegram_user = event.from_user
        else:
            # Unknown event type, skip
            return await handler(event, data)

        if not telegram_user:
            return await handler(event, data)

        # Create database session
        async with async_session_maker() as session:
            user_service = UserService(session)

            try:
                # Get or create user
                user, created = await user_service.get_or_create_user(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    language_code=telegram_user.language_code
                )

                # Give new users a test request (small amount of tokens)
                if created:
                    from app.services.subscription.subscription_service import SubscriptionService

                    sub_service = SubscriptionService(session)
                    # Give 5000 tokens for 1 test request (eternal subscription)
                    # This is enough for one simple text request
                    await sub_service.add_eternal_tokens(
                        user_id=user.id,
                        tokens=5000,
                        subscription_type="welcome_bonus"
                    )
                    logger.info(
                        "new_user_welcome_bonus",
                        user_id=user.id,
                        telegram_id=telegram_user.id,
                        bonus_tokens=5000
                    )

                # Add user to handler data
                data["user"] = user
                data["user_service"] = user_service

            except UserBannedError as e:
                # User is banned
                logger.warning(
                    "banned_user_blocked",
                    telegram_id=telegram_user.id,
                    reason=e.details.get("reason")
                )

                # Send ban message
                if isinstance(event, Message):
                    await event.answer(
                        f"❌ Вы заблокированы.\n\nПричина: {e.details.get('reason', 'Не указана')}"
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"❌ Вы заблокированы: {e.details.get('reason', 'Не указана')}",
                        show_alert=True
                    )

                return  # Don't call handler

        # Call handler
        return await handler(event, data)
