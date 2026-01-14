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

    webhook_start = datetime.utcnow()

    try:
        body = await request.json()

        logger.info(
            "yukassa_webhook_received_raw",
            timestamp=webhook_start.isoformat(),
            content_type=request.headers.get("content-type"),
            body_keys=list(body.keys()) if body else [],
            full_body=body
        )

        # Process webhook
        yookassa_service = YooKassaService()
        webhook_data = yookassa_service.process_webhook(body)

        if not webhook_data:
            logger.error(
                "yukassa_webhook_invalid",
                body=body,
                reason="process_webhook returned None"
            )
            raise HTTPException(status_code=400, detail="Invalid webhook data")

        event_type = webhook_data.get("event", "")
        logger.info(
            "yukassa_webhook_parsed",
            event_type=event_type,
            payment_id=webhook_data.get("payment_id"),
            status=webhook_data.get("status"),
            paid=webhook_data.get("paid"),
            amount=webhook_data.get("amount")
        )

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

            logger.info(
                "yukassa_searching_payment",
                yukassa_payment_id=payment_id
            )

            payment = await payment_service.get_payment_by_yukassa_id(payment_id)

            if not payment:
                logger.error(
                    "yukassa_payment_not_found_in_db",
                    yukassa_payment_id=payment_id,
                    searched_field="yukassa_payment_id"
                )
                raise HTTPException(status_code=404, detail="Payment not found")

            logger.info(
                "yukassa_payment_found",
                payment_id=payment.payment_id,
                yukassa_payment_id=payment_id,
                current_status=payment.status,
                user_id=payment.user_id
            )

            # Handle successful payment
            if event_type == "payment.succeeded" and webhook_data.get("paid"):
                logger.info(
                    "yukassa_payment_succeeded_event",
                    payment_id=payment.payment_id,
                    yukassa_payment_id=payment_id,
                    amount=webhook_data["amount"],
                    current_payment_status=payment.status,
                    metadata=webhook_data.get("metadata", {})
                )

                # Update yukassa_response before processing
                payment.yukassa_response = webhook_data
                await session.commit()

                logger.info(
                    "yukassa_calling_process_successful_payment",
                    payment_id=payment.payment_id,
                    user_id=payment.user_id
                )

                # Process payment through PaymentService
                success = await payment_service.process_successful_payment(payment)

                if not success:
                    logger.error(
                        "yukassa_payment_processing_failed",
                        payment_id=payment.payment_id,
                        yukassa_payment_id=payment_id
                    )
                    raise HTTPException(status_code=500, detail="Payment processing failed")

                logger.info(
                    "yukassa_payment_processed_successfully",
                    payment_id=payment.payment_id,
                    user_id=payment.user_id
                )

                # Notify user about credited tokens
                subscription_service = SubscriptionService(session)
                total_tokens = await subscription_service.get_available_tokens(payment.user_id)

                logger.info(
                    "yukassa_checking_tokens_for_notification",
                    user_id=payment.user_id,
                    total_tokens=total_tokens
                )

                if total_tokens > 0:
                    user_result = await session.execute(
                        select(User).where(User.id == payment.user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    if user:
                        # Get tokens_added from metadata
                        metadata = webhook_data.get("metadata") or {}
                        if not metadata and payment.yukassa_response:
                            metadata = payment.yukassa_response.get("metadata") or {}

                        try:
                            tokens_added = int(metadata.get("tokens", 0))
                        except (TypeError, ValueError):
                            tokens_added = 0

                        logger.info(
                            "yukassa_preparing_notification",
                            user_id=payment.user_id,
                            telegram_id=user.telegram_id,
                            tokens_added=tokens_added,
                            total_tokens=total_tokens
                        )

                        if tokens_added > 0:
                            message = (
                                "✅ Бонусы начислены!\n\n"
                                f"🎁 Начислено: {tokens_added:,} токенов\n"
                                f"💎 Всего токенов: {total_tokens:,}"
                            )
                            try:
                                await bot.send_message(user.telegram_id, message)
                                logger.info(
                                    "yukassa_notification_sent",
                                    user_id=payment.user_id,
                                    telegram_id=user.telegram_id
                                )
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
                logger.info(
                    "yukassa_payment_canceled_event",
                    payment_id=payment.payment_id,
                    yukassa_payment_id=payment_id
                )

                # Payment was canceled
                await payment_service.update_payment_status(
                    payment_id=payment.payment_id,
                    status="failed",
                    yukassa_response=webhook_data
                )

                logger.info(
                    "yukassa_payment_canceled_processed",
                    payment_id=payment.payment_id
                )

            else:
                logger.info(
                    "yukassa_payment_event_ignored",
                    event_type=event_type,
                    payment_id=payment.payment_id
                )

        webhook_duration = (datetime.utcnow() - webhook_start).total_seconds()
        logger.info(
            "yukassa_webhook_completed",
            event_type=event_type,
            duration_seconds=webhook_duration
        )

        return {"status": "ok"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "yukassa_webhook_error",
            error=str(e),
            error_type=type(e).__name__,
            traceback=str(e.__traceback__) if hasattr(e, '__traceback__') else None
        )
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
