"""
OpenAI DALL-E image generation service.
"""
import time
from typing import Optional, Callable, Awaitable
from pathlib import Path
import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse
from app.bot.utils.image_utils import compress_image_if_needed, ensure_png_format

logger = get_logger(__name__)

# Lazy import - only import when actually used
_openai = None
_OPENAI_CHECKED = False


def _get_openai():
    """Lazy import of openai."""
    global _openai, _OPENAI_CHECKED

    if _OPENAI_CHECKED:
        return _openai

    _OPENAI_CHECKED = True
    try:
        from openai import AsyncOpenAI
        _openai = AsyncOpenAI
        return _openai
    except Exception as e:
        logger.warning("openai_import_failed", error=str(e))
        _openai = None
        return None


def _get_dalle_error_message(error: Exception) -> str:
    """Get user-friendly error message for DALL-E errors."""
    error_str = str(error).lower()

    # Check for specific error types
    if "content_policy_violation" in error_str or "safety system" in error_str:
        return (
            "🛡️ Запрос отклонен системой безопасности OpenAI.\n\n"
            "Ваш промпт может содержать контент, который не разрешен политикой безопасности. "
            "Попробуйте:\n"
            "• Изменить формулировку промпта\n"
            "• Сделать описание менее детальным\n"
            "• Использовать другие слова\n\n"
            "Если вы считаете это ошибкой, попробуйте отправить запрос повторно."
        )

    if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
        return "💳 Проблема с биллингом OpenAI. Обратитесь к администратору."

    if "rate_limit" in error_str or "too many requests" in error_str:
        return "⏱️ Превышен лимит запросов. Попробуйте через минуту."

    if "invalid" in error_str and "size" in error_str:
        return "📐 Неверный размер изображения. Попробуйте другой размер."

    if "timeout" in error_str:
        return "⏰ Превышено время ожидания. Попробуйте еще раз."

    # Return original error for unknown cases
    return f"❌ Ошибка DALL-E: {error}"


class DalleService(BaseImageProvider):
    """OpenAI DALL-E API integration for image generation."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.openai_api_key)
        self.client = None

        if self.api_key:
            openai_class = _get_openai()
            if openai_class:
                self.client = openai_class(api_key=self.api_key)

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using DALL-E.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - model: DALL-E model (dall-e-2, dall-e-3, default: dall-e-3)
                - size: Image size (1024x1024, 1792x1024, 1024x1792 for dall-e-3)
                - quality: Image quality (standard, hd, default: standard)
                - style: Image style (vivid, natural, default: vivid)
                - n: Number of images (1-10 for dall-e-2, only 1 for dall-e-3)

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.client:
            return ImageResponse(
                success=False,
                error="OpenAI API key not configured or library not installed",
                processing_time=time.time() - start_time
            )

        try:
            # Get parameters
            model = kwargs.get("model", "dall-e-3")
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "standard")
            style = kwargs.get("style", "vivid")
            n = kwargs.get("n", 1)

            # Validate size based on model
            if model == "dall-e-3":
                valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
                if size not in valid_sizes:
                    size = "1024x1024"
                n = 1  # DALL-E 3 only supports n=1
            else:  # dall-e-2
                valid_sizes = ["256x256", "512x512", "1024x1024"]
                if size not in valid_sizes:
                    size = "1024x1024"

            if progress_callback:
                await progress_callback(f"🎨 Генерирую изображение ({model}, {size})...")

            # Generate image
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality if model == "dall-e-3" else None,
                style=style if model == "dall-e-3" else None,
                n=n,
                response_format="url"
            )

            # Download the first image
            image_url = response.data[0].url

            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

            # Download image
            filename = self._generate_filename("png")
            image_path = await self._download_file(image_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "dalle_image_generated",
                model=model,
                size=size,
                quality=quality,
                prompt=prompt[:100],
                time=processing_time
            )

            dalle_billing = get_image_model_billing("dalle3")
            tokens_used = dalle_billing.tokens_per_generation

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "openai",
                    "model": model,
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "prompt": prompt,
                    "tokens_used": tokens_used
                }
            )

        except Exception as e:
            error_msg = _get_dalle_error_message(e)
            logger.error("dalle_image_generation_failed", error=str(e), prompt=prompt[:100])

            if progress_callback:
                await progress_callback(f"❌ {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process image (DALL-E primarily generates, but can also edit/vary).

        Args:
            image_path: Path to input image (for variations)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters

        Returns:
            ImageResponse with processed image path or error
        """
        operation = kwargs.get("operation", "variation")

        if operation == "variation":
            return await self.create_variation(image_path, progress_callback, **kwargs)
        else:
            return ImageResponse(
                success=False,
                error=f"Unsupported operation: {operation}"
            )

    async def create_variation(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Create variation of an existing image.

        Args:
            image_path: Path to input image
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters

        Returns:
            ImageResponse with variation image path or error
        """
        start_time = time.time()

        if not self.client:
            return ImageResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            input_file = Path(image_path)
            if not input_file.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            model = kwargs.get("model", "dall-e-2")  # Only DALL-E 2 supports variations
            size = kwargs.get("size", "1024x1024")
            n = kwargs.get("n", 1)

            if progress_callback:
                await progress_callback("🎨 Подготавливаю изображение...")

            # CRITICAL: DALL-E requires PNG format and < 4MB
            # Convert to PNG and compress if needed
            image_path = ensure_png_format(image_path)
            image_path = compress_image_if_needed(image_path, max_size_mb=3.9, output_format="PNG")

            if progress_callback:
                await progress_callback("🎨 Создаю вариацию изображения...")

            # Create variation
            with open(image_path, 'rb') as image_file:
                response = await self.client.images.create_variation(
                    image=image_file,
                    n=n,
                    size=size,
                    response_format="url"
                )

            # Download the first variation
            variation_url = response.data[0].url

            if progress_callback:
                await progress_callback("💾 Сохраняю вариацию...")

            # Download image
            filename = self._generate_filename("png")
            variation_path = await self._download_file(variation_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Вариация готова!")

            logger.info(
                "dalle_variation_created",
                input=image_path,
                output=variation_path,
                time=processing_time
            )

            return ImageResponse(
                success=True,
                image_path=variation_path,
                processing_time=processing_time,
                metadata={
                    "provider": "openai",
                    "operation": "variation",
                    "model": model,
                    "size": size,
                    "input_path": image_path,
                    "tokens_used": get_image_model_billing("dalle3").tokens_per_generation
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("dalle_variation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )
