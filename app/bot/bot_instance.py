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
    from app.bot.middlewares.broadcast_tracking import BroadcastTrackingMiddleware

    # Register middlewares
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(BroadcastTrackingMiddleware())

    # Register handlers
    from app.bot.handlers import (
        start,
        navigation,
        media_handler,
        suno_handler,
        profile,
        text_ai,
        common,
        download_handler,
        async_kling_handler  # Async Kling handler for job queue
    )
    from app.bot.handlers import dialog_handler

    # Order matters! Commands should come before FSM handlers, dialog_handler should be last
    dp.include_router(start.router)
    dp.include_router(navigation.router)
    dp.include_router(common.router)  # Commands BEFORE FSM handlers
    dp.include_router(download_handler.router)  # Download handler
    dp.include_router(suno_handler.router)  # Suno handlers
    dp.include_router(async_kling_handler.router)  # Async Kling BEFORE media_handler
    dp.include_router(media_handler.router)  # FSM state handlers
    dp.include_router(profile.router)
    dp.include_router(text_ai.router)
    dp.include_router(dialog_handler.router)  # MUST be last

    # Setup bot commands menu
    from app.bot.commands import setup_bot_commands
    await setup_bot_commands(bot)

    from app.core.error_notifier import setup_error_notifications
    setup_error_notifications(bot)

    # Start video worker for async video generation
    from app.workers.video_worker import VideoWorker
    video_worker = VideoWorker(bot, poll_interval=30)
    video_worker.start()
    logger.info("video_worker_started")

    logger.info("bot_setup_completed")

    return dp


async def shutdown_bot(dp: Dispatcher) -> None:
    """Cleanup on bot shutdown."""
    await bot.session.close()
    await dp.storage.close()
    logger.info("bot_shutdown_completed")
