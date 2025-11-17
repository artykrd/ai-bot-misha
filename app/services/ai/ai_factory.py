"""
AI Service Factory - returns appropriate AI service based on model.
"""
from typing import Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider
from app.services.ai.openai_service import OpenAIService
from app.services.ai.anthropic_service import AnthropicService
from app.services.ai.google_service import GoogleService
from app.services.ai.deepseek_service import DeepSeekService
from app.services.ai.mock_service import MockAIService

logger = get_logger(__name__)


class AIServiceFactory:
    """Factory for creating AI service instances."""

    # Model to provider mapping
    MODEL_PROVIDERS = {
        "gpt-4": "openai",
        "gpt-4-turbo": "openai",
        "gpt-4-mini": "openai",
        "gpt-3.5-turbo": "openai",
        "claude": "anthropic",
        "claude-3-5-sonnet": "anthropic",
        "claude-sonnet-4": "anthropic",
        "claude-3.7": "anthropic",
        "claude-3.5": "anthropic",
        "claude-3-opus": "anthropic",
        "anthropic/claude-3.7": "anthropic",
        "anthropic/claude-3.5": "anthropic",
        "gemini": "google",
        "gemini-pro": "google",
        "gemini-flash-2.0": "google",
        "gemini-2.0-flash-001": "google",
        "google/gemini-2.5-pro-preview": "google",
        "deepseek": "deepseek",
        "deepseek-chat": "deepseek",
    }

    # OpenAI model name mapping
    OPENAI_MODEL_NAMES = {
        "gpt-4": "gpt-4-turbo-preview",
        "gpt-4-mini": "gpt-4-0125-preview",
    }

    # Anthropic model name mapping
    ANTHROPIC_MODEL_NAMES = {
        "claude": "claude-sonnet-4-20250514",
        "claude-3-5-sonnet": "claude-sonnet-4-20250514",
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-sonnet-4-20250514": "claude-sonnet-4-20250514",
        "claude-3.7": "claude-sonnet-4-20250514",
        "claude-3.5": "claude-3-5-sonnet-20241022",
        "anthropic/claude-3.7": "claude-sonnet-4-20250514",
        "anthropic/claude-3.5": "claude-3-5-sonnet-20241022",
    }

    # Google model name mapping
    GOOGLE_MODEL_NAMES = {
        "gemini": "gemini-2.0-flash-exp",
        "gemini-pro": "gemini-2.0-flash-exp",
        "gemini-flash-2.0": "gemini-2.0-flash-exp",
        "gemini-2.0-flash-001": "gemini-2.0-flash-exp",
        "google/gemini-2.5-pro-preview": "gemini-2.0-flash-exp",
    }

    # DeepSeek model name mapping
    DEEPSEEK_MODEL_NAMES = {
        "deepseek": "deepseek-chat",
        "deepseek-chat": "deepseek-chat",
    }

    @classmethod
    def get_provider_name(cls, model: str) -> str:
        """Get provider name for a given model."""
        return cls.MODEL_PROVIDERS.get(model, "openai")

    @classmethod
    def get_real_model_name(cls, model: str) -> str:
        """Get the real API model name."""
        provider = cls.get_provider_name(model)

        if provider == "openai":
            return cls.OPENAI_MODEL_NAMES.get(model, model)
        elif provider == "anthropic":
            return cls.ANTHROPIC_MODEL_NAMES.get(model, model)
        elif provider == "google":
            return cls.GOOGLE_MODEL_NAMES.get(model, model)
        elif provider == "deepseek":
            return cls.DEEPSEEK_MODEL_NAMES.get(model, model)

        return model

    @classmethod
    def create_service(
        cls,
        model: str,
        use_mock: Optional[bool] = None
    ) -> BaseAIProvider:
        """
        Create appropriate AI service for the given model.

        Args:
            model: Model identifier (e.g., "gpt-4", "claude", "gemini")
            use_mock: Force mock mode (default: auto-detect based on API keys)

        Returns:
            BaseAIProvider instance
        """
        provider = cls.get_provider_name(model)

        # Auto-detect mock mode if not specified
        if use_mock is None:
            api_keys = {
                "openai": settings.openai_api_key,
                "anthropic": settings.anthropic_api_key,
                "google": settings.google_ai_api_key,
                "deepseek": settings.deepseek_api_key,
            }
            use_mock = not bool(api_keys.get(provider))

        # Return mock service if requested or no API key
        if use_mock:
            logger.info(
                "using_mock_service",
                model=model,
                provider=provider,
                reason="no_api_key" if use_mock is None else "forced"
            )
            return MockAIService()

        # Create real service
        try:
            if provider == "openai":
                return OpenAIService()
            elif provider == "anthropic":
                return AnthropicService()
            elif provider == "google":
                return GoogleService()
            elif provider == "deepseek":
                return DeepSeekService()
            else:
                logger.warning(
                    "unknown_provider",
                    provider=provider,
                    model=model,
                    fallback="mock"
                )
                return MockAIService()

        except Exception as e:
            logger.error(
                "service_creation_failed",
                provider=provider,
                model=model,
                error=str(e),
                fallback="mock"
            )
            return MockAIService()

    @classmethod
    async def generate_text(
        cls,
        model: str,
        prompt: str,
        use_mock: Optional[bool] = None,
        **kwargs
    ):
        """
        Convenience method to generate text without manually creating service.

        Args:
            model: Model identifier
            prompt: User prompt
            use_mock: Force mock mode
            **kwargs: Additional parameters for the AI service

        Returns:
            AIResponse
        """
        service = cls.create_service(model, use_mock=use_mock)
        real_model = cls.get_real_model_name(model)

        return await service.generate_text(prompt=prompt, model=real_model, **kwargs)
