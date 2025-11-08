"""
Redis client for caching and FSM storage.
"""
from typing import Any, Optional
import json

import redis.asyncio as redis
from redis.asyncio.client import Redis

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Async Redis client wrapper for caching and state management."""

    def __init__(self):
        self._client: Optional[Redis] = None
        self._fsm_client: Optional[Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            # Main Redis client for caching
            self._client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

            # FSM client for aiogram states (separate database)
            fsm_url = settings.redis_url.rsplit("/", 1)[0] + f"/{settings.redis_fsm_db}"
            self._fsm_client = await redis.from_url(
                fsm_url,
                encoding="utf-8",
                decode_responses=True,
            )

            # Test connection
            await self._client.ping()
            await self._fsm_client.ping()

            logger.info("redis_connected", url=settings.redis_url)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
        if self._fsm_client:
            await self._fsm_client.close()
        logger.info("redis_disconnected")

    @property
    def client(self) -> Redis:
        """Get main Redis client."""
        if not self._client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    @property
    def fsm_client(self) -> Redis:
        """Get FSM Redis client for aiogram."""
        if not self._fsm_client:
            raise RuntimeError("Redis FSM client not connected. Call connect() first.")
        return self._fsm_client

    # ===================================
    # Cache Operations
    # ===================================

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to store
            expire: Expiration time in seconds

        Returns:
            True if successful
        """
        try:
            await self.client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error("redis_set_failed", key=key, error=str(e))
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache."""
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return None
        except json.JSONDecodeError as e:
            logger.error("redis_json_decode_failed", key=key, error=str(e))
            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache."""
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, expire)
        except (TypeError, json.JSONEncodeError) as e:
            logger.error("redis_json_encode_failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error("redis_delete_failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error("redis_exists_failed", key=key, error=str(e))
            return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error("redis_increment_failed", key=key, error=str(e))
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key."""
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error("redis_expire_failed", key=key, error=str(e))
            return False

    async def get_ttl(self, key: str) -> int:
        """Get TTL for key in seconds."""
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error("redis_ttl_failed", key=key, error=str(e))
            return -1


# Global Redis client instance
redis_client = RedisClient()
