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
from app.core.billing_config import (
    get_text_model_billing,
    get_image_model_billing,
    get_video_model_billing,
    format_token_amount,
)
from app.bot.states.media import clear_state_preserve_settings

router = Router(name="profile")


def calculate_service_availability(total_tokens: int) -> str:
    """Calculate what services are available with current token balance."""
    lines = []

    gpt_billing = get_text_model_billing("gpt-4.1-mini")
    gpt_estimate = gpt_billing.calculate_cost(500, 1000)
    count = total_tokens // gpt_estimate
    lines.append(f"- {count} запросов к ChatGPT 4.1 Mini (оценка);")

    nano_billing = get_image_model_billing("nano-banana-image")
    dalle_billing = get_image_model_billing("dalle3")
    stable_billing = get_image_model_billing("stable-diffusion")
    recraft_billing = get_image_model_billing("recraft")
    face_billing = get_image_model_billing("face-swap")

    if total_tokens >= nano_billing.tokens_per_generation:
        count = total_tokens // nano_billing.tokens_per_generation
        lines.append(f"- Nano Banana: {count} запроса;")

    if total_tokens >= dalle_billing.tokens_per_generation:
        count = total_tokens // dalle_billing.tokens_per_generation
        lines.append(f"- DALL·E 3: {count} запросов;")

    count = total_tokens // stable_billing.tokens_per_generation
    lines.append(f"- Stable Diffusion: {count} запросов;")

    count = total_tokens // recraft_billing.tokens_per_generation
    lines.append(f"- Recraft: {count} запросов;")

    count = total_tokens // face_billing.tokens_per_generation
    lines.append(f"- Face Swap: {count} запросов;")

    sora_billing = get_video_model_billing("sora2")
    veo_billing = get_video_model_billing("veo-3.1-fast")
    mj_sd_billing = get_video_model_billing("midjourney-video-sd")
    hailuo_billing = get_video_model_billing("hailuo")
    luma_billing = get_video_model_billing("luma")
    kling_billing = get_video_model_billing("kling-video")
    kling_fx_billing = get_video_model_billing("kling-effects")

    lines.append(f"- Sora 2: {total_tokens // sora_billing.tokens_per_generation} запросов;")
    lines.append(f"- Veo 3.1: {total_tokens // veo_billing.tokens_per_generation} запросов;")
    lines.append(f"- Midjourney Video SD: {total_tokens // mj_sd_billing.tokens_per_generation} запросов;")
    lines.append(f"- Hailuo: {total_tokens // hailuo_billing.tokens_per_generation} запросов;")
    lines.append(f"- Luma: {total_tokens // luma_billing.tokens_per_generation} запросов;")
    lines.append(f"- Kling: {total_tokens // kling_billing.tokens_per_generation} запросов;")
    lines.append(f"- Kling Effects: {total_tokens // kling_fx_billing.tokens_per_generation} запросов;")

    suno_cost = 20000
    whisper_cost = 1000
    tts_cost = 1

    lines.append(f"- Создание песен: {total_tokens // suno_cost} запросов (Suno);")
    lines.append(f"- {total_tokens // whisper_cost} минут расшифровки аудио;")
    lines.append(f"- {(total_tokens // tts_cost) * 1000:,} символов перевода текста в голос.")

    return "\n".join(lines)


