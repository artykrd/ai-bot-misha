"""
xAI Grok Video generation service (async polling).
API docs: https://api.x.ai/v1/videos/generations
Model: grok-imagine-video
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_grok_video_tokens_cost
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

XAI_BASE_URL = "https://api.x.ai/v1"
GROK_VIDEO_MODEL = "grok-imagine-video"


class GrokVideoService(BaseVideoProvider):
    """
    xAI Grok video generation via async polling.

    Flow:
    1. POST /v1/videos/generations → request_id
    2. Poll GET /v1/videos/{request_id} until status=done
    3. Download video from returned URL
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, "grok_ai_api", None))
        if not self.api_key:
            logger.warning("grok_ai_api_missing_for_video")

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs,
    ) -> VideoResponse:
        """
        Generate video using Grok Video.

        kwargs:
            resolution: str — "480p" or "720p" (default "480p")
            duration: int — 1-15 seconds (default 5)
            aspect_ratio: str — "16:9"|"9:16"|"1:1"|"4:3"|"3:4"|"3:2"|"2:3" (default "16:9")
            image_path: str — optional local path to first-frame image (image-to-video)
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Grok API ключ не настроен (GROK_AI_API).",
                processing_time=time.time() - start_time,
            )

        resolution = kwargs.get("resolution", "480p")
        duration = int(kwargs.get("duration", 5))
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        # Support both "image_path" (direct call) and "images" list (job service)
        image_path = kwargs.get("image_path", None)
        if not image_path:
            images = kwargs.get("images", [])
            if images:
                image_path = images[0]

        # Clamp duration to valid range
        duration = max(1, min(duration, 15))

        tokens_used = get_grok_video_tokens_cost(resolution, duration)

        if progress_callback:
            mode_str = "изображения в видео" if image_path else "текста в видео"
            await progress_callback(
                f"🎬 Начинаю генерацию Grok Video ({resolution}, {duration}с)..."
            )

        try:
            request_id = await self._submit_generation(
                prompt=prompt,
                resolution=resolution,
                duration=duration,
                aspect_ratio=aspect_ratio,
                image_path=image_path,
            )

            logger.info(
                "grok_video_request_created",
                request_id=request_id,
                resolution=resolution,
                duration=duration,
            )

            video_url = await self._poll_until_done(
                request_id=request_id,
                progress_callback=progress_callback,
            )

            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "grok_video_generated",
                path=video_path,
                time=processing_time,
                resolution=resolution,
                duration=duration,
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                tokens_used=tokens_used,
                metadata={
                    "provider": "grok_video",
                    "model": GROK_VIDEO_MODEL,
                    "request_id": request_id,
                    "resolution": resolution,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                },
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("grok_video_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time,
                tokens_used=tokens_used,
            )

    async def _submit_generation(
        self,
        prompt: str,
        resolution: str,
        duration: int,
        aspect_ratio: str,
        image_path: Optional[str] = None,
    ) -> str:
        """Submit video generation request, return request_id."""
        import base64
        from pathlib import Path

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "model": GROK_VIDEO_MODEL,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        }

        if image_path:
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                ext = Path(image_path).suffix.lower()
                mime = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".webp": "image/webp",
                }.get(ext, "image/jpeg")
                b64 = base64.b64encode(image_bytes).decode()
                payload["image"] = {
                    "type": "base64",
                    "data": f"data:{mime};base64,{b64}",
                }
            except Exception as e:
                logger.warning("grok_video_image_encode_failed", error=str(e))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{XAI_BASE_URL}/videos/generations",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status not in (200, 201, 202):
                    error_text = await response.text()
                    raise Exception(
                        f"Grok Video API error {response.status}: {error_text}"
                    )
                data = await response.json()

        request_id = data.get("request_id")
        if not request_id:
            raise Exception(f"No request_id in response: {data}")
        return request_id

    async def _poll_until_done(
        self,
        request_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait: int = 1200,  # 20 minutes
        poll_interval: int = 8,
    ) -> str:
        """Poll until video is done, return video URL."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{XAI_BASE_URL}/videos/{request_id}"

        start = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start > max_wait:
                    raise Exception("Grok Video: timeout ожидания генерации")

                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status not in (200, 202):
                        error_text = await response.text()
                        raise Exception(
                            f"Grok Video poll error {response.status}: {error_text}"
                        )
                    data = await response.json()

                status = data.get("status", "pending")

                if status != last_status and progress_callback:
                    messages = {
                        "pending": "⏳ Видео в очереди генерации...",
                        "processing": "⚙️ Генерирую видео...",
                    }
                    msg = messages.get(status)
                    if msg:
                        await progress_callback(msg)
                last_status = status

                if status == "done":
                    video_url = data.get("video", {}).get("url")
                    if not video_url:
                        raise Exception("Grok Video: нет URL в ответе")
                    return video_url

                if status in ("expired", "failed"):
                    error = data.get("error", {})
                    raise Exception(
                        f"Grok Video {status}: {error.get('message', 'неизвестная ошибка')}"
                    )

                await asyncio.sleep(poll_interval)
