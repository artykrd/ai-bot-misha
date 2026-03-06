"""
Throttling middleware to protect from message spam and Telegram flood control.

Limits how often a single user can trigger bot handlers.
Uses Redis for distributed rate limiting.
"""
import time
from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.core.logger import get_logger

logger = get_logger(__name__)

# In-memory fallback when Redis is unavailable
_user_timestamps: Dict[int, list[float]] = {}


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware that rate-limits messages per user.

    Drops excessive messages silently to prevent Telegram flood control errors.
    Uses Redis when available, falls back to in-memory storage.
    """

    def __init__(
        self,
        rate_limit: float = 1.0,
        max_burst: int = 3,
        cooldown_message: Optional[str] = None,
    ):
        """
        Args:
            rate_limit: Minimum interval between messages in seconds.
            max_burst: Number of messages allowed in a burst before throttling.
            cooldown_message: Message to send when throttled (None = silent drop).
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.max_burst = max_burst
        self.cooldown_message = cooldown_message

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._get_user_id(event)
        if user_id is None:
            return await handler(event, data)

        throttled = await self._check_throttle_redis(user_id)

        if throttled:
            logger.warning(
                "throttled_message",
                user_id=user_id,
                rate_limit=self.rate_limit,
                max_burst=self.max_burst,
            )
            if self.cooldown_message and isinstance(event, Message):
                try:
                    await event.answer(self.cooldown_message)
                except Exception:
                    pass
            return None

        return await handler(event, data)

    @staticmethod
    def _get_user_id(event: TelegramObject) -> Optional[int]:
        if isinstance(event, Message) and event.from_user:
            return event.from_user.id
        if isinstance(event, CallbackQuery) and event.from_user:
            return event.from_user.id
        return None

    async def _check_throttle_redis(self, user_id: int) -> bool:
        """Check throttle using Redis. Falls back to in-memory on error."""
        try:
            from app.core.redis_client import redis_client
            redis = redis_client.client

            now = time.time()
            key = f"throttle:user:{user_id}"
            window = self.rate_limit * self.max_burst

            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, int(window) + 1)
            results = await pipe.execute()

            count = results[2]
            return count > self.max_burst

        except Exception:
            return self._check_throttle_memory(user_id)

    def _check_throttle_memory(self, user_id: int) -> bool:
        """In-memory fallback throttle check."""
        now = time.time()
        window = self.rate_limit * self.max_burst

        if user_id not in _user_timestamps:
            _user_timestamps[user_id] = []

        timestamps = _user_timestamps[user_id]
        # Remove old timestamps
        _user_timestamps[user_id] = [t for t in timestamps if now - t < window]
        _user_timestamps[user_id].append(now)

        return len(_user_timestamps[user_id]) > self.max_burst
