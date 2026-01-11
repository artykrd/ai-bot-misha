"""
FastAPI application for webhooks and REST API.
"""
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.database.database import init_db, close_db
from app.core.redis_client import redis_client

logger = get_logger(__name__)


# Create FastAPI app
app = FastAPI(
    title="AI Bot API",
    description="API for AI Telegram Bot",
    version="1.0.0",
    debug=settings.debug
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("api_starting")

    await init_db()
    await redis_client.connect()

    logger.info("api_started")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event."""
    logger.info("api_shutting_down")

    await redis_client.disconnect()
    await close_db()

    logger.info("api_shutdown_complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint."""
    # TODO: Implement webhook handling
    logger.info("telegram_webhook_received")

    return {"status": "ok"}


@app.post("/webhook/yukassa")
async def yukassa_webhook(request: Request):
    """YooKassa payment webhook."""
    from app.database.database import async_session_maker
    from app.services.payment import PaymentService, YooKassaService
    from app.services.subscription import SubscriptionService
    from datetime import datetime, timedelta

    try:
        body = await request.json()

        logger.info("yukassa_webhook_received", data=body)

        # Process webhook
        yookassa_service = YooKassaService()
        webhook_data = yookassa_service.process_webhook(body)

        if not webhook_data:
            logger.error("yukassa_webhook_invalid", body=body)
            raise HTTPException(status_code=400, detail="Invalid webhook data")

        # Get payment from database
        async with async_session_maker() as session:
            payment_service = PaymentService(session)
            payment = await payment_service.get_payment_by_yukassa_id(webhook_data["payment_id"])

            if not payment:
                logger.error("yukassa_payment_not_found", payment_id=webhook_data["payment_id"])
                raise HTTPException(status_code=404, detail="Payment not found")

            # Handle successful payment
            if webhook_data["event"] == "payment.succeeded" and webhook_data["paid"]:
                logger.info(
                    "yukassa_payment_succeeded",
                    payment_id=payment.payment_id,
                    amount=webhook_data["amount"]
                )

                # Update payment status
                await payment_service.update_payment_status(
                    payment_id=payment.payment_id,
                    status="success",
                    payment_method=webhook_data.get("metadata", {}).get("payment_method"),
                    yukassa_response=webhook_data
                )

                # Process payment - add tokens or activate subscription
                metadata = webhook_data.get("metadata", {})
                payment_type = metadata.get("type", "eternal_tokens")

                subscription_service = SubscriptionService(session)

                if payment_type == "eternal_tokens":
                    # Add eternal tokens to user
                    tokens = int(metadata.get("tokens", 0))
                    if tokens > 0:
                        await subscription_service.add_eternal_tokens(payment.user_id, tokens)
                        logger.info(
                            "eternal_tokens_added",
                            user_id=payment.user_id,
                            tokens=tokens
                        )

                        # Award referrer if exists
                        from app.services.referral import ReferralService
                        from decimal import Decimal

                        referral_service = ReferralService(session)
                        tokens_awarded, money_awarded = await referral_service.award_referrer_for_purchase(
                            referred_user_id=payment.user_id,
                            tokens_purchased=tokens,
                            money_paid=Decimal(str(payment.amount))
                        )

                        # Send notification to referrer if reward was given
                        if tokens_awarded or money_awarded:
                            try:
                                from app.database.models.user import User
                                from sqlalchemy import select
                                from aiogram import Bot
                                from app.core.config import settings

                                # Get referred user info
                                user_result = await session.execute(
                                    select(User).where(User.id == payment.user_id)
                                )
                                referred_user = user_result.scalar_one_or_none()

                                # Get referrer
                                referrer = await referral_service.get_referrer(payment.user_id)

                                if referrer and referred_user:
                                    bot = Bot(token=settings.telegram_bot_token)

                                    if tokens_awarded:
                                        await bot.send_message(
                                            chat_id=referrer.telegram_id,
                                            text=f"🎉 **Вам начислено {tokens_awarded:,} токенов!**\n\n"
                                                 f"Ваш реферал {referred_user.full_name or 'пользователь'} совершил покупку.",
                                            parse_mode="Markdown"
                                        )
                                    elif money_awarded:
                                        await bot.send_message(
                                            chat_id=referrer.telegram_id,
                                            text=f"💰 **Вам начислено {money_awarded:.2f} руб!**\n\n"
                                                 f"Ваш партнерский реферал {referred_user.full_name or 'пользователь'} совершил покупку.",
                                            parse_mode="Markdown"
                                        )

                                    await bot.session.close()

                            except Exception as notify_error:
                                # Don't fail payment if notification fails
                                logger.warning(
                                    "referral_notification_failed",
                                    error=str(notify_error),
                                    user_id=payment.user_id
                                )

                elif payment_type == "subscription":
                    # Activate subscription
                    days = int(metadata.get("days", 30))
                    tokens = metadata.get("tokens")

                    # Create subscription
                    from app.database.models.subscription import Subscription
                    subscription = Subscription(
                        user_id=payment.user_id,
                        subscription_type="premium",
                        start_date=datetime.utcnow(),
                        end_date=datetime.utcnow() + timedelta(days=days),
                        is_active=True,
                        auto_renew=False,
                        payment_status="paid",
                        tokens_included=tokens if tokens else 0
                    )

                    session.add(subscription)
                    await session.commit()

                    # Add tokens if included
                    if tokens:
                        await subscription_service.add_subscription_tokens(payment.user_id, tokens)

                    # Link payment to subscription
                    payment.subscription_id = subscription.id
                    await session.commit()

                    logger.info(
                        "subscription_activated",
                        user_id=payment.user_id,
                        days=days,
                        tokens=tokens
                    )

                    # Award referrer if exists
                    if tokens:
                        from app.services.referral import ReferralService
                        from decimal import Decimal

                        referral_service = ReferralService(session)
                        tokens_awarded, money_awarded = await referral_service.award_referrer_for_purchase(
                            referred_user_id=payment.user_id,
                            tokens_purchased=tokens,
                            money_paid=Decimal(str(payment.amount))
                        )

                        # Send notification to referrer if reward was given
                        if tokens_awarded or money_awarded:
                            try:
                                from app.database.models.user import User
                                from sqlalchemy import select
                                from aiogram import Bot
                                from app.core.config import settings

                                # Get referred user info
                                user_result = await session.execute(
                                    select(User).where(User.id == payment.user_id)
                                )
                                referred_user = user_result.scalar_one_or_none()

                                # Get referrer
                                referrer = await referral_service.get_referrer(payment.user_id)

                                if referrer and referred_user:
                                    bot = Bot(token=settings.telegram_bot_token)

                                    if tokens_awarded:
                                        await bot.send_message(
                                            chat_id=referrer.telegram_id,
                                            text=f"🎉 **Вам начислено {tokens_awarded:,} токенов!**\n\n"
                                                 f"Ваш реферал {referred_user.full_name or 'пользователь'} оформил подписку.",
                                            parse_mode="Markdown"
                                        )
                                    elif money_awarded:
                                        await bot.send_message(
                                            chat_id=referrer.telegram_id,
                                            text=f"💰 **Вам начислено {money_awarded:.2f} руб!**\n\n"
                                                 f"Ваш партнерский реферал {referred_user.full_name or 'пользователь'} оформил подписку.",
                                            parse_mode="Markdown"
                                        )

                                    await bot.session.close()

                            except Exception as notify_error:
                                # Don't fail payment if notification fails
                                logger.warning(
                                    "referral_notification_failed",
                                    error=str(notify_error),
                                    user_id=payment.user_id
                                )

            elif webhook_data["event"] == "payment.canceled":
                # Payment was canceled
                await payment_service.update_payment_status(
                    payment_id=payment.payment_id,
                    status="failed",
                    yukassa_response=webhook_data
                )

                logger.info(
                    "yukassa_payment_canceled",
                    payment_id=payment.payment_id
                )

        return {"status": "ok"}

    except Exception as e:
        logger.error("yukassa_webhook_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get bot statistics."""
    # TODO: Implement statistics
    return {
        "users": 0,
        "subscriptions": 0,
        "requests": 0
    }


if __name__ == "__main__":
    uvicorn.run(
        "api_main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
