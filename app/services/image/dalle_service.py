"""
OpenAI DALL-E and GPT Image 2 image generation service.
"""
import base64
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

    if "401" in error_str or "unauthorized" in error_str or "invalid api key" in error_str:
        return "🔑 Ошибка авторизации OpenAI API. Обратитесь к администратору."

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
        Generate image using DALL-E or GPT Image 2.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - model: Model ID (dall-e-2, dall-e-3, gpt-image-2-*, default: dall-e-3)
                - size: Image size
                - quality: Image quality
                - style: Image style (DALL-E 3 only: vivid, natural)
                - n: Number of images

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
            model = kwargs.get("model", "dall-e-3")
            is_gpt_image_2 = model.startswith("gpt-image-2")

            if is_gpt_image_2:
                return await self._generate_gpt_image_2(
                    prompt=prompt,
                    model=model,
                    progress_callback=progress_callback,
                    start_time=start_time,
                    **kwargs
                )

            # DALL-E path
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "standard")
            style = kwargs.get("style", "vivid")
            n = kwargs.get("n", 1)

            if model == "dall-e-3":
                valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
                if size not in valid_sizes:
                    size = "1024x1024"
                n = 1
            else:  # dall-e-2
                valid_sizes = ["256x256", "512x512", "1024x1024"]
                if size not in valid_sizes:
                    size = "1024x1024"

            if progress_callback:
                await progress_callback(f"🎨 Генерирую изображение ({model}, {size})...")

            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality if model == "dall-e-3" else None,
                style=style if model == "dall-e-3" else None,
                n=n,
                response_format="url"
            )

            image_url = response.data[0].url

            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

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

    async def _generate_gpt_image_2(
        self,
        prompt: str,
        model: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]],
        start_time: float,
        **kwargs
    ) -> ImageResponse:
        """Generate image using GPT Image 2 via images.generate endpoint."""
        size = kwargs.get("size", "1024x1024")
        quality = kwargs.get("quality", "medium")
        n = kwargs.get("n", 1)
        output_format = kwargs.get("output_format", "png")

        valid_sizes = ["1024x1024", "1536x1024", "1024x1536", "auto"]
        if size not in valid_sizes:
            size = "1024x1024"

        valid_qualities = ["low", "medium", "high", "auto"]
        if quality not in valid_qualities:
            quality = "medium"

        n = max(1, min(n, 4))

        if progress_callback:
            await progress_callback(f"🖼 Генерирую изображение GPT Image 2 ({size}, {quality})...")

        try:
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
                response_format="b64_json",
                output_format=output_format,
            )
        except TypeError:
            # Fallback if SDK version doesn't support output_format
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
                response_format="b64_json",
            )

        if progress_callback:
            await progress_callback("💾 Сохраняю изображение...")

        b64_data = response.data[0].b64_json
        image_bytes = base64.b64decode(b64_data)

        ext = output_format if output_format in ("jpeg", "webp") else "png"
        filename = self._generate_filename(ext)
        image_path = str(self.storage_path / filename)
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        processing_time = time.time() - start_time

        if progress_callback:
            await progress_callback("✅ Изображение готово!")

        logger.info(
            "gpt_image_2_generated",
            model=model,
            size=size,
            quality=quality,
            prompt=prompt[:100],
            time=processing_time
        )

        gpt_image_billing = get_image_model_billing("gpt-image-2")
        tokens_used = gpt_image_billing.tokens_per_generation

        return ImageResponse(
            success=True,
            image_path=image_path,
            processing_time=processing_time,
            metadata={
                "provider": "openai",
                "model": model,
                "size": size,
                "quality": quality,
                "output_format": output_format,
                "prompt": prompt,
                "tokens_used": tokens_used
            }
        )

    async def edit_image_gpt_image_2(
        self,
        prompt: str,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Edit an existing image using GPT Image 2 via images.edit endpoint.

        Supports multi-image input: pass additional images as reference_image_paths list.
        """
        start_time = time.time()

        if not self.client:
            return ImageResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        model = kwargs.get("model", "gpt-image-2-2026-04-21")
        size = kwargs.get("size", "1024x1024")
        quality = kwargs.get("quality", "medium")
        n = kwargs.get("n", 1)
        output_format = kwargs.get("output_format", "png")
        reference_image_paths = kwargs.get("reference_image_paths", [])

        valid_sizes = ["1024x1024", "1536x1024", "1024x1536", "auto"]
        if size not in valid_sizes:
            size = "1024x1024"

        try:
            if progress_callback:
                await progress_callback("🖼 Редактирую изображение с GPT Image 2...")

            # Collect all image file handles
            image_files = []
            all_paths = [image_path] + reference_image_paths

            for path in all_paths:
                p = Path(path)
                if p.exists():
                    image_files.append(open(path, "rb"))

            if not image_files:
                raise FileNotFoundError("No valid image files found")

            try:
                # images.edit accepts a single image or list of images
                if len(image_files) == 1:
                    images_arg = image_files[0]
                else:
                    images_arg = image_files

                try:
                    response = await self.client.images.edit(
                        model=model,
                        image=images_arg,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        n=max(1, min(n, 4)),
                        response_format="b64_json",
                        output_format=output_format,
                    )
                except TypeError:
                    response = await self.client.images.edit(
                        model=model,
                        image=images_arg,
                        prompt=prompt,
                        size=size,
                        n=max(1, min(n, 4)),
                        response_format="b64_json",
                    )
            finally:
                for fh in image_files:
                    fh.close()

            if progress_callback:
                await progress_callback("💾 Сохраняю результат...")

            b64_data = response.data[0].b64_json
            image_bytes = base64.b64decode(b64_data)

            ext = output_format if output_format in ("jpeg", "webp") else "png"
            filename = self._generate_filename(ext)
            result_path = str(self.storage_path / filename)
            with open(result_path, "wb") as f:
                f.write(image_bytes)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Готово!")

            logger.info(
                "gpt_image_2_edited",
                model=model,
                size=size,
                quality=quality,
                prompt=prompt[:100],
                time=processing_time
            )

            gpt_image_billing = get_image_model_billing("gpt-image-2")
            tokens_used = gpt_image_billing.tokens_per_generation

            return ImageResponse(
                success=True,
                image_path=result_path,
                processing_time=processing_time,
                metadata={
                    "provider": "openai",
                    "model": model,
                    "operation": "edit",
                    "size": size,
                    "quality": quality,
                    "prompt": prompt,
                    "tokens_used": tokens_used
                }
            )

        except Exception as e:
            error_msg = _get_dalle_error_message(e)
            logger.error("gpt_image_2_edit_failed", error=str(e), prompt=prompt[:100])

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

            # CRITICAL: DALL-E variations requires PNG format and < 4MB
            # Convert to PNG and compress if needed (never convert to JPEG)
            image_path = ensure_png_format(image_path)
            image_path = compress_image_if_needed(
                image_path,
                max_size_mb=3.9,
                output_format="PNG",
                force_format=True  # Never convert PNG to JPEG for DALL-E variations
            )

            # Validate format and size before API call
            file_size_mb = Path(image_path).stat().st_size / (1024 * 1024)
            if not image_path.lower().endswith('.png'):
                raise ValueError(f"Image must be PNG format, got: {Path(image_path).suffix}")
            if file_size_mb >= 4.0:
                raise ValueError(f"Image must be less than 4MB, got: {file_size_mb:.2f}MB")

            logger.info(
                "dalle_variation_image_prepared",
                path=image_path,
                size_mb=round(file_size_mb, 2)
            )

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
