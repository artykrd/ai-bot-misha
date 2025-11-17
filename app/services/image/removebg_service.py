"""
Remove.bg background removal service.
"""
import time
from typing import Optional, Callable, Awaitable
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


class RemoveBgService(BaseImageProvider):
    """Remove.bg API integration for background removal."""

    BASE_URL = "https://api.remove.bg/v1.0"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.removebg_api_key)
        if not self.api_key:
            logger.warning("removebg_api_key_missing")

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Remove background from image.

        Args:
            image_path: Path to input image
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters (size, type, format, etc.)

        Returns:
            ImageResponse with processed image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Remove.bg API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🖼️ Удаляю фон с изображения...")

            # Process image
            result_path = await self._remove_background(image_path, **kwargs)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Фон удалён!")

            logger.info(
                "removebg_processed",
                input=image_path,
                output=result_path,
                time=processing_time
            )

            return ImageResponse(
                success=True,
                image_path=result_path,
                processing_time=processing_time,
                metadata={
                    "provider": "removebg",
                    "input_path": image_path
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("removebg_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _remove_background(self, image_path: str, **kwargs) -> str:
        """Remove background from image."""
        url = f"{self.BASE_URL}/removebg"

        headers = {
            "X-Api-Key": self.api_key
        }

        # Read input image
        input_file = Path(image_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Prepare form data
        data = aiohttp.FormData()
        data.add_field('image_file',
                       open(image_path, 'rb'),
                       filename=input_file.name,
                       content_type='image/png')

        # Optional parameters
        if "size" in kwargs:
            data.add_field('size', kwargs["size"])  # auto, preview, full, etc.
        if "type" in kwargs:
            data.add_field('type', kwargs["type"])  # auto, person, product, car
        if "format" in kwargs:
            data.add_field('format', kwargs["format"])  # auto, png, jpg, zip
        if "roi" in kwargs:
            data.add_field('roi', kwargs["roi"])  # Region of interest

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Remove.bg API error: {response.status} - {error_text}")

                # Save processed image
                filename = self._generate_filename("png")
                output_path = self.storage_path / filename

                with open(output_path, 'wb') as f:
                    f.write(await response.read())

                return str(output_path)

    async def replace_background(
        self,
        image_path: str,
        background_color: str = "white",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> ImageResponse:
        """
        Remove background and replace with solid color.

        Args:
            image_path: Path to input image
            background_color: Hex color code or color name
            progress_callback: Optional async callback for progress updates

        Returns:
            ImageResponse with processed image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Remove.bg API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🖼️ Заменяю фон...")

            # Remove background with color replacement
            result_path = await self._remove_background(
                image_path,
                bg_color=background_color
            )

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Фон заменён!")

            logger.info(
                "removebg_replaced",
                input=image_path,
                output=result_path,
                bg_color=background_color,
                time=processing_time
            )

            return ImageResponse(
                success=True,
                image_path=result_path,
                processing_time=processing_time,
                metadata={
                    "provider": "removebg",
                    "operation": "replace_background",
                    "background_color": background_color,
                    "input_path": image_path
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("removebg_replace_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )
