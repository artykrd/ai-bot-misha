"""
Unlimited subscription limits service.

Enforces daily limits for unlimited_1day subscriptions based on:
- Time window: 21:00 MSK to 21:00 MSK next day
- Limits defined in model_costs table
- Tracks spending via ai_requests table
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Tuple
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.subscription import Subscription
from app.database.models.model_cost import ModelCost
from app.database.models.ai_request import AIRequest
from app.database.models.system import SystemSetting
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError

logger = get_logger(__name__)

# Moscow timezone offset
MSK_OFFSET_HOURS = 3


class UnlimitedLimitsService:
    """
    Service for enforcing unlimited subscription limits.

    Prevents abuse by checking:
    - Daily request count per model
    - Daily token budget per model
    - Total daily spending
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._model_costs_cache: Dict[str, ModelCost] = {}
        self._cache_loaded = False

    async def is_feature_enabled(self) -> bool:
        """Check if unlimited limits enforcement is enabled via feature flag."""
        try:
            result = await self.session.execute(
                select(SystemSetting).where(SystemSetting.key == "unlimited_limits_enabled")
            )
            setting = result.scalar_one_or_none()
            if not setting:
                return True  # Enabled by default
            return setting.value.lower() in ("true", "1", "yes")
        except Exception as e:
            logger.warning("failed_to_check_feature_flag", error=str(e))
            return True  # Default to enabled for safety

    async def _load_model_costs(self) -> None:
        """Load model costs from database into cache."""
        if self._cache_loaded:
            return

        try:
            result = await self.session.execute(
                select(ModelCost).where(ModelCost.is_active == True)
            )
            models = result.scalars().all()
            self._model_costs_cache = {m.model_id: m for m in models}
            self._cache_loaded = True
            logger.debug("model_costs_loaded_for_limits", count=len(self._model_costs_cache))
        except Exception as e:
            logger.error("model_costs_load_failed", error=str(e))

    def _get_model_cost(self, model_id: str) -> Optional[ModelCost]:
        """Get model cost config from cache."""
        return self._model_costs_cache.get(model_id)

    def _get_daily_window(self) -> Tuple[datetime, datetime]:
        """
        Get current daily window boundaries (21:00 MSK to 21:00 MSK).

        Returns:
            Tuple of (window_start, window_end) in UTC
        """
        now_utc = datetime.now(timezone.utc)

        # Convert to MSK
        now_msk = now_utc + timedelta(hours=MSK_OFFSET_HOURS)

        # Determine window start (21:00 MSK today or yesterday)
        if now_msk.hour >= 21:
            # After 21:00 today - window started today at 21:00
            window_start_msk = now_msk.replace(hour=21, minute=0, second=0, microsecond=0)
        else:
            # Before 21:00 today - window started yesterday at 21:00
            window_start_msk = (now_msk - timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)

        window_end_msk = window_start_msk + timedelta(days=1)

        # Convert back to UTC
        window_start_utc = window_start_msk - timedelta(hours=MSK_OFFSET_HOURS)
        window_end_utc = window_end_msk - timedelta(hours=MSK_OFFSET_HOURS)

        return (window_start_utc, window_end_utc)

    async def check_unlimited_limits(
        self,
        user_id: int,
        subscription: Subscription,
        model_id: str,
        tokens_cost: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if unlimited subscription can perform operation within limits.

        Args:
            user_id: User ID
            subscription: User's subscription
            model_id: Model identifier (e.g., "kling-2.5", "suno")
            tokens_cost: Token cost of operation

        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        # Only check for unlimited subscriptions
        if not subscription.is_unlimited:
            return (True, None)

        # Check if feature is enabled
        if not await self.is_feature_enabled():
            logger.debug("unlimited_limits_disabled", user_id=user_id)
            return (True, None)

        # Load model costs
        await self._load_model_costs()

        model_cost = self._get_model_cost(model_id)
        if not model_cost:
            logger.warning("model_cost_not_found", model_id=model_id, user_id=user_id)
            # No config = allow operation (backward compatibility)
            return (True, None)

        # Get daily window
        window_start, window_end = self._get_daily_window()

        # Check request count limit
        if model_cost.unlimited_daily_limit:
            request_count = await self._get_request_count_in_window(
                user_id=user_id,
                subscription_id=subscription.id,
                model_id=model_id,
                window_start=window_start,
                window_end=window_end
            )

            if request_count >= model_cost.unlimited_daily_limit:
                logger.warning(
                    "unlimited_daily_limit_reached",
                    user_id=user_id,
                    model_id=model_id,
                    request_count=request_count,
                    limit=model_cost.unlimited_daily_limit
                )
                return (
                    False,
                    f"Достигнут дневной лимит для {model_cost.display_name}: "
                    f"{request_count}/{model_cost.unlimited_daily_limit} запросов. "
                    f"Лимит обновится сегодня в 21:00 по МСК."
                )

        # Check token budget limit
        if model_cost.unlimited_budget_tokens:
            tokens_spent = await self._get_tokens_spent_in_window(
                user_id=user_id,
                subscription_id=subscription.id,
                model_id=model_id,
                window_start=window_start,
                window_end=window_end
            )

            if tokens_spent + tokens_cost > model_cost.unlimited_budget_tokens:
                logger.warning(
                    "unlimited_budget_reached",
                    user_id=user_id,
                    model_id=model_id,
                    tokens_spent=tokens_spent,
                    tokens_cost=tokens_cost,
                    budget=model_cost.unlimited_budget_tokens
                )
                return (
                    False,
                    f"Достигнут дневной бюджет для {model_cost.display_name}: "
                    f"{tokens_spent}/{model_cost.unlimited_budget_tokens} токенов. "
                    f"Бюджет обновится сегодня в 21:00 по МСК."
                )

        # All checks passed
        return (True, None)

    async def _get_request_count_in_window(
        self,
        user_id: int,
        subscription_id: int,
        model_id: str,
        window_start: datetime,
        window_end: datetime
    ) -> int:
        """Get number of completed requests in time window."""
        try:
            result = await self.session.execute(
                select(func.count(AIRequest.id))
                .where(
                    AIRequest.user_id == user_id,
                    AIRequest.subscription_id == subscription_id,
                    AIRequest.ai_model == model_id,
                    AIRequest.status == "completed",
                    AIRequest.created_at >= window_start,
                    AIRequest.created_at < window_end
                )
            )
            count = result.scalar_one_or_none()
            return count if count is not None else 0
        except Exception as e:
            logger.error("get_request_count_failed", error=str(e), user_id=user_id)
            return 0

    async def _get_tokens_spent_in_window(
        self,
        user_id: int,
        subscription_id: int,
        model_id: str,
        window_start: datetime,
        window_end: datetime
    ) -> int:
        """Get total tokens spent in time window."""
        try:
            result = await self.session.execute(
                select(func.sum(AIRequest.tokens_cost))
                .where(
                    AIRequest.user_id == user_id,
                    AIRequest.subscription_id == subscription_id,
                    AIRequest.ai_model == model_id,
                    AIRequest.status == "completed",
                    AIRequest.created_at >= window_start,
                    AIRequest.created_at < window_end
                )
            )
            total = result.scalar_one_or_none()
            return total if total is not None else 0
        except Exception as e:
            logger.error("get_tokens_spent_failed", error=str(e), user_id=user_id)
            return 0

    async def get_unlimited_usage_stats(
        self,
        user_id: int,
        subscription_id: int
    ) -> Dict[str, any]:
        """
        Get usage statistics for unlimited subscription in current window.

        Returns:
            Dictionary with usage stats per model
        """
        await self._load_model_costs()
        window_start, window_end = self._get_daily_window()

        stats = {}

        for model_id, model_cost in self._model_costs_cache.items():
            request_count = await self._get_request_count_in_window(
                user_id=user_id,
                subscription_id=subscription_id,
                model_id=model_id,
                window_start=window_start,
                window_end=window_end
            )

            tokens_spent = await self._get_tokens_spent_in_window(
                user_id=user_id,
                subscription_id=subscription_id,
                model_id=model_id,
                window_start=window_start,
                window_end=window_end
            )

            if request_count > 0 or tokens_spent > 0:
                stats[model_id] = {
                    "display_name": model_cost.display_name,
                    "requests": request_count,
                    "request_limit": model_cost.unlimited_daily_limit,
                    "tokens_spent": tokens_spent,
                    "token_budget": model_cost.unlimited_budget_tokens,
                }

        return stats
