"""
Kling AI video generation service.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_video_model_billing
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class KlingService(BaseVideoProvider):
    """
    Kling AI API integration for video generation.

    Supports text-to-video, image-to-video, and video effects.
    Can use official Kling API or third-party providers like AI/ML API.
    """

    # Using AI/ML API as default provider
    BASE_URL = "https://api.aimlapi.com"

    def __init__(self, api_key: Optional[str] = None, use_official: bool = False):
        # Kling can use a dedicated API key or fall back to AIMLAPI
        super().__init__(api_key or getattr(settings, 'kling_api_key', None) or getattr(settings, 'aimlapi_key', None))

        if use_official:
            self.BASE_URL = "https://api.klingai.com/v1"

        if not self.api_key:
            logger.warning("kling_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        model: str = "kling-v1.6-pro",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Kling AI.

        Args:
            prompt: Video generation prompt
            model: Model version (kling-v1, kling-v1.5, kling-v1.6-pro, kling-v2, etc.)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters (image_url, duration, aspect_ratio, etc.)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Kling API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Notify user that generation is starting
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Kling AI...")

            # Step 1: Create generation request
            generation_id = await self._create_generation(prompt, model, **kwargs)
            logger.info(
                "kling_generation_created",
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
                "kling_video_generated",
                model=model,
                path=video_path,
                time=processing_time
            )

            kling_billing = get_video_model_billing("kling-video")
            tokens_used = kling_billing.tokens_per_generation

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                tokens_used=tokens_used,
                metadata={
                    "provider": "kling",
                    "model": model,
                    "generation_id": generation_id
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling_generation_failed", error=error_msg, model=model)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation(self, prompt: str, model: str, **kwargs) -> str:
        """Create video generation request and return task ID."""
        url = f"{self.BASE_URL}/generate/video/kling-ai/v1/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt
        }

        # Optional parameters
        if "image_url" in kwargs:
            payload["image"] = kwargs["image_url"]

        if "duration" in kwargs:
            payload["duration"] = kwargs["duration"]  # 5 or 10 seconds

        if "aspect_ratio" in kwargs:
            payload["aspect_ratio"] = kwargs["aspect_ratio"]  # 16:9, 9:16, 1:1, etc.

        if "negative_prompt" in kwargs:
            payload["negative_prompt"] = kwargs["negative_prompt"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Kling API error: {response.status} - {error_text}")

                data = await response.json()

                # Extract task/generation ID
                if "id" in data:
                    return data["id"]
                elif "task_id" in data:
                    return data["task_id"]
                else:
                    raise Exception("No task ID in response")

    async def _poll_generation_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,  # 10 minutes
        poll_interval: int = 5  # 5 seconds
    ) -> str:
        """
        Poll generation status until complete.

        Returns:
            URL of the generated video
        """
        url = f"{self.BASE_URL}/generate/video/kling-ai/v1/generations/{task_id}"
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
                        elif status == "processing" or status == "running":
                            await progress_callback("⚙️ Генерирую видео...")

                    last_status = status

                    # Check if complete
                    if status == "completed" or status == "success" or status == "succeeded":
                        # Get video URL from various possible response formats
                        video_url = (
                            data.get("video_url") or
                            data.get("url") or
                            data.get("output", {}).get("video_url") or
                            data.get("result", {}).get("video_url")
                        )
                        if not video_url:
                            raise Exception("Video URL not found in response")
                        return video_url

                    # Check if failed
                    if status == "failed" or status == "error":
                        error = data.get("error", {}).get("message", "Unknown error")
                        raise Exception(f"Generation failed: {error}")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
