"""
Kling AI image generation service.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


class KlingImageService(BaseImageProvider):
    """
    Kling AI API integration for image generation.

    Supports text-to-image and image-to-image generation.
    Can use official Kling API or third-party providers like AI/ML API.
    """

    # Using AI/ML API as default provider (same as video service)
    BASE_URL = "https://api.aimlapi.com"

    def __init__(self, api_key: Optional[str] = None, use_official: bool = False):
        # Kling can use a dedicated API key or fall back to AIMLAPI
        super().__init__(api_key or getattr(settings, 'kling_api_key', None) or getattr(settings, 'aimlapi_key', None))

        if use_official:
            self.BASE_URL = "https://api.klingai.com/v1"

        if not self.api_key:
            logger.warning("kling_api_key_missing")

    async def generate_image(
        self,
        prompt: str,
        model: str = "kling-v1",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Kling AI.

        Args:
            prompt: Text description for image generation
            model: Model version (kling-v1, kling-v1-5, kling-v2, kling-v2-1, default: kling-v1)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - negative_prompt: Negative prompt (optional)
                - image_url: Reference image for image-to-image (optional)
                - image_reference: Reference type (subject, face) for kling-v1-5 (optional)
                - resolution: Image resolution (1k, 2k, default: 1k)
                - aspect_ratio: Aspect ratio (16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3, 21:9)
                - n: Number of images to generate (1-9, default: 1)

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Kling API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Notify user that generation is starting
            if progress_callback:
                await progress_callback("🎨 Начинаю генерацию изображения с Kling AI...")

            # Step 1: Create generation request
            task_id = await self._create_generation(prompt, model, **kwargs)
            logger.info(
                "kling_image_generation_created",
                task_id=task_id,
                model=model
            )

            # Step 2: Poll for completion
            image_url = await self._poll_generation_status(
                task_id,
                progress_callback
            )

            # Step 3: Download image
            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

            filename = self._generate_filename("png")
            image_path = await self._download_file(image_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "kling_image_generated",
                model=model,
                path=image_path,
                time=processing_time
            )

            # Estimate token usage based on resolution and number of images
            n = kwargs.get("n", 1)
            resolution = kwargs.get("resolution", "1k")
            tokens_per_image = 5000 if resolution == "2k" else 3000
            tokens_used = tokens_per_image * n

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "kling",
                    "model": model,
                    "task_id": task_id,
                    "tokens_used": tokens_used
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling_image_generation_failed", error=error_msg, model=model)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation(self, prompt: str, model: str, **kwargs) -> str:
        """Create image generation request and return task ID."""
        # Use different endpoints based on provider
        if "aimlapi.com" in self.BASE_URL:
            # AI/ML API endpoint for Kling image generation
            url = f"{self.BASE_URL}/generate/image/kling-ai/v1/generations"
        else:
            # Official Kling API endpoint
            url = f"{self.BASE_URL}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model_name": model,
            "prompt": prompt
        }

        # Optional parameters
        if "negative_prompt" in kwargs:
            payload["negative_prompt"] = kwargs["negative_prompt"]

        if "image_url" in kwargs:
            payload["image"] = kwargs["image_url"]

        if "image_reference" in kwargs and model == "kling-v1-5":
            payload["image_reference"] = kwargs["image_reference"]

        if "resolution" in kwargs:
            payload["resolution"] = kwargs["resolution"]

        if "aspect_ratio" in kwargs:
            payload["aspect_ratio"] = kwargs["aspect_ratio"]
        else:
            payload["aspect_ratio"] = "1:1"  # Default aspect ratio

        if "n" in kwargs:
            payload["n"] = min(kwargs["n"], 9)  # Max 9 images

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Kling API error: {response.status} - {error_text}")

                data = await response.json()

                # Extract task ID
                if "data" in data and "task_id" in data["data"]:
                    return data["data"]["task_id"]
                elif "task_id" in data:
                    return data["task_id"]
                else:
                    raise Exception("No task ID in response")

    async def _poll_generation_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 300,  # 5 minutes
        poll_interval: int = 3  # 3 seconds
    ) -> str:
        """
        Poll generation status until complete.

        Returns:
            URL of the generated image
        """
        # Use different endpoints based on provider
        if "aimlapi.com" in self.BASE_URL:
            url = f"{self.BASE_URL}/generate/image/kling-ai/v1/generations/{task_id}"
        else:
            url = f"{self.BASE_URL}/images/generations/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if time.time() - start_time > max_wait_time:
                    raise Exception("Image generation timeout")

                # Poll status
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    data = await response.json()

                    # Extract status from response
                    if "data" in data:
                        status_data = data["data"]
                        status = status_data.get("task_status", "unknown")
                        status_msg = status_data.get("task_status_msg", "")
                    else:
                        status = data.get("task_status", "unknown")
                        status_msg = data.get("task_status_msg", "")

                    # Update progress if status changed
                    if status != last_status:
                        last_status = status

                        if progress_callback:
                            if status == "submitted":
                                await progress_callback("⏳ В очереди на генерацию...")
                            elif status == "processing":
                                await progress_callback("⚙️ Генерирую изображение...")

                    # Check if complete
                    if status == "succeed":
                        # Extract image URL
                        if "task_result" in status_data and "images" in status_data["task_result"]:
                            images = status_data["task_result"]["images"]
                            if images and len(images) > 0:
                                return images[0]["url"]
                        raise Exception("No image URL in response")

                    elif status == "failed":
                        error = status_msg or "Generation failed"
                        raise Exception(f"Generation failed: {error}")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)

    # Implement abstract method from base class
    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process image (not used for generation, but required by base class).
        """
        return ImageResponse(
            success=False,
            error="Use generate_image method for Kling image generation"
        )
