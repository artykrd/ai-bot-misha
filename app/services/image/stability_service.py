"""
Stability AI image processing service (upscaling, vectorization, etc.).
"""
import time
from typing import Optional, Callable, Awaitable
from pathlib import Path
import base64

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


class StabilityService(BaseImageProvider):
    """Stability AI API integration for image processing."""

    BASE_URL = "https://api.stability.ai/v2beta"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.stability_api_key)
        if not self.api_key:
            logger.warning("stability_api_key_missing")

    async def upscale_image(
        self,
        image_path: str,
        scale_factor: int = 2,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Upscale image using Stability AI.

        Args:
            image_path: Path to input image
            scale_factor: Upscale factor (2 or 4)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters

        Returns:
            ImageResponse with upscaled image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Stability AI API key not configured",
                processing_time=time.time() - start_time
            )

        if scale_factor not in [2, 4]:
            return ImageResponse(
                success=False,
                error="Scale factor must be 2 or 4",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback(f"🔍 Увеличиваю изображение в {scale_factor}x...")

            # Upscale image
            result_path = await self._upscale(image_path, scale_factor, **kwargs)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение увеличено!")

            logger.info(
                "stability_upscaled",
                input=image_path,
                output=result_path,
                scale=scale_factor,
                time=processing_time
            )

            return ImageResponse(
                success=True,
                image_path=result_path,
                processing_time=processing_time,
                metadata={
                    "provider": "stability",
                    "operation": "upscale",
                    "scale_factor": scale_factor,
                    "input_path": image_path
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("stability_upscale_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def process_image(
        self,
        image_path: str,
        operation: str = "upscale",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process image with specified operation.

        Args:
            image_path: Path to input image
            operation: Operation type (upscale, vectorize, etc.)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters for the operation

        Returns:
            ImageResponse with processed image path or error
        """
        if operation == "upscale":
            return await self.upscale_image(
                image_path,
                scale_factor=kwargs.get("scale_factor", 2),
                progress_callback=progress_callback,
                **kwargs
            )
        else:
            return ImageResponse(
                success=False,
                error=f"Unknown operation: {operation}"
            )

    async def _upscale(
        self,
        image_path: str,
        scale_factor: int,
        **kwargs
    ) -> str:
        """Upscale image using Stability AI."""
        url = f"{self.BASE_URL}/stable-image/upscale/conservative"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }

        # Read input image
        input_file = Path(image_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Prepare form data
        data = aiohttp.FormData()
        data.add_field('image',
                       open(image_path, 'rb'),
                       filename=input_file.name,
                       content_type='image/png')

        # Add parameters
        data.add_field('output_format', 'png')

        # Determine upscale mode based on scale factor
        if scale_factor == 2:
            data.add_field('prompt', kwargs.get('prompt', 'high quality, detailed'))
        elif scale_factor == 4:
            # For 4x, we might need to use a different endpoint or call 2x twice
            data.add_field('prompt', kwargs.get('prompt', 'ultra high quality, highly detailed'))

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Stability AI error: {response.status} - {error_text}")

                # Save upscaled image
                filename = self._generate_filename("png")
                output_path = self.storage_path / filename

                with open(output_path, 'wb') as f:
                    f.write(await response.read())

                return str(output_path)

    async def vectorize_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> ImageResponse:
        """
        Vectorize image (convert to SVG).

        Note: This is a placeholder for vectorization functionality.
        Stability AI may not directly support vectorization, so this might
        need to use a different service or approach.

        Args:
            image_path: Path to input image
            progress_callback: Optional async callback for progress updates

        Returns:
            ImageResponse with vectorized image path or error
        """
        start_time = time.time()

        return ImageResponse(
            success=False,
            error="Vectorization not yet implemented. Use third-party service like vectorizer.ai",
            processing_time=time.time() - start_time
        )
