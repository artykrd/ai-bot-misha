"""
Stand-alone FastAPI entry point.

This is a thin alternative to the integrated server in `main.py`. The two
versions of the YooKassa webhook handler must stay in sync, so the canonical
implementation lives in `main.py` and this module re-exports it.
"""
import json

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.core.log_safety import sanitise_headers
from app.database.database import init_db, close_db
from app.core.redis_client import redis_client

logger = get_logger(__name__)

app = FastAPI(
    title="AI Bot API",
    description="API for AI Telegram Bot",
    version="1.0.0",
    debug=settings.effective_debug,
)


@app.middleware("http")
async def debug_http_middleware(request: Request, call_next):
    logger.info(
        "HTTP_INCOMING_REQUEST",
        method=request.method,
        url=str(request.url),
        headers=sanitise_headers(dict(request.headers)),
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


# Refuse credentialled CORS when origins are wildcarded — that combination is
# a known way to lose same-origin protections for any browser-based client.
_cors_allow_credentials = settings.cors_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=_cors_allow_credentials,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
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
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
    }


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    logger.info("telegram_webhook_received")
    return {"status": "ok"}


@app.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    """Authenticate and dispatch to the canonical webhook handler in main.py."""
    from app.database.database import async_session_maker
    from app.services.payment import PaymentService, YooKassaService
    from app.services.payment.yookassa_service import (
        is_yookassa_source_ip,
        verify_yookassa_signature,
    )
    from app.api.rate_limit import enforce_rate_limit

    await enforce_rate_limit(
        request,
        scope="yookassa_webhook",
        max_requests=120,
        window_seconds=60,
    )

    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "")
    client_ip = client_ip.split(",")[0].strip() if client_ip else ""
    if not is_yookassa_source_ip(client_ip):
        logger.warning("yukassa_webhook_blocked_ip", client_ip=client_ip)
        raise HTTPException(status_code=403, detail="Forbidden")

    raw_body = await request.body()
    signature = request.headers.get("x-yookassa-signature") or request.headers.get(
        "X-Yookassa-Signature"
    )
    if not verify_yookassa_signature(raw_body, signature):
        logger.warning("yukassa_webhook_bad_signature", client_ip=client_ip)
        raise HTTPException(status_code=401, detail="Bad signature")

    try:
        body = json.loads(raw_body or b"{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    yookassa_service = YooKassaService()
    webhook_data = yookassa_service.process_webhook(body)
    if not webhook_data:
        raise HTTPException(status_code=400, detail="Invalid webhook data")

    if webhook_data["event"] != "payment.succeeded":
        return {"status": "ok"}

    async with async_session_maker() as session:
        payment_service = PaymentService(session)
        payment = await payment_service.get_payment_by_yukassa_id(
            webhook_data["payment_id"], lock_for_update=True
        )
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        await payment_service.process_successful_payment(payment)

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "api_main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.effective_debug,
        log_level=settings.log_level.lower(),
    )
