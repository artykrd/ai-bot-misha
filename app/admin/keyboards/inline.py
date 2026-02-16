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
    builder.button(text="✉️ Отправить сообщение", callback_data=f"admin:user_message:{user_id}")
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


# ==================== Broadcast Keyboards ====================


def broadcast_type_menu() -> InlineKeyboardMarkup:
    """Broadcast type selection menu."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📨 Простая рассылка", callback_data="admin:broadcast_type:simple")
    builder.button(text="📨 Рассылка с кнопками", callback_data="admin:broadcast_type:advanced")
    builder.button(text="📊 Статистика рассылок", callback_data="admin:broadcast_stats")
    builder.button(text="🔙 Назад", callback_data="admin:back")

    builder.adjust(1)
    return builder.as_markup()


def skip_image_keyboard() -> InlineKeyboardMarkup:
    """Skip image attachment keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="⏭ Пропустить", callback_data="admin:broadcast_skip_image")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()


def button_input_menu() -> InlineKeyboardMarkup:
    """Button input menu."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📱 Выбрать готовую кнопку", callback_data="admin:broadcast_preset_buttons")
    builder.button(text="❌ Без кнопок", callback_data="admin:broadcast_no_buttons")
    builder.button(text="🔙 Отмена", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()


def preset_button_categories() -> InlineKeyboardMarkup:
    """Preset button categories keyboard."""
    from app.admin.config import get_category_names

    builder = InlineKeyboardBuilder()

    for category_key, category_name in get_category_names():
        builder.button(text=category_name, callback_data=f"admin:broadcast_category:{category_key}")

    builder.button(text="◀️ Назад", callback_data="admin:broadcast_button_input")

    builder.adjust(1)
    return builder.as_markup()


def preset_button_list(category_key: str) -> InlineKeyboardMarkup:
    """List of preset buttons for category."""
    from app.admin.config import get_category_buttons

    builder = InlineKeyboardBuilder()

    buttons = get_category_buttons(category_key)
    for idx, button in enumerate(buttons):
        builder.button(
            text=f"✅ {button['text']}",
            callback_data=f"admin:broadcast_select_btn:{category_key}:{idx}"
        )

    builder.button(text="◀️ Назад", callback_data="admin:broadcast_preset_buttons")

    builder.adjust(1)
    return builder.as_markup()


def button_text_choice(default_text: str) -> InlineKeyboardMarkup:
    """Choose button text: use default or enter custom."""
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Использовать стандартный", callback_data="admin:broadcast_use_default_text")
    builder.button(text="✏️ Ввести свой текст", callback_data="admin:broadcast_custom_text")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()


def add_more_buttons_keyboard(current_count: int, max_count: int = 8) -> InlineKeyboardMarkup:
    """Add more buttons or finish."""
    builder = InlineKeyboardBuilder()

    if current_count < max_count:
        builder.button(text="➕ Добавить ещё кнопку", callback_data="admin:broadcast_add_more")

    builder.button(text="✅ Готово", callback_data="admin:broadcast_buttons_done")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()


def broadcast_filter_keyboard() -> InlineKeyboardMarkup:
    """Select broadcast recipients filter."""
    builder = InlineKeyboardBuilder()

    builder.button(text="👤 Все пользователи", callback_data="admin:broadcast_filter:all")
    builder.button(text="💎 С подпиской", callback_data="admin:broadcast_filter:subscribed")
    builder.button(text="🆓 Без подписки", callback_data="admin:broadcast_filter:free")
    builder.button(text="❌ Отмена", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()


def broadcast_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Confirm or cancel broadcast."""
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ ОТПРАВИТЬ", callback_data="admin:broadcast_confirm_send")
    builder.button(text="❌ Отменить", callback_data="admin:cancel")

    builder.adjust(1)
    return builder.as_markup()


def build_user_broadcast_keyboard(buttons_data: list[dict]) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for user broadcast message.

    Args:
        buttons_data: List of dicts with 'text' and 'callback_data' or 'copy_text'

    Returns:
        InlineKeyboardMarkup with buttons arranged in 1-2 per row
    """
    from aiogram.types import InlineKeyboardButton
    try:
        from aiogram.types import CopyTextButton
        has_copy_text = True
    except ImportError:
        has_copy_text = False

    rows = []
    current_row = []

    for button in buttons_data:
        if "copy_text" in button and has_copy_text:
            btn = InlineKeyboardButton(
                text=button["text"],
                copy_text=CopyTextButton(text=button["copy_text"])
            )
        elif "copy_text" in button and not has_copy_text:
            # Fallback: use callback_data if CopyTextButton is not available
            btn = InlineKeyboardButton(
                text=button["text"],
                callback_data=button.get("callback_data", "noop")
            )
        elif "url" in button:
            btn = InlineKeyboardButton(
                text=button["text"],
                url=button["url"]
            )
        else:
            btn = InlineKeyboardButton(
                text=button["text"],
                callback_data=button["callback_data"]
            )

        # Short buttons can be paired, long ones get their own row
        if len(button["text"]) < 20:
            current_row.append(btn)
            if len(current_row) >= 2:
                rows.append(current_row)
                current_row = []
        else:
            if current_row:
                rows.append(current_row)
                current_row = []
            rows.append([btn])

    if current_row:
        rows.append(current_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def broadcast_stats_keyboard(page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Broadcast statistics list pagination."""
    builder = InlineKeyboardBuilder()

    # Navigation
    if page > 0:
        builder.button(text="◀️ Назад", callback_data=f"admin:broadcast_stats_page:{page-1}")
    if page < total_pages - 1:
        builder.button(text="Вперед ▶️", callback_data=f"admin:broadcast_stats_page:{page+1}")

    builder.button(text="🔙 Назад в меню", callback_data="admin:back")

    builder.adjust(2, 1)
    return builder.as_markup()
