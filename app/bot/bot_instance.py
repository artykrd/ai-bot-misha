"""
Main bot instance initialization.
"""
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.logger import get_logger

logger = get_logger(__name__)


# Initialize bot instance
bot = Bot(token=settings.telegram_bot_token, parse_mode="Markdown")


# Initialize FSM storage with Redis
storage = RedisStorage(redis=redis_client.fsm_client)


# Initialize dispatcher
dp = Dispatcher(storage=storage)


async def setup_bot() -> None:
    """Setup bot (middlewares, handlers, etc.)."""
    from app.bot.middlewares.auth import AuthMiddleware
    from app.bot.middlewares.logging import LoggingMiddleware

    # Register middlewares
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Register handlers
    from app.bot.handlers import (
        start,
        profile,
        subscription,
        text_ai,
        common
    )

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(subscription.router)
    dp.include_router(text_ai.router)
    dp.include_router(common.router)

    logger.info("bot_setup_completed")


async def shutdown_bot() -> None:
    """Cleanup on bot shutdown."""
    await bot.session.close()
    await dp.storage.close()
    logger.info("bot_shutdown_completed")
