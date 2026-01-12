"""
Recraft AI image generation service.
Documentation: https://www.recraft.ai/docs
"""
import time
from typing import Optional, Callable, Awaitable

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


class RecraftService(BaseImageProvider):
    """
    Recraft AI API integration for image generation.

    Supports:
    - Text-to-Image (realistic, digital illustration, vector, icon)
    - Multiple styles and substyles
    - Custom colors and controls
    - Recraft V3 (default) and V2 models

    Pricing:
    - V3 Raster: $0.04 (40 API units)
    - V2 Raster: $0.022 (22 API units) - cheaper option
    - V3 Vector: $0.08 (80 API units)
    - V2 Vector: $0.044 (44 API units)
    """

    BASE_URL = "https://external.api.recraft.ai/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'recraft_api_key', None))
        if not self.api_key:
            logger.warning("recraft_api_key_missing")

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Recraft AI.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - model: Model to use (recraftv3, recraftv2, default: recraftv2 for cheaper)
                - style: Image style (realistic_image, digital_illustration, vector_illustration, icon)
                - substyle: Optional substyle for more specific look
                - size: Image size (default: "1024x1024")
                - n: Number of images to generate (1-6, default: 1)

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Recraft API ключ не настроен. Добавьте RECRAFT_API_KEY в .env файл.",
                processing_time=time.time() - start_time
            )

        try:
            # Get parameters
            # Use V2 by default for cheaper cost ($0.022 vs $0.04)
            model = kwargs.get("model", "recraftv2")
            style = kwargs.get("style", "realistic_image")
            substyle = kwargs.get("substyle", None)
            size = kwargs.get("size", "1024x1024")
            n = kwargs.get("n", 1)

            if progress_callback:
                await progress_callback(f"🎨 Генерирую изображение с Recraft AI ({model}, {style})...")

            # Generate image
            image_url = await self._generate_image_api(
                prompt=prompt,
                model=model,
                style=style,
                substyle=substyle,
                size=size,
                n=n
            )

            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

            # Download image
            filename = self._generate_filename("png")
            image_path = await self._download_file(image_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "recraft_image_generated",
                model=model,
                style=style,
                size=size,
                prompt=prompt[:100],
                time=processing_time
            )

            recraft_billing = get_image_model_billing("recraft")
            tokens_used = recraft_billing.tokens_per_generation

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "recraft",
                    "model": model,
                    "style": style,
                    "substyle": substyle,
                    "size": size,
                    "prompt": prompt,
                    "tokens_used": tokens_used
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("recraft_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _generate_image_api(
        self,
        prompt: str,
        model: str = "recraftv2",
        style: str = "realistic_image",
        substyle: Optional[str] = None,
        size: str = "1024x1024",
        n: int = 1
    ) -> str:
        """
        Call Recraft API to generate image.

        API Endpoint: POST /images/generations

        Returns:
            URL of the generated image
        """
        url = f"{self.BASE_URL}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build payload
        payload = {
            "prompt": prompt,
            "model": model,
            "style": style,
            "size": size,
            "n": n,
            "response_format": "url"
        }

        # Add substyle if provided
        if substyle:
            payload["substyle"] = substyle

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error("recraft_api_error", status=response.status, error=error_text)
                    raise Exception(f"Recraft API error {response.status}: {error_text}")

                data = await response.json()

                # Response format: {"data": [{"url": "..."}, ...]}
                if "data" not in data or len(data["data"]) == 0:
                    raise Exception("No image data in response")

                # Get first image URL
                image_url = data["data"][0].get("url")
                if not image_url:
                    raise Exception("No image URL in response")

                logger.info("recraft_image_url_received", url=image_url)

                return image_url

    # Implement required abstract method from BaseImageProvider
    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process image - not used for Recraft (text-to-image only).
        Kept for compatibility with BaseImageProvider interface.
        """
        return ImageResponse(
            success=False,
            error="Recraft service only supports text-to-image generation. Use generate_image() instead.",
            processing_time=0.0
        )
