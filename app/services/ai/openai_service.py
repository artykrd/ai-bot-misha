"""
OpenAI service for GPT, DALL-E, Whisper, TTS.
"""
import time
from typing import Optional, List, Dict

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import BaseAIProvider, AIResponse

logger = get_logger(__name__)


class OpenAIService(BaseAIProvider):
    """OpenAI API integration."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.openai_api_key)
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate text using GPT models."""
        start_time = time.time()

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": prompt})

            # O3/O1 models don't support max_tokens parameter - remove it
            if 'o1-' in model or 'o3-' in model:
                kwargs.pop('max_tokens', None)
                kwargs.pop('max_completion_tokens', None)

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
                "openai_text_generated",
                model=model,
                tokens=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=content,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                processing_time=processing_time,
                metadata={"model": model}
            )

        except Exception as e:
            logger.error("openai_text_generation_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> AIResponse:
        """Generate image using DALL-E."""
        start_time = time.time()

        try:
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            image_url = response.data[0].url

            processing_time = time.time() - start_time

            logger.info(
                "openai_image_generated",
                model=model,
                size=size,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=image_url,
                processing_time=processing_time,
                metadata={"model": model, "size": size}
            )

        except Exception as e:
            logger.error("openai_image_generation_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def transcribe_audio(
        self,
        audio_path: str,
        model: str = "whisper-1",
        language: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Transcribe audio using Whisper."""
        start_time = time.time()

        try:
            with open(audio_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=language
                )

            content = response.text

            processing_time = time.time() - start_time

            logger.info(
                "openai_audio_transcribed",
                model=model,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=content,
                processing_time=processing_time,
                metadata={"model": model}
            )

        except Exception as e:
            logger.error("openai_transcription_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def generate_audio(
        self,
        prompt: str,
        model: str = "tts-1",
        voice: str = "alloy",
        **kwargs
    ) -> AIResponse:
        """Generate speech using TTS."""
        start_time = time.time()

        try:
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=prompt
            )

            # Response content is audio bytes
            # Need to save to file
            processing_time = time.time() - start_time

            logger.info(
                "openai_audio_generated",
                model=model,
                voice=voice,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=str(response),  # Placeholder
                processing_time=processing_time,
                metadata={"model": model, "voice": voice}
            )

        except Exception as e:
            logger.error("openai_tts_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
