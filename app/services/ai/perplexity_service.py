"""
Perplexity AI service (OpenAI-compatible API with web search).
"""
import asyncio
import time
from typing import Optional, List, Dict

from openai import AsyncOpenAI
import httpx

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)

# Timeout settings for Perplexity requests
PERPLEXITY_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=120.0,  # Web search can take time
    write=30.0,
    pool=10.0
)


class PerplexityService(BaseAIProvider):
    """Perplexity AI API integration (OpenAI-compatible with web search)."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.perplexity_api_key)

        # Perplexity uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai",
            timeout=PERPLEXITY_TIMEOUT,
            max_retries=2
        ) if self.api_key else None

    async def generate_text(
        self,
        prompt: str,
        model: str = "sonar",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate text using Perplexity models with web search."""
        start_time = time.time()

        if not self.client:
            return AIResponse(
                success=False,
                error="Perplexity API key not configured",
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
                "perplexity_text_generated",
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
            logger.error("perplexity_text_generation_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Perplexity does not support image generation."""
        return AIResponse(
            success=False,
            error="Perplexity does not support image generation"
        )
