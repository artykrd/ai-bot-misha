"""
Admin bot entry point.
"""
import asyncio
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.database.database import init_db, close_db

logger = get_logger(__name__)


# Initialize admin bot
admin_bot = Bot(token=settings.telegram_admin_bot_token, parse_mode="Markdown")


# Router
admin_router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_user_ids


@admin_router.message(Command("start"))
async def admin_start(message: Message):
    """Admin start command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    text = """🔐 **Админ-панель**

Доступные команды:

📊 **Статистика:**
/stats - Общая статистика
/users - Список пользователей

👥 **Управление пользователями:**
/ban <user_id> <reason> - Заблокировать пользователя
/unban <user_id> - Разблокировать пользователя
/give_tokens <user_id> <amount> - Выдать токены

💰 **Платежи:**
/payments - Список платежей
/refund <payment_id> - Вернуть платеж

🎁 **Промокоды:**
/create_promo <code> <tokens> - Создать промокод
/promos - Список промокодов

⚙️ **Система:**
/logs - Показать последние логи
/broadcast <text> - Рассылка всем пользователям"""

    await message.answer(text)


@admin_router.message(Command("stats"))
async def show_stats(message: Message):
    """Show statistics."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models import User, Subscription, Payment
    from sqlalchemy import select, func

    async with async_session_maker() as session:
        # Get stats
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_subscriptions = await session.scalar(select(func.count()).select_from(Subscription))
        total_payments = await session.scalar(select(func.count()).select_from(Payment))

    text = f"""📊 **Статистика**

👥 **Пользователи:** {total_users}
📦 **Подписки:** {total_subscriptions}
💳 **Платежи:** {total_payments}

⚠️ Полная статистика в разработке"""

    await message.answer(text)


@admin_router.message(Command("users"))
async def list_users(message: Message):
    """List recent users."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).order_by(User.created_at.desc()).limit(10)
        )
        users = result.scalars().all()

    text = "👥 **Последние 10 пользователей:**\n\n"

    for user in users:
        text += f"ID: `{user.telegram_id}` | {user.full_name}\n"
        text += f"   Создан: {user.created_at.strftime('%d.%m.%Y')}\n\n"

    await message.answer(text)


async def main():
    """Main admin bot loop."""
    admin_dp = None
    try:
        logger.info("admin_bot_starting")

        # Initialize database
        await init_db()

        # Connect to Redis
        await redis_client.connect()

        # Create dispatcher with Redis storage
        storage = RedisStorage(redis=redis_client.fsm_client)
        admin_dp = Dispatcher(storage=storage)

        # Register router
        admin_dp.include_router(admin_router)

        logger.info("admin_bot_started")

        # Start polling
        await admin_dp.start_polling(
            admin_bot,
            allowed_updates=admin_dp.resolve_used_update_types()
        )

    except Exception as e:
        logger.error("admin_bot_error", error=str(e))
        raise
    finally:
        logger.info("admin_bot_shutting_down")

        # Close connections
        await redis_client.disconnect()
        await close_db()
        await admin_bot.session.close()

        # Close dispatcher storage
        if admin_dp:
            await admin_dp.storage.close()

        logger.info("admin_bot_shutdown_complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("admin_bot_stopped_by_user")
        sys.exit(0)
    except Exception as e:
        logger.critical("admin_bot_crashed", error=str(e))
        sys.exit(1)
