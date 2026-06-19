"""
Central auto-refund safety net for token reservations.

Problem this solves: handlers deduct tokens *before* running a generation, and
most of them only refund when the provider returns ``result.success == False``.
If the generation call itself *raises* (timeout, network error, parsing bug),
control skips the refund branch and the user silently loses tokens.

How it works (zero changes needed in individual handlers):
- ``SubscriptionService.check_and_use_tokens`` records every successful
  deduction in a per-update context list via :func:`track_reservation`.
- :class:`TokenAutoRefundMiddleware` resets the list before each handler and,
  if the handler raises, refunds whatever is still pending. On normal handler
  completion the list is cleared (tokens were legitimately spent, or the
  handler already refunded a soft failure via ``rollback_tokens``).

Everything runs inside one asyncio task per update, so the context list set in
the middleware is the same object mutated deep inside the handler.
"""
import contextvars
from typing import List, Tuple

from app.core.logger import get_logger

logger = get_logger(__name__)

# Per-update reservations made during the current handler: list of (user_id, tokens).
_pending: contextvars.ContextVar[List[Tuple[int, int]]] = contextvars.ContextVar(
    "pending_token_reservations", default=None
)


def begin_request() -> None:
    """Start tracking reservations for a new update."""
    _pending.set([])


def track_reservation(user_id: int, tokens: int) -> None:
    """Record a successful token deduction so it can be auto-refunded on error."""
    lst = _pending.get()
    if lst is not None and tokens > 0:
        lst.append((user_id, tokens))


def clear_reservations() -> None:
    """Forget pending reservations (handler finished normally)."""
    _pending.set([])


async def refund_pending(reason: str = "exception") -> None:
    """Refund any reservations still pending (handler raised before completing)."""
    lst = _pending.get()
    if not lst:
        return
    items = list(lst)
    _pending.set([])

    # Imported lazily to avoid a circular import at module load time.
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService

    for user_id, tokens in items:
        try:
            async with async_session_maker() as session:
                await SubscriptionService(session).rollback_tokens(user_id, tokens)
            logger.info(
                "auto_refund_on_exception",
                user_id=user_id,
                tokens=tokens,
                reason=reason,
            )
        except Exception as e:
            logger.error(
                "auto_refund_failed",
                user_id=user_id,
                tokens=tokens,
                error=str(e),
            )
