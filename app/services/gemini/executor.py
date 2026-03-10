"""Centralized Gemini request execution with queue, rate limiting, and retries."""
from __future__ import annotations

import asyncio
import os
import socket
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Deque, Dict, Optional, TypeVar

from app.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

_GEMINI_RATE_LIMIT_RPS = 5
_RETRY_DELAYS_SECONDS = (5, 15, 45, 90)


@dataclass
class _GeminiJob:
    request_id: str
    operation: str
    model: str
    request_fn: Callable[[], Awaitable[Any]]
    future: asyncio.Future
    queued_at: float


class GeminiExecutionLayer:
    """Global execution layer for all Gemini API calls."""

    def __init__(self) -> None:
        self._local_queue: asyncio.Queue[str] = asyncio.Queue()
        self._pending_jobs: Dict[str, _GeminiJob] = {}
        self._worker_task: Optional[asyncio.Task] = None
        self._start_lock = asyncio.Lock()

        self._redis_available: Optional[bool] = None
        instance_id = f"{socket.gethostname()}:{os.getpid()}"
        self._redis_queue_key = f"gemini:queue:{instance_id}"

        # in-memory fallback limiter (token timestamps in 1-second rolling window)
        self._request_timestamps: Deque[float] = deque()

    async def execute(
        self,
        operation: str,
        model: str,
        request_fn: Callable[[], Awaitable[T]],
    ) -> T:
        """Queue and execute a Gemini request while preserving await semantics."""
        await self._ensure_worker_started()

        loop = asyncio.get_running_loop()
        request_id = uuid.uuid4().hex
        future: asyncio.Future = loop.create_future()

        job = _GeminiJob(
            request_id=request_id,
            operation=operation,
            model=model,
            request_fn=request_fn,
            future=future,
            queued_at=time.time(),
        )
        self._pending_jobs[request_id] = job

        await self._enqueue_request(request_id)

        logger.info(
            "gemini_request_queued",
            request_id=request_id,
            operation=operation,
            model=model,
            backend="redis" if await self._is_redis_available() else "asyncio",
        )

        return await future

    async def _ensure_worker_started(self) -> None:
        if self._worker_task and not self._worker_task.done():
            return

        async with self._start_lock:
            if self._worker_task and not self._worker_task.done():
                return
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def _worker_loop(self) -> None:
        while True:
            request_id = await self._dequeue_request_id()
            if not request_id:
                continue

            job = self._pending_jobs.get(request_id)
            if not job:
                continue

            logger.info(
                "gemini_request_started",
                request_id=job.request_id,
                operation=job.operation,
                model=job.model,
                queue_wait_ms=int((time.time() - job.queued_at) * 1000),
            )

            try:
                result = await self._execute_with_retries(job)
                if not job.future.done():
                    job.future.set_result(result)

                logger.info(
                    "gemini_request_completed",
                    request_id=job.request_id,
                    operation=job.operation,
                    model=job.model,
                )
            except Exception as exc:  # noqa: BLE001
                if not job.future.done():
                    job.future.set_exception(exc)

                logger.error(
                    "gemini_request_failed",
                    request_id=job.request_id,
                    operation=job.operation,
                    model=job.model,
                    error=str(exc),
                )
            finally:
                self._pending_jobs.pop(job.request_id, None)

    async def _execute_with_retries(self, job: _GeminiJob) -> Any:
        max_attempt = len(_RETRY_DELAYS_SECONDS)

        for attempt in range(max_attempt + 1):
            await self._acquire_rate_slot()
            try:
                return await job.request_fn()
            except Exception as exc:  # noqa: BLE001
                is_429 = self._is_rate_limit_error(exc)
                if not is_429 or attempt >= max_attempt:
                    raise

                delay = _RETRY_DELAYS_SECONDS[attempt]
                logger.warning(
                    "gemini_retry",
                    request_id=job.request_id,
                    operation=job.operation,
                    model=job.model,
                    attempt=attempt + 1,
                    max_retries=max_attempt,
                    delay_seconds=delay,
                    error=str(exc),
                )
                await asyncio.sleep(delay)

        raise RuntimeError("Gemini request retry loop exhausted")

    async def _enqueue_request(self, request_id: str) -> None:
        if await self._is_redis_available():
            try:
                from app.core.redis_client import redis_client

                await redis_client.client.rpush(self._redis_queue_key, request_id)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("gemini_redis_queue_push_failed", error=str(exc))
                self._redis_available = False

        await self._local_queue.put(request_id)

    async def _dequeue_request_id(self) -> Optional[str]:
        if await self._is_redis_available():
            try:
                from app.core.redis_client import redis_client

                item = await redis_client.client.blpop(self._redis_queue_key, timeout=1)
                if item:
                    _, request_id = item
                    return request_id
            except Exception as exc:  # noqa: BLE001
                logger.warning("gemini_redis_queue_pop_failed", error=str(exc))
                self._redis_available = False

        try:
            return await asyncio.wait_for(self._local_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    async def _acquire_rate_slot(self) -> None:
        if await self._is_redis_available():
            await self._acquire_rate_slot_redis()
            return
        await self._acquire_rate_slot_memory()

    async def _acquire_rate_slot_redis(self) -> None:
        from app.core.redis_client import redis_client

        while True:
            now_sec = int(time.time())
            key = f"gemini:rate:{now_sec}"
            count = await redis_client.client.incr(key)
            if count == 1:
                await redis_client.client.expire(key, 2)
            if count <= _GEMINI_RATE_LIMIT_RPS:
                return
            await asyncio.sleep(0.2)

    async def _acquire_rate_slot_memory(self) -> None:
        while True:
            now = time.time()
            while self._request_timestamps and now - self._request_timestamps[0] >= 1.0:
                self._request_timestamps.popleft()

            if len(self._request_timestamps) < _GEMINI_RATE_LIMIT_RPS:
                self._request_timestamps.append(now)
                return

            wait_for = 1.0 - (now - self._request_timestamps[0])
            await asyncio.sleep(max(wait_for, 0.05))

    async def _is_redis_available(self) -> bool:
        if self._redis_available is not None:
            return self._redis_available

        try:
            from app.core.redis_client import redis_client

            await redis_client.client.ping()
            self._redis_available = True
        except Exception:
            self._redis_available = False

        return self._redis_available

    @staticmethod
    def _is_rate_limit_error(exc: Exception) -> bool:
        error_text = str(exc)
        return (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "Too Many Requests" in error_text
        )


gemini_execution_layer = GeminiExecutionLayer()
