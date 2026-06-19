"""
Middleware that auto-refunds reserved tokens when a handler crashes.

Works together with ``app.core.token_guard``: tokens deducted via
``SubscriptionService.check_and_use_tokens`` during a handler are tracked, and
refunded here if the handler raises before completing. On normal completion the
tracking list is cleared (tokens were legitimately spent, or the handler already
refunded a soft failure itself).
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.token_guard import begin_request, clear_reservations, refund_pending


class TokenAutoRefundMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        begin_request()
        try:
            result = await handler(event, data)
        except Exception:
            # Handler crashed after possibly reserving tokens -> give them back.
            await refund_pending("handler_exception")
            raise
        else:
            clear_reservations()
            return result
