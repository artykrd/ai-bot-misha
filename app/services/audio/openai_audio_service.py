"""
OpenAI audio services: Whisper (STT) and TTS.
"""
import time
from typing import Optional, Callable, Awaitable
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.audio.base import BaseAudioProvider, AudioResponse

logger = get_logger(__name__)


class OpenAIAudioService(BaseAudioProvider):
    """OpenAI audio services: Whisper and TTS."""

    BASE_URL = "https://api.openai.com/v1"

    # Available TTS voices
    TTS_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.openai_api_key)
        if not self.api_key:
            logger.warning("openai_api_key_missing")

    async def generate_audio(
        self,
        prompt: str,
        voice: str = "alloy",
        model: str = "tts-1",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> AudioResponse:
        """
        Generate speech using OpenAI TTS.

        Args:
            prompt: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters

        Returns:
            AudioResponse with audio path or error
        """
        start_time = time.time()

        if not self.api_key:
            return AudioResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        if voice not in self.TTS_VOICES:
            return AudioResponse(
                success=False,
                error=f"Invalid voice. Available: {', '.join(self.TTS_VOICES)}",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎙️ Генерирую речь...")

            # Generate speech
            audio_path = await self._generate_tts(prompt, voice, model)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Аудио готово!")

            logger.info(
                "openai_tts_generated",
                voice=voice,
                model=model,
                path=audio_path,
                time=processing_time
            )

            return AudioResponse(
                success=True,
                audio_path=audio_path,
                processing_time=processing_time,
                metadata={
                    "provider": "openai",
                    "service": "tts",
                    "voice": voice,
                    "model": model
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("openai_tts_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return AudioResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> AudioResponse:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'ru', 'en')
            **kwargs: Additional parameters

        Returns:
            AudioResponse with transcribed text
        """
        start_time = time.time()

        if not self.api_key:
            return AudioResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Transcribe audio
            text = await self._transcribe_whisper(audio_path, language)

            processing_time = time.time() - start_time

            logger.info(
                "openai_whisper_transcribed",
                path=audio_path,
                language=language,
                time=processing_time
            )

            return AudioResponse(
                success=True,
                text=text,
                processing_time=processing_time,
                metadata={
                    "provider": "openai",
                    "service": "whisper",
                    "language": language
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("openai_whisper_failed", error=error_msg)

            return AudioResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _generate_tts(
        self,
        text: str,
        voice: str,
        model: str
    ) -> str:
        """Generate speech and save to file."""
        url = f"{self.BASE_URL}/audio/speech"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "input": text,
            "voice": voice
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI TTS error: {response.status} - {error_text}")

                # Save audio file
                filename = self._generate_filename("mp3")
                file_path = self.storage_path / filename

                with open(file_path, 'wb') as f:
                    f.write(await response.read())

                return str(file_path)

    async def _transcribe_whisper(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> str:
        """Transcribe audio file using Whisper."""
        url = f"{self.BASE_URL}/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        # Read audio file
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Prepare form data
        data = aiohttp.FormData()
        data.add_field('file',
                       open(audio_path, 'rb'),
                       filename=audio_file.name,
                       content_type='audio/mpeg')
        data.add_field('model', 'whisper-1')

        if language:
            data.add_field('language', language)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI Whisper error: {response.status} - {error_text}")

                result = await response.json()
                return result.get("text", "")
