"""
Main entry point for the Telegram bot.
"""
import asyncio
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.core.scheduler import scheduler
from app.database.database import init_db, close_db
from app.bot.bot_instance import bot, setup_bot, shutdown_bot

logger = get_logger(__name__)


async def main() -> None:
    """Main bot loop."""
    dp = None
    try:
        logger.info("bot_starting", environment=settings.environment)

        # Initialize database
        await init_db()

        # Connect to Redis
        await redis_client.connect()

        # Setup bot (middlewares, handlers) and get dispatcher
        dp = await setup_bot()

        # Setup error notifications to admin bot
        from app.core.error_notifier import setup_error_notifications
        setup_error_notifications(bot)
        logger.info("error_notifications_enabled", admin_count=len(settings.admin_user_ids))

        # Start background scheduler
        scheduler.start()

        # Register background tasks
        from app.services.subscription.subscription_service import SubscriptionService
        from app.database.database import async_session_maker

        async def cleanup_expired_subscriptions():
            """Background task to deactivate expired subscriptions."""
            async with async_session_maker() as session:
                service = SubscriptionService(session)
                await service.deactivate_expired_subscriptions()

        # Run every hour
        scheduler.add_interval_job(cleanup_expired_subscriptions, hours=1)

        logger.info("bot_started_successfully")

        # Start polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )

    except Exception as e:
        logger.error("bot_fatal_error", error=str(e))
        raise
    finally:
        logger.info("bot_shutting_down")

        # Shutdown scheduler
        scheduler.shutdown()

        # Close Redis
        await redis_client.disconnect()

        # Close database
        await close_db()

        # Shutdown bot
        if dp:
            await shutdown_bot(dp)

        logger.info("bot_shutdown_complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("bot_stopped_by_user")
        sys.exit(0)
    except Exception as e:
        logger.critical("bot_crashed", error=str(e))
        sys.exit(1)
