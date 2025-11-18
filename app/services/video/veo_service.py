"""
Google Veo 3.1 video generation service via Gemini API.
Updated for 2025 API - uses google-generativeai library.
"""
import time
import os
from typing import Optional, Callable, Awaitable
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

# Lazy import - only import when actually used
_genai = None
_GENAI_CHECKED = False


def _get_genai():
    """Lazy import of google.genai."""
    global _genai, _GENAI_CHECKED

    if _GENAI_CHECKED:
        return _genai

    _GENAI_CHECKED = True
    try:
        from google import genai
        _genai = genai
        return _genai
    except Exception as e:
        logger.warning("genai_import_failed", error=str(e))
        _genai = None
        return None


class VeoService(BaseVideoProvider):
    """Google Veo 3.1 API integration via Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        # Veo 3.1 uses Gemini API key (not Vertex AI credentials)
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        super().__init__(api_key=self.api_key or "")

        self.client = None
        self._genai = None

        # Don't import on init, wait until first use
        if self.api_key:
            self._genai = _get_genai()
            if self._genai:
                try:
                    # Initialize Gemini client with API key
                    # Set the API key as environment variable for the library
                    os.environ["GEMINI_API_KEY"] = self.api_key
                    self.client = self._genai.Client(api_key=self.api_key)
                    logger.info("veo_initialized", api_key_present=bool(self.api_key))
                except Exception as e:
                    logger.error("veo_init_failed", error=str(e))
                    self.client = None

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Google Veo 3.1.

        Args:
            prompt: Text description for video generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - duration: Video duration in seconds (4, 6, 8, default: 8)
                - aspect_ratio: Video aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, default: 16:9)
                - negative_prompt: Things to avoid in the video
                - resolution: Video resolution (720p, 1080p, default: 720p)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.client or not self.api_key:
            return VideoResponse(
                success=False,
                error="Google Gemini API key not configured. Set GOOGLE_GEMINI_API_KEY in .env. Get your key at: https://aistudio.google.com/apikey",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Инициализация Veo 3.1...")

            if not self._genai:
                self._genai = _get_genai()

            if not self._genai:
                return VideoResponse(
                    success=False,
                    error="google-generativeai library not available. Install with: pip install google-generativeai>=0.8.3",
                    processing_time=time.time() - start_time
                )

            # Get parameters
            duration = kwargs.get("duration", 8)  # Default 8 seconds
            aspect_ratio = kwargs.get("aspect_ratio", "16:9")
            negative_prompt = kwargs.get("negative_prompt", None)
            resolution = kwargs.get("resolution", "720p")

            if progress_callback:
                await progress_callback(f"🎥 Генерирую видео {duration}с, {aspect_ratio}, {resolution}...")

            # Generate video using Veo model
            video_path = await self._generate_veo_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt,
                resolution=resolution,
                progress_callback=progress_callback
            )

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "veo_video_generated",
                prompt=prompt[:100],
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                time=processing_time
            )

            # Token usage for Veo 3.1: approximately 15,000 tokens per 8-second video
            tokens_used = 15000

            return VideoResponse(
                success=True,
                video_path=video_path,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={
                    "provider": "veo",
                    "model": "veo-3.1-generate-preview",
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "prompt": prompt
                }
            )

        except Exception as e:
            error_msg = str(e)

            # Special handling for quota/rate limit errors
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                error_msg = (
                    "❌ Превышена квота API или требуется платная подписка.\n\n"
                    "Veo 3.1 требует:\n"
                    "1. Активную оплату в Google AI Studio\n"
                    "2. Tier 1 или выше API ключ\n\n"
                    "Проверьте:\n"
                    "• https://aistudio.google.com/apikey (ваш API ключ)\n"
                    "• https://ai.dev/usage?tab=rate-limit (использование)\n"
                    "• https://ai.google.dev/pricing (цены и лимиты)\n\n"
                    f"Оригинальная ошибка: {error_msg}"
                )

            logger.error("veo_video_generation_failed", error=error_msg, prompt=prompt[:100])

            if progress_callback:
                await progress_callback(f"❌ Ошибка: см. сообщение ниже")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _generate_veo_video(
        self,
        prompt: str,
        duration: int,
        aspect_ratio: str,
        negative_prompt: Optional[str],
        resolution: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate video using Veo 3.1 model via Gemini API."""

        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # Prepare generation config according to official docs
                config_params = {}

                # Add aspect ratio
                if aspect_ratio:
                    config_params["aspect_ratio"] = aspect_ratio

                # Add negative prompt if provided
                if negative_prompt:
                    config_params["negative_prompt"] = negative_prompt

                # Add resolution if not default
                if resolution:
                    config_params["resolution"] = resolution

                # Add duration
                if duration:
                    config_params["duration_seconds"] = str(duration)

                # Generate video using Veo 3.1 according to official Python example
                # from google import genai
                # client = genai.Client()
                operation = self.client.models.generate_videos(
                    model="veo-3.1-generate-preview",
                    prompt=prompt,
                    config=config_params if config_params else None,
                )

                # Wait for the video to be generated (polling)
                # According to docs: poll until operation.done is True
                max_wait_time = 360  # 6 minutes max (docs say up to 6 min during peak)
                start = time.time()
                poll_interval = 10  # Poll every 10 seconds

                while not operation.done:
                    if time.time() - start > max_wait_time:
                        raise TimeoutError("Video generation timed out after 6 minutes")

                    time.sleep(poll_interval)
                    # Refresh operation status
                    operation = self.client.operations.get(operation)

                # Get the generated video from response
                # According to docs: operation.response.generated_videos[0]
                generated_video = operation.response.generated_videos[0]

                # Save video to storage
                filename = self._generate_filename("mp4")
                video_path = self.storage_path / filename

                # Download and save video file
                # According to docs: client.files.download(file=video.video)
                self.client.files.download(file=generated_video.video)
                generated_video.video.save(str(video_path))

                logger.info(
                    "veo_video_saved",
                    path=str(video_path),
                    size=video_path.stat().st_size
                )

                return str(video_path)

            except Exception as e:
                logger.error("veo_generation_error", error=str(e))
                raise

        try:
            if progress_callback:
                await progress_callback("⏳ Обработка запроса... это может занять 1-6 минут")

            # Generate video in executor to not block async event loop
            video_path = await loop.run_in_executor(None, _generate)

            return video_path

        except Exception as e:
            logger.error("veo_executor_error", error=str(e))
            raise
