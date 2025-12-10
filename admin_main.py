"""
Admin bot entry point.
"""
import asyncio
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.database.database import init_db, close_db
from app.admin.keyboards.inline import (
    main_admin_menu,
    unlimited_links_menu,
    promo_menu,
    ban_menu,
    cancel_keyboard,
    back_keyboard
)
from app.admin.states import (
    CreateUnlimitedLink,
    GiveTokens,
    BanUser,
    UnbanUser,
    CreatePromo,
    Broadcast
)

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


# ==================== START COMMAND ====================

@admin_router.message(Command("start"))
async def admin_start(message: Message):
    """Admin start command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    text = "🔐 **Админ-панель**\n\nВыберите действие из меню ниже:"
    await message.answer(text, reply_markup=main_admin_menu())


# ==================== CALLBACK HANDLERS ====================

@admin_router.callback_query(F.data == "admin:back")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Back to main menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.clear()
    text = "🔐 **Админ-панель**\n\nВыберите действие из меню ниже:"
    await callback.message.edit_text(text, reply_markup=main_admin_menu())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.clear()
    await callback.message.edit_text(
        "❌ Операция отменена.",
        reply_markup=back_keyboard()
    )
    await callback.answer()


# ==================== STATISTICS ====================

@admin_router.callback_query(F.data == "admin:stats")
async def show_stats_callback(callback: CallbackQuery):
    """Show statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models import User, Subscription, Payment
    from sqlalchemy import select, func

    async with async_session_maker() as session:
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_subscriptions = await session.scalar(select(func.count()).select_from(Subscription))
        total_payments = await session.scalar(select(func.count()).select_from(Payment))

    text = f"""📊 **Статистика**

👥 **Пользователи:** {total_users}
📦 **Подписки:** {total_subscriptions}
💳 **Платежи:** {total_payments}"""

    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:users")
async def list_users_callback(callback: CallbackQuery):
    """List recent users."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
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

    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


# ==================== UNLIMITED LINKS ====================

@admin_router.callback_query(F.data == "admin:unlimited_menu")
async def unlimited_menu_callback(callback: CallbackQuery):
    """Show unlimited links menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    text = "🔗 **Безлимитные пригласительные ссылки**\n\nВыберите действие:"
    await callback.message.edit_text(text, reply_markup=unlimited_links_menu())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:create_unlimited")
async def start_create_unlimited(callback: CallbackQuery, state: FSMContext):
    """Start creating unlimited link."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(CreateUnlimitedLink.waiting_for_days)
    await callback.message.edit_text(
        "➕ **Создание безлимитной ссылки**\n\n"
        "Введите количество дней (например: 7, 14, 30):",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(CreateUnlimitedLink.waiting_for_days))
async def process_unlimited_days(message: Message, state: FSMContext):
    """Process duration days input."""
    if not is_admin(message.from_user.id):
        return

    try:
        days = int(message.text.strip())
        if days <= 0:
            await message.answer("❌ Количество дней должно быть больше 0")
            return

        await state.update_data(duration_days=days)
        await state.set_state(CreateUnlimitedLink.waiting_for_max_uses)

        await message.answer(
            f"✅ Длительность: {days} дней\n\n"
            "Введите максимальное количество использований\n"
            "(или отправьте 0 для неограниченного количества):",
            reply_markup=cancel_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")


@admin_router.message(StateFilter(CreateUnlimitedLink.waiting_for_max_uses))
async def process_unlimited_max_uses(message: Message, state: FSMContext):
    """Process max uses input."""
    if not is_admin(message.from_user.id):
        return

    try:
        max_uses = int(message.text.strip())
        if max_uses < 0:
            await message.answer("❌ Количество должно быть 0 или больше")
            return

        max_uses = None if max_uses == 0 else max_uses
        await state.update_data(max_uses=max_uses)
        await state.set_state(CreateUnlimitedLink.waiting_for_description)

        await message.answer(
            f"✅ Макс. использований: {max_uses if max_uses else '∞'}\n\n"
            "Введите описание ссылки (или отправьте '-' чтобы пропустить):",
            reply_markup=cancel_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")


@admin_router.message(StateFilter(CreateUnlimitedLink.waiting_for_description))
async def process_unlimited_description(message: Message, state: FSMContext):
    """Process description and create link."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models.unlimited_invite import UnlimitedInviteLink

    description = message.text.strip()
    if description == "-":
        description = None

    data = await state.get_data()
    duration_days = data['duration_days']
    max_uses = data['max_uses']

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

            # Get bot username - need to get the main bot username, not admin bot
            from app.core.config import settings
            from aiogram import Bot

            main_bot = Bot(token=settings.telegram_bot_token)
            bot_info = await main_bot.get_me()
            bot_username = bot_info.username
            await main_bot.session.close()

            invite_url = f"https://t.me/{bot_username}?start={invite_code}"

            text = f"""✅ **Безлимитная ссылка создана!**

🔗 **Код:** `{invite_code}`
📅 **Длительность:** {duration_days} дней
👥 **Макс. использований:** {max_uses if max_uses else '∞'}
📝 **Описание:** {description if description else 'Нет'}

Ссылка для приглашений:
`{invite_url}`

Пользователи, перешедшие по этой ссылке, получат безлимитный доступ на {duration_days} дней!"""

            await message.answer(text, reply_markup=back_keyboard())

            logger.info(
                "unlimited_invite_link_created",
                admin_id=message.from_user.id,
                invite_code=invite_code,
                duration_days=duration_days,
                max_uses=max_uses
            )

    except Exception as e:
        logger.error("create_unlimited_link_error", error=str(e))
        await message.answer(f"❌ Ошибка при создании ссылки: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


@admin_router.callback_query(F.data == "admin:list_unlimited")
async def list_unlimited_links_callback(callback: CallbackQuery):
    """List all unlimited invite links."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
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
        await callback.message.edit_text("📋 Безлимитных ссылок пока нет.", reply_markup=back_keyboard())
        await callback.answer()
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

    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


# ==================== LEGACY COMMAND HANDLERS ====================
# Keep these for backwards compatibility

@admin_router.message(Command("stats"))
async def show_stats(message: Message):
    """Show statistics (legacy command)."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models import User, Subscription, Payment
    from sqlalchemy import select, func

    async with async_session_maker() as session:
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_subscriptions = await session.scalar(select(func.count()).select_from(Subscription))
        total_payments = await session.scalar(select(func.count()).select_from(Payment))

    text = f"""📊 **Статистика**

👥 **Пользователи:** {total_users}
📦 **Подписки:** {total_subscriptions}
💳 **Платежи:** {total_payments}"""

    await message.answer(text, reply_markup=back_keyboard())


@admin_router.message(Command("users"))
async def list_users(message: Message):
    """List recent users (legacy command)."""
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

    await message.answer(text, reply_markup=back_keyboard())


@admin_router.message(Command("unlimited_links"))
async def list_unlimited_links_command(message: Message):
    """List unlimited links (legacy command)."""
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
        await message.answer("📋 Безлимитных ссылок пока нет.", reply_markup=back_keyboard())
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

    await message.answer(text, reply_markup=back_keyboard())


@admin_router.message(Command("deactivate_unlimited"))
async def deactivate_unlimited_link(message: Message):
    """Deactivate unlimited invite link (legacy command)."""
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
            f"Использовано раз: {link.current_uses}",
            reply_markup=back_keyboard()
        )

        logger.info(
            "unlimited_invite_link_deactivated",
            admin_id=message.from_user.id,
            invite_code=invite_code
        )


# ==================== MAIN LOOP ====================

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
