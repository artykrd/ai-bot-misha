"""
Nano Banana 2 image generation service via Kie.ai API.

Supports:
- Text-to-image generation
- Image-to-image generation (up to 8 reference images)
- Image editing (photo + description)
- Resolutions: 1K, 2K, 4K
- Multiple aspect ratios
- Output formats: jpg, png
"""
import time
import asyncio
import json
import base64
from typing import Optional, Callable, Awaitable, List
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


class NanoBanana2Service(BaseImageProvider):
    """
    Nano Banana 2 image generation via Kie.ai API.

    Two-step async flow:
    1. POST /api/v1/jobs/createTask -> returns taskId
    2. Poll GET /api/v1/jobs/recordInfo?taskId=... until state=success

    Supports:
    - Text-to-image (prompt only)
    - Image-to-image (up to 8 images + prompt)
    - Editing (image + editing instruction)
    - Resolutions: 1K, 2K, 4K
    - Aspect ratios: 1:1, 16:9, 9:16, 3:2, 21:9, auto
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'kie_api_key', None) or "")
        if not self.api_key:
            logger.warning("kie_api_key_missing_for_nano_banana_2")

    def _get_auth_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def _upload_image(self, image_path: str) -> str:
        """
        Convert local image file to base64 data URL for API input.

        Args:
            image_path: Path to local image file

        Returns:
            Base64 data URL string
        """
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

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process/edit image using Nano Banana 2.

        Args:
            image_path: Path to input image for editing
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters including:
                - prompt: Text instruction for editing

        Returns:
            ImageResponse with processed image or error
        """
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return ImageResponse(
                success=False,
                error="Prompt is required for image editing"
            )

        # Redirect to generate_image with the image as input
        return await self.generate_image(
            prompt=prompt,
            progress_callback=progress_callback,
            image_paths=[image_path],
            **{k: v for k, v in kwargs.items() if k != "prompt"}
        )

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Nano Banana 2 via Kie.ai API.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - image_paths: List of image paths for image-to-image (up to 8)
                - aspect_ratio: Image aspect ratio (default: "auto")
                - resolution: Image resolution "1K", "2K", "4K" (default: "2K")
                - output_format: Output format "jpg" or "png" (default: "jpg")

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Kie.ai API key not configured. Set KIE_API_KEY in .env",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🍌 Nano Banana 2: начинаю генерацию...")

            # Get parameters
            image_paths = kwargs.get("image_paths", [])
            aspect_ratio = kwargs.get("aspect_ratio", "auto")
            resolution = kwargs.get("resolution", "2K")
            output_format = kwargs.get("output_format", "jpg")

            # Determine mode
            if image_paths:
                mode = "image-to-image"
            else:
                mode = "text-to-image"

            if progress_callback:
                await progress_callback(
                    f"🎨 Генерирую изображение (Nano Banana 2, {mode}, {resolution}, {aspect_ratio})..."
                )

            # Build API payload
            payload = self._build_payload(
                prompt=prompt,
                image_paths=image_paths,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_format=output_format,
            )

            # Attach images if provided
            if image_paths:
                payload = await self._attach_images(payload, image_paths)

            # Step 1: Create task
            task_id = await self._create_task(payload)

            logger.info(
                "nano_banana_2_task_created",
                task_id=task_id,
                mode=mode,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                images_count=len(image_paths),
            )

            if progress_callback:
                await progress_callback("⏳ Изображение генерируется...")

            # Step 2: Poll for result
            image_url = await self._poll_task_status(
                task_id=task_id,
                progress_callback=progress_callback,
            )

            # Step 3: Download image
            if progress_callback:
                await progress_callback("📥 Скачиваю изображение...")

            ext = output_format if output_format in ("jpg", "png") else "jpg"
            filename = self._generate_filename(ext)
            image_path_result = await self._download_file(image_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "nano_banana_2_image_generated",
                path=image_path_result,
                time=processing_time,
                mode=mode,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
            )

            return ImageResponse(
                success=True,
                image_path=image_path_result,
                processing_time=processing_time,
                metadata={
                    "provider": "nano_banana_2",
                    "model": "nano-banana-2",
                    "task_id": task_id,
                    "mode": mode,
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "images_count": len(image_paths),
                    "prompt": prompt,
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(
                "nano_banana_2_generation_failed",
                error=error_msg,
                prompt=prompt[:100] if prompt else "None",
            )

            if progress_callback:
                await progress_callback("❌ Ошибка генерации")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time,
            )

    def _build_payload(
        self,
        prompt: str,
        image_paths: List[str],
        aspect_ratio: str,
        resolution: str,
        output_format: str,
    ) -> dict:
        """Build API request payload for Nano Banana 2."""
        # Validate resolution
        if resolution not in ("1K", "2K", "4K"):
            logger.warning("nano_banana_2_invalid_resolution", resolution=resolution)
            resolution = "2K"

        # Validate output format
        if output_format not in ("jpg", "png"):
            output_format = "jpg"

        payload = {
            "model": "nano-banana-2",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": output_format,
                "google_search": False,
            }
        }

        return payload

    async def _attach_images(self, payload: dict, image_paths: List[str]) -> dict:
        """Attach base64-encoded images to the payload."""
        image_urls = []
        for path in image_paths[:8]:  # Limit to 8 images as per ТЗ
            try:
                data_url = await self._upload_image(path)
                image_urls.append(data_url)
            except Exception as e:
                logger.warning("nano_banana_2_image_attach_failed", path=path, error=str(e))

        if image_urls:
            payload["input"]["image_input"] = image_urls

        return payload

    async def _create_task(self, payload: dict) -> str:
        """Create a generation task via Kie.ai API."""
        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload,
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
                    elif error_code == 422:
                        raise Exception(f"Ошибка валидации параметров: {error_msg}")
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
        max_wait_time: int = 300,
        poll_interval: int = 5,
    ) -> str:
        """
        Poll task status until completion.

        Args:
            task_id: Task ID from createTask response
            progress_callback: Optional progress callback
            max_wait_time: Maximum wait time in seconds (default 5 minutes)
            poll_interval: Polling interval in seconds

        Returns:
            Image URL from resultJson
        """
        url = f"{self.BASE_URL}/api/v1/jobs/recordInfo"
        start_time = time.time()
        last_state = None
        retry_count = 0
        max_retries = 4

        async with aiohttp.ClientSession() as session:
            while True:
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    raise Exception("Таймаут генерации изображения (5 минут)")

                try:
                    async with session.get(
                        url,
                        headers=self._get_auth_headers(),
                        params={"taskId": task_id},
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
                            elapsed_int = int(elapsed)
                            state_messages = {
                                "waiting": f"⏳ В очереди... ({elapsed_int}с)",
                                "queuing": f"⏳ В очереди на генерацию... ({elapsed_int}с)",
                                "generating": f"🎨 Генерирую изображение... ({elapsed_int}с)",
                            }
                            msg = state_messages.get(state)
                            if msg:
                                await progress_callback(msg)

                        last_state = state
                        retry_count = 0

                        if state == "success":
                            # Extract image URL from resultJson
                            result_json_str = task_data.get("resultJson", "{}")
                            try:
                                result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                            except json.JSONDecodeError:
                                raise Exception("Ошибка разбора результата генерации")

                            result_urls = result_json.get("resultUrls", [])
                            if not result_urls:
                                raise Exception("URL изображения не найден в ответе")

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
                        "nano_banana_2_poll_retry",
                        retry=retry_count,
                        backoff=backoff_time,
                        error=str(e),
                    )
                    await asyncio.sleep(backoff_time)
                    continue

                await asyncio.sleep(poll_interval)
