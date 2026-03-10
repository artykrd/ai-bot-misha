"""
Centralized Gemini execution layer.

Controls concurrency and retries for all Gemini API calls.

ARCHITECTURE NOTE:
  Uses a per-event-loop semaphore instead of a background worker + asyncio.Queue.
  asyncio.Queue binds to the event loop on first use; if the bot restarts and a new
  loop is created the old Queue raises "bound to a different event loop", crashing
  every worker task and flooding the system with errors.

  A Semaphore recreated whenever the running loop changes avoids that entirely.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Awaitable, Callable, TypeVar

from app.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

# Max simultaneous Gemini API calls across all services
_MAX_CONCURRENT = 3

# Retry delays (seconds) for 429 / RESOURCE_EXHAUSTED, index = attempt number
_RETRY_DELAYS = [5, 15, 45, 90]
_MAX_RETRIES = len(_RETRY_DELAYS)


class GeminiExecutionLayer:
    """
    Thin execution wrapper for Gemini API calls.

    Provides:
      - Global concurrency cap (semaphore, not a background worker)
      - Automatic retry with backoff on 429 / RESOURCE_EXHAUSTED
      - Structured log events compatible with existing monitoring

    Thread-safety: the semaphore is recreated automatically if the asyncio event
    loop changes (e.g. after a bot restart without process exit).
    """

    def __init__(self, max_concurrent: int = _MAX_CONCURRENT) -> None:
        self._max_concurrent = max_concurrent
        # These are reset whenever the running loop changes.
        self._semaphore: asyncio.Semaphore | None = None
        self._bound_loop: asyncio.AbstractEventLoop | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Return the semaphore for the *current* event loop.

        Creates (or recreates) the semaphore if the running loop has changed.
        This prevents "bound to a different event loop" RuntimeErrors that occur
        when asyncio primitives are created in one loop and used in another.
        """
        try:
            loop: asyncio.AbstractEventLoop | None = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if self._semaphore is None or self._bound_loop is not loop:
            self._semaphore = asyncio.Semaphore(self._max_concurrent)
            self._bound_loop = loop

        return self._semaphore

    @staticmethod
    def _is_rate_limit_error(exc: Exception) -> bool:
        error_text = str(exc)
        return (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "Too Many Requests" in error_text
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def execute(
        self,
        operation: str,
        model: str,
        request_fn: Callable[[], Awaitable[T]],
    ) -> T:
        """Execute a Gemini API call with concurrency control and 429 retry.

        Args:
            operation:  Name of the operation (for logging).
            model:      Model name (for logging).
            request_fn: Async zero-arg callable that performs the Gemini call.

        Returns:
            Whatever request_fn returns.

        Raises:
            The last exception raised by request_fn if all retries are exhausted.
        """
        request_id = uuid.uuid4().hex[:8]
        semaphore = self._get_semaphore()

        logger.info(
            "gemini_request_queued",
            request_id=request_id,
            operation=operation,
            model=model,
        )

        async with semaphore:
            logger.info(
                "gemini_request_started",
                request_id=request_id,
                operation=operation,
                model=model,
            )

            last_exc: BaseException | None = None

            for attempt in range(_MAX_RETRIES + 1):
                try:
                    result = await request_fn()

                    logger.info(
                        "gemini_request_completed",
                        request_id=request_id,
                        operation=operation,
                        model=model,
                        attempt=attempt,
                    )
                    return result

                except Exception as exc:
                    is_quota = self._is_rate_limit_error(exc)

                    if is_quota and attempt < _MAX_RETRIES:
                        delay = _RETRY_DELAYS[attempt]
                        logger.warning(
                            "gemini_retry",
                            request_id=request_id,
                            operation=operation,
                            model=model,
                            attempt=attempt + 1,
                            max_retries=_MAX_RETRIES,
                            delay=delay,
                            error=str(exc)[:120],
                        )
                        await asyncio.sleep(delay)
                        last_exc = exc
                        continue

                    # Non-quota error or retries exhausted — propagate
                    last_exc = exc
                    break

            logger.error(
                "gemini_request_failed",
                request_id=request_id,
                operation=operation,
                model=model,
                attempts=attempt + 1,  # type: ignore[possibly-undefined]
                error=str(last_exc)[:200],
            )
            raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Shared singleton — import this in every service that calls Gemini
# ---------------------------------------------------------------------------
gemini_execution_layer = GeminiExecutionLayer()

# Backward-compatible alias
gemini_executor = gemini_execution_layer
