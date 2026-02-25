"""
Admin bot entry point.
"""
import asyncio
import sys
import html as html_module

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.database.database import init_db, close_db
from app.admin.keyboards.inline import (
    unlimited_links_menu,
    promo_menu,
    ban_menu,
    cancel_keyboard,
    back_keyboard,
    user_management_keyboard,
    users_list_keyboard,
    tariff_selection_keyboard
)
from app.admin.states import (
    CreateUnlimitedLink,
    GiveTokens,
    BanUser,
    UnbanUser,
    CreatePromo,
    Broadcast,
    BroadcastWithButtons,
    SearchUser,
    ManageUserTariff,
    SendUserMessage,
    ExpiryNotification,
    ChannelBonusSetup,
    BroadcastWithChannelBonus,
    BroadcastTargeted,
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


def safe_text(text: str) -> str:
    """Remove emoji and special characters that could cause Telegram parse errors."""
    if not text:
        return ""

    import re

    # Remove all emoji (Unicode ranges)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002700-\U000027BF"  # dingbats
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U00002600-\U000026FF"  # misc symbols
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)

    # Replace problematic characters for Markdown
    replacements = {
        '<': '',
        '>': '',
        '&': 'and',
        '_': ' ',
        '*': '',
        '[': '(',
        ']': ')',
        '`': "'",
        '~': '-',
        '#': 'No.',
        '{': '(',
        '}': ')',
        '|': '-',
        '\\': '',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def admin_reply_keyboard() -> ReplyKeyboardMarkup:
    """Persistent reply keyboard for admin bot."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👥 Пользователи")],
            [KeyboardButton(text="📢 Рассылка"), KeyboardButton(text="💰 Выдать токены")],
            [KeyboardButton(text="🔨 Бан/Разбан"), KeyboardButton(text="💵 Финансы")],
            [KeyboardButton(text="🎁 Промокоды"), KeyboardButton(text="🔗 Безлимит ссылки")],
            [KeyboardButton(text="📢 Бонус за подписку")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def escape_markdown(text: str) -> str:
    """Escape special Markdown characters for safe display."""
    if not text:
        return ""

    # Characters that need escaping in MarkdownV2 and Markdown
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!', '\\']

    result = str(text)
    for char in escape_chars:
        result = result.replace(char, '\\' + char)

    return result


# ==================== START COMMAND ====================

@admin_router.message(Command("start"))
async def admin_start(message: Message):
    """Admin start command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    # Send persistent reply keyboard only
    await message.answer(
        "🔐 Админ-панель\n\nИспользуйте кнопки меню внизу.",
        reply_markup=admin_reply_keyboard()
    )


# ==================== REPLY KEYBOARD HANDLERS ====================

REPLY_KEYBOARD_MAP = {
    "📊 Статистика": "admin:stats",
    "👥 Пользователи": "admin:users",
    "📢 Рассылка": "admin:broadcast",
    "🔨 Бан/Разбан": "admin:ban_menu",
    "💰 Выдать токены": "admin:give_tokens",
    "🎁 Промокоды": "admin:promo_menu",
    "🔗 Безлимит ссылки": "admin:unlimited_menu",
    "💵 Финансы": "admin:finance",
    "📢 Бонус за подписку": "admin:channel_bonus_menu",
}


@admin_router.message(F.text.in_(REPLY_KEYBOARD_MAP.keys()))
async def handle_reply_keyboard(message: Message, state: FSMContext):
    """Route reply keyboard button presses to corresponding inline callback handlers."""
    if not is_admin(message.from_user.id):
        return

    await state.clear()
    callback_data = REPLY_KEYBOARD_MAP[message.text]

    if callback_data == "admin:stats":
        text = await _build_stats_text()
        await message.answer(text, reply_markup=back_keyboard())
    elif callback_data == "admin:users":
        await _show_users_page_message(message, page=0)
    elif callback_data == "admin:broadcast":
        from app.admin.keyboards.inline import broadcast_type_menu
        await message.answer(
            "📢 Рассылка\n\nВыберите тип рассылки:",
            reply_markup=broadcast_type_menu()
        )
    elif callback_data == "admin:ban_menu":
        from app.admin.keyboards.inline import ban_menu
        await message.answer(
            "🔨 Управление банами\n\nВыберите действие:",
            reply_markup=ban_menu()
        )
    elif callback_data == "admin:give_tokens":
        await _show_give_tokens_message(message)
    elif callback_data == "admin:promo_menu":
        from app.admin.keyboards.inline import promo_menu
        await message.answer(
            "🎁 Промокоды\n\nВыберите действие:",
            reply_markup=promo_menu()
        )
    elif callback_data == "admin:unlimited_menu":
        from app.admin.keyboards.inline import unlimited_links_menu
        await message.answer(
            "🔗 Безлимитные ссылки\n\nВыберите действие:",
            reply_markup=unlimited_links_menu()
        )
    elif callback_data == "admin:finance":
        text = await _build_finance_text("all")
        keyboard = _finance_period_keyboard()
        await message.answer(text, reply_markup=keyboard)
    elif callback_data == "admin:channel_bonus_menu":
        from app.admin.keyboards.inline import channel_bonus_menu
        await message.answer(
            "📢 Бонус за подписку на канал/группу\n\n"
            "Создайте бонус за подписку или управляйте существующими.\n"
            "При рассылке пользователи получат кнопку для проверки подписки\n"
            "и начисления бонусных токенов.",
            reply_markup=channel_bonus_menu()
        )


# ==================== REPLY KEYBOARD HELPER FUNCTIONS ====================


async def _show_users_page_message(message: Message, page: int = 0):
    """Show users page as a new message (for reply keyboard handler)."""
    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select, func
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    users_per_page = 10
    offset = page * users_per_page

    async with async_session_maker() as session:
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_pages = (total_users + users_per_page - 1) // users_per_page

        result = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(users_per_page)
            .offset(offset)
        )
        users = result.scalars().all()

    text = f"👥 Пользователи (стр. {page + 1}/{total_pages})\n"
    text += f"Всего: {total_users}\n\n"

    builder = InlineKeyboardBuilder()

    for user in users:
        ban_status = "🚫" if user.is_banned else ""
        active_sub = user.get_active_subscription()
        sub_emoji = "💎" if active_sub else ""

        button_text = f"{ban_status}{sub_emoji} {safe_text(user.full_name)} (ID: {user.telegram_id})"
        builder.button(
            text=button_text[:64],
            callback_data=f"admin:user_view:{user.telegram_id}"
        )

    if page > 0:
        builder.button(text="◀️ Назад", callback_data=f"admin:users_page:{page - 1}")
    if page < total_pages - 1:
        builder.button(text="Вперед ▶️", callback_data=f"admin:users_page:{page + 1}")

    builder.button(text="🔍 Поиск пользователя", callback_data="admin:search_user")
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup())


async def _show_give_tokens_message(message: Message):
    """Show give tokens panel as a new message (for reply keyboard handler)."""
    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).order_by(User.last_activity.desc().nullslast()).limit(10)
        )
        recent_users = result.scalars().all()

    text = f"💰 Выдача токенов\n\n"
    text += f"Последние активные пользователи:\n"

    builder = InlineKeyboardBuilder()

    for user in recent_users:
        active_sub = user.get_active_subscription()
        sub_emoji = "💎" if active_sub else ""
        button_text = f"{sub_emoji} {safe_text(user.full_name)} (ID: {user.telegram_id})"
        builder.button(
            text=button_text[:64],
            callback_data=f"admin:give_tokens_to:{user.telegram_id}"
        )

    builder.button(text="🔍 Поиск пользователя", callback_data="admin:give_tokens_search")
    builder.button(text="✏️ Ввести ID вручную", callback_data="admin:give_tokens_manual")
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup())


# ==================== CALLBACK HANDLERS ====================

@admin_router.callback_query(F.data == "admin:back")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Back to main menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.clear()
    try:
        await callback.message.edit_text(
            "🔐 Используйте кнопки меню внизу."
        )
    except Exception:
        pass
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

    text = await _build_stats_text()
    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


async def _build_stats_text() -> str:
    """Build statistics text with accurate data."""
    from app.database.database import async_session_maker
    from app.database.models import User, Subscription, Payment
    from sqlalchemy import select, func, and_
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    async with async_session_maker() as session:
        # Total users
        total_users = await session.scalar(select(func.count()).select_from(User))

        # New users today
        new_today = await session.scalar(
            select(func.count()).select_from(User).where(User.created_at >= today_start)
        )

        # Active paid subscriptions (distinct users with usable tokens)
        from app.core.subscription_plans import PAID_SUBSCRIPTION_TYPES
        active_subs = await session.scalar(
            select(func.count(func.distinct(Subscription.user_id)))
            .select_from(Subscription).where(
                and_(
                    Subscription.is_active == True,
                    Subscription.tokens_amount > Subscription.tokens_used,
                    Subscription.subscription_type.in_(PAID_SUBSCRIPTION_TYPES)
                )
            )
        )

        # Paid subscriptions (with associated successful payment)
        paid_subs = await session.scalar(
            select(func.count(func.distinct(Subscription.id)))
            .select_from(Subscription)
            .join(Payment, Payment.subscription_id == Subscription.id)
            .where(Payment.status == "success")
        )

        # Successful payments count and total revenue
        successful_payments = await session.scalar(
            select(func.count()).select_from(Payment).where(Payment.status == "success")
        )
        total_revenue = await session.scalar(
            select(func.sum(Payment.amount)).where(Payment.status == "success")
        ) or 0

        # Revenue this month
        month_revenue = await session.scalar(
            select(func.sum(Payment.amount)).where(
                and_(Payment.status == "success", Payment.created_at >= month_ago)
            )
        ) or 0

        # Revenue today
        today_revenue = await session.scalar(
            select(func.sum(Payment.amount)).where(
                and_(Payment.status == "success", Payment.created_at >= today_start)
            )
        ) or 0

        # Blocked users (who blocked the bot)
        blocked_users = await session.scalar(
            select(func.count()).select_from(User).where(User.is_bot_blocked == True)
        )

    active_users = total_users - blocked_users
    text = (
        f"📊 Статистика\n\n"
        f"👥 Пользователи: {total_users}\n"
        f"✅ Активных: {active_users}\n"
        f"🚫 Заблокировали бота: {blocked_users}\n"
        f"🆕 Новых сегодня: {new_today}\n\n"
        f"📦 Активные подписки: {active_subs}\n"
        f"💳 Оплаченных подписок: {paid_subs}\n\n"
        f"💰 Платежи (успешные): {successful_payments}\n"
        f"💵 Выручка всего: {total_revenue:,.0f} RUB\n"
        f"📅 За месяц: {month_revenue:,.0f} RUB\n"
        f"📆 Сегодня: {today_revenue:,.0f} RUB"
    )
    return text


@admin_router.callback_query(F.data == "admin:users")
async def list_users_callback(callback: CallbackQuery):
    """List users with pagination and management."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await show_users_page(callback, page=0)


async def show_users_page(callback: CallbackQuery, page: int = 0):
    """Show users page with pagination."""
    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select, func
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    users_per_page = 10
    offset = page * users_per_page

    async with async_session_maker() as session:
        # Get total count
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_pages = (total_users + users_per_page - 1) // users_per_page

        # Get users for this page
        result = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(users_per_page)
            .offset(offset)
        )
        users = result.scalars().all()

    text = f"👥 Пользователи (стр. {page + 1}/{total_pages})\n"
    text += f"Всего: {total_users}\n\n"

    # Create inline keyboard with user buttons
    builder = InlineKeyboardBuilder()

    for user in users:
        ban_status = "🚫" if user.is_banned else ""
        active_sub = user.get_active_subscription()
        sub_emoji = "💎" if active_sub else ""

        button_text = f"{ban_status}{sub_emoji} {safe_text(user.full_name)} (ID: {user.telegram_id})"
        builder.button(
            text=button_text[:64],  # Telegram limit
            callback_data=f"admin:user_view:{user.telegram_id}"
        )

    # Add pagination buttons
    if page > 0:
        builder.button(text="◀️ Назад", callback_data=f"admin:users_page:{page-1}")
    if page < total_pages - 1:
        builder.button(text="Вперед ▶️", callback_data=f"admin:users_page:{page+1}")

    # Add search and back buttons
    builder.button(text="🔍 Поиск", callback_data="admin:search_user")
    builder.button(text="🔙 Назад в меню", callback_data="admin:back")

    # Adjust layout: users in column, navigation in row, search and back in row
    buttons_count = len(users)
    adjust_pattern = [1] * buttons_count + [2, 2]
    builder.adjust(*adjust_pattern)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:users_page:"))
async def users_page_callback(callback: CallbackQuery):
    """Handle pagination for users list."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    page = int(callback.data.split(":")[-1])
    await show_users_page(callback, page=page)


@admin_router.callback_query(F.data.startswith("admin:user_view:"))
async def user_view_callback(callback: CallbackQuery):
    """View user details and management options."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.services.user.user_service import UserService

    try:
        async with async_session_maker() as session:
            user_service = UserService(session)
            stats = await user_service.get_user_stats(telegram_id)

        user = stats
        text = f"👤 Информация о пользователе\n\n"
        text += f"ID: {user['telegram_id']}\n"
        text += f"Имя: {safe_text(user['full_name'])}\n"
        if user['username']:
            text += f"Username: @{safe_text(user['username'])}\n"
        text += f"Статус: {'🚫 Забанен' if user['is_banned'] else '✅ Активен'}\n"
        text += f"Токенов: {user['total_tokens']:,}\n"

        if user['has_active_subscription']:
            text += f"\n📦 Подписка: {safe_text(str(user['subscription_type']))}\n"
            if user['subscription_expires_at']:
                text += f"Истекает: {user['subscription_expires_at'].strftime('%d.%m.%Y %H:%M')}\n"
        else:
            text += f"\n📦 Подписка: Нет активной\n"

        text += f"\n🕐 Зарегистрирован: {user['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        if user['last_activity']:
            text += f"Последняя активность: {user['last_activity'].strftime('%d.%m.%Y %H:%M')}\n"

        await callback.message.edit_text(text, reply_markup=user_management_keyboard(telegram_id), parse_mode=None)
        await callback.answer()

    except Exception as e:
        logger.error("admin_user_view_error", error=str(e), telegram_id=telegram_id)
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# ==================== USER SEARCH ====================

@admin_router.callback_query(F.data == "admin:search_user")
async def start_search_user(callback: CallbackQuery, state: FSMContext):
    """Start user search."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(SearchUser.waiting_for_query)
    await callback.message.edit_text(
        "🔍 Поиск пользователя\n\n"
        "Введите Telegram ID, username или имя пользователя:\n\n"
        "Примеры:\n"
        "• 123456789 — поиск по ID\n"
        "• @username — поиск по username\n"
        "• Артем — поиск по имени",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(SearchUser.waiting_for_query))
