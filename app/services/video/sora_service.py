"""
OpenAI Sora video generation service.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class SoraService(BaseVideoProvider):
    """OpenAI Sora API integration for video generation.

    Note: Sora API access requires explicit invitation from OpenAI.
    As of 2025, the API is not publicly available.
    """

    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.openai_api_key)
        if not self.api_key:
            logger.warning("sora_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        model: str = "sora-2",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Sora models.

        Args:
            prompt: Video generation prompt
            model: Model name (sora-2 or sora-2-pro)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters (duration, aspect_ratio, etc.)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Notify user that generation is starting
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео...")

            # Step 1: Create video generation request
            generation_id = await self._create_generation(prompt, model, **kwargs)
            logger.info(
                "sora_generation_created",
                generation_id=generation_id,
                model=model
            )

            # Step 2: Poll for completion
            video_url = await self._poll_generation_status(
                generation_id,
                progress_callback
            )

            # Step 3: Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "sora_video_generated",
                model=model,
                path=video_path,
                time=processing_time
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                metadata={
                    "model": model,
                    "generation_id": generation_id
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("sora_generation_failed", error=error_msg, model=model)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> str:
        """Create video generation request and return generation ID.

        API Endpoint: POST /v1/videos
        Documentation: https://platform.openai.com/docs/guides/video-generation
        """
        url = f"{self.BASE_URL}/videos"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt
        }

        # Optional parameters
        # Duration: "4", "8", or "12" seconds (string)
        if "duration" in kwargs:
            payload["seconds"] = str(kwargs["duration"])
        # Size: resolution string like "1920x1080", "1280x720"
        if "size" in kwargs:
            payload["size"] = kwargs["size"]
        if "resolution" in kwargs:
            # Convert resolution to size format if needed
            payload["size"] = kwargs["resolution"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Sora API error: {response.status} - {error_text}")

                data = await response.json()
                return data["id"]

    async def _poll_generation_status(
        self,
        generation_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,  # 10 minutes
        poll_interval: int = 5  # 5 seconds
    ) -> str:
        """
        Poll generation status until complete.

        Returns:
            URL of the generated video
        """
        url = f"{self.BASE_URL}/videos/{generation_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if time.time() - start_time > max_wait_time:
                    raise Exception("Video generation timeout")

                # Poll status
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    data = await response.json()
                    status = data["status"]

                    # Update user if status changed
                    if status != last_status and progress_callback:
                        if status == "processing":
                            await progress_callback("⚙️ Обрабатываю видео...")
                        elif status == "rendering":
                            await progress_callback("🎨 Рендерю видео...")
                        elif status == "finalizing":
                            await progress_callback("🔄 Почти готово...")

                    last_status = status

                    # Check if complete
                    if status == "completed":
                        # Return video URL
                        if "url" in data:
                            return data["url"]
                        elif "output" in data and "url" in data["output"]:
                            return data["output"]["url"]
                        else:
                            raise Exception("Video URL not found in response")

                    # Check if failed
                    if status == "failed":
                        error = data.get("error", {}).get("message", "Unknown error")
                        raise Exception(f"Generation failed: {error}")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
