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


@app.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    """YooKassa payment webhook."""
    from app.database.database import async_session_maker
    from app.services.payment import PaymentService, YooKassaService
    from app.services.subscription import SubscriptionService
    from app.bot.bot_instance import bot
    from app.database.models.user import User
    from datetime import datetime, timedelta
    from sqlalchemy import select

    try:
        body = await request.json()

        logger.info("yukassa_webhook_received", data=body)

        # Process webhook
        yookassa_service = YooKassaService()
        webhook_data = yookassa_service.process_webhook(body)

        if not webhook_data:
            logger.error("yukassa_webhook_invalid", body=body)
            raise HTTPException(status_code=400, detail="Invalid webhook data")

        event_type = webhook_data.get("event", "")

        # Handle refund events - just acknowledge them
        if event_type.startswith("refund."):
            logger.info(
                "yukassa_refund_event_received",
                refund_id=webhook_data.get("refund_id"),
                payment_id=webhook_data.get("payment_id"),
                webhook_event=event_type
            )
            return {"status": "ok"}

        # Handle payment events
        if not event_type.startswith("payment."):
            logger.warning("yukassa_unsupported_event", webhook_event=event_type)
            return {"status": "ok"}

        # Get payment from database
        async with async_session_maker() as session:
            payment_service = PaymentService(session)
            payment_id = webhook_data.get("payment_id")

            if not payment_id:
                logger.error("yukassa_no_payment_id", webhook_data=webhook_data)
                raise HTTPException(status_code=400, detail="No payment_id in webhook")

            payment = await payment_service.get_payment_by_yukassa_id(payment_id)

            if not payment:
                logger.error("yukassa_payment_not_found", payment_id=payment_id)
                raise HTTPException(status_code=404, detail="Payment not found")

            # Handle successful payment
            if event_type == "payment.succeeded" and webhook_data.get("paid"):
                if payment.status == "success":
                    logger.info(
                        "yukassa_payment_already_processed",
                        payment_id=payment.payment_id,
                        yukassa_payment_id=payment_id
                    )
                    return {"status": "ok"}

                logger.info(
                    "yukassa_payment_succeeded",
                    payment_id=payment.payment_id,
                    amount=webhook_data["amount"]
                )

                # Process payment - add tokens or activate subscription
                metadata = webhook_data.get("metadata") or {}
                if not metadata and payment.yukassa_response:
                    metadata = payment.yukassa_response.get("metadata") or {}
                payment_type = metadata.get("type", "eternal_tokens")
                tokens_added = 0

                subscription_service = SubscriptionService(session)

                if payment_type == "eternal_tokens":
                    # Add eternal tokens to user
                    try:
                        tokens = int(metadata.get("tokens", 0))
                    except (TypeError, ValueError):
                        tokens = 0
                    if tokens > 0:
                        await subscription_service.add_eternal_tokens(payment.user_id, tokens)
                        tokens_added = tokens
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

                        if tokens_awarded or money_awarded:
                            logger.info(
                                "referral_reward_awarded",
                                user_id=payment.user_id,
                                tokens_awarded=tokens_awarded,
                                money_awarded=money_awarded
                            )

                elif payment_type == "subscription":
                    # Activate subscription
                    try:
                        days = int(metadata.get("days", 30))
                    except (TypeError, ValueError):
                        days = 30
                    tokens = metadata.get("tokens")
                    if tokens is not None:
                        try:
                            tokens = int(tokens)
                        except (TypeError, ValueError):
                            tokens = 0

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
                        tokens_added = tokens

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

                        if tokens_awarded or money_awarded:
                            logger.info(
                                "referral_reward_awarded_subscription",
                                user_id=payment.user_id,
                                tokens_awarded=tokens_awarded,
                                money_awarded=money_awarded
                            )

                # Update payment status after successful processing
                await payment_service.update_payment_status(
                    payment_id=payment.payment_id,
                    status="success",
                    payment_method=metadata.get("payment_method"),
                    yukassa_response=webhook_data
                )

                # Notify user about credited tokens
                if tokens_added > 0:
                    total_tokens = await subscription_service.get_available_tokens(payment.user_id)
                    user_result = await session.execute(
                        select(User).where(User.id == payment.user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    if user:
                        message = (
                            "✅ Бонусы начислены!\n\n"
                            f"🎁 Начислено: {tokens_added:,} токенов\n"
                            f"💎 Всего токенов: {total_tokens:,}"
                        )
                        try:
                            await bot.send_message(user.telegram_id, message)
                        except Exception as send_error:
                            logger.error(
                                "yukassa_bonus_notification_failed",
                                error=str(send_error),
                                user_id=payment.user_id,
                                payment_id=payment.payment_id
                            )
                    else:
                        logger.error(
                            "yukassa_user_not_found_for_notification",
                            user_id=payment.user_id,
                            payment_id=payment.payment_id
                        )

            elif event_type == "payment.canceled":
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
