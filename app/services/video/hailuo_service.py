"""
Hailuo (MiniMax) AI video generation service.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class HailuoService(BaseVideoProvider):
    """
    Hailuo (MiniMax) API integration for video generation.

    Supports both text-to-video and image-to-video generation.
    Using AI/ML API as the provider.
    """

    BASE_URL = "https://api.aimlapi.com/v2"

    def __init__(self, api_key: Optional[str] = None):
        # Hailuo can use a dedicated API key or fall back to a general AIMLAPI key
        super().__init__(api_key or getattr(settings, 'hailuo_api_key', None) or getattr(settings, 'aimlapi_key', None))
        if not self.api_key:
            logger.warning("hailuo_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Hailuo AI.

        Args:
            prompt: Video generation prompt
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters (image_url for image-to-video)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Hailuo API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Notify user that generation is starting
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Hailuo AI...")

            # Step 1: Create generation request
            generation_id = await self._create_generation(prompt, **kwargs)
            logger.info(
                "hailuo_generation_created",
                generation_id=generation_id
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
                "hailuo_video_generated",
                path=video_path,
                time=processing_time
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                tokens_used=7000,  # Estimated token cost
                metadata={
                    "provider": "hailuo",
                    "generation_id": generation_id
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("hailuo_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation(self, prompt: str, **kwargs) -> str:
        """
        Create video generation request and return generation ID.

        API uses a two-step process:
        1. Create generation task
        2. Poll for completion
        """
        url = f"{self.BASE_URL}/generate/video/minimax/generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "hailuo-02",  # Latest Hailuo model
            "prompt": prompt
        }

        # Optional: image-to-video
        if "image_url" in kwargs:
            payload["image_url"] = kwargs["image_url"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Hailuo API error: {response.status} - {error_text}")

                data = await response.json()

                # The API returns a generation_id or task_id
                if "generation_id" in data:
                    return data["generation_id"]
                elif "id" in data:
                    return data["id"]
                else:
                    raise Exception("No generation ID in response")

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
        url = f"{self.BASE_URL}/generate/video/minimax/generation/{generation_id}"
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
                    status = data.get("status", "unknown")

                    # Update user if status changed
                    if status != last_status and progress_callback:
                        if status == "pending" or status == "queued":
                            await progress_callback("⏳ Видео в очереди...")
                        elif status == "processing" or status == "generating":
                            await progress_callback("⚙️ Генерирую видео...")

                    last_status = status

                    # Check if complete
                    if status == "completed" or status == "success":
                        # Get video URL
                        video_url = data.get("video_url") or data.get("url") or data.get("output", {}).get("url")
                        if not video_url:
                            raise Exception("Video URL not found in response")
                        return video_url

                    # Check if failed
                    if status == "failed" or status == "error":
                        error = data.get("error", {}).get("message", "Unknown error")
                        raise Exception(f"Generation failed: {error}")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
