"""
Main bot instance initialization.
"""
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# Initialize bot instance
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)


async def setup_bot() -> Dispatcher:
    """Setup bot (middlewares, handlers, etc.)."""
    from app.core.redis_client import redis_client

    # Create dispatcher with Redis storage
    redis_storage = RedisStorage(redis=redis_client.fsm_client)
    dp = Dispatcher(storage=redis_storage)

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

    # Setup bot commands menu
    from app.bot.commands import setup_bot_commands
    await setup_bot_commands(bot)

    logger.info("bot_setup_completed")

    return dp


async def shutdown_bot(dp: Dispatcher) -> None:
    """Cleanup on bot shutdown."""
    await bot.session.close()
    await dp.storage.close()
    logger.info("bot_shutdown_completed")
