"""
Mock AI service for testing without API keys.
"""
import time
import asyncio
from typing import Optional, List, Dict

from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)


class MockAIService(BaseAIProvider):
    """Mock AI service that returns fake responses for testing."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or "mock-api-key")

    async def generate_text(
        self,
        prompt: str,
        model: str = "mock-model",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate mock text response."""
        start_time = time.time()

        # Simulate processing delay
        await asyncio.sleep(0.5)

        # Generate mock response based on model
        mock_responses = {
            "gpt-4": f"[Mock GPT-4 Response]\n\nВаш запрос: {prompt[:50]}...\n\nЭто тестовый ответ от GPT-4. API ключ не настроен.",
            "gpt-4-mini": f"[Mock GPT-4 Mini Response]\n\nВаш запрос: {prompt[:50]}...\n\nЭто быстрый тестовый ответ.",
            "claude": f"[Mock Claude 4 Response]\n\nВаш запрос: {prompt[:50]}...\n\nЭто тестовый ответ от Claude.",
            "gemini": f"[Mock Gemini Pro Response]\n\nВаш запрос: {prompt[:50]}...\n\nЭто тестовый ответ от Gemini.",
            "deepseek": f"[Mock DeepSeek Response]\n\nВаш запрос: {prompt[:50]}...\n\nЭто тестовый ответ от DeepSeek.",
        }

        content = mock_responses.get(
            model,
            f"[Mock AI Response]\n\nВаш запрос: {prompt[:100]}\n\nЭто тестовый ответ. API ключи не настроены."
        )

        processing_time = time.time() - start_time

        logger.info(
            "mock_text_generated",
            model=model,
            prompt_length=len(prompt),
            time=processing_time
        )

        return AIResponse(
            success=True,
            content=content,
            tokens_used=100,  # Mock token count
            processing_time=processing_time,
            metadata={"model": model, "mock": True}
        )

    async def generate_image(
        self,
        prompt: str,
        **kwargs
    ) -> AIResponse:
        """Generate mock image response."""
        start_time = time.time()

        await asyncio.sleep(0.5)

        logger.info("mock_image_generated", prompt_length=len(prompt))

        return AIResponse(
            success=True,
            content="[Mock Image URL: https://placeholder.com/800x800]",
            processing_time=time.time() - start_time,
            metadata={"mock": True}
        )

    async def transcribe_audio(
        self,
        audio_path: str,
        **kwargs
    ) -> AIResponse:
        """Mock audio transcription."""
        await asyncio.sleep(0.3)

        return AIResponse(
            success=True,
            content="[Mock Transcription] Это тестовая транскрипция аудио.",
            processing_time=0.3,
            metadata={"mock": True}
        )

    async def generate_audio(
        self,
        prompt: str,
        **kwargs
    ) -> AIResponse:
        """Mock audio generation."""
        await asyncio.sleep(0.3)

        return AIResponse(
            success=True,
            content="[Mock Audio File Path]",
            processing_time=0.3,
            metadata={"mock": True}
        )
