"""
Google Gemini service.
"""
import time
from typing import Optional, List, Dict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)


class GoogleService(BaseAIProvider):
    """Google Gemini API integration."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.google_ai_api_key)

        if not GEMINI_AVAILABLE:
            logger.warning("google_generativeai_not_installed")
            self.client = None
        else:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = True
            else:
                self.client = None

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
            model_instance = genai.GenerativeModel(model)

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
