"""
Kling 3.0 video generation service via Kie.ai API.

Supports text-to-video, image-to-video (1-2 images).
Uses callback-based architecture with polling fallback.
API model: kling-3.0/video, modes: std (720p) / pro (1080p).
"""
import time
import asyncio
import base64
from typing import Optional, Callable, Awaitable, List
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

# Callback URL for async notifications
KLING3_CALLBACK_URL = "https://mikhail-bot.archy-tech.ru/api/kling3_callback"


class Kling3Service(BaseVideoProvider):
    """
    Kling 3.0 API integration via Kie.ai.

    Two-step flow:
    1. POST /api/v1/jobs/createTask -> returns taskId
    2. Poll GET /api/v1/jobs/recordInfo?taskId=... until state=success

    Supports:
    - Text-to-video (prompt only)
    - Image-to-video (1 image + prompt)
    - Multi-image-to-video (2 images + prompt)
    - Modes: std (720p), pro (1080p)
    - Duration: 5, 10, 15 seconds
    - Aspect ratios: 1:1, 16:9, 9:16
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'kie_api_key', None) or "")
        if not self.api_key:
            logger.warning("kie_api_key_missing_for_kling3")

    def _get_auth_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def _image_to_base64_url(self, image_path: str) -> str:
        """Convert local image file to base64 data URL."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(path, "rb") as f:
            image_data = f.read()

        # Detect mime type from extension
        ext = path.suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")

        b64 = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

    async def generate_video(
        self,
        prompt: str,
        model: str = "kling-3.0/video",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Kling 3.0 via Kie.ai API.

        Args:
            prompt: Video generation prompt
            model: API model name (always "kling-3.0/video")
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - images: List of image paths (0-2 images)
                - duration: Video duration (5, 10, or 15 seconds)
                - aspect_ratio: Aspect ratio (1:1, 16:9, 9:16)
                - mode: Resolution mode ("std" for 720p, "pro" for 1080p)
                - version: UI version string for billing (unused here, billing handled externally)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        images = kwargs.get("images", [])
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        mode = kwargs.get("mode", "std")

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Kie.ai API ключ не настроен для Kling 3.0",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Kling 3.0...")

            # Build payload
            payload = self._build_payload(
                prompt=prompt,
                images=images,
                duration=duration,
                aspect_ratio=aspect_ratio,
                mode=mode,
            )

            # Attach images if provided
            if images:
                payload = await self._attach_images_to_payload(payload, images)

            # Step 1: Create task
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

            # Step 2: Poll for result
            video_url = await self._poll_task_status(
                task_id=task_id,
                progress_callback=progress_callback
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
                    "model": "kling-3.0/video",
                    "task_id": task_id,
                    "mode": mode,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "images_count": len(images),
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling3_generation_failed", error=error_msg)

            # User-friendly messages for server errors
            if "500" in error_msg and "Server exception" in error_msg:
                error_msg = (
                    "⚠️ Сервер Kling 3.0 временно недоступен.\n"
                    "Попробуйте повторить запрос через несколько минут."
                )

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    def _build_payload(
        self,
        prompt: str,
        images: List[str],
        duration: int,
        aspect_ratio: str,
        mode: str,
    ) -> dict:
        """Build API request payload for Kling 3.0."""
        # Validate mode
        if mode not in ("std", "pro"):
            logger.warning("kling3_invalid_mode", mode=mode)
            mode = "std"

        # Validate duration
        if duration not in (5, 10, 15):
            logger.warning("kling3_invalid_duration", duration=duration)
            duration = 5

        # Validate aspect_ratio
        valid_ratios = ("16:9", "9:16", "1:1")
        if aspect_ratio not in valid_ratios:
            logger.warning("kling3_invalid_aspect_ratio", aspect_ratio=aspect_ratio)
            aspect_ratio = "1:1"

        payload = {
            "model": "kling-3.0/video",
            "input": {
                "mode": mode,
                "prompt": prompt,
                "duration": str(duration),
                "aspect_ratio": aspect_ratio,
                "multi_shots": False,
                "sound": True,
            }
        }

        return payload

    async def _attach_images_to_payload(self, payload: dict, images: List[str]) -> dict:
        """Attach base64-encoded images to the payload."""
        if len(images) >= 1:
            payload["input"]["image"] = await self._image_to_base64_url(images[0])
        if len(images) >= 2:
            payload["input"]["image_tail"] = await self._image_to_base64_url(images[1])
        return payload

    async def _create_task(self, payload: dict) -> str:
        """Create a generation task via Kie.ai API with retry for transient errors."""
        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
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

                        # Retry on 5xx server errors
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

                        data = await response.json()

                        if data.get("code") != 200:
                            error_msg = data.get("msg") or data.get("message") or "Unknown error"
                            error_code = data.get("code", "unknown")

                            # Retry on server-side error codes
                            if isinstance(error_code, int) and error_code >= 500 and attempt < max_retries:
                                backoff = 2 ** (attempt + 1)
                                logger.warning(
                                    "kling3_api_error_retry",
                                    error_code=error_code,
                                    error_msg=error_msg,
                                    attempt=attempt + 1,
                                    backoff=backoff,
                                )
                                await asyncio.sleep(backoff)
                                continue

                            if error_code == 401:
                                raise Exception("Ошибка аутентификации. Проверьте KIE_API_KEY.")
                            elif error_code == 402:
                                raise Exception("Недостаточно средств на аккаунте Kie.ai.")
                            elif error_code == 429:
                                raise Exception("Превышен лимит запросов. Попробуйте позже.")
                            else:
                                raise Exception(f"Kie.ai API error ({error_code}): {error_msg}")

                        task_id = data.get("data", {}).get("taskId")
                        if not task_id:
                            raise Exception("No taskId in API response")

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
                raise Exception(f"Kie.ai API network error after {max_retries} retries: {e}")

    async def _poll_task_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 1200,
        poll_interval: int = 10,
    ) -> str:
        """
        Poll task status until completion.

        Returns:
            Video URL from resultJson
        """
        url = f"{self.BASE_URL}/api/v1/jobs/recordInfo"
        start_time = time.time()
        last_state = None
        retry_count = 0
        max_retries = 4

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации видео (20 минут)")

                try:
                    async with session.get(
                        url,
                        headers=self._get_auth_headers(),
                        params={"taskId": task_id}
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Status check failed: {response.status} - {error_text}")

                        data = await response.json()

                        if data.get("code") != 200:
                            error_msg = data.get("msg", "Unknown error")
                            raise Exception(f"Status API error: {error_msg}")

                        task_data = data.get("data", {})
                        state = task_data.get("state", "unknown")

                        # Update progress on state change
                        if state != last_state and progress_callback:
                            if state == "waiting":
                                elapsed = int(time.time() - start_time)
                                await progress_callback(f"⚙️ Генерирую видео... ({elapsed}с)")

                        last_state = state
                        retry_count = 0

                        if state == "success":
                            # Extract video URL from resultJson
                            result_json_str = task_data.get("resultJson", "{}")
                            import json
                            try:
                                result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                            except json.JSONDecodeError:
                                raise Exception("Ошибка разбора результата генерации")

                            result_urls = result_json.get("resultUrls", [])
                            if not result_urls:
                                raise Exception("URL видео не найден в ответе")

                            return result_urls[0]

                        if state == "fail":
                            fail_msg = task_data.get("failMsg") or "Неизвестная ошибка"
                            fail_code = task_data.get("failCode") or ""
                            raise Exception(f"Генерация не удалась: {fail_msg} ({fail_code})")

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
        Create task and return taskId without waiting for result.
        Useful for callback-based flow.
        """
        if not self.api_key:
            raise Exception("Kie.ai API ключ не настроен для Kling 3.0")

        payload = self._build_payload(
            prompt=prompt,
            images=images or [],
            duration=duration,
            aspect_ratio=aspect_ratio,
            mode=mode,
        )

        # Attach images if provided
        if images:
            payload = await self._attach_images_to_payload(payload, images)

        payload["callBackUrl"] = KLING3_CALLBACK_URL

        return await self._create_task(payload)
