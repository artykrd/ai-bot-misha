"""
Profile handler.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.inline import profile_keyboard, subscription_manage_keyboard, back_to_main_keyboard
from app.database.models.user import User
from app.database.database import async_session_maker
from app.services.subscription.subscription_service import SubscriptionService

router = Router(name="profile")


# Token costs for different services
TOKEN_COSTS = {
    "gpt-4-mini": 500,
    "gpt-4-mini-vision": 3000,
    "nano-banana": 8000,
    "gpt-image": 8000,
    "midjourney": 20000,
    "dalle": 10000,
    "stable-diffusion": 15000,
    "recraft": 15000,
    "faceswap": 8000,
    "photo-enhance": 2000,
    "bg-replace": 15000,
    "bg-remove": 8000,
    "vectorize": 8000,
    "sora": 50000,
    "veo": 50000,
    "mj-video": 30000,
    "hailuo": 30000,
    "luma": 30000,
    "kling": 30000,
    "kling-effects": 30000,
    "suno": 20000,
    "whisper-per-min": 1000,
    "tts-per-1k-chars": 1,
}


def calculate_service_availability(total_tokens: int) -> str:
    """Calculate what services are available with current token balance."""
    lines = []

    if total_tokens >= TOKEN_COSTS["gpt-4-mini"]:
        count = total_tokens // TOKEN_COSTS["gpt-4-mini"]
        lines.append(f"- {count} запросов к ChatGPT 4 Omni Mini;")

    if total_tokens >= TOKEN_COSTS["gpt-4-mini-vision"]:
        count = total_tokens // TOKEN_COSTS["gpt-4-mini-vision"]
        lines.append(f"- {count} запросов к ChatGPT Omni Mini с обработкой фотографий;")

    if total_tokens >= TOKEN_COSTS["nano-banana"]:
        count = total_tokens // TOKEN_COSTS["nano-banana"]
        lines.append(f"- Nano Banana: {count} запроса;")

    if total_tokens >= TOKEN_COSTS["gpt-image"]:
        count = total_tokens // TOKEN_COSTS["gpt-image"]
        lines.append(f"- GPT Image 1: {count} запроса;")

    count = total_tokens // TOKEN_COSTS["midjourney"]
    lines.append(f"- Midjourney: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["dalle"]
    lines.append(f"- DALL·E: {count} запрос{'ов' if count != 1 else ''};")

    count = total_tokens // TOKEN_COSTS["stable-diffusion"]
    lines.append(f"- Stable Diffusion: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["recraft"]
    lines.append(f"- Recraft: {count} запросов;")

    if total_tokens >= TOKEN_COSTS["faceswap"]:
        count = total_tokens // TOKEN_COSTS["faceswap"]
        lines.append(f"- Замена лиц: {count} запроса для замены лиц;")

    if total_tokens >= TOKEN_COSTS["photo-enhance"]:
        count = total_tokens // TOKEN_COSTS["photo-enhance"]
        lines.append(f"- Улучшение фото: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["bg-replace"]
    lines.append(f"- Замена фона: {count} запросов;")

    if total_tokens >= TOKEN_COSTS["bg-remove"]:
        count = total_tokens // TOKEN_COSTS["bg-remove"]
        lines.append(f"- Удаление фона: {count} запроса;")

    if total_tokens >= TOKEN_COSTS["vectorize"]:
        count = total_tokens // TOKEN_COSTS["vectorize"]
        lines.append(f"- Векторизация фото: {count} запроса;")

    count = total_tokens // TOKEN_COSTS["sora"]
    lines.append(f"- Sora 2: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["veo"]
    lines.append(f"- Veo 3.1: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["mj-video"]
    lines.append(f"- Midjourney Video: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["hailuo"]
    lines.append(f"- Hailuo: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["luma"]
    lines.append(f"- Luma Dream Machine: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["kling"]
    lines.append(f"- Kling: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["kling-effects"]
    lines.append(f"- Kling Effects: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["suno"]
    lines.append(f"- Создание песен: {count} запросов (Suno);")

    minutes = total_tokens // TOKEN_COSTS["whisper-per-min"]
    lines.append(f"- {minutes} минут расшифровки аудио;")

    chars = total_tokens // TOKEN_COSTS["tts-per-1k-chars"] * 1000
    lines.append(f"- {chars:,} символов перевода текста в голос.")

    return "\n".join(lines)


@router.callback_query(F.data == "bot.profile")
@router.message(Command("profile"))
async def show_profile(event, user: User, state: FSMContext):
    """Show user profile with detailed token breakdown."""

    # CRITICAL FIX: Always clear FSM state when entering profile
    # This prevents state conflicts (e.g., hailuo video generation continuing after entering profile)
    await state.clear()

    # Handle both callback and message
    is_callback = isinstance(event, CallbackQuery)

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        total_tokens = await sub_service.get_user_total_tokens(user.id)
        # Get total spent tokens (placeholder for now)
        spent_tokens = 0  # TODO: implement tracking

    # Calculate service availability
    services_text = calculate_service_availability(total_tokens)

    # Format profile text in HTML
    profile_text = f"""📊 <b>Мой профиль</b>

🆔 ID: {user.telegram_id}
👤 Имя: {user.full_name}
📨 Имейл: не указан
🔹 Баланс: {total_tokens:,} токенов

ℹ️ На какие сервисы хватит баланса? · примерно
{services_text}

