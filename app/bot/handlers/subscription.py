#!/usr/bin/env python3
# coding: utf-8
"""
Subscription handlers.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.bot.keyboards.inline import (
    subscription_keyboard,
    eternal_tokens_keyboard,
    back_to_main_keyboard
)
from app.bot.states import PromocodeStates
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
    from app.core.subscription_plans import ETERNAL_PLANS

    subscription_type = callback.data.split(":")[1]

    plan = ETERNAL_PLANS.get(subscription_type)
    if not plan:
        await callback.answer("❌ Неизвестный тариф", show_alert=True)
        return

    logger.info(
        "subscription_purchase_initiated",
        user_id=user.id,
        subscription_type=subscription_type,
        amount=plan.price
    )

    # Create payment
    async with async_session_maker() as session:
        payment_service = PaymentService(session)

        payment = await payment_service.create_payment(
            user_id=user.id,
            amount=plan.price,
            description=f"Покупка {plan.display_name}",
            metadata={
                "subscription_type": subscription_type,
                "tokens": plan.tokens,
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

📦 **Тариф:** {plan.display_name}
💰 **Стоимость:** {plan.price} руб.

🔹 Токены вечные и никогда не сгорают
🔹 После оплаты токены будут автоматически зачислены

Нажмите кнопку "Оплатить" для перехода к оплате."""

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "activate_promocode")
async def activate_promocode(callback: CallbackQuery, state: FSMContext):
    """Start promocode activation."""
    from app.bot.states import PromocodeStates

    await state.set_state(PromocodeStates.waiting_for_code)

    text = """🔢 Активация промокода

Отправьте промокод в следующем сообщении.

Промокод может дать вам:
– Дополнительные токены
– Скидку на подписку
– Бесплатную подписку

Пример: PROMO2025"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.message(StateFilter(PromocodeStates.waiting_for_code))
async def process_promocode(message: Message, state: FSMContext, user: User):
    """Process promocode activation."""
    from app.database.database import async_session_maker
    from app.database.models.promocode import Promocode, PromocodeUse
    from app.services.subscription.subscription_service import SubscriptionService
    from sqlalchemy import select
    from app.bot.states import PromocodeStates
    from app.core.error_handlers import format_user_error

    code = message.text.strip().upper()

    try:
        async with async_session_maker() as session:
            # Find promocode
            result = await session.execute(
                select(Promocode).where(Promocode.code == code)
            )
            promo = result.scalar_one_or_none()

            if not promo:
                await message.answer(
                    "❌ Промокод не найден.\n\n"
                    "Проверьте правильность ввода и попробуйте снова."
                )
                await state.clear()
                return

            # Check if promocode is valid
            if not promo.is_valid:
                await message.answer(
                    "❌ Промокод недействителен или истек.",
                    reply_markup=back_to_main_keyboard()
                )
                await state.clear()
                return

            # Check if user already used this promocode
            result = await session.execute(
                select(PromocodeUse).where(
                    PromocodeUse.promocode_id == promo.id,
                    PromocodeUse.user_id == user.id
                )
            )
            existing_use = result.scalar_one_or_none()

            if existing_use:
                await message.answer(
                    "❌ Вы уже использовали этот промокод.",
                    reply_markup=back_to_main_keyboard()
                )
                await state.clear()
                return

            # Apply promocode
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            sub_service = SubscriptionService(session)

            if promo.bonus_type == "tokens":
                # Give tokens
                await sub_service.add_eternal_tokens(
                    user_id=user.id,
                    tokens=promo.bonus_value,
                    subscription_type=f"promo_{promo.code}"
                )

                # Record promocode use
                promo_use = PromocodeUse(
                    promocode_id=promo.id,
                    user_id=user.id,
                    bonus_received=promo.bonus_value
                )
                session.add(promo_use)
                promo.current_uses += 1
                await session.commit()

                total_tokens = await sub_service.get_available_tokens(user.id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💎 Проверить баланс", callback_data="profile")],
                    [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
                ])

                await message.answer(
                    f"✅ Промокод активирован!\n\n"
                    f"🎁 Вы получили: {promo.bonus_value:,} токенов\n"
                    f"💎 Всего токенов: {total_tokens:,}",
                    reply_markup=keyboard
                )

                logger.info(
                    "promocode_activated",
                    user_id=user.id,
                    code=code,
                    bonus_type="tokens",
                    tokens=promo.bonus_value
                )

            elif promo.bonus_type == "discount_percent":
                # Store discount in user's state for next purchase
                discount = promo.bonus_value  # percent (e.g. 20 = 20%)

                # Record promocode use
                promo_use = PromocodeUse(
                    promocode_id=promo.id,
                    user_id=user.id,
                    bonus_received=discount
                )
                session.add(promo_use)
                promo.current_uses += 1

                # Give discount as bonus tokens (discount_percent of cheapest plan price in tokens)
                # Simpler approach: give equivalent tokens as a bonus
                from app.core.subscription_plans import ETERNAL_PLANS
                # Give tokens equivalent to discount% of the 150k plan
                base_tokens = 150_000
                bonus_tokens = int(base_tokens * discount / 100)

                await sub_service.add_eternal_tokens(
                    user_id=user.id,
                    tokens=bonus_tokens,
                    subscription_type=f"promo_discount_{promo.code}"
                )
                await session.commit()

                total_tokens = await sub_service.get_available_tokens(user.id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💎 Проверить баланс", callback_data="profile")],
                    [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
                ])

                await message.answer(
                    f"✅ Промокод активирован!\n\n"
                    f"🎁 Скидка {discount}% применена!\n"
                    f"💎 Вы получили: {bonus_tokens:,} бонусных токенов\n"
                    f"💎 Всего токенов: {total_tokens:,}",
                    reply_markup=keyboard
                )

                logger.info(
                    "promocode_activated",
                    user_id=user.id,
                    code=code,
                    bonus_type="discount_percent",
                    discount=discount,
                    bonus_tokens=bonus_tokens
                )

            elif promo.bonus_type == "subscription":
                # Give a subscription plan
                # bonus_value contains tokens amount for the subscription
                tokens_amount = promo.bonus_value

                await sub_service.add_eternal_tokens(
                    user_id=user.id,
                    tokens=tokens_amount,
                    subscription_type=f"promo_sub_{promo.code}"
                )

                # Record promocode use
                promo_use = PromocodeUse(
                    promocode_id=promo.id,
                    user_id=user.id,
                    bonus_received=tokens_amount
                )
                session.add(promo_use)
                promo.current_uses += 1
                await session.commit()

                total_tokens = await sub_service.get_available_tokens(user.id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💎 Проверить баланс", callback_data="profile")],
                    [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
                ])

                await message.answer(
                    f"✅ Промокод активирован!\n\n"
                    f"🎁 Вы получили подписку: {tokens_amount:,} токенов\n"
                    f"💎 Всего токенов: {total_tokens:,}",
                    reply_markup=keyboard
                )

                logger.info(
                    "promocode_activated",
                    user_id=user.id,
                    code=code,
                    bonus_type="subscription",
                    tokens=tokens_amount
                )

            else:
                await message.answer(
                    f"❌ Неизвестный тип промокода: {promo.bonus_type}",
                    reply_markup=back_to_main_keyboard()
                )
                await state.clear()
                return

    except ValueError:
        await message.answer("❌ Неверный формат промокода.")
    except Exception as e:
        logger.error("promocode_activation_error", error=str(e), user_id=user.id)
        user_message = format_user_error(e, provider="Promocode", user_id=user.id)
        await message.answer(f"❌ {user_message}")

    await state.clear()
