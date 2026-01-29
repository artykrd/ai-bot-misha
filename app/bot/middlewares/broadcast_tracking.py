"""
Broadcast click tracking middleware.
Tracks user clicks on broadcast message buttons.
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from app.core.logger import get_logger
from app.database.database import async_session_maker
from app.admin.services import get_broadcast_by_callback, record_broadcast_click

logger = get_logger(__name__)


class BroadcastTrackingMiddleware(BaseMiddleware):
    """
    Middleware to track clicks on broadcast buttons.

    This middleware is transparent - it doesn't interfere with normal
    callback handling, but logs clicks if the callback_data matches
    a broadcast button.
    """

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Process callback query and track if it's from broadcast."""

        # Get callback data
        callback_data = event.data

        # Try to find broadcast with this callback_data
        try:
            async with async_session_maker() as session:
                broadcast = await get_broadcast_by_callback(session, callback_data)

                if broadcast and broadcast.buttons:
                    # Find button index
                    button_index = -1
                    button_text = ""

                    for idx, button in enumerate(broadcast.buttons):
                        if button.get("callback_data") == callback_data:
                            button_index = idx
                            button_text = button.get("text", "")
                            break

                    if button_index >= 0:
                        # Get user from data (set by auth middleware)
                        user = data.get("user")

                        if user:
                            # Record click (async, don't wait)
                            try:
                                async with async_session_maker() as click_session:
                                    await record_broadcast_click(
                                        session=click_session,
                                        broadcast_id=broadcast.id,
                                        user_id=user.id,
                                        button_index=button_index,
                                        button_text=button_text,
                                        button_callback_data=callback_data
                                    )

                                logger.info(
                                    "broadcast_click_tracked",
                                    broadcast_id=broadcast.id,
                                    user_id=user.id,
                                    button_index=button_index,
                                    button_text=button_text
                                )
                            except Exception as e:
                                # Don't fail the request if tracking fails
                                logger.error(
                                    "broadcast_click_tracking_error",
                                    error=str(e),
                                    broadcast_id=broadcast.id,
                                    user_id=user.id
                                )

        except Exception as e:
            # Don't fail the request if tracking fails
            logger.error("broadcast_tracking_middleware_error", error=str(e))

        # Continue with normal processing
        return await handler(event, data)