async def process_search_query(message: Message, state: FSMContext):
    """Process search query - search by ID, username, or name."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select, or_

    query = message.text.strip()

    try:
        async with async_session_maker() as session:
            # Try to search by telegram_id first
            if query.isdigit():
                telegram_id = int(query)
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
            else:
                # Remove @ if present and search by username, first_name, or last_name
                search_term = query.lstrip('@')
                result = await session.execute(
                    select(User).where(
                        or_(
                            User.username.ilike(f"%{search_term}%"),
                            User.first_name.ilike(f"%{search_term}%"),
                            User.last_name.ilike(f"%{search_term}%")
                        )
                    ).limit(50)
                )

            users = result.scalars().all()

            if not users:
                await message.answer(
                    "❌ Пользователи не найдены.\n\nПопробуйте:\n• Telegram ID (число)\n• Username (без @)\n• Имя пользователя",
                    reply_markup=back_keyboard(),
                    parse_mode=None
                )
            elif len(users) == 1:
                # Show single user directly
                user = users[0]
                from app.services.user.user_service import UserService
                user_service = UserService(session)
                stats = await user_service.get_user_stats(user.telegram_id)

                text = f"👤 Найден пользователь\n\n"
                text += f"ID: {stats['telegram_id']}\n"
                text += f"Имя: {safe_text(stats['full_name'])}\n"
                if stats['username']:
                    text += f"Username: @{safe_text(stats['username'])}\n"
                text += f"Статус: {'🚫 Забанен' if stats['is_banned'] else '✅ Активен'}\n"
                text += f"Токенов: {stats['total_tokens']:,}\n"

                if stats['has_active_subscription']:
                    text += f"\n📦 Подписка: {safe_text(str(stats['subscription_type']))}\n"
                    if stats['subscription_expires_at']:
                        text += f"Истекает: {stats['subscription_expires_at'].strftime('%d.%m.%Y %H:%M')}\n"
                else:
                    text += f"\n📦 Подписка: Нет активной\n"

                await message.answer(text, reply_markup=user_management_keyboard(user.telegram_id), parse_mode=None)
            else:
                # Show list of found users
                text = f"🔍 Найдено пользователей: {len(users)}\n\n"
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                builder = InlineKeyboardBuilder()

                for user in users[:20]:  # Limit to 20
                    button_text = f"{safe_text(user.full_name or 'Без имени')} (ID: {user.telegram_id})"
                    builder.button(
                        text=button_text[:64],
                        callback_data=f"admin:user_view:{user.telegram_id}"
                    )

                builder.button(text="🔙 Назад", callback_data="admin:users")
                builder.adjust(1)

                await message.answer(text, reply_markup=builder.as_markup(), parse_mode=None)

    except Exception as e:
        logger.error("admin_search_error", error=str(e))
        await message.answer(f"❌ Ошибка поиска: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


# ==================== USER DETAILS ====================

@admin_router.callback_query(F.data.startswith("admin:user_details:"))
async def user_details_callback(callback: CallbackQuery):
    """Show detailed user information."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.database.models import User, Subscription, AIRequest, Payment
    from sqlalchemy import select, func

    try:
        async with async_session_maker() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await callback.answer("❌ Пользователь не найден", show_alert=True)
                return

            # Get statistics
            total_subs = await session.scalar(
                select(func.count()).select_from(Subscription).where(Subscription.user_id == user.id)
            )
            total_requests = await session.scalar(
                select(func.count()).select_from(AIRequest).where(AIRequest.user_id == user.id)
            )
            total_payments = await session.scalar(
                select(func.count()).select_from(Payment).where(Payment.user_id == user.id)
            )

            # Get active subscription
            active_sub = user.get_active_subscription()

            text = f"👁️ Детальная информация\n\n"
            text += f"ID: {user.telegram_id}\n"
            text += f"Имя: {safe_text(user.full_name)}\n"
            if user.username:
                text += f"Username: @{safe_text(user.username)}\n"
            text += f"Язык: {user.language_code or 'не указан'}\n"
            text += f"Статус: {'🚫 Забанен' if user.is_banned else '✅ Активен'}\n"
            if user.is_banned and user.ban_reason:
                text += f"Причина бана: {safe_text(user.ban_reason)}\n"

            text += f"\n💎 Токенов всего: {user.get_total_tokens():,}\n"

            if active_sub:
                text += f"\n📦 Активная подписка:\n"
                text += f"   Тип: {safe_text(str(active_sub.subscription_type))}\n"
                text += f"   Токенов: {active_sub.tokens_remaining:,} из {active_sub.tokens_amount:,}\n"
                if active_sub.expires_at:
                    text += f"   Истекает: {active_sub.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
                else:
                    text += f"   Вечная подписка\n"
            else:
                text += f"\n📦 Активной подписки нет\n"

            text += f"\n📊 Статистика:\n"
            text += f"   Подписок куплено: {total_subs}\n"
            text += f"   Запросов сделано: {total_requests}\n"
            text += f"   Платежей: {total_payments}\n"

            text += f"\n🕐 Создан: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            if user.last_activity:
                text += f"Последняя активность: {user.last_activity.strftime('%d.%m.%Y %H:%M')}\n"

            await callback.message.edit_text(text, reply_markup=user_management_keyboard(telegram_id), parse_mode=None)
            await callback.answer()

    except Exception as e:
        logger.error("admin_user_details_error", error=str(e))
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# ==================== USER REQUESTS HISTORY ====================

@admin_router.callback_query(F.data.startswith("admin:user_requests:"))
async def user_requests_callback(callback: CallbackQuery):
    """Show user's AI requests history."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.database.models import User, AIRequest
    from sqlalchemy import select

    try:
        async with async_session_maker() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await callback.answer("❌ Пользователь не найден", show_alert=True)
                return

            # Get recent requests
            result = await session.execute(
                select(AIRequest)
                .where(AIRequest.user_id == user.id)
                .order_by(AIRequest.created_at.desc())
                .limit(15)
            )
            requests = result.scalars().all()

            text = f"📊 История запросов\n"
            text += f"Пользователь: {safe_text(user.full_name)}\n\n"

            if not requests:
                text += "Запросов пока нет."
            else:
                for req in requests:
                    status_emoji = {
                        "completed": "✅",
                        "pending": "⏳",
                        "failed": "❌"
                    }.get(req.status, "❓")

                    text += f"{status_emoji} {req.request_type} | {req.ai_model}\n"
                    text += f"   Токенов: {req.tokens_cost}\n"
                    if req.prompt:
                        prompt_preview = req.prompt[:50] + "..." if len(req.prompt) > 50 else req.prompt
                        text += f"   Промпт: {prompt_preview}\n"
                    text += f"   {req.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

            await callback.message.edit_text(text, reply_markup=user_management_keyboard(telegram_id))
            await callback.answer()

    except Exception as e:
        logger.error("admin_user_requests_error", error=str(e))
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# ==================== USER MANAGEMENT ACTIONS ====================

@admin_router.callback_query(F.data.startswith("admin:user_give_tokens:"))
async def user_give_tokens_shortcut(callback: CallbackQuery, state: FSMContext):
    """Quick give tokens to user from their card."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])
    await state.update_data(user_id=telegram_id)
    await state.set_state(GiveTokens.waiting_for_amount)

    await callback.message.edit_text(
        f"💰 Выдача токенов\n"
        f"User ID: {telegram_id}\n\n"
        "Введите количество токенов:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:user_ban:"))
async def user_ban_shortcut(callback: CallbackQuery, state: FSMContext):
    """Quick ban user from their card."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])
    await state.update_data(user_id=telegram_id)
    await state.set_state(BanUser.waiting_for_reason)

    await callback.message.edit_text(
        f"🚫 Бан пользователя\n"
        f"User ID: {telegram_id}\n\n"
        "Введите причину бана:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


# ==================== SEND MESSAGE TO USER ====================

@admin_router.callback_query(F.data.startswith("admin:user_message:"))
async def start_user_message(callback: CallbackQuery, state: FSMContext):
    """Start sending message to specific user."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])
    await state.update_data(target_user_id=telegram_id)
    await state.set_state(SendUserMessage.waiting_for_message)

    await callback.message.edit_text(
        f"✉️ Отправка сообщения пользователю\n"
        f"User ID: {telegram_id}\n\n"
        "Введите текст сообщения:\n\n"
        "💡 Можете прикрепить фото к сообщению.",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(SendUserMessage.waiting_for_message))
async def process_user_message(message: Message, state: FSMContext):
    """Process and send message to specific user."""
    if not is_admin(message.from_user.id):
        return

    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties

    data = await state.get_data()
    target_user_id = data.get("target_user_id")

    if not target_user_id:
        await message.answer("❌ Ошибка: ID пользователя не найден", reply_markup=back_keyboard())
        await state.clear()
        return

    try:
        # Create main bot without default parse_mode
        main_bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties())

        # Check if message has photo
        if message.photo:
            photo = message.photo[-1]
            caption = message.caption or ""
            await main_bot.send_photo(
                chat_id=target_user_id,
                photo=photo.file_id,
                caption=caption,
                parse_mode=None
            )
        else:
            await main_bot.send_message(
                chat_id=target_user_id,
                text=message.text,
                parse_mode=None
            )

        await main_bot.session.close()

        logger.info(
            "admin_user_message_sent",
            admin_id=message.from_user.id,
            target_user_id=target_user_id,
            has_photo=bool(message.photo)
        )

        await message.answer(
            f"✅ Сообщение отправлено пользователю {target_user_id}!",
            reply_markup=back_keyboard()
        )

    except Exception as e:
        error_msg = str(e)
        logger.error("admin_user_message_error", target_user_id=target_user_id, error=error_msg)
        await message.answer(
            f"❌ Ошибка отправки: {error_msg}",
            reply_markup=back_keyboard()
        )

    await state.clear()


@admin_router.callback_query(F.data.startswith("admin:user_tariff:"))
async def user_tariff_callback(callback: CallbackQuery):
    """Show tariff selection for user."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])

    text = f"📦 Изменение тарифа\n"
    text += f"User ID: {telegram_id}\n\n"
    text += "Выберите тариф:"

    # Store telegram_id in callback data
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()

    tariffs = [
        ("7 дней - 150k токенов", "7days"),
        ("14 дней - 250k токенов", "14days"),
        ("21 день - 500k токенов", "21days"),
        ("30 дней - 1M токенов", "30days_1m"),
        ("30 дней - 5M токенов", "30days_5m"),
        ("1 день безлимит", "unlimited_1day"),
        ("♾️ Вечная 150k", "eternal_150k"),
        ("♾️ Вечная 250k", "eternal_250k"),
        ("♾️ Вечная 500k", "eternal_500k"),
        ("♾️ Вечная 1M", "eternal_1m"),
    ]

    for label, tariff_type in tariffs:
        builder.button(
            text=label,
            callback_data=f"admin:assign_tariff:{telegram_id}:{tariff_type}"
        )

    builder.button(text="🔙 Назад", callback_data=f"admin:user_view:{telegram_id}")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:assign_tariff:"))
async def assign_tariff_callback(callback: CallbackQuery):
    """Assign tariff to user."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    parts = callback.data.split(":")
    telegram_id = int(parts[2])
    tariff_type = parts[3]

    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService
    from app.services.user.user_service import UserService

    try:
        async with async_session_maker() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)

            sub_service = SubscriptionService(session)
            subscription = await sub_service.create_subscription(
                user_id=user.id,
                subscription_type=tariff_type
            )

            await callback.answer(f"✅ Тариф {tariff_type} выдан!", show_alert=True)

            # Show updated user info
            stats = await user_service.get_user_stats(telegram_id)

            text = f"👤 Информация о пользователе\n\n"
            text += f"ID: {stats['telegram_id']}\n"
            text += f"Имя: {stats['full_name']}\n"
            text += f"Токенов: {stats['total_tokens']:,}\n"
            text += f"\n📦 Новая подписка: {tariff_type}\n"

            if stats['subscription_expires_at']:
                text += f"Истекает: {stats['subscription_expires_at'].strftime('%d.%m.%Y %H:%M')}\n"

            await callback.message.edit_text(text, reply_markup=user_management_keyboard(telegram_id))

            logger.info(
                "admin_assign_tariff",
                admin_id=callback.from_user.id,
                user_id=telegram_id,
                tariff=tariff_type
            )

    except Exception as e:
        logger.error("admin_assign_tariff_error", error=str(e))
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# ==================== UNLIMITED LINKS ====================

@admin_router.callback_query(F.data == "admin:unlimited_menu")
async def unlimited_menu_callback(callback: CallbackQuery):
    """Show unlimited links menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    text = "🔗 Безлимитные пригласительные ссылки\n\nВыберите действие:"
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
        "➕ Создание безлимитной ссылки\n\n"
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

            text = f"""✅ Безлимитная ссылка создана!

🔗 Код: {invite_code}
📅 Длительность: {duration_days} дней
👥 Макс. использований: {max_uses if max_uses else '∞'}
📝 Описание: {description if description else 'Нет'}

Ссылка для приглашений:
{invite_url}

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

    text = "🔗 Безлимитные пригласительные ссылки:\n\n"

    for link in links:
        status = "✅ Активна" if link.is_active else "❌ Неактивна"
        if link.is_active and not link.is_valid:
            status = "⚠️ Истекла"

        text += f"Код: {link.invite_code}\n"
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


# ==================== BAN/UNBAN ====================

