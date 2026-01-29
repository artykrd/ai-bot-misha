"""
AI Logging Service for tracking all AI operations.

This service:
- Works in parallel with existing code (non-blocking)
- Retrieves costs from database (model_costs table)
- Logs all AI operations with full cost tracking
- Safe to use - errors don't block operations
"""
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session_maker
from app.database.models.ai_request import AIRequest
from app.database.models.model_cost import ModelCost
from app.database.models.subscription import Subscription
from app.core.logger import get_logger

logger = get_logger(__name__)

# Default USD to RUB rate (should be updated from external source)
DEFAULT_USD_RUB_RATE = 90.0


class AILoggingService:
    """
    Service for logging AI operations with cost tracking.

    Key principles:
    - Non-blocking: errors don't stop the main operation
    - Data from DB: costs and categories from model_costs table
    - Backward compatible: works alongside existing code
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        """
        Initialize the logging service.

        Args:
            session: Optional database session. If not provided,
                    a new session will be created for each operation.
        """
        self._session = session
        self._model_costs_cache: Dict[str, ModelCost] = {}
        self._cache_loaded = False

    async def _get_session(self) -> AsyncSession:
        """Get or create database session."""
        if self._session:
            return self._session
        return async_session_maker()

    async def _load_model_costs(self, session: AsyncSession) -> None:
        """Load model costs from database into cache."""
        if self._cache_loaded:
            return

        try:
            result = await session.execute(
                select(ModelCost).where(ModelCost.is_active == True)
            )
            models = result.scalars().all()
            self._model_costs_cache = {m.model_id: m for m in models}
            self._cache_loaded = True
            logger.debug("model_costs_cache_loaded", count=len(self._model_costs_cache))
        except Exception as e:
            logger.warning("model_costs_cache_load_failed", error=str(e))

    def _get_model_cost(self, model_id: str) -> Optional[ModelCost]:
        """Get model cost from cache."""
        return self._model_costs_cache.get(model_id)

    async def _get_active_subscription(
        self,
        session: AsyncSession,
        user_id: int
    ) -> Optional[Subscription]:
        """Get user's active subscription."""
        try:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True
                ).order_by(Subscription.created_at.desc()).limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.warning("get_subscription_failed", user_id=user_id, error=str(e))
            return None

    async def log_operation(
        self,
        user_id: int,
        model_id: str,
        operation_category: str,
        tokens_cost: int,
        request_type: Optional[str] = None,
        prompt: Optional[str] = None,
        status: str = "completed",
        response_file_path: Optional[str] = None,
        error_message: Optional[str] = None,
        processing_time_seconds: Optional[int] = None,
        input_data: Optional[Dict[str, Any]] = None,
        units: float = 1.0,
    ) -> Optional[int]:
        """
        Log an AI operation with cost tracking.

        This method is safe to call - it catches all errors
        and logs them without blocking the main operation.

        Args:
            user_id: User ID
            model_id: Model identifier (e.g., "suno", "kling-2.5", "gpt-4o")
            operation_category: Category code (e.g., "video_gen", "audio_gen")
            tokens_cost: Internal tokens charged for this operation
            request_type: Request type (text, image, video, audio). Inferred from category if not provided.
            prompt: User prompt (truncated to 500 chars)
            status: Operation status (pending, completed, failed)
            response_file_path: Path to generated file
            error_message: Error message if failed
            processing_time_seconds: Time taken to process
            input_data: Additional input parameters (resolution, duration, etc.)
            units: Number of units for cost calculation (default 1.0)

        Returns:
            AI request ID if successful, None otherwise
        """
        try:
            should_close_session = self._session is None
            session = await self._get_session()

            try:
                # Load model costs cache
                await self._load_model_costs(session)

                # Get model cost config from DB
                model_cost = self._get_model_cost(model_id)

                # Calculate USD cost
                cost_usd: Optional[Decimal] = None
                cost_rub: Optional[Decimal] = None

                if model_cost:
                    cost_usd = model_cost.calculate_cost_usd(units)
                    cost_rub = cost_usd * Decimal(str(DEFAULT_USD_RUB_RATE))

                    # Use category from model_cost if not provided
                    if not operation_category:
                        operation_category = model_cost.category_code

                # Infer request_type from category if not provided
                if not request_type:
                    request_type = self._category_to_request_type(operation_category)

                # Get active subscription
                subscription = await self._get_active_subscription(session, user_id)
                subscription_id = subscription.id if subscription else None
                is_unlimited = subscription.is_unlimited if subscription else False

                # Create AI request record
                ai_request = AIRequest(
                    user_id=user_id,
                    request_type=request_type,
                    ai_model=model_id,
                    prompt=prompt[:500] if prompt else None,
                    tokens_cost=tokens_cost,
                    status=status,
                    response_file_path=response_file_path,
                    error_message=error_message,
                    processing_time_seconds=processing_time_seconds,
                    # New fields
                    cost_usd=cost_usd,
                    cost_rub=cost_rub,
                    operation_category=operation_category,
                    subscription_id=subscription_id,
                    is_unlimited_subscription=is_unlimited,
                    input_data=input_data,
                )

                session.add(ai_request)
                await session.commit()
                await session.refresh(ai_request)

                logger.info(
                    "ai_operation_logged",
                    ai_request_id=ai_request.id,
                    user_id=user_id,
                    model=model_id,
                    category=operation_category,
                    tokens=tokens_cost,
                    cost_usd=float(cost_usd) if cost_usd else None,
                    is_unlimited=is_unlimited,
                )

                return ai_request.id

            finally:
                if should_close_session:
                    await session.close()

        except Exception as e:
            # Log error but don't raise - this should never block the main operation
            logger.error(
                "ai_operation_log_failed",
                user_id=user_id,
                model=model_id,
                error=str(e),
            )
            return None

    async def update_operation_status(
        self,
        ai_request_id: int,
        status: str,
        response_file_path: Optional[str] = None,
        error_message: Optional[str] = None,
        processing_time_seconds: Optional[int] = None,
    ) -> bool:
        """
        Update an existing AI request record.

        Args:
            ai_request_id: ID of the AI request to update
            status: New status (completed, failed)
            response_file_path: Path to generated file
            error_message: Error message if failed
            processing_time_seconds: Time taken to process

        Returns:
            True if successful, False otherwise
        """
        try:
            should_close_session = self._session is None
            session = await self._get_session()

            try:
                result = await session.execute(
                    select(AIRequest).where(AIRequest.id == ai_request_id)
                )
                ai_request = result.scalar_one_or_none()

                if not ai_request:
                    logger.warning("ai_request_not_found", ai_request_id=ai_request_id)
                    return False

                ai_request.status = status
                if response_file_path:
                    ai_request.response_file_path = response_file_path
                if error_message:
                    ai_request.error_message = error_message
                if processing_time_seconds is not None:
                    ai_request.processing_time_seconds = processing_time_seconds

                await session.commit()

                logger.info(
                    "ai_operation_updated",
                    ai_request_id=ai_request_id,
                    status=status,
                )

                return True

            finally:
                if should_close_session:
                    await session.close()

        except Exception as e:
            logger.error(
                "ai_operation_update_failed",
                ai_request_id=ai_request_id,
                error=str(e),
            )
            return False

    def _category_to_request_type(self, category: str) -> str:
        """Map operation category to request type."""
        mapping = {
            "text": "text",
            "text_with_image": "text",
            "image_gen": "image",
            "image_edit": "image",
            "video_gen": "video",
            "audio_gen": "audio",
            "transcription": "audio",
            "tts": "audio",
        }
        return mapping.get(category, category)


