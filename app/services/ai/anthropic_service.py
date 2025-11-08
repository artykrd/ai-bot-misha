"""
Anthropic Claude service.
"""
import time
from typing import Optional, List, Dict

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)

# Lazy import
_AsyncAnthropic = None
_ANTHROPIC_CHECKED = False


def _get_anthropic():
    """Lazy import of anthropic."""
    global _AsyncAnthropic, _ANTHROPIC_CHECKED

    if _ANTHROPIC_CHECKED:
        return _AsyncAnthropic

    _ANTHROPIC_CHECKED = True
    try:
        from anthropic import AsyncAnthropic
        _AsyncAnthropic = AsyncAnthropic
        return _AsyncAnthropic
    except Exception as e:
        logger.warning("anthropic_import_failed", error=str(e))
        _AsyncAnthropic = None
        return None


class AnthropicService(BaseAIProvider):
    """Anthropic Claude API integration."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.anthropic_api_key)
        self.client = None

        if self.api_key:
            AsyncAnthropic = _get_anthropic()
            if AsyncAnthropic:
                self.client = AsyncAnthropic(api_key=self.api_key)

    async def generate_text(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        max_tokens: int = 4096,
        **kwargs
    ) -> AIResponse:
        """Generate text using Claude models."""
        start_time = time.time()

        if not self.client:
            return AIResponse(
                success=False,
                error="Anthropic API key not configured or library not installed",
                processing_time=time.time() - start_time
            )

        try:
            messages = []

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": prompt})

            # Claude requires system to be separate parameter
            kwargs_clean = kwargs.copy()
            if system_prompt:
                kwargs_clean["system"] = system_prompt

            response = await self.client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                **kwargs_clean
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            processing_time = time.time() - start_time

            logger.info(
                "anthropic_text_generated",
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
            logger.error("anthropic_text_generation_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Claude does not support image generation."""
        return AIResponse(
            success=False,
            error="Claude does not support image generation"
        )