@admin_router.callback_query(F.data == "admin:ban_menu")
async def ban_menu_callback(callback: CallbackQuery):
    """Show ban/unban menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    text = "🔨 Управление банами\n\nВыберите действие:"
    await callback.message.edit_text(text, reply_markup=ban_menu())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:ban_user")
async def start_ban_user(callback: CallbackQuery, state: FSMContext):
    """Start ban user flow."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(BanUser.waiting_for_user_id)
    await callback.message.edit_text(
        "🚫 Бан пользователя\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(BanUser.waiting_for_user_id))
async def process_ban_user_id(message: Message, state: FSMContext):
    """Process user ID for ban."""
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.strip())
        await state.update_data(user_id=user_id)
        await state.set_state(BanUser.waiting_for_reason)

        await message.answer(
            f"✅ User ID: {user_id}\n\n"
            "Введите причину бана:",
            reply_markup=cancel_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")


@admin_router.message(StateFilter(BanUser.waiting_for_reason))
async def process_ban_reason(message: Message, state: FSMContext):
    """Process ban reason and ban user."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.services.user.user_service import UserService

    reason = message.text.strip()
    data = await state.get_data()
    user_id = data['user_id']

    try:
        async with async_session_maker() as session:
            user_service = UserService(session)
            user = await user_service.ban_user(
                telegram_id=user_id,
                reason=reason,
                admin_id=message.from_user.id
            )

            await message.answer(
                f"✅ Пользователь забанен\n\n"
                f"👤 Пользователь: {safe_text(user.full_name)} ({user.telegram_id})\n"
                f"📝 Причина: {reason}",
                reply_markup=back_keyboard()
            )

            logger.info(
                "admin_ban_user",
                admin_id=message.from_user.id,
                user_id=user_id,
                reason=reason
            )

    except Exception as e:
        logger.error("admin_ban_error", error=str(e), user_id=user_id)
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


@admin_router.callback_query(F.data == "admin:unban_user")
async def start_unban_user(callback: CallbackQuery, state: FSMContext):
    """Show list of banned users."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    async with async_session_maker() as session:
        # Get banned users
        result = await session.execute(
            select(User).where(User.is_banned == True).order_by(User.created_at.desc()).limit(20)
        )
        banned_users = result.scalars().all()

    if not banned_users:
        await callback.message.edit_text(
            "✅ Нет забаненных пользователей",
            reply_markup=back_keyboard()
        )
        await callback.answer()
        return

    text = f"🚫 Забаненные пользователи ({len(banned_users)}):\n\n"
    text += "Выберите пользователя для разбана:\n"

    builder = InlineKeyboardBuilder()

    for user in banned_users:
        button_text = f"{safe_text(user.full_name)} (ID: {user.telegram_id})"
        if user.ban_reason:
            button_text += f" - {user.ban_reason[:20]}"
        builder.button(
            text=button_text[:64],
            callback_data=f"admin:unban_confirm:{user.telegram_id}"
        )

    builder.button(text="🔍 Ввести ID вручную", callback_data="admin:unban_manual")
    builder.button(text="🔙 Назад", callback_data="admin:ban_menu")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:unban_manual")
async def unban_manual(callback: CallbackQuery, state: FSMContext):
    """Manual unban by ID input."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(UnbanUser.waiting_for_user_id)
    await callback.message.edit_text(
        "✅ Разбан пользователя\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:unban_confirm:"))
async def unban_confirm(callback: CallbackQuery):
    """Unban user by callback."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.services.user.user_service import UserService

    try:
        async with async_session_maker() as session:
            user_service = UserService(session)
            user = await user_service.unban_user(
                telegram_id=telegram_id,
                admin_id=callback.from_user.id
            )

            await callback.message.edit_text(
                f"✅ Пользователь разбанен\n\n"
                f"👤 Пользователь: {safe_text(user.full_name)} ({user.telegram_id})",
                reply_markup=back_keyboard()
            )

            logger.info(
                "admin_unban_user",
                admin_id=callback.from_user.id,
                user_id=telegram_id
            )

            await callback.answer("✅ Пользователь разбанен", show_alert=True)

    except Exception as e:
        logger.error("admin_unban_error", error=str(e), user_id=telegram_id)
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@admin_router.message(StateFilter(UnbanUser.waiting_for_user_id))
async def process_unban_user_id(message: Message, state: FSMContext):
    """Process user ID for unban."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.services.user.user_service import UserService

    try:
        user_id = int(message.text.strip())

        async with async_session_maker() as session:
            user_service = UserService(session)
            user = await user_service.unban_user(
                telegram_id=user_id,
                admin_id=message.from_user.id
            )

            await message.answer(
                f"✅ Пользователь разбанен\n\n"
                f"👤 Пользователь: {safe_text(user.full_name)} ({user.telegram_id})",
                reply_markup=back_keyboard()
            )

            logger.info(
                "admin_unban_user",
                admin_id=message.from_user.id,
                user_id=user_id
            )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")
    except Exception as e:
        logger.error("admin_unban_error", error=str(e), user_id=user_id)
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


# ==================== GIVE TOKENS ====================

@admin_router.callback_query(F.data == "admin:give_tokens")
async def start_give_tokens(callback: CallbackQuery, state: FSMContext):
    """Show recent users list for token giving."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models import User
    from sqlalchemy import select
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    async with async_session_maker() as session:
        # Get last 10 users
        result = await session.execute(
            select(User).order_by(User.last_activity.desc().nullslast()).limit(10)
        )
        recent_users = result.scalars().all()

    text = f"💰 Выдача токенов\n\n"
    text += f"Последние активные пользователи:\n"

    builder = InlineKeyboardBuilder()

    for user in recent_users:
        active_sub = user.get_active_subscription()
        sub_emoji = "💎" if active_sub else ""
        button_text = f"{sub_emoji} {safe_text(user.full_name)} (ID: {user.telegram_id})"
        builder.button(
            text=button_text[:64],
            callback_data=f"admin:give_tokens_to:{user.telegram_id}"
        )

    builder.button(text="🔍 Поиск пользователя", callback_data="admin:give_tokens_search")
    builder.button(text="✏️ Ввести ID вручную", callback_data="admin:give_tokens_manual")
    builder.button(text="🔙 Назад", callback_data="admin:back")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:give_tokens_search")
async def give_tokens_search(callback: CallbackQuery, state: FSMContext):
    """Search user for giving tokens."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(SearchUser.waiting_for_query)
    await state.update_data(return_action="give_tokens")
    await callback.message.edit_text(
        "🔍 Поиск пользователя\n\n"
        "Введите Telegram ID или username:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin:give_tokens_manual")
async def give_tokens_manual(callback: CallbackQuery, state: FSMContext):
    """Manual token giving by ID input."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(GiveTokens.waiting_for_user_id)
    await callback.message.edit_text(
        "💰 Выдача токенов\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:give_tokens_to:"))
async def give_tokens_to_user(callback: CallbackQuery, state: FSMContext):
    """Give tokens to selected user."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    telegram_id = int(callback.data.split(":")[-1])
    await state.update_data(user_id=telegram_id)
    await state.set_state(GiveTokens.waiting_for_amount)

    await callback.message.edit_text(
        f"💰 Выдача токенов\n"
        f"User ID: {telegram_id}\n\n"
        "Введите количество токенов:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(GiveTokens.waiting_for_user_id))
async def process_give_tokens_user_id(message: Message, state: FSMContext):
    """Process user ID for giving tokens."""
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.strip())
        await state.update_data(user_id=user_id)
        await state.set_state(GiveTokens.waiting_for_amount)

        await message.answer(
            f"✅ User ID: {user_id}\n\n"
            "Введите количество токенов:",
            reply_markup=cancel_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")


@admin_router.message(StateFilter(GiveTokens.waiting_for_amount))
async def process_give_tokens_amount(message: Message, state: FSMContext):
    """Process token amount and give tokens."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService
    from app.services.user.user_service import UserService

    try:
        amount = int(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Количество токенов должно быть больше 0")
            return

        data = await state.get_data()
        user_id = data['user_id']

        async with async_session_maker() as session:
            # Check if user exists
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(user_id)

            # Give tokens (add eternal subscription with tokens)
            sub_service = SubscriptionService(session)
            subscription = await sub_service.add_eternal_tokens(
                user_id=user.id,
                tokens=amount,
                subscription_type="admin_gift"
            )

            # Get total tokens after adding
            total_tokens = user.get_total_tokens()

            # Send notification to user
            from aiogram import Bot
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            from app.core.config import settings
            try:
                main_bot = Bot(token=settings.telegram_bot_token)

                # Create keyboard with profile button
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💎 Проверить баланс", callback_data="profile")]
                ])

                await main_bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"🎉 Поздравляем!\n\n"
                         f"Вам начислено {amount:,} токенов!\n"
                         f"💎 Всего токенов: {total_tokens:,}",
                    reply_markup=keyboard
                )
                await main_bot.session.close()
            except Exception as e:
                logger.error("notify_user_tokens_error", error=str(e), user_id=user_id)

            await message.answer(
                f"✅ Токены выданы\n\n"
                f"👤 Пользователь: {safe_text(user.full_name)} ({user.telegram_id})\n"
                f"💎 Количество: {amount:,} токенов\n"
                f"💎 Всего токенов: {total_tokens:,}",
                reply_markup=back_keyboard()
            )

            logger.info(
                "admin_give_tokens",
                admin_id=message.from_user.id,
                user_id=user_id,
                amount=amount
            )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")
    except Exception as e:
        logger.error("admin_give_tokens_error", error=str(e))
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


# ==================== FINANCE ====================

def _finance_period_keyboard():
    """Create inline keyboard for finance period selection."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="📆 Сегодня", callback_data="admin:finance:today")
    builder.button(text="📅 Неделя", callback_data="admin:finance:week")
    builder.button(text="🗓 Месяц", callback_data="admin:finance:month")
    builder.button(text="📊 Всё время", callback_data="admin:finance:all")
    builder.button(text="🔙 Назад в меню", callback_data="admin:back")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


async def _build_finance_text(period: str) -> str:
    """Build finance analytics text for the given period."""
    from app.database.database import async_session_maker
    from app.database.models import Payment, Subscription, User
    from sqlalchemy import select, func, and_
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)

    period_labels = {
        "today": "Сегодня",
        "week": "За неделю",
        "month": "За месяц",
        "all": "За всё время",
    }

    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    async with async_session_maker() as session:
        # Base payment filters
        success_filter = [Payment.status == "success"]
        if start_date:
            success_filter.append(Payment.created_at >= start_date)

        # Successful payments count
        successful_count = await session.scalar(
            select(func.count()).select_from(Payment).where(and_(*success_filter))
        ) or 0

        # Total revenue
        revenue = await session.scalar(
            select(func.sum(Payment.amount)).where(and_(*success_filter))
        ) or 0

        # Average check
        avg_check = await session.scalar(
            select(func.avg(Payment.amount)).where(and_(*success_filter))
        ) or 0

        # Failed payments
        fail_filter = [Payment.status == "failed"]
        if start_date:
            fail_filter.append(Payment.created_at >= start_date)
        failed_count = await session.scalar(
            select(func.count()).select_from(Payment).where(and_(*fail_filter))
        ) or 0

        # Refunded payments
        refund_filter = [Payment.status == "refunded"]
        if start_date:
            refund_filter.append(Payment.created_at >= start_date)
        refunded_count = await session.scalar(
            select(func.count()).select_from(Payment).where(and_(*refund_filter))
        ) or 0
        refunded_amount = await session.scalar(
            select(func.sum(Payment.amount)).where(and_(*refund_filter))
        ) or 0

        # Pending payments
        pending_filter = [Payment.status == "pending"]
        if start_date:
            pending_filter.append(Payment.created_at >= start_date)
        pending_count = await session.scalar(
            select(func.count()).select_from(Payment).where(and_(*pending_filter))
        ) or 0

        # New paid subscriptions in period (distinct users)
        from app.core.subscription_plans import PAID_SUBSCRIPTION_TYPES
        sub_filter = [
            Subscription.subscription_type.in_(PAID_SUBSCRIPTION_TYPES)
        ]
        if start_date:
            sub_filter.append(Subscription.started_at >= start_date)
        new_subs = await session.scalar(
            select(func.count(func.distinct(Subscription.user_id)))
            .select_from(Subscription).where(and_(*sub_filter))
        ) or 0

        # Currently active paid subscriptions (distinct users with usable tokens)
        active_subs = await session.scalar(
            select(func.count(func.distinct(Subscription.user_id)))
            .select_from(Subscription).where(
                and_(
                    Subscription.is_active == True,
                    Subscription.tokens_amount > Subscription.tokens_used,
                    Subscription.subscription_type.in_(PAID_SUBSCRIPTION_TYPES)
                )
            )
        ) or 0

        # New users in period
        user_filter = []
        if start_date:
            user_filter.append(User.created_at >= start_date)
        if user_filter:
            new_users = await session.scalar(
                select(func.count()).select_from(User).where(and_(*user_filter))
            ) or 0
        else:
            new_users = await session.scalar(
                select(func.count()).select_from(User)
            ) or 0

        # Last 5 payments in period
        pay_query = select(Payment).where(Payment.status == "success").order_by(Payment.created_at.desc()).limit(5)
        if start_date:
            pay_query = select(Payment).where(
                and_(Payment.status == "success", Payment.created_at >= start_date)
            ).order_by(Payment.created_at.desc()).limit(5)
        result = await session.execute(pay_query)
        recent_payments = result.scalars().all()

    label = period_labels.get(period, "За всё время")

    text = (
        f"💵 Финансы — {label}\n\n"
        f"💰 Выручка: {revenue:,.0f} RUB\n"
        f"✅ Успешных платежей: {successful_count}\n"
        f"📊 Средний чек: {avg_check:,.0f} RUB\n\n"
        f"❌ Неудачных: {failed_count}\n"
        f"↩️ Возвратов: {refunded_count} ({refunded_amount:,.0f} RUB)\n"
        f"⏳ Ожидающих: {pending_count}\n\n"
        f"📦 Новых подписок: {new_subs}\n"
        f"🟢 Активных подписок: {active_subs}\n"
        f"👥 Новых пользователей: {new_users}\n"
    )

    if recent_payments:
        text += "\n📋 Последние платежи:\n"
        for p in recent_payments:
            text += f"  {p.created_at.strftime('%d.%m %H:%M')} — {p.amount:,.0f} RUB (ID: {p.user_id})\n"

    return text


@admin_router.callback_query(F.data == "admin:finance")
async def finance_callback(callback: CallbackQuery):
    """Show finance section."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    text = await _build_finance_text("all")
    await callback.message.edit_text(text, reply_markup=_finance_period_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:finance:"))
async def finance_period_callback(callback: CallbackQuery):
    """Show finance for selected period."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    period = callback.data.split(":")[-1]
    text = await _build_finance_text(period)
    await callback.message.edit_text(text, reply_markup=_finance_period_keyboard())
    await callback.answer()


# ==================== PAYMENTS ====================

@admin_router.callback_query(F.data == "admin:payments")
async def show_payments_callback(callback: CallbackQuery):
    """Show recent payments."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models import Payment
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Payment).order_by(Payment.created_at.desc()).limit(20)
        )
        payments = result.scalars().all()

    if not payments:
        await callback.message.edit_text("💳 Платежей пока нет.", reply_markup=back_keyboard())
        await callback.answer()
        return

    text = "💳 Последние 20 платежей:\n\n"

    for payment in payments:
        status_emoji = {
            "success": "✅",
            "pending": "⏳",
            "failed": "❌",
            "refunded": "↩️"
        }.get(payment.status, "❓")

        text += f"{status_emoji} ID: {payment.payment_id}\n"
        text += f"💰 Сумма: {payment.amount} {payment.currency}\n"
        text += f"👤 User ID: {payment.user_id}\n"
        text += f"📊 Статус: {payment.status}\n"
        text += f"🕐 {payment.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


# ==================== PROMOCODES ====================

@admin_router.callback_query(F.data == "admin:promo_menu")
async def promo_menu_callback(callback: CallbackQuery):
    """Show promocode menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    text = "🎁 Управление промокодами\n\nВыберите действие:"
    await callback.message.edit_text(text, reply_markup=promo_menu())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:create_promo")
async def start_create_promo(callback: CallbackQuery, state: FSMContext):
    """Start creating promocode."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(CreatePromo.waiting_for_code)
    await callback.message.edit_text(
        "➕ Создание промокода\n\n"
        "Введите код промокода (например: WELCOME2024):",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(CreatePromo.waiting_for_code))
async def process_promo_code(message: Message, state: FSMContext):
    """Process promocode."""
    if not is_admin(message.from_user.id):
        return

    code = message.text.strip().upper()

    if len(code) < 3:
        await message.answer("❌ Код должен содержать минимум 3 символа")
        return

    # Check if code already exists
    from app.database.database import async_session_maker
    from app.database.models.promocode import Promocode
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Promocode).where(Promocode.code == code)
        )
        existing = result.scalar_one_or_none()

    if existing:
        await message.answer(
            f"❌ Промокод с кодом {code} уже существует.",
            reply_markup=back_keyboard()
        )
        await state.clear()
        return

    await state.update_data(code=code)
    await state.set_state(CreatePromo.waiting_for_bonus_type)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Токены", callback_data="promo_type:tokens")
    builder.button(text="📦 Подписка (токены)", callback_data="promo_type:subscription")
    builder.button(text="💸 Скидка (%)", callback_data="promo_type:discount_percent")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")
    builder.adjust(1)

    await message.answer(
        f"✅ Код: {code}\n\n"
        "Выберите тип бонуса:",
        reply_markup=builder.as_markup()
    )