# Convenience functions for non-blocking logging

async def log_ai_operation(
    user_id: int,
    model_id: str,
    operation_category: str,
    tokens_cost: int,
    **kwargs
) -> Optional[int]:
    """
    Convenience function to log an AI operation.

    Creates a new session and logs the operation.
    Safe to call - errors are caught and logged.

    Args:
        user_id: User ID
        model_id: Model identifier
        operation_category: Category code
        tokens_cost: Tokens charged
        **kwargs: Additional arguments for log_operation

    Returns:
        AI request ID if successful, None otherwise
    """
    service = AILoggingService()
    return await service.log_operation(
        user_id=user_id,
        model_id=model_id,
        operation_category=operation_category,
        tokens_cost=tokens_cost,
        **kwargs
    )


def log_ai_operation_background(
    user_id: int,
    model_id: str,
    operation_category: str,
    tokens_cost: int,
    **kwargs
) -> None:
    """
    Log an AI operation in the background (fire-and-forget).

    This function schedules the logging as a background task
    and returns immediately. Use this when you don't need
    to wait for the logging to complete.

    Args:
        user_id: User ID
        model_id: Model identifier
        operation_category: Category code
        tokens_cost: Tokens charged
        **kwargs: Additional arguments for log_operation
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(
                log_ai_operation(
                    user_id=user_id,
                    model_id=model_id,
                    operation_category=operation_category,
                    tokens_cost=tokens_cost,
                    **kwargs
                )
            )
        else:
            # Fallback for sync context
            loop.run_until_complete(
                log_ai_operation(
                    user_id=user_id,
                    model_id=model_id,
                    operation_category=operation_category,
                    tokens_cost=tokens_cost,
                    **kwargs
                )
            )
    except Exception as e:
        logger.error(
            "background_logging_failed",
            user_id=user_id,
            model=model_id,
            error=str(e),
        )


# Global instance for convenience
ai_logger = AILoggingService()
