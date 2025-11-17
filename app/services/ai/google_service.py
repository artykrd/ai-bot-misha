"""
Google Gemini service.
"""
import time
from typing import Optional, List, Dict, TYPE_CHECKING

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)

# Lazy import - only import when actually used
_genai = None
_GEMINI_CHECKED = False


def _get_genai():
    """Lazy import of google.generativeai."""
    global _genai, _GEMINI_CHECKED

    if _GEMINI_CHECKED:
        return _genai

    _GEMINI_CHECKED = True
    try:
        import google.generativeai as genai
        _genai = genai
        return _genai
    except Exception as e:
        logger.warning("google_generativeai_import_failed", error=str(e))
        _genai = None
        return None


class GoogleService(BaseAIProvider):
    """Google Gemini API integration."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.google_ai_api_key)
        self.client = None
        self._genai = None

        # Don't import on init, wait until first use
        if self.api_key:
            self._genai = _get_genai()
            if self._genai:
                self._genai.configure(api_key=self.api_key)
                self.client = True

    async def generate_text(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash-exp",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate text using Gemini models."""
        start_time = time.time()

        if not self.client:
            return AIResponse(
                success=False,
                error="Google AI API key not configured or library not installed",
                processing_time=time.time() - start_time
            )

        try:
            if not self._genai:
                self._genai = _get_genai()

            if not self._genai:
                return AIResponse(
                    success=False,
                    error="Google Gemini library not available",
                    processing_time=time.time() - start_time
                )

            # Configure generation settings
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_tokens", 8192),
            }

            # Create model instance
            model_instance = self._genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )

            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Generate content
            response = model_instance.generate_content(full_prompt)

            content = response.text

            # Get token usage if available
            tokens_used = 0
            if hasattr(response, 'usage_metadata'):
                tokens_used = (
                    getattr(response.usage_metadata, 'prompt_token_count', 0) +
                    getattr(response.usage_metadata, 'candidates_token_count', 0)
                )

            processing_time = time.time() - start_time

            logger.info(
                "google_text_generated",
                model=model,
                tokens=tokens_used,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=content,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={"model": model}
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("google_text_generation_failed", error=error_msg, model=model)
            return AIResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Gemini Pro does not support image generation (Imagen does)."""
        return AIResponse(
            success=False,
            error="Image generation not supported in current Gemini model"
        )
