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
    try:
        body = await request.json()

        logger.info("yukassa_webhook_received", data=body)

        # TODO: Implement payment processing
        # 1. Verify webhook signature
        # 2. Process payment
        # 3. Activate subscription

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