@admin_router.callback_query(F.data.startswith("promo_type:"), StateFilter(CreatePromo.waiting_for_bonus_type))
async def process_promo_bonus_type(callback: CallbackQuery, state: FSMContext):
    """Process bonus type selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    bonus_type = callback.data.split(":")[1]
    await state.update_data(bonus_type=bonus_type)
    await state.set_state(CreatePromo.waiting_for_tokens)

    if bonus_type == "tokens":
        prompt = "Введите количество токенов:"
    elif bonus_type == "subscription":
        prompt = "Введите количество токенов для подписки:"
    else:  # discount_percent
        prompt = "Введите размер скидки (в процентах, например 20):"

    await callback.message.edit_text(prompt)
    await callback.answer()


@admin_router.message(StateFilter(CreatePromo.waiting_for_tokens))
async def process_promo_tokens(message: Message, state: FSMContext):
    """Process bonus value for promocode."""
    if not is_admin(message.from_user.id):
        return

    try:
        value = int(message.text.strip())
        if value <= 0:
            await message.answer("❌ Значение должно быть больше 0")
            return

        data = await state.get_data()
        bonus_type = data.get('bonus_type', 'tokens')

        if bonus_type == "discount_percent" and value > 100:
            await message.answer("❌ Скидка не может быть больше 100%")
            return

        await state.update_data(bonus_value=value)
        await state.set_state(CreatePromo.waiting_for_max_uses)

        await message.answer(
            "Введите макс. кол-во использований\n"
            "(или 0 для неограниченного):",
            reply_markup=cancel_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")


@admin_router.message(StateFilter(CreatePromo.waiting_for_max_uses))
async def process_promo_max_uses(message: Message, state: FSMContext):
    """Process max uses and ask for expiration date."""
    if not is_admin(message.from_user.id):
        return

    try:
        max_uses = int(message.text.strip())
        if max_uses < 0:
            await message.answer("❌ Значение не может быть отрицательным")
            return

        await state.update_data(max_uses=max_uses)
        await state.set_state(CreatePromo.waiting_for_expires_at)

        await message.answer(
            "📅 Введите срок действия промокода:\n\n"
            "Форматы:\n"
            "• Количество дней: 7, 30, 90\n"
            "• Дата: 31.12.2026\n"
            "• 0 — без ограничения срока\n\n"
            "Пример: 30 (промокод будет действовать 30 дней)",
            reply_markup=cancel_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число.")


@admin_router.message(StateFilter(CreatePromo.waiting_for_expires_at))
async def process_promo_expires_at(message: Message, state: FSMContext):
    """Process expiration date and create promocode."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models.promocode import Promocode
    from datetime import datetime, timedelta, timezone

    try:
        text = message.text.strip()
        expires_at = None

        if text == "0":
            expires_at = None  # No expiration
        elif "." in text:
            # Date format: DD.MM.YYYY
            try:
                expires_at = datetime.strptime(text, "%d.%m.%Y").replace(
                    hour=23, minute=59, second=59, tzinfo=timezone.utc
                )
            except ValueError:
                await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ (например: 31.12.2026)")
                return
        else:
            # Number of days
            days = int(text)
            if days < 0:
                await message.answer("❌ Количество дней не может быть отрицательным")
                return
            if days > 0:
                expires_at = datetime.now(timezone.utc) + timedelta(days=days)

        data = await state.get_data()
        code = data['code']
        bonus_type = data.get('bonus_type', 'tokens')
        bonus_value = data['bonus_value']
        max_uses = data['max_uses']

        async with async_session_maker() as session:
            promo = Promocode(
                code=code,
                bonus_type=bonus_type,
                bonus_value=bonus_value,
                max_uses=max_uses if max_uses > 0 else None,
                current_uses=0,
                is_active=True,
                expires_at=expires_at
            )

            session.add(promo)
            await session.commit()
            await session.refresh(promo)

            type_labels = {
                "tokens": f"{bonus_value:,} токенов",
                "subscription": f"Подписка ({bonus_value:,} токенов)",
                "discount_percent": f"Скидка {bonus_value}%",
            }
            uses_text = f"{max_uses}" if max_uses > 0 else "Неограничено"
            expires_text = expires_at.strftime("%d.%m.%Y %H:%M") if expires_at else "Бессрочно"

            await message.answer(
                f"✅ Промокод создан!\n\n"
                f"🎁 Код: {code}\n"
                f"📦 Тип: {type_labels.get(bonus_type, bonus_type)}\n"
                f"👥 Использований: {uses_text}\n"
                f"📅 Действует до: {expires_text}",
                reply_markup=back_keyboard()
            )

            logger.info(
                "admin_create_promo",
                admin_id=message.from_user.id,
                code=code,
                bonus_type=bonus_type,
                bonus_value=bonus_value,
                max_uses=max_uses,
                expires_at=str(expires_at)
            )

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число дней или дату (ДД.ММ.ГГГГ)")
    except Exception as e:
        logger.error("admin_create_promo_error", error=str(e))
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


@admin_router.callback_query(F.data == "admin:list_promos")
async def list_promos_callback(callback: CallbackQuery):
    """List all promocodes."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models.promocode import Promocode
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Promocode).order_by(Promocode.created_at.desc())
        )
        promos = result.scalars().all()

    if not promos:
        await callback.message.edit_text("🎁 Промокодов пока нет.", reply_markup=back_keyboard())
        await callback.answer()
        return

    text = "🎁 Промокоды:\n\n"

    for promo in promos:
        status = "✅ Активен" if promo.is_active else "❌ Неактивен"
        if promo.is_active and not promo.is_valid:
            status = "⚠️ Истек"

        type_labels = {
            "tokens": f"{promo.bonus_value:,} токенов",
            "subscription": f"Подписка ({promo.bonus_value:,} токенов)",
            "discount_percent": f"Скидка {promo.bonus_value}%",
        }
        text += f"Код: {promo.code}\n"
        text += f"💎 Бонус: {type_labels.get(promo.bonus_type, f'{promo.bonus_value:,} токенов')}\n"
        text += f"👥 Использований: {promo.current_uses}"
        if promo.max_uses:
            text += f"/{promo.max_uses}"
        text += f"\n📊 Статус: {status}\n"
        if promo.expires_at:
            text += f"📅 Действует до: {promo.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
        else:
            text += f"📅 Срок: Бессрочно\n"
        text += f"🕐 Создан: {promo.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


# ==================== LOGS ====================

@admin_router.callback_query(F.data == "admin:logs")
async def show_logs_callback(callback: CallbackQuery):
    """Show recent admin logs."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models.system import AdminLog
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(AdminLog).order_by(AdminLog.created_at.desc()).limit(15)
        )
        logs = result.scalars().all()

    if not logs:
        await callback.message.edit_text("📝 Логов пока нет.", reply_markup=back_keyboard())
        await callback.answer()
        return

    text = "📝 Последние 15 действий:\n\n"

    for log in logs:
        text += f"🔹 {log.action}\n"
        text += f"👤 Admin ID: {log.admin_id}\n"
        if log.target_type and log.target_id:
            text += f"🎯 Target: {log.target_type} #{log.target_id}\n"
        text += f"🕐 {log.created_at.strftime('%d.%m.%Y %H:%M:%S')}\n\n"

    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()


# ==================== BROADCAST ====================


async def _resolve_specific_users(session, user_identifiers: list[str]) -> list:
    """
    Resolve user identifiers (IDs, @usernames) to User objects.

    Args:
        session: Database session
        user_identifiers: List of strings - telegram IDs or @usernames

    Returns:
        List of User objects
    """
    from app.database.models import User
    from sqlalchemy import select as sa_select, or_

    users = []
    telegram_ids = []
    usernames = []

    for identifier in user_identifiers:
        identifier = identifier.strip()
        if identifier.startswith("@"):
            usernames.append(identifier[1:].lower())
        elif identifier.lstrip("-").isdigit():
            telegram_ids.append(int(identifier))
        else:
            # Try as username without @
            usernames.append(identifier.lower())

    conditions = []
    if telegram_ids:
        conditions.append(User.telegram_id.in_(telegram_ids))
    if usernames:
        from sqlalchemy import func as sa_func
        conditions.append(sa_func.lower(User.username).in_(usernames))

    if conditions:
        result = await session.execute(
            sa_select(User).where(
                or_(*conditions),
                User.is_banned == False,
                User.is_bot_blocked == False,
            )
        )
        users = list(result.scalars().all())

    return users


@admin_router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Show broadcast type selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    # Clear any stale state from previous broadcast flows
    await state.clear()

    from app.admin.keyboards.inline import broadcast_type_menu

    text = "📢 Рассылка сообщения\n\n"
    text += "Выберите тип рассылки:"

    await callback.message.edit_text(text, reply_markup=broadcast_type_menu())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_type:simple")
async def start_simple_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start simple broadcast (legacy flow)."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    # Set state to prevent conflict with advanced broadcast filter handler
    await state.set_state(Broadcast.waiting_for_filter)

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    text = "📢 Простая рассылка\n\n"
    text += "Выберите целевую аудиторию:"

    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Всем пользователям", callback_data="admin:broadcast_filter:all")
    builder.button(text="💎 С активной подпиской", callback_data="admin:broadcast_filter:subscribed")
    builder.button(text="🆓 Без подписки", callback_data="admin:broadcast_filter:no_subscription")
    builder.button(text="🎯 Выборочно (по ID/username)", callback_data="admin:broadcast_filter:specific")
    builder.button(text="🧪 Тестовая отправка", callback_data="admin:broadcast_filter:test")
    builder.button(text="🔙 Назад", callback_data="admin:broadcast")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:broadcast_filter:"), StateFilter(Broadcast.waiting_for_filter))
