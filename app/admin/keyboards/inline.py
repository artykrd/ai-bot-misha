"""
Inline keyboards for admin bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_admin_menu() -> InlineKeyboardMarkup:
    """Main admin menu keyboard."""
    builder = InlineKeyboardBuilder()

    # Statistics
    builder.button(text="📊 Статистика", callback_data="admin:stats")
    builder.button(text="👥 Пользователи", callback_data="admin:users")

    # User management
    builder.button(text="🔨 Бан/Разбан", callback_data="admin:ban_menu")
    builder.button(text="💰 Выдать токены", callback_data="admin:give_tokens")

    # Payments
    builder.button(text="💳 Платежи", callback_data="admin:payments")

    # Promocodes
    builder.button(text="🎁 Промокоды", callback_data="admin:promo_menu")

    # Unlimited links
    builder.button(text="🔗 Безлимитные ссылки", callback_data="admin:unlimited_menu")

    # System
    builder.button(text="📝 Логи", callback_data="admin:logs")
    builder.button(text="📢 Рассылка", callback_data="admin:broadcast")

    builder.adjust(2)
    return builder.as_markup()


def unlimited_links_menu() -> InlineKeyboardMarkup:
    """Unlimited links management menu."""
    builder = InlineKeyboardBuilder()

    builder.button(text="➕ Создать ссылку", callback_data="admin:create_unlimited")
    builder.button(text="📋 Список ссылок", callback_data="admin:list_unlimited")
    builder.button(text="🔙 Назад", callback_data="admin:back")

    builder.adjust(1)
    return builder.as_markup()


def promo_menu() -> InlineKeyboardMarkup:
    """Promocode management menu."""
    builder = InlineKeyboardBuilder()

    builder.button(text="➕ Создать промокод", callback_data="admin:create_promo")
    builder.button(text="📋 Список промокодов", callback_data="admin:list_promos")
    builder.button(text="🔙 Назад", callback_data="admin:back")

    builder.adjust(1)
    return builder.as_markup()


def ban_menu() -> InlineKeyboardMarkup:
    """Ban/unban menu."""
    builder = InlineKeyboardBuilder()

    builder.button(text="🚫 Забанить", callback_data="admin:ban_user")
    builder.button(text="✅ Разбанить", callback_data="admin:unban_user")
    builder.button(text="🔙 Назад", callback_data="admin:back")

    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel action keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="admin:cancel")
    return builder.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    """Back to menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад в меню", callback_data="admin:back")
    return builder.as_markup()


def user_management_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """User management keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="👁️ Подробная информация", callback_data=f"admin:user_details:{user_id}")
    builder.button(text="💰 Выдать токены", callback_data=f"admin:user_give_tokens:{user_id}")
    builder.button(text="📦 Изменить тариф", callback_data=f"admin:user_tariff:{user_id}")
    builder.button(text="📊 История запросов", callback_data=f"admin:user_requests:{user_id}")
    builder.button(text="🚫 Забанить", callback_data=f"admin:user_ban:{user_id}")
    builder.button(text="🔙 Назад", callback_data="admin:users")

    builder.adjust(1)
    return builder.as_markup()


def users_list_keyboard(page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Users list with pagination."""
    builder = InlineKeyboardBuilder()

    # Navigation buttons
    if page > 0:
        builder.button(text="◀️ Назад", callback_data=f"admin:users_page:{page-1}")
    if page < total_pages - 1:
        builder.button(text="Вперед ▶️", callback_data=f"admin:users_page:{page+1}")

    # Search button
    builder.button(text="🔍 Поиск пользователя", callback_data="admin:search_user")
    builder.button(text="🔙 Назад в меню", callback_data="admin:back")

    builder.adjust(2, 1, 1)
    return builder.as_markup()


def tariff_selection_keyboard() -> InlineKeyboardMarkup:
    """Tariff selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="7 дней - 150k токенов", callback_data="admin:tariff:7days")
    builder.button(text="14 дней - 250k токенов", callback_data="admin:tariff:14days")
    builder.button(text="21 день - 500k токенов", callback_data="admin:tariff:21days")
    builder.button(text="30 дней - 1M токенов", callback_data="admin:tariff:30days_1m")
    builder.button(text="30 дней - 5M токенов", callback_data="admin:tariff:30days_5m")
    builder.button(text="1 день безлимит", callback_data="admin:tariff:unlimited_1day")
    builder.button(text="♾️ Вечная 150k", callback_data="admin:tariff:eternal_150k")
    builder.button(text="♾️ Вечная 250k", callback_data="admin:tariff:eternal_250k")
    builder.button(text="♾️ Вечная 500k", callback_data="admin:tariff:eternal_500k")
    builder.button(text="♾️ Вечная 1M", callback_data="admin:tariff:eternal_1m")
    builder.button(text="🎨 Своя настройка", callback_data="admin:tariff:custom")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()
