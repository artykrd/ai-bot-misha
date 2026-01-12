"""
Billing service for calculating and managing token costs.

This service handles:
- Token cost calculation for text, image, and video models
- Token deduction from user subscriptions
- Cost tracking and logging
"""
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.billing_config import (
    ModelType,
    get_text_model_billing,
    get_image_model_billing,
    get_video_model_billing,
    calculate_text_cost,
    get_fixed_cost,
    tokens_to_rub,
)
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError, SubscriptionExpiredError
from app.services.subscription.subscription_service import SubscriptionService
from app.database.repositories.ai_request import AIRequestRepository
from app.database.models.ai_request import AIRequest

logger = get_logger(__name__)


class BillingService:
    """Service for billing operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.subscription_service = SubscriptionService(session)
        self.ai_request_repository = AIRequestRepository(session)

    async def calculate_and_charge_text(
        self,
        user_id: int,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        prompt: Optional[str] = None,
    ) -> Tuple[int, AIRequest]:
        """
        Calculate cost for text generation and charge user.

        Args:
            user_id: User ID
            model_id: Text model identifier
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            prompt: Optional prompt text for logging

        Returns:
            Tuple of (tokens_charged, ai_request_record)

        Raises:
            ValueError: If model not found
            InsufficientTokensError: If user doesn't have enough tokens
            SubscriptionExpiredError: If subscription expired
        """
        # Get billing config
        billing = get_text_model_billing(model_id)
        if not billing:
            raise ValueError(f"Unknown text model: {model_id}")

        # Calculate cost
        tokens_cost = billing.calculate_cost(prompt_tokens, completion_tokens)

        logger.info(
            "text_billing_calculated",
            user_id=user_id,
            model=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            tokens_cost=tokens_cost,
            cost_rub=tokens_to_rub(tokens_cost),
        )

        # Create AI request record (pending)
        ai_request = AIRequest(
            user_id=user_id,
            request_type="text",
            ai_model=model_id,
            prompt=prompt,
            tokens_cost=tokens_cost,
            status="pending",
        )
        self.session.add(ai_request)
        await self.session.commit()
        await self.session.refresh(ai_request)

        # Charge user
        try:
            await self.subscription_service.check_and_use_tokens(user_id, tokens_cost)
        except (InsufficientTokensError, SubscriptionExpiredError) as e:
            # Update AI request as failed
            ai_request.status = "failed"
            ai_request.error_message = str(e)
            await self.session.commit()
            raise

        logger.info(
            "text_billing_charged",
            user_id=user_id,
            model=model_id,
            tokens_cost=tokens_cost,
            ai_request_id=ai_request.id,
        )

        return tokens_cost, ai_request

    async def calculate_and_charge_fixed(
        self,
        user_id: int,
        model_id: str,
        model_type: ModelType,
        prompt: Optional[str] = None,
    ) -> Tuple[int, AIRequest]:
        """
        Calculate cost for image/video generation and charge user.

        Args:
            user_id: User ID
            model_id: Model identifier
            model_type: Type of model (IMAGE or VIDEO)
            prompt: Optional prompt text for logging

        Returns:
            Tuple of (tokens_charged, ai_request_record)

        Raises:
            ValueError: If model not found
            InsufficientTokensError: If user doesn't have enough tokens
            SubscriptionExpiredError: If subscription expired
        """
        # Get billing config
        tokens_cost = get_fixed_cost(model_id, model_type)
        if tokens_cost is None:
            raise ValueError(f"Unknown {model_type} model: {model_id}")

        logger.info(
            f"{model_type}_billing_calculated",
            user_id=user_id,
            model=model_id,
            tokens_cost=tokens_cost,
            cost_rub=tokens_to_rub(tokens_cost),
        )

        # Create AI request record (pending)
        ai_request = AIRequest(
            user_id=user_id,
            request_type=model_type.value,
            ai_model=model_id,
            prompt=prompt,
            tokens_cost=tokens_cost,
            status="pending",
        )
        self.session.add(ai_request)
        await self.session.commit()
        await self.session.refresh(ai_request)

        # Charge user
        try:
            await self.subscription_service.check_and_use_tokens(user_id, tokens_cost)
        except (InsufficientTokensError, SubscriptionExpiredError) as e:
            # Update AI request as failed
            ai_request.status = "failed"
            ai_request.error_message = str(e)
            await self.session.commit()
            raise

        logger.info(
            f"{model_type}_billing_charged",
            user_id=user_id,
            model=model_id,
            tokens_cost=tokens_cost,
            ai_request_id=ai_request.id,
        )

        return tokens_cost, ai_request

    async def mark_request_completed(
        self,
        ai_request_id: int,
        response_file_path: Optional[str] = None,
        processing_time_seconds: Optional[int] = None,
    ) -> None:
        """
        Mark AI request as completed.

        Args:
            ai_request_id: AI request ID
            response_file_path: Optional path to generated file
            processing_time_seconds: Optional processing time
        """
        ai_request = await self.ai_request_repository.get_by_id(ai_request_id)
        if not ai_request:
            logger.warning("ai_request_not_found", ai_request_id=ai_request_id)
            return

        ai_request.status = "completed"
        if response_file_path:
            ai_request.response_file_path = response_file_path
        if processing_time_seconds:
            ai_request.processing_time_seconds = processing_time_seconds

        await self.session.commit()

        logger.info(
            "ai_request_completed",
            ai_request_id=ai_request_id,
            user_id=ai_request.user_id,
            model=ai_request.ai_model,
            tokens_cost=ai_request.tokens_cost,
        )

    async def mark_request_failed(
        self,
        ai_request_id: int,
        error_message: str,
        refund_tokens: bool = True,
    ) -> None:
        """
        Mark AI request as failed and optionally refund tokens.

        Args:
            ai_request_id: AI request ID
            error_message: Error message
            refund_tokens: Whether to refund tokens to user
        """
        ai_request = await self.ai_request_repository.get_by_id(ai_request_id)
        if not ai_request:
            logger.warning("ai_request_not_found", ai_request_id=ai_request_id)
            return

        ai_request.status = "failed"
        ai_request.error_message = error_message

        # Refund tokens if requested
        if refund_tokens and ai_request.tokens_cost > 0:
            # Get active subscription and refund tokens
            subscription = await self.subscription_service.get_active_subscription(
                ai_request.user_id
            )
            if subscription:
                subscription.tokens_used = max(
                    0, subscription.tokens_used - ai_request.tokens_cost
                )
                logger.info(
                    "tokens_refunded",
                    user_id=ai_request.user_id,
                    ai_request_id=ai_request_id,
                    tokens_refunded=ai_request.tokens_cost,
                )

        await self.session.commit()

        logger.info(
            "ai_request_failed",
            ai_request_id=ai_request_id,
            user_id=ai_request.user_id,
            model=ai_request.ai_model,
            error=error_message,
            refunded=refund_tokens,
        )

    async def get_model_cost_info(
        self, model_id: str, model_type: ModelType
    ) -> Optional[dict]:
        """
        Get cost information for a model.

        Args:
            model_id: Model identifier
            model_type: Type of model

        Returns:
            Dictionary with cost information or None if model not found
        """
        if model_type == ModelType.TEXT:
            billing = get_text_model_billing(model_id)
            if billing:
                return {
                    "model_id": model_id,
                    "display_name": billing.display_name,
                    "model_type": "text",
                    "billing_type": "dynamic",
                    "base_tokens": billing.base_tokens,
                    "per_gpt_token": billing.per_gpt_token,
                }
        elif model_type == ModelType.IMAGE:
            billing = get_image_model_billing(model_id)
            if billing:
                return {
                    "model_id": model_id,
                    "display_name": billing.display_name,
                    "model_type": "image",
                    "billing_type": "fixed",
                    "tokens_per_generation": billing.tokens_per_generation,
                    "cost_rub": tokens_to_rub(billing.tokens_per_generation),
                    "description_suffix": billing.description_suffix,
                }
        elif model_type == ModelType.VIDEO:
            billing = get_video_model_billing(model_id)
            if billing:
                return {
                    "model_id": model_id,
                    "display_name": billing.display_name,
                    "model_type": "video",
                    "billing_type": "fixed",
                    "tokens_per_generation": billing.tokens_per_generation,
                    "cost_rub": tokens_to_rub(billing.tokens_per_generation),
                    "description_suffix": billing.description_suffix,
                }

        return None

    async def estimate_text_cost(
        self, model_id: str, prompt_tokens: int, estimated_completion_tokens: int
    ) -> Optional[int]:
        """
        Estimate cost for text generation (before making the request).

        Args:
            model_id: Text model identifier
            prompt_tokens: Number of prompt tokens
            estimated_completion_tokens: Estimated completion tokens

        Returns:
            Estimated token cost or None if model not found
        """
        return calculate_text_cost(model_id, prompt_tokens, estimated_completion_tokens)

    async def estimate_fixed_cost(self, model_id: str, model_type: ModelType) -> Optional[int]:
        """
        Get fixed cost for image/video generation.

        Args:
            model_id: Model identifier
            model_type: Type of model

        Returns:
            Token cost or None if model not found
        """
        return get_fixed_cost(model_id, model_type)
