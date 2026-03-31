"""
Kling O1 (Omni Video) generation service via Kie.ai API.

Supports:
- Text-to-video
- Image/element reference generation
- Video editing (base video + prompt)
- Video feature reference

API model: kling-video-o1
Uses Kie.ai's /api/v1/jobs/createTask endpoint.
"""
import time
import asyncio
import base64
import re
from typing import Optional, Callable, Awaitable, List, Dict
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

# Model name for Kie.ai API
# Note: Kie.ai may update model names. If this fails, check their docs for current names.
KLING_O1_MODEL = "kling-v2-master"

# Callback URL for async notifications
KLING_O1_CALLBACK_URL = "https://mikhail-bot.archy-tech.ru/api/kling_o1_callback"

# Max images: 4 with video, 7 without
MAX_IMAGES_WITH_VIDEO = 4
MAX_IMAGES_WITHOUT_VIDEO = 7

# Max video size for base64 encoding (10MB limit to avoid huge payloads)
MAX_VIDEO_BASE64_SIZE = 10 * 1024 * 1024


def translate_mentions_to_api_format(prompt: str) -> str:
    """
    Translate user-friendly @mentions to API <<<>>> format.

    Mappings:
    - @Video1, @video1 → <<<video_1>>>
    - @Image1, @image1 → <<<image_1>>>
    - @Element1, @element1 → <<<image_N>>> (elements are passed as images)

    Elements are placed before plain images in image_list, so @Element1 maps
    to <<<image_1>>> if element 1 is at index 0, etc.
    """
    def _make_video_ref(m: re.Match) -> str:
        return "<<<video_" + m.group(1) + ">>>"

    def _make_image_ref(m: re.Match) -> str:
        return "<<<image_" + m.group(1) + ">>>"

    # @Video1 → <<<video_1>>>
    prompt = re.sub(r'@[Vv]ideo(\d+)', _make_video_ref, prompt)

    # @Image1 → <<<image_1>>>
    prompt = re.sub(r'@[Ii]mage(\d+)', _make_image_ref, prompt)

    # @Element1 → <<<image_N>>> (elements stored in image_list)
    prompt = re.sub(r'@[Ee]lement(\d+)', _make_image_ref, prompt)

    return prompt


