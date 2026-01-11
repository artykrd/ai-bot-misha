"""
Health checks for external services.
Checks availability of webhook, Redis, and PostgreSQL.
"""
import asyncio
from typing import Dict, Any
from datetime import datetime

import httpx
from sqlalchemy import text

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.logger import get_logger
from app.database.database import async_session_maker

logger = get_logger(__name__)


class HealthChecker:
    """Performs health checks for external services."""

    def __init__(self):
        self.webhook_url = f"http://127.0.0.1:{settings.app_port}/health"

    async def check_webhook(self, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Check webhook availability.

        Args:
            timeout: Request timeout in seconds

        Returns:
            Dict with status, response_time, error
        """
        start_time = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(self.webhook_url)
                response_time = (datetime.utcnow() - start_time).total_seconds()

                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "error": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error("webhook_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_redis(self, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Check Redis availability.

        Args:
            timeout: Ping timeout in seconds

        Returns:
            Dict with status, response_time, error
        """
        start_time = datetime.utcnow()
        try:
            # Try to ping Redis with timeout
            await asyncio.wait_for(
                redis_client.client.ping(),
                timeout=timeout
            )
            response_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "status": "healthy",
                "response_time": response_time,
                "error": None,
                "timestamp": datetime.utcnow().isoformat()
            }
        except asyncio.TimeoutError:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error("redis_health_check_timeout", timeout=timeout)
            return {
                "status": "unhealthy",
                "response_time": response_time,
                "error": "Timeout",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error("redis_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_postgresql(self, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Check PostgreSQL availability.

        Args:
            timeout: Query timeout in seconds

        Returns:
            Dict with status, response_time, error
        """
        start_time = datetime.utcnow()
        try:
            async with async_session_maker() as session:
                # Simple query to check database connection
                result = await asyncio.wait_for(
                    session.execute(text("SELECT 1")),
                    timeout=timeout
                )
                response_time = (datetime.utcnow() - start_time).total_seconds()

                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "error": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except asyncio.TimeoutError:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error("postgresql_health_check_timeout", timeout=timeout)
            return {
                "status": "unhealthy",
                "response_time": response_time,
                "error": "Timeout",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error("postgresql_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_all_services(self) -> Dict[str, Any]:
        """
        Check all services in parallel.

        Returns:
            Dict with results for all services
        """
        webhook_check, redis_check, postgresql_check = await asyncio.gather(
            self.check_webhook(),
            self.check_redis(),
            self.check_postgresql(),
            return_exceptions=True
        )

        # Handle exceptions
        if isinstance(webhook_check, Exception):
            webhook_check = {
                "status": "unhealthy",
                "error": str(webhook_check),
                "timestamp": datetime.utcnow().isoformat()
            }
        if isinstance(redis_check, Exception):
            redis_check = {
                "status": "unhealthy",
                "error": str(redis_check),
                "timestamp": datetime.utcnow().isoformat()
            }
        if isinstance(postgresql_check, Exception):
            postgresql_check = {
                "status": "unhealthy",
                "error": str(postgresql_check),
                "timestamp": datetime.utcnow().isoformat()
            }

        # Determine overall status
        all_healthy = all([
            webhook_check.get("status") == "healthy",
            redis_check.get("status") == "healthy",
            postgresql_check.get("status") == "healthy"
        ])

        return {
            "webhook": webhook_check,
            "redis": redis_check,
            "postgresql": postgresql_check,
            "overall_status": "healthy" if all_healthy else "unhealthy",
            "checked_at": datetime.utcnow().isoformat()
        }