@router.callback_query(F.data == "bot.profile")
@router.message(Command("profile"))
@router.message(F.text == "👤 Мой профиль")
async def show_profile(event, user: User, state: FSMContext):
    """Show user profile with detailed token breakdown."""

    # CRITICAL FIX: Always clear FSM state when entering profile
    # This prevents state conflicts (e.g., hailuo video generation continuing after entering profile)
    await clear_state_preserve_settings(state)

    # Handle both callback and message
    is_callback = isinstance(event, CallbackQuery)

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        total_tokens = await sub_service.get_available_tokens(user.id)
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
        total_tokens = await sub_service.get_available_tokens(user.id)

    text = f"""💎 **Токены**

**Что такое токены?**
Токены — это внутренняя валюта бота. За токены вы можете использовать все AI-модели: ChatGPT, генерацию изображений, видео, музыки и многое другое.

💰 **Ваш баланс:** {total_tokens:,} токенов

**Как получить токены?**
• Купить подписку через /shop
• Пригласить друзей (реферальная программа)
• Активировать промокод

**Стоимость запросов (фиксированная для медиа):**
• Nano Banana (фото) — {format_token_amount(get_image_model_billing("nano-banana-image").tokens_per_generation)} токенов
• Banana PRO (фото) — {format_token_amount(get_image_model_billing("banana-pro").tokens_per_generation)} токенов
• DALL-E 3 — {format_token_amount(get_image_model_billing("dalle3").tokens_per_generation)} токенов
• Stable Diffusion — {format_token_amount(get_image_model_billing("stable-diffusion").tokens_per_generation)} токенов
• Recraft — {format_token_amount(get_image_model_billing("recraft").tokens_per_generation)} токенов
• Sora 2 (видео) — {format_token_amount(get_video_model_billing("sora2").tokens_per_generation)} токенов
• Veo 3.1 Fast (видео) — {format_token_amount(get_video_model_billing("veo-3.1-fast").tokens_per_generation)} токенов
• Kling (видео) — {format_token_amount(get_video_model_billing("kling-video").tokens_per_generation)} токенов
• Kling Effects (видео) — {format_token_amount(get_video_model_billing("kling-effects").tokens_per_generation)} токенов
• Hailuo (видео) — {format_token_amount(get_video_model_billing("hailuo").tokens_per_generation)} токенов
• Luma (видео) — {format_token_amount(get_video_model_billing("luma").tokens_per_generation)} токенов
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

    subscription_type_names = {
        "eternal": "Вечные токены",
        "eternal_purchase": "Вечные токены",
        "eternal_150k": "Вечные токены 150K",
        "eternal_250k": "Вечные токены 250K",
        "eternal_500k": "Вечные токены 500K",
        "eternal_1m": "Вечные токены 1M",
        "eternal_test": "Вечные токены (тест)",
        "expired_carryover": "Перенесённые токены",
        "refund": "Возврат токенов",
        "referral_money_exchange": "Реферальные токены",
        "tenth_purchase_bonus": "Бонус за покупки",
        "channel_bonus": "Бонус за подписку",
        "admin_gift": "Подарок от админа",
        "premium_subscription": "Премиум подписка",
        "7days": "7 дней",
        "14days": "14 дней",
        "21days": "21 день",
        "30days": "30 дней",
        "unlimited_1day": "Безлимит 1 день",
    }

    # Calculate totals across all subscriptions
    total_remaining = sum(s.tokens_remaining for s in subscriptions)
    total_used = sum(s.tokens_used for s in subscriptions)

    # Build per-subscription details
    sub_lines = []
    # Find the most recent subscription with a price for the manage button
    manageable_subscription = None
    for sub in subscriptions:
        type_name = subscription_type_names.get(sub.subscription_type, sub.subscription_type)

        if sub.is_unlimited:
            tokens_info = "Безлимитные"
        else:
            tokens_info = f"{sub.tokens_remaining:,} / {sub.tokens_amount:,}"

        if sub.expires_at:
            expires_info = f"до {sub.expires_at.strftime('%d.%m.%Y')}"
        else:
            expires_info = "бессрочно"

        sub_lines.append(f"  • {type_name}: {tokens_info} ({expires_info})")

        if sub.price and float(sub.price) > 0 and manageable_subscription is None:
            manageable_subscription = sub

    subs_detail = "\n".join(sub_lines)

    text = f"""📦 <b>Мои подписки</b>

💎 <b>Общий баланс:</b> {total_remaining:,} токенов
📊 <b>Всего использовано:</b> {total_used:,} токенов
📋 <b>Активных подписок:</b> {len(subscriptions)}

<b>Детализация:</b>
{subs_detail}

ℹ️ <b>Отмена подписки</b>
При отмене подписки вам будет возвращена сумма пропорционально неиспользованным токенам (минус уже использованные токены).

<b>Формула возврата:</b>
Сумма возврата = Стоимость × (Неиспользованные токены / Всего токенов)

⚠️ <b>Важно:</b> Минимальная сумма возврата — 10 рублей. Если рассчитанная сумма меньше, возврат не производится."""

    # Use the first manageable subscription or the first subscription for the manage button
    manage_sub = manageable_subscription or subscriptions[0]
    await callback.message.edit_text(
        text,
        reply_markup=subscription_manage_keyboard(manage_sub.id),
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

Пожалуйста, обратитесь в поддержку: @nova_support_new"""

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
Пожалуйста, обратитесь в поддержку: @nova_support_new"""
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
