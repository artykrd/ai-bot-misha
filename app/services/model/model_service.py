"""
Service for managing AI models and costs.
This is the SINGLE SOURCE OF TRUTH for model pricing.
"""
from typing import Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.system import AIModel
from app.core.logger import get_logger

logger = get_logger(__name__)


class ModelService:
    """Service for AI model cost management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._cache: Dict[str, AIModel] = {}

    async def get_model_cost(self, model_name: str) -> int:
        """
        Get token cost for a model from database.

        Args:
            model_name: Model system name (e.g., 'veo-3.1', 'sora-2', 'nano-banana')

        Returns:
            Token cost per request

        Raises:
            ValueError: If model not found
        """
        # Check cache first
        if model_name in self._cache:
            return self._cache[model_name].tokens_per_request

        # Query database
        result = await self.session.execute(
            select(AIModel).where(
                AIModel.name == model_name,
                AIModel.is_active == True
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            logger.error("model_not_found", model_name=model_name)
            # Fallback: return default cost
            return 1000

        # Cache result
        self._cache[model_name] = model

        return model.tokens_per_request

    async def get_model(self, model_name: str) -> Optional[AIModel]:
        """Get model object from database."""
        result = await self.session.execute(
            select(AIModel).where(
                AIModel.name == model_name,
                AIModel.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def list_active_models(self, model_type: Optional[str] = None) -> list[AIModel]:
        """List all active models, optionally filtered by type."""
        query = select(AIModel).where(AIModel.is_active == True)

        if model_type:
            query = query.where(AIModel.model_type == model_type)

        result = await self.session.execute(query.order_by(AIModel.display_name))
        return list(result.scalars().all())

    def clear_cache(self):
        """Clear model cache."""
        self._cache.clear()
