"""
Logging middleware for tracking user actions.
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user actions."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Log event and call handler."""

        if isinstance(event, Message):
            logger.info(
                "message_received",
                user_id=event.from_user.id if event.from_user else None,
                chat_id=event.chat.id,
                text=event.text[:100] if event.text else None,
                content_type=event.content_type
            )

        elif isinstance(event, CallbackQuery):
            logger.info(
                "callback_received",
                user_id=event.from_user.id if event.from_user else None,
                callback_data=event.data
            )

        # Call handler
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.error(
                "handler_error",
                error=str(e),
                event_type=type(event).__name__
            )
            raise
