"""
Luma Labs (Dream Machine) video generation service.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class LumaService(BaseVideoProvider):
    """Luma Labs API integration for video generation."""

    BASE_URL = "https://api.lumalabs.ai/dream-machine/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'luma_api_key', None))
        if not self.api_key:
            logger.warning("luma_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Luma Dream Machine.

        Args:
            prompt: Video generation prompt
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters (aspect_ratio, loop, etc.)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Luma API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Notify user that generation is starting
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Luma...")

            # Step 1: Create generation request
            generation_id = await self._create_generation(prompt, **kwargs)
            logger.info(
                "luma_generation_created",
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
                "luma_video_generated",
                path=video_path,
                time=processing_time
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                metadata={
                    "provider": "luma",
                    "generation_id": generation_id
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("luma_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation(self, prompt: str, **kwargs) -> str:
        """Create video generation request and return generation ID."""
        url = f"{self.BASE_URL}/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "model": kwargs.get("model", "ray-2")  # ray-1-6, ray-2, ray-flash-2, ray-3, ray-hdr-3, ray-flash-3
        }

        # Optional parameters
        if "aspect_ratio" in kwargs:
            payload["aspect_ratio"] = kwargs["aspect_ratio"]  # 16:9, 9:16, 1:1, 4:3, 3:4
        if "loop" in kwargs:
            payload["loop"] = kwargs["loop"]
        if "keyframes" in kwargs:
            # keyframes for image-to-video
            payload["keyframes"] = kwargs["keyframes"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Luma API error: {response.status} - {error_text}")

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
        url = f"{self.BASE_URL}/generations/{generation_id}"
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
                    status = data.get("state", "unknown")

                    # Update user if status changed
                    if status != last_status and progress_callback:
                        if status == "queued":
                            await progress_callback("⏳ В очереди на генерацию...")
                        elif status == "processing":
                            await progress_callback("⚙️ Обрабатываю видео...")
                        elif status == "dreaming":
                            await progress_callback("💭 Dream Machine создаёт видео...")

                    last_status = status

                    # Check if complete
                    if status == "completed":
                        # Get video URL from assets
                        video_url = data.get("assets", {}).get("video")
                        if not video_url:
                            raise Exception("Video URL not found in response")
                        return video_url

                    # Check if failed
                    if status == "failed":
                        error = data.get("failure_reason", "Unknown error")
                        raise Exception(f"Generation failed: {error}")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
