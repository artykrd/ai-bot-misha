"""
Telegram Stars payment handler.
Handles payments via Telegram Stars (XTR currency).
"""
import json
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery

from app.database.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="stars_payment")


def _get_star_price_and_meta(pay_type: str, plan_key: str) -> Optional[Dict[str, Any]]:
    """
    Get star price and metadata for a given payment type and plan key.

    Returns dict with keys: star_price, title, description, tokens, days, meta
    or None if plan not found.
    """
    from app.core.subscription_plans import (
        get_subscription_plan, UNLIMITED_PLAN, UNLIMITED_PLAN_STAR_PRICE,
        ETERNAL_PLANS,
    )

    if pay_type == "sub":
        plan = get_subscription_plan(plan_key)
        if plan_key == "22":
            return {
                "star_price": UNLIMITED_PLAN_STAR_PRICE,
                "title": "Безлимит на 1 день",
                "description": "Безлимитный доступ ко всем моделям на 1 день",
                "tokens": None,
                "days": 1,
                "meta": {
                    "type": "subscription",
                    "tariff_id": plan_key,
                    "days": 1,
                    "tokens": None,
                    "payment_method": "telegram_stars",
                },
            }
        if not plan:
            return None
        return {
            "star_price": plan.package.star_price,
            "title": f"Подписка: {plan.display_name}",
            "description": f"{plan.tokens:,} токенов на {plan.days} дней",
            "tokens": plan.tokens,
            "days": plan.days,
            "meta": {
                "type": "subscription",
                "tariff_id": plan_key,
                "days": plan.days,
                "tokens": plan.tokens,
                "payment_method": "telegram_stars",
            },
        }

    if pay_type == "eternal":
        plan = ETERNAL_PLANS.get(plan_key)
        if not plan:
            return None
        return {
            "star_price": plan.star_price,
            "title": f"Вечные токены: {plan.display_name}",
            "description": f"{plan.tokens:,} вечных токенов",
            "tokens": plan.tokens,
            "days": None,
            "meta": {
                "type": "eternal_tokens",
                "subscription_type": plan_key,
                "tokens": plan.tokens,
                "payment_method": "telegram_stars",
            },
        }

    return None


