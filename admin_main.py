"""
Admin bot entry point.
"""
import asyncio
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.database.database import init_db, close_db

logger = get_logger(__name__)


# Initialize admin bot
admin_bot = Bot(
    token=settings.telegram_admin_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)


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

🔗 **Безлимитные ссылки:**
/create_unlimited <days> [max_uses] [description] - Создать безлимитную ссылку
/unlimited_links - Список безлимитных ссылок
/deactivate_unlimited <code> - Деактивировать ссылку

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


@admin_router.message(Command("create_unlimited"))
async def create_unlimited_link(message: Message):
    """Create unlimited invite link."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models.unlimited_invite import UnlimitedInviteLink

    # Parse command arguments
    parts = message.text.split(maxsplit=3)
    if len(parts) < 2:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Используйте: `/create_unlimited <days> [max_uses] [description]`\n"
            "Примеры:\n"
            "- `/create_unlimited 7` - 7 дней, без ограничений\n"
            "- `/create_unlimited 14 100` - 14 дней, макс. 100 использований\n"
            "- `/create_unlimited 7 50 Для партнеров` - с описанием"
        )
        return

    try:
        duration_days = int(parts[1])
        max_uses = None
        description = None

        if len(parts) >= 3:
            try:
                max_uses = int(parts[2])
            except ValueError:
                description = parts[2]

        if len(parts) >= 4:
            description = parts[3]

        if duration_days <= 0:
            await message.answer("❌ Количество дней должно быть больше 0")
            return

        if max_uses is not None and max_uses <= 0:
            await message.answer("❌ Количество использований должно быть больше 0")
            return

    except ValueError:
        await message.answer("❌ Неверный формат чисел")
        return

    try:
        async with async_session_maker() as session:
            # Create unlimited invite link
            invite_code = UnlimitedInviteLink.generate_code()

            invite_link = UnlimitedInviteLink(
                invite_code=invite_code,
                duration_days=duration_days,
                max_uses=max_uses,
                current_uses=0,
                is_active=True,
                description=description
            )

            session.add(invite_link)
            await session.commit()
            await session.refresh(invite_link)

            # Get bot username for link generation
            bot_info = await message.bot.get_me()
            bot_username = bot_info.username
            invite_url = f"https://t.me/{bot_username}?start={invite_code}"

            text = f"""✅ **Безлимитная ссылка создана!**

🔗 **Код:** `{invite_code}`
📅 **Длительность:** {duration_days} дней
👥 **Макс. использований:** {max_uses if max_uses else '∞'}
📝 **Описание:** {description if description else 'Нет'}

**Ссылка для приглашений:**
{invite_url}

Пользователи, перешедшие по этой ссылке, получат безлимитный доступ на {duration_days} дней!"""

            await message.answer(text)

            logger.info(
                "unlimited_invite_link_created",
                admin_id=message.from_user.id,
                invite_code=invite_code,
                duration_days=duration_days,
                max_uses=max_uses
            )

    except Exception as e:
        logger.error("create_unlimited_link_error", error=str(e))
        await message.answer(f"❌ Ошибка при создании ссылки: {str(e)}")


@admin_router.message(Command("unlimited_links"))
async def list_unlimited_links(message: Message):
    """List all unlimited invite links."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models.unlimited_invite import UnlimitedInviteLink
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(UnlimitedInviteLink).order_by(UnlimitedInviteLink.created_at.desc())
        )
        links = result.scalars().all()

    if not links:
        await message.answer("📋 Безлимитных ссылок пока нет.")
        return

    text = "🔗 **Безлимитные пригласительные ссылки:**\n\n"

    for link in links:
        status = "✅ Активна" if link.is_active else "❌ Неактивна"
        if link.is_active and not link.is_valid:
            status = "⚠️ Истекла"

        text += f"**Код:** `{link.invite_code}`\n"
        text += f"📅 Длительность: {link.duration_days} дней\n"
        text += f"👥 Использований: {link.current_uses}"
        if link.max_uses:
            text += f"/{link.max_uses}"
        text += f"\n📊 Статус: {status}\n"

        if link.description:
            text += f"📝 Описание: {link.description}\n"

        text += f"🕐 Создана: {link.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += "\n"

    await message.answer(text)


@admin_router.message(Command("deactivate_unlimited"))
async def deactivate_unlimited_link(message: Message):
    """Deactivate unlimited invite link."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models.unlimited_invite import UnlimitedInviteLink
    from sqlalchemy import select

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Используйте: `/deactivate_unlimited <invite_code>`"
        )
        return

    invite_code = parts[1].strip()

    async with async_session_maker() as session:
        result = await session.execute(
            select(UnlimitedInviteLink).where(UnlimitedInviteLink.invite_code == invite_code)
        )
        link = result.scalar_one_or_none()

        if not link:
            await message.answer(f"❌ Ссылка с кодом `{invite_code}` не найдена.")
            return

        link.is_active = False
        await session.commit()

        await message.answer(
            f"✅ Ссылка `{invite_code}` деактивирована.\n"
            f"Использовано раз: {link.current_uses}"
        )

        logger.info(
            "unlimited_invite_link_deactivated",
            admin_id=message.from_user.id,
            invite_code=invite_code
        )


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
