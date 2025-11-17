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

    subscription_type = callback.data.split(":")[1]

    # TODO: Integrate with payment service (YooKassa)
    # For now, just show a message

    logger.info(
        "subscription_purchase_initiated",
        user_id=user.id,
        subscription_type=subscription_type
    )

    text = f"""💳 **Оплата подписки**

Тариф: `{subscription_type}`

⚠️ **Интеграция с ЮKassa в разработке**

Пока вы можете активировать подписку через промокод.
Свяжитесь с поддержкой для получения промокода."""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
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
