import uvicorn
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.database.database import init_db, close_db
from app.core.redis_client import redis_client

logger = get_logger(__name__)

app = FastAPI(
    title="AI Bot API",
    description="API for AI Telegram Bot",
    version="1.0.0",
    debug=settings.debug
)

@app.middleware("http")
async def debug_http_middleware(request: Request, call_next):
    logger.info(
        "HTTP_INCOMING_REQUEST",
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
    )

    try:
        response = await call_next(request)
        logger.info(
            "HTTP_RESPONSE",
            status_code=response.status_code,
            url=str(request.url),
        )
        return response
    except Exception as e:
        logger.exception(
            "HTTP_EXCEPTION_BEFORE_HANDLER",
            error=str(e),
            url=str(request.url),
        )
        raise


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info("api_starting")
    await init_db()
    await redis_client.connect()
    logger.info("api_started")


@app.on_event("shutdown")
async def shutdown():
    logger.info("api_shutting_down")
    await redis_client.disconnect()
    await close_db()
    logger.info("api_shutdown_complete")


@app.get("/")
async def root():
    return {
        "service": "AI Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    logger.info("telegram_webhook_received")
    return {"status": "ok"}


@app.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    raw_body = await request.body()
    logger.info("yukassa_webhook_received_raw")

    body = json.loads(raw_body)

    yookassa_service = YooKassaService()
    webhook_data = yookassa_service.process_webhook(body)

    if webhook_data["event"] != "payment.succeeded":
        return {"status": "ok"}

    async with async_session_maker() as session:
        payment_service = PaymentService(session)
        payment = await payment_service.get_payment_by_yukassa_id(
            webhook_data["payment_id"]
        )

        await payment_service.process_successful_payment(payment)

    return {"status": "ok"}


@app.get("/stats")
async def get_stats():
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