@router.callback_query(F.data.startswith("stars_pay:"))
async def handle_stars_payment(callback: CallbackQuery, user: User):
    """Send Telegram Stars invoice when user chooses to pay with Stars."""
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Ошибка: неверный формат", show_alert=True)
        return

    pay_type = parts[1]  # "sub" or "eternal"
    plan_key = parts[2]

    info = _get_star_price_and_meta(pay_type, plan_key)
    if not info or info["star_price"] <= 0:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    try:
        await callback.answer()
    except Exception:
        pass

    payload = json.dumps(info["meta"])

    try:
        await callback.message.answer_invoice(
            title=info["title"],
            description=info["description"],
            payload=payload,
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=info["title"], amount=info["star_price"])],
        )
    except Exception as e:
        logger.error("stars_invoice_send_failed", error=str(e), user_id=user.id)
        await callback.message.answer(
            "Ошибка при создании платежа через Звёзды. Попробуйте позже."
        )


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Approve pre-checkout query for Stars payment."""
    try:
        payload = json.loads(pre_checkout_query.invoice_payload)
        if payload.get("payment_method") != "telegram_stars":
            await pre_checkout_query.answer(ok=False, error_message="Неизвестный метод оплаты")
            return
        await pre_checkout_query.answer(ok=True)
    except Exception as e:
        logger.error("pre_checkout_error", error=str(e))
        await pre_checkout_query.answer(ok=False, error_message="Ошибка обработки платежа")


@router.message(F.successful_payment)
async def process_successful_stars_payment(message: Message, user: User):
    """Process successful Telegram Stars payment."""
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService
    from app.services.referral import ReferralService
    from app.database.models.payment import Payment
    import uuid

    payment_info = message.successful_payment
    try:
        payload = json.loads(payment_info.invoice_payload)
    except (json.JSONDecodeError, TypeError):
        logger.error("stars_payment_invalid_payload", user_id=user.id)
        await message.answer("Ошибка обработки платежа. Обратитесь в поддержку.")
        return

    payment_type = payload.get("type")
    tokens = payload.get("tokens")
    days = payload.get("days")
    stars_amount = payment_info.total_amount

    logger.info(
        "stars_payment_successful",
        user_id=user.id,
        telegram_payment_charge_id=payment_info.telegram_payment_charge_id,
        stars_amount=stars_amount,
        payload=payload,
    )

    try:
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)

            # Record payment in database
            db_payment = Payment(
                payment_id=f"STARS-{uuid.uuid4().hex[:16].upper()}",
                user_id=user.id,
                amount=Decimal(str(stars_amount)),
                currency="XTR",
                status="success",
                payment_method="telegram_stars",
                yukassa_payment_id=payment_info.telegram_payment_charge_id,
                yukassa_response={
                    "telegram_payment_charge_id": payment_info.telegram_payment_charge_id,
                    "provider_payment_charge_id": payment_info.provider_payment_charge_id,
                    "currency": "XTR",
                    "total_amount": stars_amount,
                    "metadata": payload,
                },
            )
            session.add(db_payment)

            if payment_type == "eternal_tokens" and tokens and int(tokens) > 0:
                subscription = await sub_service.add_eternal_tokens(
                    user_id=user.id,
                    tokens=int(tokens),
                )
                db_payment.subscription_id = subscription.id
                await session.commit()

                total_tokens = await sub_service.get_available_tokens(user.id)
                await message.answer(
                    f"Оплата прошла успешно!\n\n"
                    f"Вам начислено {int(tokens):,} вечных токенов.\n"
                    f"Баланс: {total_tokens:,} токенов"
                )

            elif payment_type == "subscription":
                if tokens and int(tokens) > 0:
                    subscription = await sub_service.add_subscription_tokens(
                        user_id=user.id,
                        tokens=int(tokens),
                        days=int(days) if days else 30,
                        subscription_type="premium_subscription",
                    )
                elif days:
                    # Unlimited plan
                    from app.database.models.subscription import Subscription
                    started_at = datetime.now(timezone.utc)
                    from datetime import timedelta
                    expires_at = started_at + timedelta(days=int(days))
                    subscription = Subscription(
                        user_id=user.id,
                        subscription_type="unlimited_1day",
                        tokens_amount=999999999,
                        tokens_used=0,
                        price=Decimal("0.00"),
                        is_active=True,
                        started_at=started_at,
                        expires_at=expires_at,
                    )
                    session.add(subscription)
                    await session.flush()
                else:
                    await session.commit()
                    await message.answer("Оплата прошла, но произошла ошибка начисления. Обратитесь в поддержку.")
                    return

                db_payment.subscription_id = subscription.id
                await session.commit()

                total_tokens = await sub_service.get_available_tokens(user.id)
                if tokens and int(tokens) > 0:
                    await message.answer(
                        f"Оплата прошла успешно!\n\n"
                        f"Подписка активирована: {int(tokens):,} токенов на {days} дней.\n"
                        f"Баланс: {total_tokens:,} токенов"
                    )
                else:
                    await message.answer(
                        f"Оплата прошла успешно!\n\n"
                        f"Безлимитный доступ активирован на {days} день!"
                    )
            else:
                await session.commit()
                await message.answer("Оплата прошла, но произошла ошибка начисления. Обратитесь в поддержку.")
                return

            # Award referrer if exists
            try:
                referral_service = ReferralService(session)
                await referral_service.award_referrer_for_purchase(
                    referred_user_id=user.id,
                    tokens_purchased=int(tokens) if tokens else 0,
                    money_paid=Decimal(str(stars_amount)),
                )
            except Exception as e:
                logger.warning("stars_referral_award_error", error=str(e))

    except Exception as e:
        logger.error(
            "stars_payment_processing_failed",
            error=str(e),
            user_id=user.id,
            payload=payload,
        )
        await message.answer(
            "Оплата получена, но произошла ошибка при начислении.\n"
            "Пожалуйста, обратитесь в поддержку с ID платежа: "
            f"{payment_info.telegram_payment_charge_id}"
        )
