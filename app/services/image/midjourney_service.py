"""
Midjourney image generation service via Kie.ai API.
Supports: txt2img, img2img, video, style_reference, omni_reference.
"""
import time
import asyncio
import json
from typing import Optional, Callable, Awaitable, List
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MidjourneyResponse:
    """Standard Midjourney generation response."""
    success: bool
    image_paths: List[str] = None
    error: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0
    metadata: dict = None

    def __post_init__(self):
        if self.image_paths is None:
            self.image_paths = []
        if self.metadata is None:
            self.metadata = {}


class MidjourneyService:
    """Midjourney API integration via Kie.ai for image generation.

    Supports task types:
    - mj_txt2img: Text to image
    - mj_img2img: Image to image
    - mj_video: Image to video
    - mj_style_reference: Style reference
    - mj_omni_reference: Omni reference
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'kie_api_key', None) or ""
        self.storage_path = Path(settings.storage_path) / "images"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.api_key:
            logger.warning("kie_api_key_missing_for_midjourney")

    async def generate_image(
        self,
        prompt: str,
        task_type: str = "mj_txt2img",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> MidjourneyResponse:
        """
        Generate image using Midjourney via Kie.ai API.

        Args:
            prompt: Image generation prompt
            task_type: One of mj_txt2img, mj_img2img, mj_video, mj_style_reference, mj_omni_reference
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - speed: 'relaxed', 'fast', 'turbo' (default: 'fast')
                - file_url: URL of input image (for img2img, video, style_reference)
                - aspect_ratio: Output aspect ratio (default: '16:9')
                - version: Midjourney version (default: '7')
                - variety: Diversity (0-100, default: 10)
                - stylization: Style intensity (0-1000)
                - weirdness: Creativity (0-3000)

        Returns:
            MidjourneyResponse with image paths or error
        """
        start_time = time.time()

        if not self.api_key:
            return MidjourneyResponse(
                success=False,
                error="Kie.ai API ключ не настроен. Добавьте KIE_API_KEY в .env файл.",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎨 Начинаю генерацию изображения с Midjourney...")

            # Build request payload
            payload = self._build_payload(prompt, task_type, **kwargs)

            # Step 1: Create task
            task_id = await self._create_task(payload)
            logger.info("midjourney_task_created", task_id=task_id, task_type=task_type)

            if progress_callback:
                await progress_callback("⏳ Изображение в очереди на генерацию...")

            # Step 2: Poll for completion
            result_urls = await self._poll_task_status(task_id, progress_callback)

            # Step 3: Download images
            if progress_callback:
                await progress_callback("📥 Скачиваю изображения...")

            image_paths = []
            for i, url in enumerate(result_urls):
                filename = self._generate_filename(i)
                file_path = await self._download_file(url, filename)
                image_paths.append(file_path)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "midjourney_image_generated",
                task_type=task_type,
                count=len(image_paths),
                time=processing_time
            )

            return MidjourneyResponse(
                success=True,
                image_paths=image_paths,
                tokens_used=0,  # Will be set by handler
                processing_time=processing_time,
                metadata={
                    "task_type": task_type,
                    "task_id": task_id,
                    "version": kwargs.get("version", "7"),
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("midjourney_generation_failed", error=error_msg, task_type=task_type)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return MidjourneyResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    def _build_payload(self, prompt: str, task_type: str, **kwargs) -> dict:
        """Build API request payload."""
        payload = {
            "taskType": task_type,
            "prompt": prompt,
        }

        # Speed (not used for mj_video and mj_omni_reference)
        if task_type not in ("mj_video", "mj_omni_reference"):
            payload["speed"] = kwargs.get("speed", "fast")

        # Aspect ratio
        if kwargs.get("aspect_ratio"):
            payload["aspectRatio"] = kwargs["aspect_ratio"]

        # Version
        payload["version"] = kwargs.get("version", "7")

        # Image URL for image-based modes
        if kwargs.get("file_url"):
            payload["fileUrls"] = [kwargs["file_url"]]

        # Optional parameters
        if kwargs.get("variety") is not None:
            payload["variety"] = kwargs["variety"]
        if kwargs.get("stylization") is not None:
            payload["stylization"] = kwargs["stylization"]
        if kwargs.get("weirdness") is not None:
            payload["weirdness"] = kwargs["weirdness"]
        if kwargs.get("ow") is not None and task_type == "mj_omni_reference":
            payload["ow"] = kwargs["ow"]

        return payload

    async def _create_task(self, payload: dict) -> str:
        """Create Midjourney generation task via Kie.ai API."""
        url = f"{self.BASE_URL}/api/v1/mj/generate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()

                if data.get("code") != 200:
                    error_msg = data.get("msg", "Unknown error")
                    raise Exception(f"Midjourney API error: {error_msg}")

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
    ) -> list:
        """Poll task status until complete. Returns list of result URLs."""
        url = f"{self.BASE_URL}/api/v1/mj/queryTask"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {"taskId": task_id}

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации изображения (10 минут)")

                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()

                    if data.get("code") != 200:
                        task_data = data.get("data", {})
                        state = task_data.get("state", "unknown") if isinstance(task_data, dict) else "unknown"
                        if state == "fail":
                            fail_msg = task_data.get("failMsg", data.get("msg", "Unknown error"))
                            raise Exception(f"Генерация не удалась: {fail_msg}")
                        # Some status codes are expected while processing
                        if data.get("code") not in (200, 201, 202):
                            error_msg = data.get("msg", "Unknown error")
                            if "processing" not in error_msg.lower() and "pending" not in error_msg.lower():
                                raise Exception(f"Status check failed: {error_msg}")

                    task_data = data.get("data", {})
                    if isinstance(task_data, dict):
                        state = task_data.get("state", "unknown")
                    else:
                        state = "processing"

                    if progress_callback and state != last_status:
                        if state == "pending":
                            await progress_callback("⏳ Изображение в очереди...")
                        elif state in ("processing", "running"):
                            await progress_callback("⚙️ Генерирую изображение...")
                    last_status = state

                    if state == "success":
                        result_urls = task_data.get("resultUrls", [])
                        if not result_urls:
                            raise Exception("Нет URL результата в ответе API")
                        return result_urls

                    if state == "fail":
                        fail_msg = task_data.get("failMsg", "Unknown error")
                        raise Exception(f"Генерация не удалась: {fail_msg}")

                await asyncio.sleep(poll_interval)

    async def _download_file(self, url: str, filename: str) -> str:
        """Download file from URL to storage."""
        file_path = self.storage_path / filename

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())

                    logger.info(
                        "midjourney_image_downloaded",
                        url=url[:100],
                        path=str(file_path),
                        size=file_path.stat().st_size
                    )
                    return str(file_path)
                else:
                    raise Exception(f"Failed to download: HTTP {response.status}")

    def _generate_filename(self, index: int = 0) -> str:
        """Generate unique filename for image."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"mj_{timestamp}_{index}.png"
