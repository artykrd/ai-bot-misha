"""
xAI Grok Image generation service.
API: https://api.x.ai/v1/images/generations (OpenAI-compatible)
Model: grok-imagine-image
"""
import time
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)

XAI_BASE_URL = "https://api.x.ai/v1"
GROK_IMAGE_MODEL = "grok-imagine-image"


class GrokImageService(BaseImageProvider):
    """xAI Grok image generation via /v1/images/generations."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, "grok_ai_api", None))
        if not self.api_key:
            logger.warning("grok_ai_api_missing")

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs,
    ) -> ImageResponse:
        """
        Generate image using Grok Images.

        kwargs:
            aspect_ratio: str — "auto"|"1:1"|"16:9"|"9:16"|"4:3"|"3:4"|"3:2"|"2:3"|...
            resolution: str — "1k" or "2k"
            n: int — number of images (1-10, default 1)
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Grok API ключ не настроен (GROK_AI_API).",
                processing_time=time.time() - start_time,
            )

        aspect_ratio = kwargs.get("aspect_ratio", "auto")
        resolution = kwargs.get("resolution", "1k")
        n = max(1, min(int(kwargs.get("n", 1)), 10))

        if progress_callback:
            await progress_callback(
                f"🤖 Генерирую изображение Grok Images ({resolution}, {aspect_ratio})..."
            )

        try:
            payload: dict = {
                "model": GROK_IMAGE_MODEL,
                "prompt": prompt,
                "n": n,
            }
            if aspect_ratio and aspect_ratio != "auto":
                payload["aspect_ratio"] = aspect_ratio
            if resolution:
                payload["resolution"] = resolution

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{XAI_BASE_URL}/images/generations",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status not in (200, 201):
                        error_text = await response.text()
                        logger.error(
                            "grok_image_api_error",
                            status=response.status,
                            error=error_text,
                        )
                        raise Exception(
                            f"Grok API error {response.status}: {error_text}"
                        )

                    data = await response.json()

            image_url = data["data"][0]["url"]

            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

            filename = self._generate_filename("jpg")
            image_path = await self._download_file(image_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            billing = get_image_model_billing("grok-imagine-image")
            tokens_used = billing.tokens_per_generation if billing else 18500

            logger.info(
                "grok_image_generated",
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                prompt=prompt[:80],
                time=processing_time,
            )

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "grok_image",
                    "model": GROK_IMAGE_MODEL,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "prompt": prompt,
                    "tokens_used": tokens_used,
                },
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("grok_image_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time,
            )

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs,
    ) -> ImageResponse:
        """Not used for generation-only model."""
        return ImageResponse(success=False, error="process_image not supported by GrokImageService")
