"""
Kling 3.0 video generation service via official Kling API.

Supports text-to-video, image-to-video (1-2 images).
Uses /v1/videos/omni-video endpoint with JWT authentication.
API model: kling-v3-omni, modes: std (720p) / pro (1080p).
"""
import time
import asyncio
import base64
import jwt
from typing import Optional, Callable, Awaitable, List
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

# Official Kling API
OFFICIAL_API_URL = "https://api-singapore.klingai.com"

# Model name for official API
KLING3_MODEL = "kling-v3-omni"


class Kling3Service(BaseVideoProvider):
    """
    Kling 3.0 API integration via official Kling platform.

    Two-step flow:
    1. POST /v1/videos/omni-video -> returns task_id
    2. Poll GET /v1/videos/omni-video/{task_id} until task_status=succeed

    Supports:
    - Text-to-video (prompt only)
    - Image-to-video (1 image as first frame + prompt)
    - Multi-image-to-video (2 images as start + end frame + prompt)
    - Modes: std (720p), pro (1080p)
    - Duration: 3-15 seconds
    - Aspect ratios: 1:1, 16:9, 9:16
    """

    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.access_key = access_key or getattr(settings, 'kling_access_key', None)
        self.secret_key = secret_key or getattr(settings, 'kling_secret_key', None)
        self.base_url = OFFICIAL_API_URL

        if not self.access_key or not self.secret_key:
            logger.warning("kling3_official_keys_missing")

        super().__init__(self.access_key or "")

        self._jwt_token = None
        self._jwt_expires_at = 0

    def _generate_jwt_token(self) -> str:
        """Generate JWT token for official Kling API authentication."""
        if not self.access_key or not self.secret_key:
            raise ValueError("Kling access_key and secret_key are required")

        current_time = int(time.time())

        # Reuse if valid for 5+ minutes
        if self._jwt_token and current_time < (self._jwt_expires_at - 300):
            return self._jwt_token

        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": current_time + 1800,
            "nbf": current_time - 5,
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)
        self._jwt_token = token
        self._jwt_expires_at = current_time + 1800

        return token

    def _get_auth_headers(self) -> dict:
        token = self._generate_jwt_token()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    async def _image_to_base64(self, image_path: str) -> str:
        """Convert local image file to raw base64 string (no data: prefix)."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(path, "rb") as f:
            image_data = f.read()

        return base64.b64encode(image_data).decode("utf-8")

    async def generate_video(
        self,
        prompt: str,
        model: str = KLING3_MODEL,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Kling 3.0 via official API.

        Args:
            prompt: Video generation prompt
            model: API model name (kling-v3-omni)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - images: List of image paths (0-2 images)
                - duration: Video duration (3-15 seconds)
                - aspect_ratio: Aspect ratio (1:1, 16:9, 9:16)
                - mode: Resolution mode ("std" for 720p, "pro" for 1080p)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        images = kwargs.get("images", [])
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        mode = kwargs.get("mode", "std")

        if not self.access_key or not self.secret_key:
            return VideoResponse(
                success=False,
                error="Kling API ключи не настроены для Kling 3.0",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Kling 3.0...")

            # Build payload
            payload = await self._build_payload(
                prompt=prompt,
                images=images,
                duration=duration,
                aspect_ratio=aspect_ratio,
                mode=mode,
            )

            # Create task
            task_id = await self._create_task(payload)

            logger.info(
                "kling3_task_created",
                task_id=task_id,
                mode=mode,
                duration=duration,
                images_count=len(images)
            )

            if progress_callback:
                await progress_callback("⏳ Видео в очереди на генерацию...")

            # Poll for result
            video_url, video_id = await self._poll_task_status(
                task_id=task_id,
                progress_callback=progress_callback
            )

            # Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "kling3_video_generated",
                path=video_path,
                time=processing_time,
                mode=mode,
                duration=duration,
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                metadata={
                    "provider": "kling3",
                    "model": KLING3_MODEL,
                    "task_id": task_id,
                    "video_id": video_id,
                    "mode": mode,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "images_count": len(images),
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling3_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _build_payload(
        self,
        prompt: str,
        images: List[str],
        duration: int,
        aspect_ratio: str,
        mode: str,
    ) -> dict:
        """Build API request payload for Kling 3.0 official API."""
        if mode not in ("std", "pro"):
            logger.warning("kling3_invalid_mode", mode=mode)
            mode = "std"

        if duration not in range(3, 16):
            logger.warning("kling3_invalid_duration", duration=duration)
            duration = 5

        valid_ratios = ("16:9", "9:16", "1:1")
        if aspect_ratio not in valid_ratios:
            logger.warning("kling3_invalid_aspect_ratio", aspect_ratio=aspect_ratio)
            aspect_ratio = "1:1"

        payload = {
            "model_name": KLING3_MODEL,
            "prompt": prompt,
            "mode": mode,
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
            "sound": "on",
        }

        # Add images as image_list
        if images:
            image_list = []
            if len(images) >= 1:
                b64 = await self._image_to_base64(images[0])
                image_list.append({"image_url": b64, "type": "first_frame"})
            if len(images) >= 2:
                b64 = await self._image_to_base64(images[1])
                image_list.append({"image_url": b64, "type": "end_frame"})
            payload["image_list"] = image_list

        return payload

    async def _create_task(self, payload: dict) -> str:
        """Create a generation task via official Kling API with retry."""
        url = f"{self.base_url}/v1/videos/omni-video"
        timeout = aiohttp.ClientTimeout(total=60)
        max_retries = 3

        for attempt in range(max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        url,
                        headers=self._get_auth_headers(),
                        json=payload
                    ) as response:
                        response_status = response.status

                        # Retry on 5xx
                        if response_status >= 500 and attempt < max_retries:
                            response_text = await response.text()
                            backoff = 2 ** (attempt + 1)
                            logger.warning(
                                "kling3_server_error_retry",
                                status=response_status,
                                attempt=attempt + 1,
                                backoff=backoff,
                                response=response_text[:300],
                            )
                            await asyncio.sleep(backoff)
                            continue

                        if response_status == 401:
                            self._jwt_token = None
                            self._jwt_expires_at = 0
                            error_text = await response.text()
                            raise Exception(f"Ошибка аутентификации. Проверьте ключи API. ({error_text})")

                        if response_status == 429:
                            error_text = await response.text()
                            raise Exception(f"Превышен лимит запросов или недостаточно средств. ({error_text})")

                        if response_status not in [200, 201]:
                            error_text = await response.text()
                            raise Exception(f"Kling API error: {response_status} - {error_text}")

                        data = await response.json()

                        task_id = data.get("data", {}).get("task_id")
                        if not task_id:
                            raise Exception(f"No task_id in API response: {data}")

                        return task_id

            except aiohttp.ClientError as e:
                if attempt < max_retries:
                    backoff = 2 ** (attempt + 1)
                    logger.warning(
                        "kling3_network_error_retry",
                        error=str(e),
                        attempt=attempt + 1,
                        backoff=backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                raise Exception(f"Kling API network error after {max_retries} retries: {e}")

        raise Exception("Kling API: max retries exceeded")

    async def _poll_task_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 1200,
        poll_interval: int = 5,
    ) -> tuple:
        """
        Poll task status until completion.

        Returns:
            Tuple of (video_url, video_id)
        """
        url = f"{self.base_url}/v1/videos/omni-video/{task_id}"
        start_time = time.time()
        last_status = None
        retry_count = 0
        max_retries = 4

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации видео (20 минут)")

                try:
                    async with session.get(
                        url,
                        headers=self._get_auth_headers()
                    ) as response:
                        if response.status == 401:
                            self._jwt_token = None
                            self._jwt_expires_at = 0
                            await asyncio.sleep(poll_interval)
                            continue

                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Status check failed: {response.status} - {error_text}")

                        data = await response.json()
                        task_data = data.get("data", {})
                        status = task_data.get("task_status", "unknown")
                        status_msg = task_data.get("task_status_msg", "")

                        if status != last_status and progress_callback:
                            if status in ["submitted", "pending", "queued"]:
                                await progress_callback("⏳ Видео в очереди...")
                            elif status in ["processing", "running"]:
                                elapsed = int(time.time() - start_time)
                                await progress_callback(f"⚙️ Генерирую видео... ({elapsed}с)")

                        last_status = status
                        retry_count = 0

                        if status in ["succeed", "completed"]:
                            videos = task_data.get("task_result", {}).get("videos", [])
                            if videos:
                                video_url = videos[0].get("url")
                                video_id = videos[0].get("id")
                                return (video_url, video_id)
                            raise Exception("URL видео не найден в ответе")

                        if status in ["failed", "error"]:
                            fail_msg = status_msg or "Неизвестная ошибка"
                            raise Exception(f"Генерация не удалась: {fail_msg}")

                except aiohttp.ClientError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Сетевая ошибка после {max_retries} попыток: {e}")
                    backoff_time = 2 ** retry_count
                    logger.warning(
                        "kling3_poll_retry",
                        retry=retry_count,
                        backoff=backoff_time,
                        error=str(e)
                    )
                    await asyncio.sleep(backoff_time)
                    continue

                await asyncio.sleep(poll_interval)

    async def create_task_only(
        self,
        prompt: str,
        images: List[str] = None,
        duration: int = 5,
        aspect_ratio: str = "1:1",
        mode: str = "std",
    ) -> str:
        """
        Create task and return task_id without waiting for result.
        Useful for callback-based flow.
        """
        if not self.access_key or not self.secret_key:
            raise Exception("Kling API ключи не настроены для Kling 3.0")

        payload = await self._build_payload(
            prompt=prompt,
            images=images or [],
            duration=duration,
            aspect_ratio=aspect_ratio,
            mode=mode,
        )

        return await self._create_task(payload)
