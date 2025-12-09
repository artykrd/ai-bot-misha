#!/usr/bin/env python3
# coding: utf-8
"""
Subscription handlers.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.keyboards.inline import (
    subscription_keyboard,
    eternal_tokens_keyboard,
    back_to_main_keyboard
)
from app.database.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="subscription")


@router.callback_query(F.data == "subscription")
async def show_subscriptions(callback: CallbackQuery, user: User):
    """Show subscription options."""

    text = """💎 **Оформить подписку**

🤩 **Наш бот предоставляет вам лучший сервис** без каких либо ограничений и продолжает это делать ежедневно 24/7. **Подписка позволит вам получить больше возможностей**, чем если бы вы покупали доступ к каждой нейросети отдельно.

✨ **Что входит в подписку:**
– Доступ ко всем AI моделям (GPT-4, Claude, Gemini, и др.)
– Генерация изображений (Midjourney, DALL-E, Stable Diffusion)
– Генерация видео (Sora, Veo, Luma, Kling)
– Создание музыки (Suno)
– Инструменты для работы с фото и аудио

🎁 **Бонусы:**
– Безлимитный GPT-4 Mini при нулевом балансе
– Приоритетная поддержка
– Ранний доступ к новым моделям

Выберите подходящий тариф:"""

    await callback.message.edit_text(
        text,
        reply_markup=subscription_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "eternal_tokens")
async def show_eternal_tokens(callback: CallbackQuery):
    """Show eternal tokens options."""

    text = """🔹 **Вечные токены**

Купите токены, которые **никогда не сгорают**!

Вечные токены идеально подходят для:
– Нерегулярного использования
– Тестирования сервиса
– Накопления запаса

Выберите количество токенов:"""

    await callback.message.edit_text(
        text,
        reply_markup=eternal_tokens_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy:"))
async def process_subscription_purchase(callback: CallbackQuery, user: User):
    """Process subscription purchase."""
    from app.database.database import async_session_maker
    from app.services.payment import PaymentService
    from decimal import Decimal

    subscription_type = callback.data.split(":")[1]

    # Define tariff details
    TARIFFS = {
        "eternal_150k": {"tokens": 150000, "price": Decimal("149.00"), "name": "150,000 токенов"},
        "eternal_250k": {"tokens": 250000, "price": Decimal("279.00"), "name": "250,000 токенов"},
        "eternal_500k": {"tokens": 500000, "price": Decimal("519.00"), "name": "500,000 токенов"},
        "eternal_1m": {"tokens": 1000000, "price": Decimal("999.00"), "name": "1,000,000 токенов"},
    }

    tariff = TARIFFS.get(subscription_type)
    if not tariff:
        await callback.answer("❌ Неизвестный тариф", show_alert=True)
        return

    logger.info(
        "subscription_purchase_initiated",
        user_id=user.id,
        subscription_type=subscription_type,
        amount=tariff["price"]
    )

    # Create payment
    async with async_session_maker() as session:
        payment_service = PaymentService(session)

        payment = await payment_service.create_payment(
            user_id=user.id,
            amount=tariff["price"],
            description=f"Покупка {tariff['name']}",
            metadata={
                "subscription_type": subscription_type,
                "tokens": tariff["tokens"],
                "type": "eternal_tokens"
            }
        )

        if not payment:
            await callback.answer("❌ Ошибка создания платежа. Попробуйте позже.", show_alert=True)
            return

        # Get payment URL from yukassa_response
        confirmation_url = payment.yukassa_response.get("confirmation_url")

        if not confirmation_url:
            await callback.answer("❌ Ошибка получения ссылки на оплату", show_alert=True)
            return

    # Build payment message
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Оплатить", url=confirmation_url)
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot#shop")
    )

    text = f"""💳 **Оплата токенов**

📦 **Тариф:** {tariff['name']}
💰 **Стоимость:** {tariff['price']} руб.

🔹 Токены вечные и никогда не сгорают
🔹 После оплаты токены будут автоматически зачислены

Нажмите кнопку "Оплатить" для перехода к оплате."""

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "activate_promocode")
async def activate_promocode(callback: CallbackQuery):
    """Start promocode activation."""

    text = """🔢 **Активация промокода**

Отправьте промокод в следующем сообщении.

Промокод может дать вам:
– Дополнительные токены
– Скидку на подписку
– Бесплатную подписку

Пример: `PROMO2025`"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

    # TODO: Set FSM state to wait for promocode
