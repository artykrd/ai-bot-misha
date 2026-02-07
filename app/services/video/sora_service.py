"""
Sora 2 video generation service via Kie.ai API.
Supports: Stable (text/image-to-video), Pro (text/image-to-video), Characters Pro.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


# Model name mapping for API calls
SORA_MODELS = {
    "sora2-stable-t2v": "sora-2-text-to-video-stable",
    "sora2-stable-i2v": "sora-2-image-to-video-stable",
    "sora2-pro-t2v": "sora-2-text-to-video",
    "sora2-pro-i2v": "sora-2-image-to-video",
    "sora2-characters-pro": "sora-2-characters-pro",
}


class SoraService(BaseVideoProvider):
    """Sora 2 API integration via Kie.ai for video generation.

    Supports 5 models:
    - sora-2-text-to-video-stable (Stable text-to-video)
    - sora-2-image-to-video-stable (Stable image-to-video)
    - sora-2-text-to-video (Pro text-to-video)
    - sora-2-image-to-video (Pro image-to-video)
    - sora-2-characters-pro (Characters Pro)
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'kie_api_key', None) or "")
        if not self.api_key:
            logger.warning("kie_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        model: str = "sora-2-text-to-video-stable",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Sora 2 models via Kie.ai API.

        Args:
            prompt: Video generation prompt
            model: API model name (e.g. sora-2-text-to-video-stable)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - image_url: URL of image for image-to-video models
                - aspect_ratio: 'portrait' or 'landscape' (default: 'landscape')
                - n_frames: '10' or '15' (duration in seconds, default: '10')
                - remove_watermark: bool (only for Pro models)
                - origin_task_id: str (for Characters Pro)
                - character_user_name: str (for Characters Pro)
                - character_prompt: str (for Characters Pro)
                - timestamps: str (for Characters Pro, e.g. '3.55,5.55')

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Kie.ai API ключ не настроен. Добавьте KIE_API_KEY в .env файл.",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Sora 2...")

            # Build request payload
            payload = self._build_payload(model, prompt, **kwargs)

            # Step 1: Create task
            task_id = await self._create_task(payload)
            logger.info("sora_task_created", task_id=task_id, model=model)

            if progress_callback:
                await progress_callback("⏳ Видео в очереди на генерацию...")

            # Step 2: Poll for completion
            result_data = await self._poll_task_status(
                task_id, progress_callback
            )

            # Step 3: Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            result_urls = result_data.get("resultUrls", [])
            if not result_urls:
                # Characters Pro returns resultObject instead
                result_object = result_data.get("resultObject", {})
                if result_object:
                    return VideoResponse(
                        success=True,
                        video_path=None,
                        tokens_used=0,
                        processing_time=time.time() - start_time,
                        metadata={
                            "model": model,
                            "task_id": task_id,
                            "character_id": result_object.get("character_id"),
                            "character_user_name": result_object.get("character_user_name"),
                            "is_character_result": True,
                        }
                    )
                raise Exception("Нет URL результата в ответе API")

            video_url = result_urls[0]
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
                tokens_used=0,  # Will be set by handler based on billing config
                processing_time=processing_time,
                metadata={
                    "model": model,
                    "task_id": task_id
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

    def _build_payload(self, model: str, prompt: str, **kwargs) -> dict:
        """Build API request payload based on model type."""
        payload = {
            "model": model,
            "input": {}
        }

        if model == "sora-2-characters-pro":
            # Characters Pro has different input parameters
            payload["input"]["character_prompt"] = prompt
            if kwargs.get("origin_task_id"):
                payload["input"]["origin_task_id"] = kwargs["origin_task_id"]
            if kwargs.get("character_user_name"):
                payload["input"]["character_user_name"] = kwargs["character_user_name"]
            if kwargs.get("timestamps"):
                payload["input"]["timestamps"] = kwargs["timestamps"]
            if kwargs.get("safety_instruction"):
                payload["input"]["safety_instruction"] = kwargs["safety_instruction"]
        else:
            # Standard video generation models
            payload["input"]["prompt"] = prompt
            payload["input"]["aspect_ratio"] = kwargs.get("aspect_ratio", "landscape")
            payload["input"]["n_frames"] = kwargs.get("n_frames", "10")
            payload["input"]["upload_method"] = "s3"

            # Image-to-video models need image_urls
            if "image" in model and kwargs.get("image_url"):
                payload["input"]["image_urls"] = [kwargs["image_url"]]

            # Pro models support remove_watermark
            if model in ("sora-2-text-to-video", "sora-2-image-to-video"):
                payload["input"]["remove_watermark"] = kwargs.get("remove_watermark", True)

        return payload

    async def _create_task(self, payload: dict) -> str:
        """Create video generation task via Kie.ai API."""
        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()

                if data.get("code") != 200:
                    error_msg = data.get("message", "Unknown error")
                    raise Exception(f"Kie.ai API error: {error_msg}")

                task_id = data.get("data", {}).get("taskId")
                if not task_id:
                    raise Exception("No taskId in API response")

                return task_id

    async def _poll_task_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,
        poll_interval: int = 10
    ) -> dict:
        """Poll task status until complete. Returns result data."""
        url = f"{self.BASE_URL}/api/v1/jobs/queryTask"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {"taskId": task_id}

        start_time = time.time()
        last_status = None
        # Wait before first poll to let the task initialize
        await asyncio.sleep(5)

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации видео (10 минут)")

                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()

                    elapsed = int(time.time() - start_time)

                    if data.get("code") != 200:
                        task_data = data.get("data", {})
                        # Check for explicit failure
                        if isinstance(task_data, dict) and task_data.get("state") == "fail":
                            fail_msg = task_data.get("failMsg", data.get("message", "Unknown error"))
                            raise Exception(f"Генерация не удалась: {fail_msg}")
                        # Non-200 codes are expected while task is initializing/processing - continue polling
                        logger.info("sora_poll_non200", task_id=task_id, code=data.get("code"), message=data.get("message", ""), elapsed=elapsed)
                        await asyncio.sleep(poll_interval)
                        continue

                    task_data = data.get("data", {})
                    state = task_data.get("state", "unknown")
                    logger.info("sora_poll_status", task_id=task_id, state=state, elapsed=elapsed)

                    if progress_callback and state != last_status:
                        if state == "pending":
                            await progress_callback("⏳ Видео в очереди...")
                        elif state == "processing":
                            await progress_callback("⚙️ Генерирую видео...")
                    last_status = state

                    if state == "success":
                        import json
                        result_json_str = task_data.get("resultJson", "{}")
                        try:
                            result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                        except (json.JSONDecodeError, TypeError):
                            result_json = {}
                        return result_json

                    if state == "fail":
                        fail_msg = task_data.get("failMsg", "Unknown error")
                        raise Exception(f"Генерация не удалась: {fail_msg}")

                await asyncio.sleep(poll_interval)
