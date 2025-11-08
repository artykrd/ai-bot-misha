"""
Profile handler.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.keyboards.inline import back_to_main_keyboard
from app.database.models.user import User
from app.database.database import async_session_maker
from app.services.subscription.subscription_service import SubscriptionService

router = Router(name="profile")


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, user: User):
    """Show user profile."""

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        total_tokens = await sub_service.get_user_total_tokens(user.id)
        active_sub = await sub_service.get_active_subscription(user.id)

    # Format subscription info
    if active_sub:
        if active_sub.is_unlimited:
            sub_info = f"🔥 Безлимит (до {active_sub.expires_at.strftime('%d.%m.%Y')})"
        elif active_sub.is_eternal:
            sub_info = f"♾ Вечная подписка ({active_sub.tokens_remaining:,} токенов)"
        else:
            sub_info = f"{active_sub.subscription_type} (до {active_sub.expires_at.strftime('%d.%m.%Y')})"
    else:
        sub_info = "Нет активной подписки"

    username_display = f"@{user.username}" if user.username else "не указан"

    profile_text = f"""👤 **Ваш профиль**

**ID:** `{user.telegram_id}`
**Имя:** {user.full_name}
**Username:** {username_display}

💰 **Баланс:** {total_tokens:,} токенов
📦 **Подписка:** {sub_info}

📅 **Регистрация:** {user.created_at.strftime('%d.%m.%Y')}
🕐 **Последняя активность:** {user.last_activity.strftime('%d.%m.%Y %H:%M') if user.last_activity else 'N/A'}"""

    await callback.message.edit_text(
        profile_text,
        reply_markup=back_to_main_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
