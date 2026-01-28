"""
AI request limiter for controlling concurrent requests and preventing overload.
"""
import asyncio
import time
from typing import Optional
from functools import wraps

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# Global semaphore for limiting concurrent AI requests
# This prevents overloading external AI services and our own resources
MAX_CONCURRENT_AI_REQUESTS = 50
_ai_semaphore: Optional[asyncio.Semaphore] = None

# Per-user rate limiting
USER_REQUESTS_PER_MINUTE = 10  # Max requests per user per minute
_user_request_times: dict = {}  # In-memory fallback, Redis is preferred


def get_ai_semaphore() -> asyncio.Semaphore:
    """Get or create global AI semaphore."""
    global _ai_semaphore
    if _ai_semaphore is None:
        _ai_semaphore = asyncio.Semaphore(MAX_CONCURRENT_AI_REQUESTS)
    return _ai_semaphore


async def acquire_ai_slot(timeout: float = 30.0) -> bool:
    """
    Acquire a slot for AI request with timeout.

    Args:
        timeout: Maximum time to wait for a slot (seconds)

    Returns:
        True if slot acquired, False if timeout
    """
    semaphore = get_ai_semaphore()
    try:
        await asyncio.wait_for(semaphore.acquire(), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        logger.warning("ai_slot_timeout", timeout=timeout, concurrent_limit=MAX_CONCURRENT_AI_REQUESTS)
        return False


def release_ai_slot():
    """Release AI request slot."""
    semaphore = get_ai_semaphore()
    try:
        semaphore.release()
    except ValueError:
        # Already released or not acquired
        pass


async def check_user_rate_limit(user_id: int) -> tuple[bool, int]:
    """
    Check if user can make a request (rate limiting).

    Args:
        user_id: User ID to check

    Returns:
        Tuple of (allowed: bool, wait_seconds: int)
    """
    try:
        from app.core.redis_client import redis_client

        key = f"rate_limit:user:{user_id}"
        current_time = int(time.time())
        window_start = current_time - 60  # 1 minute window

        # Get request count in current window
        count_str = await redis_client.get(key)

        if count_str is None:
            # First request in window
            await redis_client.set(key, "1", expire=60)
            return True, 0

        count = int(count_str)

        if count >= USER_REQUESTS_PER_MINUTE:
            # Rate limit exceeded
            ttl = await redis_client.get_ttl(key)
            wait_seconds = max(ttl, 1) if ttl > 0 else 60
            logger.warning(
                "user_rate_limit_exceeded",
                user_id=user_id,
                count=count,
                limit=USER_REQUESTS_PER_MINUTE,
                wait_seconds=wait_seconds
            )
            return False, wait_seconds

        # Increment counter
        await redis_client.increment(key)
        return True, 0

    except Exception as e:
        logger.error("rate_limit_check_failed", user_id=user_id, error=str(e))
        # On error, allow request but log
        return True, 0


def with_ai_limits(timeout: float = 60.0, check_rate_limit: bool = True):
    """
    Decorator for AI service methods to apply concurrency and rate limits.

    Args:
        timeout: AI request timeout in seconds
        check_rate_limit: Whether to check per-user rate limit
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to acquire AI slot
            if not await acquire_ai_slot(timeout=30.0):
                raise Exception("Сервис временно перегружен. Пожалуйста, попробуйте через несколько секунд.")

            try:
                # Execute with timeout
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error("ai_request_timeout", function=func.__name__, timeout=timeout)
                raise Exception(f"Запрос к AI занял слишком много времени (>{timeout}с). Попробуйте позже.")
            finally:
                release_ai_slot()

        return wrapper
    return decorator


class AIRequestContext:
    """
    Context manager for AI requests with automatic slot management.

    Usage:
        async with AIRequestContext(user_id=123, timeout=60) as ctx:
            if ctx.allowed:
                result = await ai_service.generate(...)
    """

    def __init__(self, user_id: Optional[int] = None, timeout: float = 60.0, check_rate_limit: bool = True):
        self.user_id = user_id
        self.timeout = timeout
        self.check_rate_limit = check_rate_limit
        self.allowed = False
        self.slot_acquired = False
        self.rate_limit_wait = 0
        self.error_message: Optional[str] = None

    async def __aenter__(self):
        # Check user rate limit first
        if self.check_rate_limit and self.user_id:
            allowed, wait_seconds = await check_user_rate_limit(self.user_id)
            if not allowed:
                self.rate_limit_wait = wait_seconds
                self.error_message = f"Слишком много запросов. Подождите {wait_seconds} секунд."
                return self

        # Acquire AI slot
        self.slot_acquired = await acquire_ai_slot(timeout=30.0)
        if not self.slot_acquired:
            self.error_message = "Сервис временно перегружен. Пожалуйста, попробуйте через несколько секунд."
            return self

        self.allowed = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.slot_acquired:
            release_ai_slot()
        return False  # Don't suppress exceptions
