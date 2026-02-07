"""
Main entry point for the Telegram bot with integrated FastAPI webhook server.
"""
import asyncio
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.core.scheduler import scheduler
from app.database.database import init_db, close_db
from app.bot.bot_instance import bot, setup_bot, shutdown_bot

logger = get_logger(__name__)

# Try to import monitoring system (optional dependency)
try:
    from app.monitoring import SystemMonitor
    MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning("monitoring_unavailable", error=str(e), message="Install psutil to enable monitoring")
    MONITORING_AVAILABLE = False


# =====================================
# FASTAPI APPLICATION
# =====================================

app = FastAPI(
    title="AI Bot API",
    description="API for AI Telegram Bot with YooKassa webhooks",
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


# Register API callback routers
from app.api.sora_callback import router as sora_callback_router
app.include_router(sora_callback_router)


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


# =====================================
# UVICORN SERVER
# =====================================

async def run_fastapi_server():
    """Run FastAPI server using uvicorn Server API."""
    config = Config(
        app=app,
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
        access_log=True
    )
    server = Server(config)

    logger.info(
        "fastapi_starting",
        host=settings.app_host,
        port=settings.app_port
    )

    try:
        await server.serve()
    except asyncio.CancelledError:
        logger.info("fastapi_shutdown_initiated")
        await server.shutdown()
    except Exception as e:
        logger.error("fastapi_error", error=str(e))
        raise


# =====================================
# MAIN BOT LOOP
# =====================================

async def main() -> None:
    """Main bot loop with integrated FastAPI server."""
    dp = None
    fastapi_task = None

    try:
        logger.info("bot_starting", environment=settings.environment)

        # Initialize database
        await init_db()

        # Connect to Redis
        await redis_client.connect()

        # Setup bot (middlewares, handlers) and get dispatcher
        dp = await setup_bot()

        # Setup error notifications to admin bot
        from app.core.error_notifier import setup_error_notifications
        setup_error_notifications(bot)
        logger.info("error_notifications_enabled", admin_count=len(settings.admin_user_ids))

        # Start background scheduler
        scheduler.start()

        # Register background tasks
        from app.services.subscription.subscription_service import SubscriptionService
        from app.database.database import async_session_maker

        async def cleanup_expired_subscriptions():
            """Background task to deactivate expired subscriptions."""
            async with async_session_maker() as session:
                service = SubscriptionService(session)
                await service.deactivate_expired_subscriptions()

        # Run every hour
        scheduler.add_interval_job(cleanup_expired_subscriptions, hours=1)

        # Start system monitoring (if available)
        if MONITORING_AVAILABLE:
            monitor = SystemMonitor()
            monitor.start()
            logger.info("system_monitoring_started")
        else:
            logger.info("system_monitoring_skipped", reason="psutil not installed")

        # Start FastAPI server in background
        fastapi_task = asyncio.create_task(run_fastapi_server())
        logger.info("fastapi_task_created")

        logger.info("bot_started_successfully")

        # Start polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )

    except Exception as e:
        logger.error("bot_fatal_error", error=str(e))
        raise
    finally:
        logger.info("bot_shutting_down")

        # Stop FastAPI server
        if fastapi_task and not fastapi_task.done():
            logger.info("stopping_fastapi_server")
            fastapi_task.cancel()
            try:
                await fastapi_task
            except asyncio.CancelledError:
                logger.info("fastapi_stopped")
            except Exception as e:
                logger.error("fastapi_shutdown_error", error=str(e))

        # Stop monitoring (if available)
        if MONITORING_AVAILABLE:
            try:
                from app.monitoring.monitor import system_monitor
                await system_monitor.stop()
                logger.info("system_monitoring_stopped")
            except Exception as e:
                logger.error("monitoring_shutdown_error", error=str(e))

        # Shutdown scheduler
        scheduler.shutdown()

        # Close Redis
        await redis_client.disconnect()

        # Close database
        await close_db()

        # Shutdown bot
        if dp:
            await shutdown_bot(dp)

        logger.info("bot_shutdown_complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("bot_stopped_by_user")
        sys.exit(0)
    except Exception as e:
        logger.critical("bot_crashed", error=str(e))
        sys.exit(1)
