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