class KlingO1Service(BaseVideoProvider):
    """
    Kling O1 (Omni Video) API integration via Kie.ai.

    Two-step flow:
    1. POST /api/v1/jobs/createTask → returns taskId
    2. Poll GET /api/v1/jobs/recordInfo?taskId=... until state=success

    Supports:
    - Text-to-video (prompt only)
    - Image-to-video (images + prompt)
    - Video editing (video + prompt, video is base type)
    - Video feature reference (video + prompt, video is feature type)
    - Mixed: video + images + prompt

    Modes: std (1080p), pro (4K)
    Duration: 5, 10 seconds
    Aspect ratios: 1:1, 16:9, 9:16 (not applicable for video editing)
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'kie_api_key', None) or "")
        if not self.api_key:
            logger.warning("kie_api_key_missing_for_kling_o1")

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

        ext = path.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "image/jpeg")
        b64 = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

    async def _video_to_base64_url(self, video_path: str) -> Optional[str]:
        """
        Convert local video file to base64 data URL.
        Returns None if file is too large for base64 encoding.
        """
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        file_size = path.stat().st_size
        if file_size > MAX_VIDEO_BASE64_SIZE:
            return None  # Too large for base64

        with open(path, "rb") as f:
            video_data = f.read()

        ext = path.suffix.lower()
        mime_map = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
        }
        mime_type = mime_map.get(ext, "video/mp4")
        b64 = base64.b64encode(video_data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

    async def generate_video(
        self,
        prompt: str,
        model: str = KLING_O1_MODEL,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Kling O1 via Kie.ai API.

        Args:
            prompt: Video generation prompt (can contain @mentions)
            model: API model name
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - images: List of local image paths
                - video_url: Public URL of reference/base video
                - video_is_base: True=video editing, False=feature reference
                - keep_original_sound: 'yes' or 'no' (default 'yes')
                - duration: Video duration (5 or 10 seconds)
                - aspect_ratio: Aspect ratio (1:1, 16:9, 9:16)
                - mode: Resolution mode ('std' for 1080p, 'pro' for 4K)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        images = kwargs.get("images", [])
        video_url = kwargs.get("video_url", None)
        video_is_base = kwargs.get("video_is_base", True)
        keep_original_sound = kwargs.get("keep_original_sound", "yes")
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        mode = kwargs.get("mode", "std")

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Kie.ai API ключ не настроен для Kling O1",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию с Kling O1...")

            # Translate @mentions to API <<<>>> format
            api_prompt = translate_mentions_to_api_format(prompt)

            # Build payload
            payload = await self._build_payload(
                prompt=api_prompt,
                images=images,
                video_url=video_url,
                video_is_base=video_is_base,
                keep_original_sound=keep_original_sound,
                duration=duration,
                aspect_ratio=aspect_ratio,
                mode=mode,
            )

            # Create task
            task_id = await self._create_task(payload)

            logger.info(
                "kling_o1_task_created",
                task_id=task_id,
                mode=mode,
                duration=duration,
                images_count=len(images),
                has_video=bool(video_url),
                video_is_base=video_is_base,
            )

            if progress_callback:
                await progress_callback("⏳ Видео добавлено в очередь на обработку...")

            # Poll for result
            video_url_result = await self._poll_task_status(
                task_id=task_id,
                progress_callback=progress_callback,
            )

            # Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю готовое видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url_result, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "kling_o1_video_generated",
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
                    "provider": "kling_o1",
                    "model": KLING_O1_MODEL,
                    "task_id": task_id,
                    "mode": mode,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "images_count": len(images),
                    "has_video": bool(video_url),
                }
            )

        except Exception as e:
            error_msg = str(e)
            if "model name" in error_msg.lower() and "not supported" in error_msg.lower():
                error_msg = "Модель Kling O1 временно недоступна. Попробуйте позже или используйте другую модель."
                logger.warning("kling_o1_model_not_supported", error=str(e))
            else:
                logger.error("kling_o1_generation_failed", error=error_msg)

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
        video_url: Optional[str],
        video_is_base: bool,
        keep_original_sound: str,
        duration: int,
        aspect_ratio: str,
        mode: str,
    ) -> dict:
        """Build API request payload for Kling O1."""
        if mode not in ("std", "pro"):
            logger.warning("kling_o1_invalid_mode", mode=mode)
            mode = "std"

        if duration not in (5, 10):
            logger.warning("kling_o1_invalid_duration", duration=duration)
            duration = 5

        # Base input
        input_data: Dict = {
            "model_name": KLING_O1_MODEL,
            "prompt": prompt,
            "mode": mode,
        }

        # Duration and aspect_ratio: not applicable for video editing (base type)
        if not (video_url and video_is_base):
            input_data["duration"] = str(duration)
            input_data["aspect_ratio"] = aspect_ratio

        # Add image_list if images provided
        if images:
            image_list = []
            for img_path in images:
                try:
                    b64_url = await self._image_to_base64_url(img_path)
                    image_list.append({"image_url": b64_url})
                except Exception as e:
                    logger.warning("kling_o1_image_encode_failed", path=img_path, error=str(e))
            if image_list:
                input_data["image_list"] = image_list

        # Add video_list if video provided
        if video_url:
            refer_type = "base" if video_is_base else "feature"
            input_data["video_list"] = [
                {
                    "video_url": video_url,
                    "refer_type": refer_type,
                    "keep_original_sound": keep_original_sound,
                }
            ]

        payload = {
            "model": KLING_O1_MODEL,
            "input": input_data,
        }

        return payload

    async def _create_task(self, payload: dict) -> str:
        """Create a generation task via Kie.ai API."""
        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                data = await response.json()

                if data.get("code") != 200:
                    error_msg = data.get("msg") or data.get("message") or "Unknown error"
                    error_code = data.get("code", "unknown")

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
                            raise Exception(
                                f"Status check failed: {response.status} - {error_text}"
                            )

                        data = await response.json()

                        if data.get("code") != 200:
                            error_msg = data.get("msg", "Unknown error")
                            raise Exception(f"Status API error: {error_msg}")

                        task_data = data.get("data", {})
                        state = task_data.get("state", "unknown")

                        if state != last_state and progress_callback:
                            if state == "waiting":
                                elapsed = int(time.time() - start_time)
                                await progress_callback(
                                    f"⚙️ Обрабатываю видео Kling O1... ({elapsed}с)"
                                )

                        last_state = state
                        retry_count = 0

                        if state == "success":
                            import json
                            result_json_str = task_data.get("resultJson", "{}")
                            try:
                                result_json = (
                                    json.loads(result_json_str)
                                    if isinstance(result_json_str, str)
                                    else result_json_str
                                )
                            except json.JSONDecodeError:
                                raise Exception("Ошибка разбора результата генерации")

                            result_urls = result_json.get("resultUrls", [])
                            if not result_urls:
                                raise Exception("URL видео не найден в ответе")

                            return result_urls[0]

                        if state == "fail":
                            fail_msg = task_data.get("failMsg") or "Неизвестная ошибка"
                            fail_code = task_data.get("failCode") or ""
                            raise Exception(
                                f"Генерация не удалась: {fail_msg} ({fail_code})"
                            )

                except aiohttp.ClientError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(
                            f"Сетевая ошибка после {max_retries} попыток: {e}"
                        )
                    backoff_time = 2 ** retry_count
                    logger.warning(
                        "kling_o1_poll_retry",
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
        video_url: Optional[str] = None,
        video_is_base: bool = True,
        keep_original_sound: str = "yes",
        duration: int = 5,
        aspect_ratio: str = "1:1",
        mode: str = "std",
    ) -> str:
        """
        Create task and return taskId without waiting for result.
        Used for callback-based async flow.
        """
        if not self.api_key:
            raise Exception("Kie.ai API ключ не настроен для Kling O1")

        api_prompt = translate_mentions_to_api_format(prompt)

        payload = await self._build_payload(
            prompt=api_prompt,
            images=images or [],
            video_url=video_url,
            video_is_base=video_is_base,
            keep_original_sound=keep_original_sound,
            duration=duration,
            aspect_ratio=aspect_ratio,
            mode=mode,
        )

        payload["callBackUrl"] = KLING_O1_CALLBACK_URL

        return await self._create_task(payload)
