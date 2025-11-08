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
        model: str = "gemini-pro",
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

            model_instance = self._genai.GenerativeModel(model)

            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Gemini uses generate_content (sync) but we can wrap it
            # For true async, need to use the async client
            response = model_instance.generate_content(full_prompt)

            content = response.text
            # Gemini doesn't provide token count in the same way
            tokens_used = 0  # Placeholder

            processing_time = time.time() - start_time

            logger.info(
                "google_text_generated",
                model=model,
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
            logger.error("google_text_generation_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Gemini Pro does not support image generation (Imagen does)."""
        return AIResponse(
            success=False,
            error="Image generation not supported in current Gemini model"
        )