🔸 Потрачено: {spent_tokens:,} токена
- ChatGPT: 0
- DALL·E 3: 0
- Stable Diffusion: 0
- Midjourney: 0"""

    if is_callback:
        await event.message.edit_text(
            profile_text,
            reply_markup=profile_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await event.answer()
    else:
        await event.answer(
            profile_text,
            reply_markup=profile_keyboard(),
            parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data == "bot.profile_tokens")
async def show_tokens_info(callback: CallbackQuery, user: User):
    """Show detailed tokens information."""
    from app.bot.keyboards.inline import back_to_main_keyboard

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_user_total_tokens(user.id)

    text = f"""💎 **Токены**

**Что такое токены?**
Токены — это внутренняя валюта бота. За токены вы можете использовать все AI-модели: ChatGPT, генерацию изображений, видео, музыки и многое другое.

💰 **Ваш баланс:** {total_tokens:,} токенов

**Как получить токены?**
• Купить подписку через /shop
• Пригласить друзей (реферальная программа)
• Активировать промокод

**Стоимость запросов:**
• ChatGPT 4 Mini — 500 токенов
• Nano Banana (фото) — 6,380 токенов
• DALL-E 3 — 5,300 токенов
• Sora 2 (видео) — 50,600 токенов
• Hailuo (видео) — 90,000 токенов
• Kling (видео) — 80,000 токенов
• Suno (музыка) — 17,600 токенов
• Whisper (расшифровка) — 1,200 токенов/мин

**Токены не сгорают** и доступны бессрочно (для вечных токенов)."""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()


@router.callback_query(F.data == "bot.profile_subscriptions")
async def show_user_subscriptions(callback: CallbackQuery, user: User):
    """Show user's active subscriptions."""
    from app.database.repositories.subscription import SubscriptionRepository

    async with async_session_maker() as session:
        sub_repo = SubscriptionRepository(session)
        subscriptions = await sub_repo.get_user_subscriptions(user.id, active_only=True)

    if not subscriptions:
        text = """📦 <b>Мои подписки</b>

У вас нет активных подписок.

Оформите подписку через /shop, чтобы получить токены и доступ ко всем возможностям бота!"""

        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    # Show first active subscription
    subscription = subscriptions[0]

    subscription_type_names = {
        "eternal": "Вечные токены",
        "7days": "7 дней",
        "14days": "14 дней",
        "21days": "21 день",
        "30days": "30 дней",
        "unlimited_1day": "Безлимит 1 день"
    }

    type_name = subscription_type_names.get(subscription.subscription_type, subscription.subscription_type)

    if subscription.is_unlimited:
        tokens_info = "Безлимитные токены"
    else:
        tokens_info = f"{subscription.tokens_remaining:,} / {subscription.tokens_amount:,} токенов"

    expires_text = ""
    if subscription.expires_at:
        from datetime import timezone
        expires_text = f"\n⏰ <b>Истекает:</b> {subscription.expires_at.strftime('%d.%m.%Y %H:%M')}"
    else:
        expires_text = "\n♾️ <b>Срок:</b> Бессрочно"

    text = f"""📦 <b>Мои подписки</b>

📋 <b>Тип:</b> {type_name}
💎 <b>Токены:</b> {tokens_info}{expires_text}
💰 <b>Стоимость:</b> {subscription.price} руб.
📊 <b>Использовано:</b> {subscription.tokens_used:,} токенов

ℹ️ <b>Отмена подписки</b>
При отмене подписки вам будет возвращена сумма пропорционально неиспользованным токенам (минус уже использованные токены).

<b>Формула возврата:</b>
Сумма возврата = Стоимость × (Неиспользованные токены / Всего токенов)

⚠️ <b>Важно:</b> Минимальная сумма возврата — 10 рублей. Если рассчитанная сумма меньше, возврат не производится."""

    await callback.message.edit_text(
        text,
        reply_markup=subscription_manage_keyboard(subscription.id),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_subscription_"))
async def cancel_subscription(callback: CallbackQuery, user: User):
    """Cancel subscription with refund."""
    from app.services.payment import PaymentService

    # Extract subscription ID from callback data
    subscription_id = int(callback.data.split("_")[2])

    # Show confirmation message first
    await callback.answer("⏳ Обрабатываем отмену подписки...", show_alert=False)

    async with async_session_maker() as session:
        payment_service = PaymentService(session)

        # Process cancellation and refund
        result = await payment_service.cancel_subscription_with_refund(
            subscription_id=subscription_id,
            user_id=user.id
        )

    if not result:
        text = """❌ <b>Ошибка отмены подписки</b>

Не удалось отменить подписку. Возможные причины:
• Подписка уже неактивна
• Платеж не найден
• Техническая ошибка

Пожалуйста, обратитесь в поддержку: @gigavidacha"""

        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    # Format success message
    if result["refund_amount"] > 0:
        if result.get("refunded"):
            refund_text = f"""
✅ <b>Возврат средств:</b> {result['refund_amount']:.2f} руб.
💳 Деньги вернутся на карту в течение 3-5 рабочих дней"""
        else:
            refund_error = result.get("refund_error", "Неизвестная ошибка")
            refund_text = f"""
⚠️ <b>Возврат средств:</b> Ошибка при возврате
❌ {refund_error}
Пожалуйста, обратитесь в поддержку: @gigavidacha"""
    else:
        refund_text = """
ℹ️ <b>Возврат средств:</b> Не требуется
Все токены были использованы, либо сумма возврата меньше минимальной (10 руб.)"""

    text = f"""✅ <b>Подписка отменена</b>

📊 <b>Статистика:</b>
• Всего токенов: {result['total_tokens']:,}
• Использовано: {result['used_tokens']:,}
• Не использовано: {result['unused_tokens']:,}
• Стоимость подписки: {result['original_price']:.2f} руб.
{refund_text}

Спасибо, что пользуетесь нашим ботом!
Вы можете оформить новую подписку в любое время через /shop"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
