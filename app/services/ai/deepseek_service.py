"""
DeepSeek service (OpenAI-compatible API).
"""
import time
from typing import Optional, List, Dict

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)


class DeepSeekService(BaseAIProvider):
    """DeepSeek API integration (OpenAI-compatible)."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.deepseek_api_key)

        # DeepSeek uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"
        ) if self.api_key else None

    async def generate_text(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate text using DeepSeek models."""
        start_time = time.time()

        if not self.client:
            return AIResponse(
                success=False,
                error="DeepSeek API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            processing_time = time.time() - start_time

            logger.info(
                "deepseek_text_generated",
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
            logger.error("deepseek_text_generation_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """DeepSeek does not support image generation."""
        return AIResponse(
            success=False,
            error="DeepSeek does not support image generation"
        )
