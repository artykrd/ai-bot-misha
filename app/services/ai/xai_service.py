"""
xAI service for Grok models.
Uses OpenAI-compatible API at https://api.x.ai/v1
"""
import time
from typing import Optional, List, Dict

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)

XAI_BASE_URL = "https://api.x.ai/v1"

XAI_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=120.0,
    write=30.0,
    pool=10.0
)


class XAIService(BaseAIProvider):
    """xAI API integration for Grok models."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.xai_api_key)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=XAI_BASE_URL,
            timeout=XAI_TIMEOUT,
            max_retries=2,
        )

    async def generate_text(
        self,
        prompt: str,
        model: str = "grok-4.3",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate text using Grok models."""
        start_time = time.time()

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": "You are Grok, a maximally truth-seeking AI assistant. Be helpful, insightful, and direct."
                })

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

            processing_time = time.time() - start_time

            logger.info(
                "xai_text_generated",
                model=model,
                tokens=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                processing_time=round(processing_time, 2),
            )

            return AIResponse(
                success=True,
                content=content,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error("xai_text_error", model=model, error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=processing_time,
            )

    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        raise NotImplementedError("Image generation not supported by xAI service")
