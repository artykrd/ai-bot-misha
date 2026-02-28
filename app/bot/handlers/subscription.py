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
from app.bot.states.media import clear_state_preserve_settings
from app.database.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="subscription")


async def get_user_active_discount(session, user_id: int) -> tuple:
    """
    Get user's active (unapplied) discount from promo codes.

    Returns:
        Tuple of (discount_percent, promo_use_id) or (0, None) if no active discount.
        discount_percent > 0 means there's an unused discount.
    """
    from app.database.models.promocode import Promocode, PromocodeUse
    from sqlalchemy import select

    result = await session.execute(
        select(PromocodeUse, Promocode).join(
            Promocode, PromocodeUse.promocode_id == Promocode.id
        ).where(
            PromocodeUse.user_id == user_id,
            Promocode.bonus_type == "discount_percent",
            PromocodeUse.bonus_received > 0  # > 0 means not yet applied
        ).order_by(PromocodeUse.created_at.desc()).limit(1)
    )
    row = result.first()
    if row:
        promo_use, promo = row
        return promo_use.bonus_received, promo_use.id
    return 0, None


async def consume_discount(session, promo_use_id: int):
    """Mark a discount promo code use as consumed (applied to a purchase)."""
    from app.database.models.promocode import PromocodeUse
    from sqlalchemy import select

    result = await session.execute(
        select(PromocodeUse).where(PromocodeUse.id == promo_use_id)
    )
    promo_use = result.scalar_one_or_none()
    if promo_use and promo_use.bonus_received > 0:
        # Set to negative to mark as consumed
        promo_use.bonus_received = -promo_use.bonus_received
        await session.commit()


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
    from decimal import Decimal

    subscription_type = callback.data.split(":")[1]

    plan = ETERNAL_PLANS.get(subscription_type)
    if not plan:
        await callback.answer("❌ Неизвестный тариф", show_alert=True)
        return

    # Check for active discount promo code
    async with async_session_maker() as session:
        discount_percent, promo_use_id = await get_user_active_discount(session, user.id)

    original_price = plan.price
    final_price = original_price
    discount_text = ""

    if discount_percent > 0:
        discount_amount = original_price * Decimal(str(discount_percent)) / Decimal("100")
        final_price = (original_price - discount_amount).quantize(Decimal("0.01"))
        # Ensure minimum price of 1 ruble
        if final_price < Decimal("1.00"):
            final_price = Decimal("1.00")
        discount_text = f"\n🎁 **Скидка:** {discount_percent}% (-{discount_amount:.2f} руб.)"

    logger.info(
        "subscription_purchase_initiated",
        user_id=user.id,
        subscription_type=subscription_type,
        original_amount=float(original_price),
        final_amount=float(final_price),
        discount_percent=discount_percent
    )

    # Create payment
    async with async_session_maker() as session:
        payment_service = PaymentService(session)

        payment = await payment_service.create_payment(
            user_id=user.id,
            amount=final_price,
            description=f"Покупка {plan.display_name}" + (f" (скидка {discount_percent}%)" if discount_percent > 0 else ""),
            metadata={
                "subscription_type": subscription_type,
                "tokens": plan.tokens,
                "type": "eternal_tokens",
                "discount_percent": discount_percent,
                "promo_use_id": promo_use_id
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

        # Consume the discount promo code after successful payment creation
        if promo_use_id:
            await consume_discount(session, promo_use_id)

    # Build payment message
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Оплатить Картой/СБП", url=confirmation_url)
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Оплатить Звёздами Telegram", callback_data=f"stars_pay:eternal:{subscription_type}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot#shop")
    )

    if discount_percent > 0:
        text = f"""💳 **Оплата токенов**

📦 **Тариф:** {plan.display_name}
💰 **Цена:** ~~{original_price}~~ **{final_price} руб.**{discount_text}

🔹 Токены вечные и никогда не сгорают
🔹 После оплаты токены будут автоматически зачислены

Нажмите кнопку "Оплатить" для перехода к оплате."""
    else:
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
                await clear_state_preserve_settings(state)
                return

            # Check if promocode is valid
            if not promo.is_valid:
                await message.answer(
                    "❌ Промокод недействителен или истек.",
                    reply_markup=back_to_main_keyboard()
                )
                await clear_state_preserve_settings(state)
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
                await clear_state_preserve_settings(state)
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
                # Save discount for the user's next purchase
                # bonus_received > 0 means discount not yet applied to a purchase
                discount = promo.bonus_value  # percent (e.g. 20 = 20%)

                # Record promocode use
                promo_use = PromocodeUse(
                    promocode_id=promo.id,
                    user_id=user.id,
                    bonus_received=discount
                )
                session.add(promo_use)
                promo.current_uses += 1
                await session.commit()

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💎 Перейти к покупке", callback_data="bot#shop")],
                    [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
                ])

                await message.answer(
                    f"✅ Промокод активирован!\n\n"
                    f"🎁 Скидка {discount}% будет применена к вашей следующей покупке.\n\n"
                    f"Перейдите в раздел подписки, чтобы оформить покупку со скидкой.",
                    reply_markup=keyboard
                )

                logger.info(
                    "promocode_activated",
                    user_id=user.id,
                    code=code,
                    bonus_type="discount_percent",
                    discount=discount
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
                await clear_state_preserve_settings(state)
                return

    except ValueError:
        await message.answer("❌ Неверный формат промокода.")
    except Exception as e:
        logger.error("promocode_activation_error", error=str(e), user_id=user.id)
        user_message = format_user_error(e, provider="Promocode", user_id=user.id)
        await message.answer(f"❌ {user_message}")

    await clear_state_preserve_settings(state)