async def broadcast_filter_selected(callback: CallbackQuery, state: FSMContext):
    """Start broadcast with selected filter (simple broadcast only)."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    filter_type = callback.data.split(":")[-1]
    await state.update_data(broadcast_filter=filter_type)

    # Handle specific users - ask for user list first
    if filter_type == "specific":
        await state.set_state(BroadcastTargeted.waiting_for_users)
        await callback.message.edit_text(
            "🎯 Выборочная рассылка\n\n"
            "Введите список пользователей через запятую, пробел или новую строку.\n\n"
            "Поддерживаемые форматы:\n"
            "• Telegram ID: 123456789\n"
            "• Username: @username\n"
            "• Смешанный: 123456789, @user1, @user2\n\n"
            "Пример:\n"
            "123456789, @user1, @user2",
            reply_markup=cancel_keyboard()
        )
        await callback.answer()
        return

    # Handle test - proceed to message input
    if filter_type == "test":
        admin_count = len(settings.admin_user_ids)
        await state.set_state(Broadcast.waiting_for_message)
        await callback.message.edit_text(
            f"🧪 Тестовая рассылка\n\n"
            f"Сообщение будет отправлено только администраторам ({admin_count} чел.)\n\n"
            f"Введите текст сообщения:",
            reply_markup=cancel_keyboard()
        )
        await callback.answer()
        return

    await state.set_state(Broadcast.waiting_for_message)

    filter_names = {
        "all": "всем пользователям",
        "subscribed": "пользователям с активной подпиской",
        "no_subscription": "пользователям без подписки",
    }

    await callback.message.edit_text(
        f"📢 Рассылка сообщения\n\n"
        f"Целевая аудитория: {filter_names.get(filter_type, 'всем')}\n\n"
        f"Введите текст сообщения:\n\n"
        f"⚠️ Будьте осторожны! Сообщение будет отправлено выбранной аудитории.",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(Broadcast.waiting_for_message))
async def process_broadcast_message(message: Message, state: FSMContext):
    """Process and send broadcast message."""
    if not is_admin(message.from_user.id):
        return

    from app.database.database import async_session_maker
    from app.database.models import User
    from app.admin.services import send_broadcast_message
    from sqlalchemy import select
    from aiogram import Bot

    broadcast_text = message.text
    data = await state.get_data()
    filter_type = data.get('broadcast_filter', 'all')

    try:
        # Get main bot instance - without default parse_mode to avoid Markdown issues
        from app.core.config import settings
        from aiogram.client.default import DefaultBotProperties
        main_bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties())

        async with async_session_maker() as session:
            # Build query based on filter (exclude blocked users)
            query = select(User).where(User.is_banned == False, User.is_bot_blocked == False)

            if filter_type == "test":
                # Send to admin IDs only
                result = await session.execute(
                    select(User).where(User.telegram_id.in_(settings.admin_user_ids))
                )
                users = list(result.scalars().all())
            elif filter_type == "specific":
                specific_users = data.get("specific_users", [])
                users = await _resolve_specific_users(session, specific_users)
            elif filter_type == "subscribed":
                # Get users with active subscription
                users_result = await session.execute(query)
                all_users = users_result.scalars().all()
                users = [u for u in all_users if u.get_active_subscription() is not None]
            elif filter_type == "no_subscription":
                # Get users without active subscription
                users_result = await session.execute(query)
                all_users = users_result.scalars().all()
                users = [u for u in all_users if u.get_active_subscription() is None]
            else:
                # All users
                result = await session.execute(query)
                users = result.scalars().all()

            total_users = len(users)
            success_count = 0
            failed_count = 0
            errors = []  # Store error details

            # Send initial status
            status_msg = await message.answer(
                f"📤 Начинаю рассылку...\n\n"
                f"👥 Всего пользователей: {total_users}\n"
                f"✅ Отправлено: 0\n"
                f"❌ Ошибок: 0"
            )

            # Send messages
            blocked_users = []
            for i, user in enumerate(users, 1):
                try:
                    await send_broadcast_message(
                        bot=main_bot,
                        chat_id=user.telegram_id,
                        text=broadcast_text,
                    )
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    # Mark user as blocked if they blocked the bot or deactivated
                    if "bot was blocked by the user" in error_msg or "user is deactivated" in error_msg:
                        blocked_users.append(user.id)
                    errors.append(f"User {user.telegram_id}: {error_msg[:50]}")
                    logger.error(
                        "broadcast_send_error",
                        user_id=user.telegram_id,
                        error=error_msg
                    )

                # Update status every 10 messages
                if i % 10 == 0 or i == total_users:
                    try:
                        await status_msg.edit_text(
                            f"📤 Рассылка в процессе...\n\n"
                            f"👥 Всего пользователей: {total_users}\n"
                            f"✅ Отправлено: {success_count}\n"
                            f"❌ Ошибок: {failed_count}\n"
                            f"📊 Прогресс: {i}/{total_users}"
                        )
                    except:
                        pass

            # Mark blocked users in database
            if blocked_users:
                for uid in blocked_users:
                    blocked_user_result = await session.execute(
                        select(User).where(User.id == uid)
                    )
                    blocked_user = blocked_user_result.scalar_one_or_none()
                    if blocked_user:
                        blocked_user.is_bot_blocked = True
                await session.commit()
                logger.info(
                    "broadcast_blocked_users_marked",
                    count=len(blocked_users)
                )

            # Final status with error details
            final_text = f"✅ Рассылка завершена!\n\n"
            final_text += f"👥 Всего пользователей: {total_users}\n"
            final_text += f"✅ Успешно отправлено: {success_count}\n"
            final_text += f"❌ Ошибок: {failed_count}"

            if errors and len(errors) <= 10:
                final_text += "\n\n❌ Детали ошибок:\n"
                for error in errors[:10]:
                    final_text += f"  • {error}\n"
            elif errors:
                final_text += f"\n\n❌ Показаны первые 10 из {len(errors)} ошибок:\n"
                for error in errors[:10]:
                    final_text += f"  • {error}\n"

            await status_msg.edit_text(final_text, reply_markup=back_keyboard())

            logger.info(
                "admin_broadcast_complete",
                admin_id=message.from_user.id,
                filter=filter_type,
                total=total_users,
                success=success_count,
                failed=failed_count
            )

        await main_bot.session.close()

    except Exception as e:
        logger.error("admin_broadcast_error", error=str(e))
        await message.answer(f"❌ Ошибка рассылки: {str(e)}", reply_markup=back_keyboard())

    await state.clear()


# ==================== BROADCAST WITH BUTTONS ====================


@admin_router.callback_query(F.data == "admin:broadcast_type:advanced")
async def start_advanced_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start advanced broadcast with buttons."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(BroadcastWithButtons.waiting_for_text)

    text = "📢 Рассылка с кнопками\n\n"
    text += "Шаг 1/5: Введите текст сообщения:"

    await callback.message.edit_text(text, reply_markup=cancel_keyboard())
    await callback.answer()


@admin_router.message(StateFilter(BroadcastWithButtons.waiting_for_text))
async def process_broadcast_text(message: Message, state: FSMContext):
    """Process broadcast text input."""
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if not text:
        await message.answer("❌ Текст не может быть пустым. Попробуйте снова:")
        return

    # Save text to state
    await state.update_data(text=text)
    await state.set_state(BroadcastWithButtons.waiting_for_image)

    from app.admin.keyboards.inline import skip_image_keyboard

    await message.answer(
        f"✅ Текст сохранён ({len(text)} символов)\n\n"
        f"Шаг 2/5: Отправьте фото для сообщения\n"
        f"или нажмите [Пропустить]",
        reply_markup=skip_image_keyboard()
    )


@admin_router.message(StateFilter(BroadcastWithButtons.waiting_for_image), F.photo)
async def process_broadcast_image(message: Message, state: FSMContext):
    """Process broadcast image."""
    if not is_admin(message.from_user.id):
        return

    # Get largest photo
    photo = message.photo[-1]
    await state.update_data(image_file_id=photo.file_id)
    await state.set_state(BroadcastWithButtons.waiting_for_buttons)

    from app.admin.keyboards.inline import button_input_menu

    await message.answer(
        f"✅ Фото прикреплено\n\n"
        f"Шаг 3/5: Добавьте кнопки к сообщению",
        reply_markup=button_input_menu()
    )


@admin_router.callback_query(F.data == "admin:broadcast_skip_image")
async def skip_broadcast_image(callback: CallbackQuery, state: FSMContext):
    """Skip image attachment."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.update_data(image_file_id=None)
    await state.set_state(BroadcastWithButtons.waiting_for_buttons)

    from app.admin.keyboards.inline import button_input_menu

    await callback.message.edit_text(
        f"⏭ Фото пропущено\n\n"
        f"Шаг 3/5: Добавьте кнопки к сообщению",
        reply_markup=button_input_menu()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_preset_buttons")
async def show_preset_button_categories(callback: CallbackQuery, state: FSMContext):
    """Show preset button categories."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.admin.keyboards.inline import preset_button_categories

    text = "📱 Выберите категорию кнопок:"

    await callback.message.edit_text(text, reply_markup=preset_button_categories())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:broadcast_category:"))
async def show_category_buttons(callback: CallbackQuery, state: FSMContext):
    """Show buttons for selected category."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    category_key = callback.data.split(":")[-1]

    from app.admin.keyboards.inline import preset_button_list
    from app.admin.config import PRESET_BUTTONS

    category = PRESET_BUTTONS.get(category_key, {})
    text = f"{category.get('name', 'Кнопки')}\n\n"
    text += f"{category.get('description', '')}\n\n"
    text += "Выберите кнопку:"

    await callback.message.edit_text(text, reply_markup=preset_button_list(category_key))
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:broadcast_select_btn:"))
async def select_preset_button(callback: CallbackQuery, state: FSMContext):
    """Process preset button selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    parts = callback.data.split(":")
    category_key = parts[-2]
    button_index = int(parts[-1])

    from app.admin.config import get_category_buttons
    from app.admin.keyboards.inline import button_text_choice

    buttons = get_category_buttons(category_key)
    if button_index >= len(buttons):
        await callback.answer("❌ Кнопка не найдена")
        return

    selected_button = buttons[button_index]

    # Save to state temporarily
    await state.update_data(
        pending_button=selected_button,
        pending_category=category_key,
        pending_index=button_index
    )

    default_text = selected_button.get("text", "")
    text = f"✅ Выбрана кнопка: {default_text}\n\n"
    text += f"Стандартный текст: \"{default_text}\"\n\n"
    text += "Использовать стандартный текст или ввести свой?"

    await callback.message.edit_text(text, reply_markup=button_text_choice(default_text))
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_use_default_text")
async def use_default_button_text(callback: CallbackQuery, state: FSMContext):
    """Use default text for button."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    data = await state.get_data()
    pending_button = data.get("pending_button")

    if not pending_button:
        await callback.answer("❌ Ошибка: кнопка не найдена")
        return

    # Add button to list
    buttons = data.get("buttons", [])
    buttons.append({
        "text": pending_button["text"],
        "callback_data": pending_button["callback_data"]
    })

    # Update state with both buttons and clear pending_button in one call
    await state.update_data(buttons=buttons, pending_button=None)

    from app.admin.keyboards.inline import add_more_buttons_keyboard

    button_count = len(buttons)
    text = f"✅ Кнопка {button_count} добавлена: \"{pending_button['text']}\"\n\n"
    text += f"Текущие кнопки ({button_count}/8):\n"
    for idx, btn in enumerate(buttons, 1):
        text += f"{idx}. {btn['text']}\n"

    logger.info(
        "broadcast_button_added_default",
        admin_id=callback.from_user.id,
        button_text=pending_button["text"],
        callback_data=pending_button["callback_data"],
        total_buttons=button_count,
        buttons_list=[b["text"] for b in buttons]
    )

    await callback.message.edit_text(text, reply_markup=add_more_buttons_keyboard(button_count))
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_custom_text")
async def request_custom_button_text(callback: CallbackQuery, state: FSMContext):
    """Request custom text for button."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(BroadcastWithButtons.waiting_for_buttons)
    await state.update_data(awaiting_custom_text=True)

    text = "✏️ Введите текст кнопки:"

    await callback.message.edit_text(text, reply_markup=cancel_keyboard())
    await callback.answer()


@admin_router.message(StateFilter(BroadcastWithButtons.waiting_for_buttons))
async def process_button_input(message: Message, state: FSMContext):
    """Process button input (manual or custom text)."""
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    buttons = data.get("buttons", [])

    # Check if max buttons reached
    if len(buttons) >= 8:
        await message.answer("❌ Максимум 8 кнопок. Нажмите [Готово] для продолжения.")
        return

    # Check if we're awaiting custom text for preset button
    if data.get("awaiting_custom_text"):
        pending_button = data.get("pending_button")
        if not pending_button:
            await message.answer("❌ Ошибка: кнопка не найдена")
            return

        custom_text = message.text.strip()
        if not custom_text:
            await message.answer("❌ Текст не может быть пустым")
            return

        # Add button with custom text
        buttons.append({
            "text": custom_text,
            "callback_data": pending_button["callback_data"]
        })
        await state.update_data(buttons=buttons, awaiting_custom_text=False, pending_button=None)

        from app.admin.keyboards.inline import add_more_buttons_keyboard

        button_count = len(buttons)
        text = f"✅ Кнопка {button_count} добавлена: \"{custom_text}\"\n\n"
        text += f"Текущие кнопки ({button_count}/8):\n"
        for idx, btn in enumerate(buttons, 1):
            text += f"{idx}. {btn['text']}\n"

        logger.info(
            "broadcast_button_added_custom",
            admin_id=message.from_user.id,
            button_text=custom_text,
            callback_data=pending_button["callback_data"],
            total_buttons=button_count,
            buttons_list=[b["text"] for b in buttons]
        )

        await message.answer(text, reply_markup=add_more_buttons_keyboard(button_count))
        return

    # Manual input format: "Text | callback_data" or "Text | copy:текст для копирования"
    text = message.text.strip()
    if "|" not in text:
        await message.answer(
            "❌ Неверный формат. Используйте:\n"
            "Текст кнопки | callback_data\n\n"
            "Пример:\n"
            "Попробовать GPT 4o | bot.start_chatgpt_dialog_325\n\n"
            "Для кнопки копирования:\n"
            "📋 Скопировать | copy:текст для копирования"
        )
        return

    button_text, action_data = text.split("|", 1)
    button_text = button_text.strip()
    action_data = action_data.strip()

    if not button_text or not action_data:
        await message.answer("❌ Текст и действие не могут быть пустыми")
        return

    # Check if it's a copy_text button
    if action_data.startswith("copy:"):
        copy_text = action_data[5:].strip()
        if not copy_text:
            await message.answer("❌ Текст для копирования не может быть пустым")
            return
        buttons.append({"text": button_text, "copy_text": copy_text})
    else:
        callback_data = action_data
        # Validate callback_data
        if not callback_data.replace("_", "").replace(".", "").replace(":", "").replace("#", "").isalnum():
            await message.answer("❌ callback_data содержит недопустимые символы")
            return
        buttons.append({"text": button_text, "callback_data": callback_data})
    await state.update_data(buttons=buttons)

    from app.admin.keyboards.inline import add_more_buttons_keyboard

    button_count = len(buttons)
    text = f"✅ Кнопка {button_count} добавлена: \"{button_text}\"\n\n"
    text += f"Текущие кнопки ({button_count}/8):\n"
    for idx, btn in enumerate(buttons, 1):
        text += f"{idx}. {btn['text']}\n"

    await message.answer(text, reply_markup=add_more_buttons_keyboard(button_count))


@admin_router.callback_query(F.data == "admin:broadcast_no_buttons")
async def broadcast_no_buttons(callback: CallbackQuery, state: FSMContext):
    """Continue without buttons."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.update_data(buttons=[])
    await state.set_state(BroadcastWithButtons.waiting_for_filter)

    from app.admin.keyboards.inline import broadcast_filter_keyboard

    text = "📊 Шаг 4/5: Выберите получателей"

    await callback.message.edit_text(text, reply_markup=broadcast_filter_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_button_input")
async def back_to_button_input(callback: CallbackQuery, state: FSMContext):
    """Go back to button input menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.admin.keyboards.inline import button_input_menu

    await callback.message.edit_text(
        "Шаг 3/5: Добавьте кнопки к сообщению",
        reply_markup=button_input_menu()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_add_more")
async def add_more_buttons(callback: CallbackQuery, state: FSMContext):
    """Add more buttons."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.admin.keyboards.inline import button_input_menu

    await callback.message.edit_text(
        "Добавьте ещё кнопку:",
        reply_markup=button_input_menu()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_buttons_done")
async def broadcast_buttons_done(callback: CallbackQuery, state: FSMContext):
    """Finish adding buttons, proceed to filter selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    data = await state.get_data()
    buttons = data.get("buttons", [])

    logger.info(
        "broadcast_buttons_done",
        admin_id=callback.from_user.id,
        buttons_count=len(buttons),
        buttons_list=[b["text"] for b in buttons] if buttons else []
    )

    if not buttons:
        await callback.answer("❌ Добавьте хотя бы одну кнопку или выберите [Без кнопок]")
        return

    await state.set_state(BroadcastWithButtons.waiting_for_filter)

    from app.admin.keyboards.inline import broadcast_filter_keyboard

    text = f"✅ Кнопки добавлены ({len(buttons)})\n\n"
    text += "📊 Шаг 4/5: Выберите получателей"

    await callback.message.edit_text(text, reply_markup=broadcast_filter_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:broadcast_filter:"), StateFilter(BroadcastWithButtons.waiting_for_filter))
async def select_broadcast_filter(callback: CallbackQuery, state: FSMContext):
    """Select recipient filter for advanced broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    filter_type = callback.data.split(":")[-1]
    await state.update_data(filter_type=filter_type)

    # Handle specific users - ask for user list
    if filter_type == "specific":
        await state.update_data(awaiting_specific_users=True)
        await callback.message.edit_text(
            "🎯 Выборочная отправка\n\n"
            "Введите список пользователей через запятую:\n"
            "• Telegram ID: 123456789\n"
            "• Username: @username\n\n"
            "Пример: 123456789, @user1, @user2",
            reply_markup=cancel_keyboard()
        )
        await callback.answer()
        return

    # Handle test filter
    if filter_type == "test":
        await state.set_state(BroadcastWithButtons.waiting_for_confirmation)
        from app.admin.keyboards.inline import broadcast_confirmation_keyboard

        admin_count = len(settings.admin_user_ids)
        data = await state.get_data()
        text = data.get("text", "")
        buttons = data.get("buttons", [])
        image_file_id = data.get("image_file_id")

        preview = (
            f"📋 Шаг 5/5: Превью (ТЕСТОВАЯ РАССЫЛКА)\n\n"
            f"─────────────────\n"
            f"{text}\n"
            f"─────────────────\n\n"
            f"🧪 Тестовая отправка: {admin_count} админам\n"
            f"📸 Фото: {'Да' if image_file_id else 'Нет'}\n"
            f"🔘 Кнопок: {len(buttons)}"
        )

        await callback.message.edit_text(preview, reply_markup=broadcast_confirmation_keyboard())
        await callback.answer()
        return

    from app.database.database import async_session_maker
    from app.admin.services import get_recipients_count
    from app.admin.keyboards.inline import broadcast_confirmation_keyboard, build_user_broadcast_keyboard

    await state.set_state(BroadcastWithButtons.waiting_for_confirmation)

    # Get recipient count
    async with async_session_maker() as session:
        recipient_count = await get_recipients_count(session, filter_type)

    # Get state data
    data = await state.get_data()
    text = data.get("text", "")
    image_file_id = data.get("image_file_id")
    buttons = data.get("buttons", [])

    logger.info(
        "broadcast_preview",
        admin_id=callback.from_user.id,
        filter_type=filter_type,
        buttons_count=len(buttons),
        buttons_list=[b["text"] for b in buttons] if buttons else [],
        has_image=bool(image_file_id)
    )

    filter_names = {
        "all": "Все пользователи",
        "subscribed": "С подпиской",
        "free": "Без подписки",
    }

    # Send preview message
    preview_text = f"📋 Шаг 5/5: Превью сообщения\n\n"
    preview_text += "─────────────────\n"
    preview_text += f"{text}\n"
    preview_text += "─────────────────\n\n"
    preview_text += f"📊 Будет отправлено: ~{recipient_count} пользователям\n"
    preview_text += f"🎯 Фильтр: {filter_names.get(filter_type, 'Неизвестно')}\n"
    preview_text += f"📸 Фото: {'Да' if image_file_id else 'Нет'}\n"
    preview_text += f"🔘 Кнопок: {len(buttons)}\n\n"

    # Send actual preview
    try:
        keyboard = build_user_broadcast_keyboard(buttons) if buttons else None

        if image_file_id:
            await callback.message.answer_photo(
                photo=image_file_id,
                caption=text,
                reply_markup=keyboard
            )
        else:
            await callback.message.answer(
                text=text,
                reply_markup=keyboard
            )

        await callback.message.answer(
            preview_text,
            reply_markup=broadcast_confirmation_keyboard()
        )
    except Exception as e:
        logger.error("broadcast_preview_error", error=str(e))
        await callback.message.answer(
            f"❌ Ошибка предпросмотра: {str(e)}",
            reply_markup=cancel_keyboard()
        )

    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast_confirm_send")
async def confirm_broadcast_send(callback: CallbackQuery, state: FSMContext):
    """Confirm and send broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    # Answer callback immediately to prevent "query is too old" error
    # (broadcast sending takes longer than Telegram's 30s callback timeout)
    await callback.answer()

    from app.database.database import async_session_maker
    from app.admin.services import (
        send_broadcast_message,
        create_broadcast_message,
        get_recipients,
        update_broadcast_stats
    )
    from app.admin.keyboards.inline import build_user_broadcast_keyboard
    from aiogram import Bot
    from app.database.models import User
    from sqlalchemy import select

    data = await state.get_data()
    text = data.get("text", "")
    image_file_id = data.get("image_file_id")
    buttons = data.get("buttons", [])
    filter_type = data.get("filter_type", "all")

    # Resolve admin Telegram ID to internal user ID
    admin_telegram_id = callback.from_user.id
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User.id).where(User.telegram_id == admin_telegram_id)
            )
            internal_admin_id = result.scalar_one_or_none()
    except Exception as e:
        logger.error("broadcast_admin_resolve_error", telegram_id=admin_telegram_id, error=str(e))
        internal_admin_id = None

    logger.info(
        "broadcast_confirm_send",
        admin_telegram_id=admin_telegram_id,
        admin_internal_id=internal_admin_id,
        filter_type=filter_type,
        buttons_count=len(buttons),
        buttons_list=[b["text"] for b in buttons] if buttons else [],
        has_image=bool(image_file_id),
        text_length=len(text)
    )

    try:
        # Create broadcast record
        async with async_session_maker() as session:
            broadcast = await create_broadcast_message(
                session=session,
                admin_id=internal_admin_id,
                text=text,
                image_file_id=image_file_id,
                buttons=buttons,
                filter_type=filter_type
            )

            # Get recipients based on filter type
            if filter_type == "test":
                from sqlalchemy import select as sa_sel
                r = await session.execute(
                    sa_sel(User).where(User.telegram_id.in_(settings.admin_user_ids))
                )
                recipients = list(r.scalars().all())
            elif filter_type == "specific":
                specific_users = data.get("specific_users", [])
                recipients = await _resolve_specific_users(session, specific_users)
            else:
                recipients = await get_recipients(session, filter_type)

        # Send broadcast - create bot without default parse_mode to avoid Markdown issues
        from aiogram.client.default import DefaultBotProperties
        from aiogram.types import BufferedInputFile
        main_bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties())
        keyboard = build_user_broadcast_keyboard(buttons) if buttons else None

        # Re-upload photo from admin bot to main bot if needed
        # (file_id is bot-specific in Telegram and cannot be shared between bots)
        main_bot_photo = None
        if image_file_id:
            try:
                admin_bot = Bot(token=settings.telegram_admin_bot_token, default=DefaultBotProperties())
                file = await admin_bot.get_file(image_file_id)
                photo_bytes = await admin_bot.download_file(file.file_path)
                main_bot_photo = BufferedInputFile(
                    file=photo_bytes.read(),
                    filename="broadcast_photo.jpg"
                )
                await admin_bot.session.close()
                logger.info("broadcast_photo_downloaded", file_id=image_file_id)
            except Exception as e:
                logger.error("broadcast_photo_download_error", error=str(e))
                main_bot_photo = None

        total_users = len(recipients)
        success_count = 0
        error_count = 0
        blocked_count = 0

        status_msg = await callback.message.answer(
            f"⏳ Отправка... 0/{total_users}"
        )

        blocked_user_ids = []
        for i, user in enumerate(recipients, 1):
            try:
                result = await send_broadcast_message(
                    bot=main_bot,
                    chat_id=user.telegram_id,
                    text=text,
                    photo=main_bot_photo if main_bot_photo else None,
                    keyboard=keyboard,
                )
                # After first successful photo send, use the returned file_id
                # for faster sending (avoids re-uploading the file each time)
                if main_bot_photo and isinstance(main_bot_photo, BufferedInputFile) and result:
                    try:
                        new_file_id = result.photo[-1].file_id
                        main_bot_photo = new_file_id
                        logger.info("broadcast_photo_cached", new_file_id=new_file_id)
                    except (AttributeError, IndexError):
                        pass
                success_count += 1
            except Exception as e:
                error_msg = str(e)
                if "bot was blocked by the user" in error_msg or "user is deactivated" in error_msg:
                    blocked_count += 1
                    blocked_user_ids.append(user.id)
                else:
                    error_count += 1
                    logger.error("broadcast_send_error", user_id=user.telegram_id, error=error_msg)

            # Update progress every 100 messages
            if i % 100 == 0 or i == total_users:
                try:
                    await status_msg.edit_text(
                        f"⏳ Отправка... {i}/{total_users}\n"
                        f"✅ Успешно: {success_count}\n"
                        f"🚫 Заблокировали: {blocked_count}\n"
                        f"❌ Ошибок: {error_count}"
                    )
                except:
                    pass

        # Mark blocked users in database
        if blocked_user_ids:
            async with async_session_maker() as session:
                for uid in blocked_user_ids:
                    blocked_user_result = await session.execute(
                        select(User).where(User.id == uid)
                    )
                    blocked_user = blocked_user_result.scalar_one_or_none()
                    if blocked_user:
                        blocked_user.is_bot_blocked = True
                await session.commit()
                logger.info(
                    "broadcast_blocked_users_marked",
                    count=len(blocked_user_ids)
                )

        # Update statistics
        async with async_session_maker() as session:
            await update_broadcast_stats(
                session=session,
                broadcast_id=broadcast.id,
                sent_count=success_count,
                error_count=error_count + blocked_count
            )

        # Final status
        final_text = f"✅ Рассылка завершена!\n\n"
        final_text += f"📊 Статистика:\n"
        final_text += f"  • Отправлено: {success_count}\n"
        if blocked_count > 0:
            final_text += f"  • Заблокировали бота: {blocked_count}\n"
        if error_count > 0:
            final_text += f"  • Ошибки: {error_count}\n"
        final_text += f"  • Успешность: {success_count*100//total_users if total_users > 0 else 0}%\n\n"
        final_text += f"🔗 ID рассылки: #{broadcast.id}\n"
        final_text += f"Статистика доступна в разделе [📊 Статистика]"

        await status_msg.edit_text(final_text, reply_markup=back_keyboard())

        await main_bot.session.close()

        logger.info(
            "admin_broadcast_with_buttons_complete",
            admin_id=callback.from_user.id,
            broadcast_id=broadcast.id,
            filter=filter_type,
            total=total_users,
            success=success_count,
            failed=error_count,
            buttons_count=len(buttons)
        )

    except Exception as e:
        logger.error("admin_broadcast_with_buttons_error", error=str(e))
        await callback.message.answer(
            f"❌ Ошибка рассылки: {str(e)}",
            reply_markup=back_keyboard()
        )

    await state.clear()


# ==================== BROADCAST STATISTICS ====================


@admin_router.callback_query(F.data == "admin:broadcast_stats")
async def show_broadcast_stats(callback: CallbackQuery):
    """Show broadcast statistics list."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await show_broadcast_stats_page(callback, page=0)


@admin_router.callback_query(F.data.startswith("admin:broadcast_stats_page:"))
async def show_broadcast_stats_page_handler(callback: CallbackQuery):
    """Show broadcast statistics page."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    page = int(callback.data.split(":")[-1])
    await show_broadcast_stats_page(callback, page=page)


async def show_broadcast_stats_page(callback: CallbackQuery, page: int = 0):
    """Show broadcast statistics for given page."""
    from app.database.database import async_session_maker
    from app.admin.services import get_recent_broadcasts
    from app.admin.keyboards.inline import broadcast_stats_keyboard
    from sqlalchemy import select, func
    from app.database.models.broadcast import BroadcastClick

    page_size = 10

    async with async_session_maker() as session:
        broadcasts, total_count = await get_recent_broadcasts(session, page=page, page_size=page_size)

        if not broadcasts:
            await callback.message.edit_text(
                "📊 Статистика рассылок\n\n"
                "Пока нет рассылок с кнопками.",
                reply_markup=back_keyboard()
            )
            await callback.answer()
            return

        text = "📊 История рассылок с кнопками\n\n"

        for broadcast in broadcasts:
            # Get click stats
            result = await session.execute(
                select(func.count(BroadcastClick.id)).where(
                    BroadcastClick.broadcast_id == broadcast.id
                )
            )
            total_clicks = result.scalar() or 0

            result = await session.execute(
                select(func.count(func.distinct(BroadcastClick.user_id))).where(
                    BroadcastClick.broadcast_id == broadcast.id
                )
            )
            unique_clicks = result.scalar() or 0

            # Format date
            date_str = broadcast.created_at.strftime("%d.%m.%Y %H:%M")

            # Truncate text
            msg_text = broadcast.text[:50] + "..." if len(broadcast.text) > 50 else broadcast.text
            msg_text = msg_text.replace("\n", " ")

            # Click rate
            click_rate = (unique_clicks * 100 // broadcast.sent_count) if broadcast.sent_count > 0 else 0

            text += f"#{broadcast.id} | {date_str}\n"
            text += f"   \"{msg_text}\"\n"
            text += f"   📤 {broadcast.sent_count} | 👆 {unique_clicks} ({click_rate}%)\n"
            text += f"   🔘 {len(broadcast.buttons)} кнопок\n\n"

        total_pages = (total_count + page_size - 1) // page_size
        text += f"\nСтраница {page + 1} из {total_pages}"

    await callback.message.edit_text(
        text,
        reply_markup=broadcast_stats_keyboard(page=page, total_pages=total_pages)
    )
    await callback.answer()


# ==================== CHANNEL SUBSCRIPTION BONUS ====================


@admin_router.callback_query(F.data == "admin:channel_bonus_menu")
async def show_channel_bonus_menu(callback: CallbackQuery, state: FSMContext):
    """Show channel bonus management menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.clear()
    from app.admin.keyboards.inline import channel_bonus_menu

    await callback.message.edit_text(
        "📢 Бонус за подписку на канал/группу\n\n"
        "Создайте бонус за подписку или управляйте существующими.\n"
        "При рассылке пользователи получат кнопку «Проверить подписку»\n"
        "и после проверки — бонусные токены.\n\n"
        "Как это работает:\n"
        "1. Создайте бонус (укажите канал и кол-во токенов)\n"
        "2. Запустите рассылку с бонусом (из меню рассылки)\n"
        "3. Пользователь подписывается на канал\n"
        "4. Нажимает «Проверить подписку» — получает токены",
        reply_markup=channel_bonus_menu()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin:channel_bonus_create")
async def start_channel_bonus_create(callback: CallbackQuery, state: FSMContext):
    """Start creating a new channel subscription bonus."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(ChannelBonusSetup.waiting_for_channel)

    await callback.message.edit_text(
        "➕ Создание бонуса за подписку\n\n"
        "Шаг 1/3: Укажите канал или группу\n\n"
        "Отправьте ссылку на канал/группу в одном из форматов:\n"
        "• @username (например: @mychannel)\n"
        "• https://t.me/mychannel\n"
        "• Числовой ID канала (например: -1001234567890)\n\n"
        "⚠️ Важно: бот должен быть администратором канала/группы,\n"
        "чтобы проверять подписку пользователей!",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(ChannelBonusSetup.waiting_for_channel))
async def process_channel_bonus_channel(message: Message, state: FSMContext):
    """Process channel input for bonus setup."""
    if not is_admin(message.from_user.id):
        return

    from app.core.config import settings
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties

    channel_input = message.text.strip()

    # Parse channel input
    channel_id = None
    channel_username = None

    if channel_input.startswith("https://t.me/"):
        channel_username = channel_input.replace("https://t.me/", "").strip("/")
        channel_input = f"@{channel_username}"
    elif channel_input.startswith("@"):
        channel_username = channel_input[1:]
    elif channel_input.lstrip("-").isdigit():
        channel_id = int(channel_input)
    else:
        await message.answer(
            "❌ Неверный формат. Укажите @username, ссылку t.me или числовой ID.\n\n"
            "Примеры:\n"
            "• @mychannel\n"
            "• https://t.me/mychannel\n"
            "• -1001234567890",
            reply_markup=cancel_keyboard()
        )
        return

    # Verify channel with the main bot
    main_bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties())
    try:
        chat_identifier = channel_id if channel_id else channel_input
        chat = await main_bot.get_chat(chat_identifier)
        channel_id = chat.id
        channel_username = chat.username
        channel_title = chat.title or chat.full_name or str(channel_id)

        # Check if bot is admin
        bot_member = await main_bot.get_chat_member(chat.id, (await main_bot.get_me()).id)
        if bot_member.status not in ("administrator", "creator"):
            await message.answer(
                f"⚠️ Бот не является администратором в «{channel_title}».\n\n"
                "Добавьте основного бота (@ваш_бот) в администраторы канала/группы,\n"
                "чтобы он мог проверять подписку пользователей.\n\n"
                "После добавления — отправьте ссылку ещё раз.",
                reply_markup=cancel_keyboard()
            )
            await main_bot.session.close()
            return
    except Exception as e:
        await message.answer(
            f"❌ Не удалось найти канал/группу.\n\n"
            f"Ошибка: {str(e)[:200]}\n\n"
            "Убедитесь, что:\n"
            "1. Канал/группа существует\n"
            "2. Основной бот добавлен в канал/группу\n"
            "3. Указан правильный формат",
            reply_markup=cancel_keyboard()
        )
        await main_bot.session.close()
        return

    await main_bot.session.close()

    await state.update_data(
        channel_id=channel_id,
        channel_username=channel_username,
        channel_title=channel_title,
    )
    await state.set_state(ChannelBonusSetup.waiting_for_tokens)

    await message.answer(
        f"✅ Канал найден: {channel_title}"
        + (f" (@{channel_username})" if channel_username else "")
        + f"\nID: {channel_id}\n\n"
        "Шаг 2/3: Сколько токенов начислить за подписку?\n\n"
        "Введите число (по умолчанию: 1000):\n"
        "Примеры: 500, 1000, 5000",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(StateFilter(ChannelBonusSetup.waiting_for_tokens))
async def process_channel_bonus_tokens(message: Message, state: FSMContext):
    """Process token amount for channel bonus."""
    if not is_admin(message.from_user.id):
        return

    try:
        tokens = int(message.text.strip())
        if tokens < 1 or tokens > 10000000:
            await message.answer("❌ Введите число от 1 до 10 000 000.", reply_markup=cancel_keyboard())
            return
    except ValueError:
        await message.answer("❌ Введите целое число.", reply_markup=cancel_keyboard())
        return

    await state.update_data(bonus_tokens=tokens)
    await state.set_state(ChannelBonusSetup.waiting_for_welcome_message)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Использовать стандартное", callback_data="admin:cb_default_welcome")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")
    builder.adjust(1)

    await message.answer(
        f"✅ Бонус: {tokens:,} токенов\n\n"
        "Шаг 3/3: Текст сообщения при получении бонуса\n\n"
        "Введите текст, который увидит пользователь после проверки подписки.\n"
        "Или нажмите «Использовать стандартное».\n\n"
        "Стандартное сообщение:\n"
        f"«Поздравляем! Вам начислено {tokens:,} бонусных токенов\n"
        "за подписку на канал!»",
        reply_markup=builder.as_markup()
    )


@admin_router.callback_query(F.data == "admin:cb_default_welcome")
async def channel_bonus_default_welcome(callback: CallbackQuery, state: FSMContext):
    """Use default welcome message for channel bonus."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    data = await state.get_data()
    tokens = data.get("bonus_tokens", 1000)
    welcome = f"🎉 Поздравляем! Вам начислено {tokens:,} бонусных токенов за подписку на канал!"

    await state.update_data(welcome_message=welcome)
    await _save_channel_bonus(callback.message, state)
    await callback.answer()


@admin_router.message(StateFilter(ChannelBonusSetup.waiting_for_welcome_message))
async def process_channel_bonus_welcome(message: Message, state: FSMContext):
    """Process custom welcome message for channel bonus."""
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if not text:
        await message.answer("❌ Текст не может быть пустым.", reply_markup=cancel_keyboard())
        return

    await state.update_data(welcome_message=text)
    await _save_channel_bonus(message, state)


async def _save_channel_bonus(message_or_callback, state: FSMContext):
    """Save channel bonus to database."""
    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService

    data = await state.get_data()

    # Determine the reply target
    if hasattr(message_or_callback, 'answer'):
        reply = message_or_callback.answer
    else:
        reply = message_or_callback.answer

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonus = await service.create_bonus(
            channel_id=data["channel_id"],
            bonus_tokens=data.get("bonus_tokens", 1000),
            channel_username=data.get("channel_username"),
            channel_title=data.get("channel_title"),
            welcome_message=data.get("welcome_message"),
        )

    from app.admin.keyboards.inline import channel_bonus_menu

    text = (
        f"✅ Бонус #{bonus.id} создан!\n\n"
        f"📢 Канал: {bonus.channel_title or 'N/A'}"
        + (f" (@{bonus.channel_username})" if bonus.channel_username else "")
        + f"\n💰 Бонус: {bonus.bonus_tokens:,} токенов\n"
        f"✅ Статус: активен\n\n"
        "Теперь запустите рассылку с бонусом через меню:\n"
        "📢 Рассылка → Рассылка с бонусом за подписку"
    )

    await reply(text, reply_markup=channel_bonus_menu())
    await state.clear()


@admin_router.callback_query(F.data == "admin:channel_bonus_list")
async def show_channel_bonus_list(callback: CallbackQuery):
    """Show list of all channel bonuses."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonuses = await service.get_all_bonuses()

        if not bonuses:
            await callback.message.edit_text(
                "📋 Список бонусов за подписку\n\n"
                "Пока нет бонусов. Создайте первый!",
                reply_markup=back_keyboard()
            )
            await callback.answer()
            return

        text = "📋 Бонусы за подписку на канал\n\n"

        for bonus in bonuses:
            status = "✅ Активен" if bonus.is_active else "❌ Неактивен"
            stats = await service.get_bonus_stats(bonus.id)
            ch_name = bonus.channel_title or str(bonus.channel_id)
            if bonus.channel_username:
                ch_name += f" (@{bonus.channel_username})"

            text += (
                f"#{bonus.id} | {ch_name}\n"
                f"   💰 {bonus.bonus_tokens:,} токенов | {status}\n"
                f"   👥 Получили: {stats['total_claims']} чел. "
                f"({stats['total_tokens_awarded']:,} токенов)\n\n"
            )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for bonus in bonuses:
        status_emoji = "✅" if bonus.is_active else "❌"
        builder.button(
            text=f"{status_emoji} #{bonus.id} - Вкл/Выкл",
            callback_data=f"admin:cb_toggle:{bonus.id}"
        )
    builder.button(text="➕ Создать бонус", callback_data="admin:channel_bonus_create")
    builder.button(text="🔙 Назад", callback_data="admin:channel_bonus_menu")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:cb_toggle:"))
async def toggle_channel_bonus(callback: CallbackQuery):
    """Toggle channel bonus on/off."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    bonus_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        new_state = await service.toggle_bonus(bonus_id)

    if new_state is None:
        await callback.answer("❌ Бонус не найден")
        return

    status = "включён" if new_state else "выключен"
    await callback.answer(f"Бонус #{bonus_id} {status}")

    # Refresh the list
    await show_channel_bonus_list(callback)


# ==================== BROADCAST WITH CHANNEL BONUS ====================


@admin_router.callback_query(F.data == "admin:broadcast_type:channel_bonus")
async def start_channel_bonus_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start broadcast with channel subscription bonus."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    # Check if there are active bonuses
    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonuses = await service.get_active_bonuses()

    if not bonuses:
        await callback.message.edit_text(
            "❌ Нет активных бонусов за подписку.\n\n"
            "Сначала создайте бонус:\n"
            "📢 Бонус за подписку → Создать бонус за подписку",
            reply_markup=back_keyboard()
        )
        await callback.answer()
        return

    await state.set_state(BroadcastWithChannelBonus.waiting_for_text)

    await callback.message.edit_text(
        "📢 Рассылка с бонусом за подписку на канал\n\n"
        "Шаг 1/5: Введите текст рассылки\n\n"
        "Это основное сообщение, которое увидят пользователи.\n"
        "К нему автоматически добавится кнопка для проверки подписки.\n\n"
        "Пример:\n"
        "«Подпишись на наш канал и получи 1000 бонусных токенов!\n"
        "Подпишись → нажми кнопку ниже → получи токены!»",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(BroadcastWithChannelBonus.waiting_for_text))
async def process_cb_broadcast_text(message: Message, state: FSMContext):
    """Process text for channel bonus broadcast."""
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if not text:
        await message.answer("❌ Текст не может быть пустым.", reply_markup=cancel_keyboard())
        return

    await state.update_data(text=text)
    await state.set_state(BroadcastWithChannelBonus.waiting_for_image)

    from app.admin.keyboards.inline import skip_image_cb_keyboard
    await message.answer(
        f"✅ Текст сохранён ({len(text)} символов)\n\n"
        "Шаг 2/5: Отправьте фото для сообщения\n"
        "или нажмите «Пропустить».",
        reply_markup=skip_image_cb_keyboard()
    )


@admin_router.message(StateFilter(BroadcastWithChannelBonus.waiting_for_image), F.photo)
async def process_cb_broadcast_image(message: Message, state: FSMContext):
    """Process image for channel bonus broadcast."""
    if not is_admin(message.from_user.id):
        return

    photo = message.photo[-1]
    await state.update_data(image_file_id=photo.file_id)
    await _show_channel_selection(message.answer, state)


@admin_router.callback_query(F.data == "admin:cb_skip_image")
async def skip_cb_broadcast_image(callback: CallbackQuery, state: FSMContext):
    """Skip image for channel bonus broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.update_data(image_file_id=None)
    await _show_channel_selection(callback.message.edit_text, state)
    await callback.answer()


async def _show_channel_selection(reply_func, state: FSMContext):
    """Show channel/bonus selection step."""
    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonuses = await service.get_active_bonuses()

    builder = InlineKeyboardBuilder()
    for bonus in bonuses:
        ch_name = bonus.channel_title or str(bonus.channel_id)
        if bonus.channel_username:
            ch_name = f"@{bonus.channel_username}"
        builder.button(
            text=f"{ch_name} ({bonus.bonus_tokens:,} токенов)",
            callback_data=f"admin:cb_select_bonus:{bonus.id}"
        )
    builder.button(text="❌ Отмена", callback_data="admin:cancel")
    builder.adjust(1)

    await state.set_state(BroadcastWithChannelBonus.waiting_for_channel)

    await reply_func(
        "Шаг 3/5: Выберите бонус за подписку\n\n"
        "Выберите канал/группу, на который пользователи\n"
        "должны подписаться для получения токенов:",
        reply_markup=builder.as_markup()
    )


@admin_router.callback_query(F.data.startswith("admin:cb_select_bonus:"), StateFilter(BroadcastWithChannelBonus.waiting_for_channel))
async def select_cb_bonus(callback: CallbackQuery, state: FSMContext):
    """Select which bonus to use for broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    bonus_id = int(callback.data.split(":")[-1])
    await state.update_data(bonus_id=bonus_id)

    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonus = await service.get_bonus_by_id(bonus_id)

    if not bonus:
        await callback.answer("❌ Бонус не найден")
        return

    ch_name = bonus.channel_title or str(bonus.channel_id)
    if bonus.channel_username:
        ch_name += f" (@{bonus.channel_username})"

    await state.set_state(BroadcastWithChannelBonus.waiting_for_filter)

    from app.admin.keyboards.inline import channel_bonus_filter_keyboard

    await callback.message.edit_text(
        f"✅ Выбран: {ch_name}\n"
        f"💰 Бонус: {bonus.bonus_tokens:,} токенов\n\n"
        "Шаг 4/5: Выберите получателей рассылки\n\n"
        "• Все пользователи — рассылка всем\n"
        "• С подпиской — только у кого есть активная подписка\n"
        "• Без подписки — у кого нет подписки\n"
        "• Выборочно — укажите конкретных пользователей по ID/username\n"
        "• Тестовая — отправить только администраторам",
        reply_markup=channel_bonus_filter_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:cb_filter:"), StateFilter(BroadcastWithChannelBonus.waiting_for_filter))
async def select_cb_broadcast_filter(callback: CallbackQuery, state: FSMContext):
    """Select recipient filter for channel bonus broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    filter_type = callback.data.split(":")[-1]
    await state.update_data(filter_type=filter_type)

    # If specific users - ask for user list
    if filter_type == "specific":
        await state.set_state(BroadcastWithChannelBonus.waiting_for_specific_users)
        await callback.message.edit_text(
            "🎯 Выборочная отправка\n\n"
            "Введите список пользователей через запятую, пробел или новую строку.\n\n"
            "Поддерживаемые форматы:\n"
            "• Telegram ID: 123456789\n"
            "• Username: @username\n"
            "• Смешанный: 123456789, @username, 987654321\n\n"
            "Пример:\n"
            "123456789, @user1, @user2, 987654321",
            reply_markup=cancel_keyboard()
        )
        await callback.answer()
        return

    # For test - use admin IDs
    if filter_type == "test":
        await state.update_data(filter_type="test")

    await _show_cb_confirmation(callback, state)
    await callback.answer()


@admin_router.message(StateFilter(BroadcastWithChannelBonus.waiting_for_specific_users))
async def process_cb_specific_users(message: Message, state: FSMContext):
    """Process specific users input for channel bonus broadcast."""
    if not is_admin(message.from_user.id):
        return

    import re
    raw = message.text.strip()
    # Split by comma, space, newline
    parts = re.split(r'[,\s\n]+', raw)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        await message.answer(
            "❌ Не указано ни одного пользователя. Попробуйте ещё раз.",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(specific_users=parts)

    # Create a fake callback for reuse
    await state.set_state(BroadcastWithChannelBonus.waiting_for_confirmation)
    await _show_cb_confirmation_msg(message, state)


async def _show_cb_confirmation(callback: CallbackQuery, state: FSMContext):
    """Show confirmation for channel bonus broadcast."""
    await state.set_state(BroadcastWithChannelBonus.waiting_for_confirmation)

    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService
    from app.admin.services import get_recipients_count
    from app.admin.keyboards.inline import channel_bonus_confirm_keyboard

    data = await state.get_data()
    filter_type = data.get("filter_type", "all")
    bonus_id = data.get("bonus_id")

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonus = await service.get_bonus_by_id(bonus_id)

        if filter_type == "test":
            recipient_count = len(settings.admin_user_ids)
        elif filter_type == "specific":
            recipient_count = len(data.get("specific_users", []))
        else:
            recipient_count = await get_recipients_count(session, filter_type)

    filter_names = {
        "all": "Все пользователи",
        "subscribed": "С подпиской",
        "free": "Без подписки",
        "specific": f"Выборочно ({len(data.get('specific_users', []))} чел.)",
        "test": f"Тестовая (админы: {len(settings.admin_user_ids)})",
    }

    ch_name = bonus.channel_title or str(bonus.channel_id)
    if bonus.channel_username:
        ch_name += f" (@{bonus.channel_username})"

    text = data.get("text", "")
    image_info = "Да" if data.get("image_file_id") else "Нет"

    preview = (
        f"📋 Шаг 5/5: Подтверждение рассылки\n\n"
        f"─────────────────\n"
        f"{text}\n"
        f"─────────────────\n\n"
        f"📢 Канал: {ch_name}\n"
        f"💰 Бонус: {bonus.bonus_tokens:,} токенов\n"
        f"📸 Фото: {image_info}\n"
        f"🎯 Фильтр: {filter_names.get(filter_type, 'Неизвестно')}\n"
        f"📊 Получателей: ~{recipient_count}\n\n"
        f"Пользователи получат сообщение с кнопкой\n"
        f"«✅ Проверить подписку и получить {bonus.bonus_tokens:,} токенов»"
    )

    await callback.message.edit_text(preview, reply_markup=channel_bonus_confirm_keyboard())


async def _show_cb_confirmation_msg(message: Message, state: FSMContext):
    """Show confirmation for channel bonus broadcast (message variant)."""
    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService
    from app.admin.services import get_recipients_count
    from app.admin.keyboards.inline import channel_bonus_confirm_keyboard

    data = await state.get_data()
    filter_type = data.get("filter_type", "all")
    bonus_id = data.get("bonus_id")

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonus = await service.get_bonus_by_id(bonus_id)

        if filter_type == "test":
            recipient_count = len(settings.admin_user_ids)
        elif filter_type == "specific":
            recipient_count = len(data.get("specific_users", []))
        else:
            recipient_count = await get_recipients_count(session, filter_type)

    filter_names = {
        "all": "Все пользователи",
        "subscribed": "С подпиской",
        "free": "Без подписки",
        "specific": f"Выборочно ({len(data.get('specific_users', []))} чел.)",
        "test": f"Тестовая (админы: {len(settings.admin_user_ids)})",
    }

    ch_name = bonus.channel_title or str(bonus.channel_id)
    if bonus.channel_username:
        ch_name += f" (@{bonus.channel_username})"

    text = data.get("text", "")
    image_info = "Да" if data.get("image_file_id") else "Нет"

    preview = (
        f"📋 Шаг 5/5: Подтверждение рассылки\n\n"
        f"─────────────────\n"
        f"{text}\n"
        f"─────────────────\n\n"
        f"📢 Канал: {ch_name}\n"
        f"💰 Бонус: {bonus.bonus_tokens:,} токенов\n"
        f"📸 Фото: {image_info}\n"
        f"🎯 Фильтр: {filter_names.get(filter_type, 'Неизвестно')}\n"
        f"📊 Получателей: ~{recipient_count}\n\n"
        f"Пользователи получат сообщение с кнопкой\n"
        f"«✅ Проверить подписку и получить {bonus.bonus_tokens:,} токенов»"
    )

    await message.answer(preview, reply_markup=channel_bonus_confirm_keyboard())


@admin_router.callback_query(F.data == "admin:cb_confirm_send")
async def confirm_cb_broadcast_send(callback: CallbackQuery, state: FSMContext):
    """Confirm and send channel bonus broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await callback.answer()

    from app.database.database import async_session_maker
    from app.admin.services import (
        send_broadcast_message,
        create_broadcast_message,
        get_recipients,
        update_broadcast_stats,
    )
    from app.services.channel_bonus import ChannelBonusService
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton

    data = await state.get_data()
    text = data.get("text", "")
    image_file_id = data.get("image_file_id")
    bonus_id = data.get("bonus_id")
    filter_type = data.get("filter_type", "all")
    specific_users = data.get("specific_users", [])

    # Get bonus info
    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonus = await service.get_bonus_by_id(bonus_id)

    if not bonus:
        await callback.message.answer("❌ Бонус не найден.", reply_markup=back_keyboard())
        await state.clear()
        return

    # Build the subscription check button
    channel_link = f"https://t.me/{bonus.channel_username}" if bonus.channel_username else None
    check_button_rows = []
    if channel_link:
        check_button_rows.append([
            InlineKeyboardButton(
                text=f"📢 Подписаться на канал",
                url=channel_link
            )
        ])
    check_button_rows.append([
        InlineKeyboardButton(
            text=f"✅ Проверить подписку и получить {bonus.bonus_tokens:,} токенов",
            callback_data=f"bot.check_channel_sub:{bonus.id}"
        )
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=check_button_rows)

    # Create broadcast record
    buttons_data = []
    if channel_link:
        buttons_data.append({"text": "Подписаться на канал", "url": channel_link})
    buttons_data.append({
        "text": f"Проверить подписку ({bonus.bonus_tokens:,} токенов)",
        "callback_data": f"bot.check_channel_sub:{bonus.id}",
    })

    # Resolve admin ID
    admin_telegram_id = callback.from_user.id
    try:
        from app.database.models import User
        from sqlalchemy import select as sa_select
        async with async_session_maker() as session:
            result = await session.execute(
                sa_select(User.id).where(User.telegram_id == admin_telegram_id)
            )
            internal_admin_id = result.scalar_one_or_none()
    except Exception:
        internal_admin_id = None

    async with async_session_maker() as session:
        broadcast = await create_broadcast_message(
            session=session,
            admin_id=internal_admin_id,
            text=text,
            image_file_id=image_file_id,
            buttons=buttons_data,
            filter_type=filter_type,
        )

    # Get recipients
    async with async_session_maker() as session:
        if filter_type == "test":
            # Send to admin IDs only
            from app.database.models import User
            from sqlalchemy import select as sa_select
            result = await session.execute(
                sa_select(User).where(User.telegram_id.in_(settings.admin_user_ids))
            )
            recipients = list(result.scalars().all())
        elif filter_type == "specific":
            recipients = await _resolve_specific_users(session, specific_users)
        else:
            recipients = await get_recipients(session, filter_type)

    # Create main bot without parse_mode to avoid Markdown issues
    main_bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties())

    # Re-upload photo if needed
    main_bot_photo = None
    if image_file_id:
        try:
            admin_bot_instance = Bot(token=settings.telegram_admin_bot_token, default=DefaultBotProperties())
            file = await admin_bot_instance.get_file(image_file_id)
            photo_bytes = await admin_bot_instance.download_file(file.file_path)
            main_bot_photo = BufferedInputFile(
                file=photo_bytes.read(),
                filename="broadcast_photo.jpg"
            )
            await admin_bot_instance.session.close()
        except Exception as e:
            logger.error("cb_broadcast_photo_download_error", error=str(e))
            main_bot_photo = None

    total_users = len(recipients)
    success_count = 0
    error_count = 0
    blocked_count = 0
    blocked_user_ids = []

    status_msg = await callback.message.answer(f"⏳ Отправка... 0/{total_users}")

    for i, user in enumerate(recipients, 1):
        try:
            result = await send_broadcast_message(
                bot=main_bot,
                chat_id=user.telegram_id,
                text=text,
                photo=main_bot_photo if main_bot_photo else None,
                keyboard=keyboard,
            )
            # Cache photo file_id after first successful send
            if main_bot_photo and isinstance(main_bot_photo, BufferedInputFile) and result:
                try:
                    new_file_id = result.photo[-1].file_id
                    main_bot_photo = new_file_id
                except (AttributeError, IndexError):
                    pass
            success_count += 1
        except Exception as e:
            error_msg = str(e)
            if "bot was blocked by the user" in error_msg or "user is deactivated" in error_msg:
                blocked_count += 1
                blocked_user_ids.append(user.id)
            else:
                error_count += 1
                logger.error("cb_broadcast_send_error", user_id=user.telegram_id, error=error_msg)

        if i % 100 == 0 or i == total_users:
            try:
                await status_msg.edit_text(
                    f"⏳ Отправка... {i}/{total_users}\n"
                    f"✅ Успешно: {success_count}\n"
                    f"🚫 Заблокировали: {blocked_count}\n"
                    f"❌ Ошибок: {error_count}"
                )
            except:
                pass

    # Mark blocked users
    if blocked_user_ids:
        from app.database.models import User
        from sqlalchemy import select as sa_select
        async with async_session_maker() as session:
            for uid in blocked_user_ids:
                r = await session.execute(sa_select(User).where(User.id == uid))
                blocked_user = r.scalar_one_or_none()
                if blocked_user:
                    blocked_user.is_bot_blocked = True
            await session.commit()

    # Update stats
    async with async_session_maker() as session:
        await update_broadcast_stats(
            session=session,
            broadcast_id=broadcast.id,
            sent_count=success_count,
            error_count=error_count + blocked_count,
        )

    # Final status
    final_text = (
        f"✅ Рассылка с бонусом за подписку завершена!\n\n"
        f"📊 Статистика:\n"
        f"  • Отправлено: {success_count}\n"
    )
    if blocked_count > 0:
        final_text += f"  • Заблокировали бота: {blocked_count}\n"
    if error_count > 0:
        final_text += f"  • Ошибки: {error_count}\n"
    rate = success_count * 100 // total_users if total_users > 0 else 0
    final_text += (
        f"  • Успешность: {rate}%\n\n"
        f"🔗 ID рассылки: #{broadcast.id}\n"
        f"📢 Канал: {bonus.channel_title}\n"
        f"💰 Бонус: {bonus.bonus_tokens:,} токенов"
    )

    await status_msg.edit_text(final_text, reply_markup=back_keyboard())
    await main_bot.session.close()

    logger.info(
        "cb_broadcast_complete",
        admin_id=callback.from_user.id,
        broadcast_id=broadcast.id,
        bonus_id=bonus.id,
        filter=filter_type,
        total=total_users,
        success=success_count,
    )

    await state.clear()


@admin_router.message(StateFilter(BroadcastTargeted.waiting_for_users))
async def process_targeted_users(message: Message, state: FSMContext):
    """Process specific users for targeted simple broadcast."""
    if not is_admin(message.from_user.id):
        return

    import re
    raw = message.text.strip()
    parts = re.split(r'[,\s\n]+', raw)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        await message.answer(
            "❌ Не указано ни одного пользователя.",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(specific_users=parts, broadcast_filter="specific")
    await state.set_state(Broadcast.waiting_for_message)

    await message.answer(
        f"✅ Указано {len(parts)} получателей\n\n"
        "Теперь введите текст сообщения:",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(StateFilter(BroadcastWithButtons.waiting_for_filter))
async def process_advanced_specific_users_input(message: Message, state: FSMContext):
    """Process specific users input for advanced broadcast with buttons."""
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    if not data.get("awaiting_specific_users"):
        return  # Not waiting for user list, ignore

    import re
    raw = message.text.strip()
    parts = re.split(r'[,\s\n]+', raw)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        await message.answer(
            "❌ Не указано ни одного пользователя.",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(
        specific_users=parts,
        filter_type="specific",
        awaiting_specific_users=False,
    )
    await state.set_state(BroadcastWithButtons.waiting_for_confirmation)

    from app.admin.keyboards.inline import broadcast_confirmation_keyboard

    text_content = data.get("text", "")
    buttons = data.get("buttons", [])
    image_file_id = data.get("image_file_id")

    preview = (
        f"📋 Шаг 5/5: Превью (ВЫБОРОЧНАЯ РАССЫЛКА)\n\n"
        f"─────────────────\n"
        f"{text_content}\n"
        f"─────────────────\n\n"
        f"🎯 Получателей: {len(parts)}\n"
        f"📸 Фото: {'Да' if image_file_id else 'Нет'}\n"
        f"🔘 Кнопок: {len(buttons)}"
    )

    await message.answer(preview, reply_markup=broadcast_confirmation_keyboard())


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

    text = f"""📊 Статистика

👥 Пользователи: {total_users}
📦 Подписки: {total_subscriptions}
💳 Платежи: {total_payments}"""

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

    text = "👥 Последние 10 пользователей:\n\n"

    for user in users:
        text += f"ID: {user.telegram_id} | {safe_text(user.full_name)}\n"
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

    text = "🔗 Безлимитные пригласительные ссылки:\n\n"

    for link in links:
        status = "✅ Активна" if link.is_active else "❌ Неактивна"
        if link.is_active and not link.is_valid:
            status = "⚠️ Истекла"

        text += f"Код: {link.invite_code}\n"
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
            "Используйте: /deactivate_unlimited <invite_code>"
        )
        return

    invite_code = parts[1].strip()

    async with async_session_maker() as session:
        result = await session.execute(
            select(UnlimitedInviteLink).where(UnlimitedInviteLink.invite_code == invite_code)
        )
        link = result.scalar_one_or_none()

        if not link:
            await message.answer(f"❌ Ссылка с кодом {invite_code} не найдена.")
            return

        link.is_active = False
        await session.commit()

        await message.answer(
            f"✅ Ссылка {invite_code} деактивирована.\n"
            f"Использовано раз: {link.current_uses}",
            reply_markup=back_keyboard()
        )

        logger.info(
            "unlimited_invite_link_deactivated",
            admin_id=message.from_user.id,
            invite_code=invite_code
        )


# ==================== EXPIRY NOTIFICATIONS ====================


@admin_router.callback_query(F.data == "admin:expiry_notifications")
async def show_expiry_notifications(callback: CallbackQuery):
    """Show expiry notification settings."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    from app.database.database import async_session_maker
    from app.database.models.expiry_notification import ExpiryNotificationSettings
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(ExpiryNotificationSettings).order_by(ExpiryNotificationSettings.id)
        )
        rules = result.scalars().all()

    text = "⏰ Напоминания после истечения подписки\n\n"

    if rules:
        for rule in rules:
            status = "✅" if rule.is_active else "❌"
            discount = f" (скидка {rule.discount_percent}%)" if rule.has_discount else ""
            text += f"{status} #{rule.id}: через {rule.delay_days} дн.{discount}\n"
            msg_preview = rule.message_text[:60] + "..." if len(rule.message_text) > 60 else rule.message_text
            text += f"   \"{msg_preview}\"\n\n"
    else:
        text += "Нет настроенных правил.\n\n"

    text += "Добавьте правило, чтобы бот автоматически напоминал\n"
    text += "пользователям о продлении подписки."

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить правило", callback_data="admin:expiry_add")
    if rules:
        for rule in rules:
            status_emoji = "✅" if rule.is_active else "❌"
            builder.button(
                text=f"{status_emoji} #{rule.id} ({rule.delay_days} дн.) - Вкл/Выкл",
                callback_data=f"admin:expiry_toggle:{rule.id}"
            )
            builder.button(
                text=f"🗑 Удалить #{rule.id}",
                callback_data=f"admin:expiry_delete:{rule.id}"
            )
    builder.button(text="🔙 Назад", callback_data="admin:back")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:expiry_add")
async def start_add_expiry_rule(callback: CallbackQuery, state: FSMContext):
    """Start adding a new expiry notification rule."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(ExpiryNotification.waiting_for_delay_days)

    await callback.message.edit_text(
        "⏰ Новое правило напоминания\n\n"
        "Шаг 1/3: Через сколько дней после истечения подписки\n"
        "отправить напоминание?\n\n"
        "Введите количество дней (например: 5):",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(ExpiryNotification.waiting_for_delay_days))
async def process_expiry_delay_days(message: Message, state: FSMContext):
    """Process delay days input."""
    if not is_admin(message.from_user.id):
        return

    try:
        days = int(message.text.strip())
        if days < 1 or days > 365:
            await message.answer("❌ Введите число от 1 до 365.")
            return
    except ValueError:
        await message.answer("❌ Введите целое число.")
        return

    await state.update_data(delay_days=days)
    await state.set_state(ExpiryNotification.waiting_for_message_text)

    await message.answer(
        f"✅ Задержка: {days} дней\n\n"
        f"Шаг 2/3: Введите текст напоминания.\n\n"
        f"Можно использовать переменные:\n"
        f"  {{name}} - имя пользователя\n"
        f"  {{days}} - дней после истечения\n\n"
        f"Пример:\n"
        f"Привет, {{name}}! Ваша подписка истекла {{days}} дней назад. "
        f"Продлите сейчас и получите доступ ко всем функциям!",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(StateFilter(ExpiryNotification.waiting_for_message_text))
async def process_expiry_message_text(message: Message, state: FSMContext):
    """Process notification message text."""
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if not text:
        await message.answer("❌ Текст не может быть пустым.")
        return

    await state.update_data(message_text=text)
    await state.set_state(ExpiryNotification.waiting_for_discount)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, добавить скидку", callback_data="admin:expiry_discount_yes")
    builder.button(text="❌ Без скидки", callback_data="admin:expiry_discount_no")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")
    builder.adjust(1)

    await message.answer(
        f"✅ Текст сохранён\n\n"
        f"Шаг 3/3: Добавить скидку к напоминанию?",
        reply_markup=builder.as_markup()
    )


@admin_router.callback_query(F.data == "admin:expiry_discount_no", StateFilter(ExpiryNotification.waiting_for_discount))
async def expiry_no_discount(callback: CallbackQuery, state: FSMContext):
    """Create rule without discount."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    data = await state.get_data()

    from app.database.database import async_session_maker
    from app.database.models.expiry_notification import ExpiryNotificationSettings

    async with async_session_maker() as session:
        rule = ExpiryNotificationSettings(
            delay_days=data["delay_days"],
            message_text=data["message_text"],
            has_discount=False,
            discount_percent=0,
            is_active=True,
        )
        session.add(rule)
        await session.commit()
        await session.refresh(rule)

    await callback.message.edit_text(
        f"✅ Правило #{rule.id} создано!\n\n"
        f"⏰ Задержка: {rule.delay_days} дней\n"
        f"💬 Текст: {rule.message_text[:100]}...\n"
        f"🎁 Скидка: нет\n\n"
        f"Напоминание будет автоматически отправляться пользователям.",
        reply_markup=back_keyboard()
    )
    await state.clear()
    await callback.answer()

    logger.info(
        "expiry_notification_rule_created",
        admin_id=callback.from_user.id,
        rule_id=rule.id,
        delay_days=rule.delay_days,
        has_discount=False
    )


@admin_router.callback_query(F.data == "admin:expiry_discount_yes", StateFilter(ExpiryNotification.waiting_for_discount))
async def expiry_with_discount(callback: CallbackQuery, state: FSMContext):
    """Ask for discount percentage."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    await state.set_state(ExpiryNotification.waiting_for_discount_percent)

    await callback.message.edit_text(
        "🎁 Введите процент скидки (1-99):\n\n"
        "Например: 20",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(StateFilter(ExpiryNotification.waiting_for_discount_percent))
async def process_expiry_discount_percent(message: Message, state: FSMContext):
    """Process discount percentage."""
    if not is_admin(message.from_user.id):
        return

    try:
        percent = int(message.text.strip())
        if percent < 1 or percent > 99:
            await message.answer("❌ Введите число от 1 до 99.")
            return
    except ValueError:
        await message.answer("❌ Введите целое число.")
        return

    data = await state.get_data()

    from app.database.database import async_session_maker
    from app.database.models.expiry_notification import ExpiryNotificationSettings

    async with async_session_maker() as session:
        rule = ExpiryNotificationSettings(
            delay_days=data["delay_days"],
            message_text=data["message_text"],
            has_discount=True,
            discount_percent=percent,
            is_active=True,
        )
        session.add(rule)
        await session.commit()
        await session.refresh(rule)

    await message.answer(
        f"✅ Правило #{rule.id} создано!\n\n"
        f"⏰ Задержка: {rule.delay_days} дней\n"
        f"💬 Текст: {rule.message_text[:100]}...\n"
        f"🎁 Скидка: {percent}%\n\n"
        f"Напоминание будет автоматически отправляться пользователям.",
        reply_markup=back_keyboard()
    )
    await state.clear()

    logger.info(
        "expiry_notification_rule_created",
        admin_id=message.from_user.id,
        rule_id=rule.id,
        delay_days=rule.delay_days,
        has_discount=True,
        discount_percent=percent
    )


@admin_router.callback_query(F.data.startswith("admin:expiry_toggle:"))
async def toggle_expiry_rule(callback: CallbackQuery):
    """Toggle expiry notification rule on/off."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    rule_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.database.models.expiry_notification import ExpiryNotificationSettings
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(ExpiryNotificationSettings).where(ExpiryNotificationSettings.id == rule_id)
        )
        rule = result.scalar_one_or_none()

        if not rule:
            await callback.answer("❌ Правило не найдено")
            return

        rule.is_active = not rule.is_active
        await session.commit()
        status = "включено" if rule.is_active else "выключено"

    await callback.answer(f"Правило #{rule_id} {status}")

    # Refresh the page
    await show_expiry_notifications(callback)


@admin_router.callback_query(F.data.startswith("admin:expiry_delete:"))
async def delete_expiry_rule(callback: CallbackQuery):
    """Delete expiry notification rule."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return

    rule_id = int(callback.data.split(":")[-1])

    from app.database.database import async_session_maker
    from app.database.models.expiry_notification import ExpiryNotificationSettings
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(ExpiryNotificationSettings).where(ExpiryNotificationSettings.id == rule_id)
        )
        rule = result.scalar_one_or_none()

        if not rule:
            await callback.answer("❌ Правило не найдено")
            return

        await session.delete(rule)
        await session.commit()

    await callback.answer(f"Правило #{rule_id} удалено")

    logger.info(
        "expiry_notification_rule_deleted",
        admin_id=callback.from_user.id,
        rule_id=rule_id
    )

    # Refresh the page
    await show_expiry_notifications(callback)


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
