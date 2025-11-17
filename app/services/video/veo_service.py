"""
Google Veo 3.1 video generation service via Vertex AI.
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
_vertexai = None
_VEO_CHECKED = False


def _get_vertexai():
    """Lazy import of google.cloud.aiplatform."""
    global _vertexai, _VEO_CHECKED

    if _VEO_CHECKED:
        return _vertexai

    _VEO_CHECKED = True
    try:
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel, VideoGenerationModel
        _vertexai = {
            'vertexai': vertexai,
            'VideoGenerationModel': VideoGenerationModel,
            'ImageGenerationModel': ImageGenerationModel
        }
        return _vertexai
    except Exception as e:
        logger.warning("vertexai_import_failed", error=str(e))
        _vertexai = None
        return None


class VeoService(BaseVideoProvider):
    """Google Veo 3.1 API integration via Vertex AI."""

    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        # Veo doesn't require API key, it uses Google Cloud credentials
        super().__init__(api_key="")

        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.client = None
        self._vertexai = None

        # Don't import on init, wait until first use
        if self.project_id:
            self._vertexai = _get_vertexai()
            if self._vertexai:
                try:
                    # Initialize Vertex AI
                    self._vertexai['vertexai'].init(
                        project=self.project_id,
                        location=self.location
                    )
                    self.client = True
                    logger.info(
                        "veo_initialized",
                        project=self.project_id,
                        location=self.location
                    )
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
                - duration: Video duration in seconds (5-10, default: 5)
                - aspect_ratio: Video aspect ratio (1:1, 16:9, 9:16, default: 16:9)
                - negative_prompt: Things to avoid in the video

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.client or not self.project_id:
            return VideoResponse(
                success=False,
                error="Google Cloud project not configured or Vertex AI not initialized",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Инициализация Veo 3.1...")

            if not self._vertexai:
                self._vertexai = _get_vertexai()

            if not self._vertexai:
                return VideoResponse(
                    success=False,
                    error="Vertex AI library not available",
                    processing_time=time.time() - start_time
                )

            # Get parameters
            duration = kwargs.get("duration", 5)
            aspect_ratio = kwargs.get("aspect_ratio", "16:9")
            negative_prompt = kwargs.get("negative_prompt", None)

            if progress_callback:
                await progress_callback(f"🎥 Генерирую видео ({duration}с, {aspect_ratio})...")

            # Generate video using Veo model
            video_path = await self._generate_veo_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt,
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
                time=processing_time
            )

            # Estimate token usage (Veo is expensive)
            # Rough estimate: ~15,000 tokens for 5s video
            tokens_used = int(duration * 3000)

            return VideoResponse(
                success=True,
                video_path=video_path,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={
                    "provider": "veo",
                    "model": "veo-3.1",
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("veo_video_generation_failed", error=error_msg, prompt=prompt[:100])

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

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
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate video using Veo model."""

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # Load the Veo model
                model = self._vertexai['VideoGenerationModel'].from_pretrained("veo-3.1")

                # Generate video
                # Note: Veo API might be in preview and syntax can change
                response = model.generate_videos(
                    prompt=prompt,
                    number_of_videos=1,
                    aspect_ratio=aspect_ratio,
                    negative_prompt=negative_prompt,
                )

                # Get the first video from response
                video = response.videos[0]

                # Save video to storage
                filename = self._generate_filename("mp4")
                video_path = self.storage_path / filename

                # Write video bytes to file
                with open(video_path, 'wb') as f:
                    f.write(video._video_bytes)

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
                await progress_callback("⏳ Обработка запроса... (это может занять 1-2 минуты)")

            # Generate video in executor
            video_path = await loop.run_in_executor(None, _generate)

            return video_path

        except Exception as e:
            logger.error("veo_executor_error", error=str(e))
            raise
