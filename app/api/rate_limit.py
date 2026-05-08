"""
Lightweight per-IP rate limiter for FastAPI HTTP endpoints.

Uses Redis when available so multiple workers share the bucket; falls back to
an in-process counter when Redis is unreachable. The limiter is intentionally
small — it's a defence against abusive callers, not a substitute for upstream
WAF/CDN protections.
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, Request

from app.core.logger import get_logger

logger = get_logger(__name__)


_local_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def enforce_rate_limit(
    request: Request,
    scope: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    """
    Reject the request if the client IP exceeded ``max_requests`` per window.

    Args:
        request: Incoming FastAPI request.
        scope: Logical bucket name (e.g. "yookassa_webhook").
        max_requests: Allowed requests per window.
        window_seconds: Window length in seconds.
    """
    ip = _client_ip(request)
    key = f"ratelimit:{scope}:{ip}"
    now = time.time()

    try:
        from app.core.redis_client import redis_client
        redis = redis_client.client
        if redis is None:
            raise RuntimeError("Redis client unavailable")
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        pipe.zadd(key, {f"{now}:{id(request)}": now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds + 1)
        results = await pipe.execute()
        count = int(results[2])
    except Exception:
        # Redis unavailable — fall back to in-memory bucket. This is best
        # effort only; a multi-process deployment should keep Redis healthy.
        bucket = _local_buckets[key]
        while bucket and bucket[0] < now - window_seconds:
            bucket.popleft()
        bucket.append(now)
        count = len(bucket)

    if count > max_requests:
        logger.warning(
            "rate_limit_exceeded",
            scope=scope,
            client_ip=ip,
            count=count,
            limit=max_requests,
        )
        raise HTTPException(status_code=429, detail="Too Many Requests")
