"""
Nano Banana - Gemini 2.5 Flash Image generation service.
Uses the new Gemini API for fast image generation.
"""
import time
import os
from typing import Optional, Callable, Awaitable
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.logger import get_logger
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)

# Lazy import - only import when actually used
_genai = None
_GENAI_CHECKED = False


def _get_genai():
    """Lazy import of google.genai."""
    global _genai, _GENAI_CHECKED

    if _GENAI_CHECKED:
        return _genai

    _GENAI_CHECKED = True
    try:
        from google import genai
        _genai = genai
        return _genai
    except Exception as e:
        logger.warning("genai_import_failed", error=str(e))
        _genai = None
        return None


class NanoBananaService(BaseImageProvider):
    """
    Nano Banana - Gemini 2.5 Flash Image generation via Gemini API.
    Fast image generation using google-generativeai library.
    """

    def __init__(self, api_key: Optional[str] = None):
        # Nano Banana uses Gemini API key
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        super().__init__(api_key=self.api_key or "")

        self.client = None
        self._genai = None

        # Initialize client
        if self.api_key:
            self._genai = _get_genai()
            if self._genai:
                try:
                    os.environ["GEMINI_API_KEY"] = self.api_key
                    self.client = self._genai.Client(api_key=self.api_key)
                    logger.info("nano_banana_initialized", api_key_present=bool(self.api_key))
                except Exception as e:
                    logger.error("nano_banana_init_failed", error=str(e))
                    self.client = None

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Nano Banana (Gemini 2.5 Flash Image).

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 3:4, 4:3, default: 1:1)
                - number_of_images: Number of images to generate (1-4, default: 1)

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.client or not self.api_key:
            return ImageResponse(
                success=False,
                error="Google Gemini API key not configured. Set GOOGLE_GEMINI_API_KEY in .env",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🍌 Инициализация Nano Banana...")

            if not self._genai:
                self._genai = _get_genai()

            if not self._genai:
                return ImageResponse(
                    success=False,
                    error="google-generativeai library not available",
                    processing_time=time.time() - start_time
                )

            # Get parameters
            aspect_ratio = kwargs.get("aspect_ratio", "1:1")
            number_of_images = kwargs.get("number_of_images", 1)

            if progress_callback:
                await progress_callback(f"🎨 Генерирую изображение ({aspect_ratio})...")

            # Generate image
            image_path = await self._generate_nano_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                number_of_images=number_of_images,
                progress_callback=progress_callback
            )

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "nano_banana_image_generated",
                prompt=prompt[:100],
                aspect_ratio=aspect_ratio,
                time=processing_time
            )

            # Token usage: approximately 3,000 tokens per image
            tokens_used = 3000 * number_of_images

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "nano_banana",
                    "model": "gemini-2.5-flash-image",
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt,
                    "tokens_used": tokens_used
                }
            )

        except Exception as e:
            error_msg = str(e)

            # Special handling for quota/rate limit errors
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                error_msg = (
                    "❌ Превышена квота API или требуется платная подписка.\n\n"
                    "Проверьте:\n"
                    "• https://aistudio.google.com/apikey (ваш API ключ)\n"
                    "• https://ai.dev/usage?tab=rate-limit (использование)\n\n"
                    f"Оригинальная ошибка: {error_msg}"
                )

            logger.error("nano_banana_generation_failed", error=error_msg, prompt=prompt[:100])

            if progress_callback:
                await progress_callback("❌ Ошибка: см. сообщение ниже")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _generate_nano_image(
        self,
        prompt: str,
        aspect_ratio: str,
        number_of_images: int,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate image using Nano Banana model."""

        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # According to documentation:
                # response = client.models.generate_content(
                #     model="gemini-2.5-flash-image",
                #     contents=prompt,
                #     config={"response_modalities":['IMAGE']}
                # )

                config = {
                    "response_modalities": ['IMAGE']
                }

                # Add aspect ratio if specified
                if aspect_ratio and aspect_ratio != "auto":
                    config["aspect_ratio"] = aspect_ratio

                # Generate image
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=prompt,
                    config=config
                )

                # Get the first generated image
                # Response contains parts with images
                if not response.parts or len(response.parts) == 0:
                    raise ValueError("No image generated in response")

                # Find the first image part
                image_part = None
                for part in response.parts:
                    if hasattr(part, 'as_image'):
                        image_part = part
                        break

                if not image_part:
                    raise ValueError("No image part found in response")

                # Save image to storage
                filename = self._generate_filename("png")
                image_path = self.storage_path / filename

                # Get image bytes and save
                image_data = image_part.as_image()

                # Save image file
                with open(image_path, 'wb') as f:
                    # If image_data has a save method, use it
                    if hasattr(image_data, 'save'):
                        image_data.save(f, format='PNG')
                    # Otherwise try to get bytes
                    elif hasattr(image_data, 'read'):
                        f.write(image_data.read())
                    # Or if it's already bytes
                    else:
                        f.write(image_data)

                logger.info(
                    "nano_banana_image_saved",
                    path=str(image_path),
                    size=image_path.stat().st_size
                )

                return str(image_path)

            except Exception as e:
                logger.error("nano_banana_generation_error", error=str(e))
                raise

        try:
            if progress_callback:
                await progress_callback("⏳ Обработка запроса... (10-30 секунд)")

            # Generate image in executor
            image_path = await loop.run_in_executor(None, _generate)

            return image_path

        except Exception as e:
            logger.error("nano_banana_executor_error", error=str(e))
            raise
