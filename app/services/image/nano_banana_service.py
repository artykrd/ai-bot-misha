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

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process image (Nano Banana primarily generates, but can also edit).

        Args:
            image_path: Path to input image (for editing)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters including:
                - prompt: Text prompt for image editing

        Returns:
            ImageResponse with processed image or error
        """
        # For now, Nano Banana doesn't support image editing
        # TODO: Implement image editing when needed
        return ImageResponse(
            success=False,
            error="Image editing not yet implemented for Nano Banana. Use text-to-image generation instead."
        )

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
                - reference_image_path: Path to reference image (optional, for image-to-image)

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
                await progress_callback("🍌 Генерирую изображение...")

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
            reference_image_path = kwargs.get("reference_image_path", None)

            mode = "text-to-image"
            if reference_image_path:
                mode = "image-to-image"

            if progress_callback:
                await progress_callback(f"🎨 Генерирую изображение ({mode}, {aspect_ratio})...")

            # Generate image
            image_path = await self._generate_nano_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                number_of_images=number_of_images,
                reference_image_path=reference_image_path,
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
                    "mode": mode,
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
        reference_image_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate image using Nano Banana model."""

        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # Import types for proper config structure
                from google.genai import types
                from PIL import Image

                # Build config according to Gemini documentation
                # Note: response_modalities must be uppercase 'IMAGE' per API spec
                config_params = {
                    "response_modalities": ['IMAGE']
                }

                # Add image config with aspect ratio if specified
                if aspect_ratio and aspect_ratio != "auto":
                    config_params["image_config"] = types.ImageConfig(
                        aspect_ratio=aspect_ratio
                    )

                # Generate image with proper types
                config = types.GenerateContentConfig(**config_params)

                # Prepare contents - can be text only or text + image
                if reference_image_path:
                    # Load reference image
                    ref_image = Image.open(reference_image_path)
                    # Convert to RGB if needed
                    if ref_image.mode != 'RGB':
                        ref_image = ref_image.convert('RGB')

                    # Enhance prompt for image-to-image to get better transformations
                    enhanced_prompt = (
                        f"Generate a NEW image based on this reference image with the following transformation: {prompt}. "
                        f"Create a completely transformed version, not just minor adjustments. "
                        f"Make significant creative changes while following the instruction."
                    )
                    # Create multimodal content: image + enhanced text prompt
                    contents = [ref_image, enhanced_prompt]
                    logger.info("nano_banana_using_reference_image", path=reference_image_path, enhanced=True)
                else:
                    # Text-only generation
                    contents = prompt

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=contents,
                    config=config
                )

                # Get the first generated image
                # Response contains parts with images
                if not response.parts or len(response.parts) == 0:
                    raise ValueError("No image generated in response")

                # Find the first image part - can be text or inline_data
                image_part = None
                for part in response.parts:
                    # Skip text parts
                    if part.text is not None:
                        continue
                    # Check for inline data (image)
                    if part.inline_data is not None or hasattr(part, 'as_image'):
                        image_part = part
                        break

                if not image_part:
                    raise ValueError("No image part found in response")

                # Save image to storage
                filename = self._generate_filename("png")
                image_path = self.storage_path / filename

                # Try to use as_image() method first (most reliable)
                try:
                    from PIL import Image
                    import io

                    pil_image = image_part.as_image()

                    logger.info("nano_banana_using_as_image", image_type=type(pil_image).__name__)

                    # Check if it's a real PIL Image or a custom object
                    if isinstance(pil_image, Image.Image):
                        # Standard PIL Image - save directly
                        pil_image.save(str(image_path), 'PNG')
                    else:
                        # Custom image object - convert to real PIL Image via buffer
                        # First save to buffer
                        buffer = io.BytesIO()
                        pil_image.save(buffer, format='PNG')
                        buffer.seek(0)

                        # Load as real PIL Image
                        real_pil_image = Image.open(buffer)

                        # Save as PNG
                        real_pil_image.save(str(image_path), 'PNG')

                        logger.info("nano_banana_converted_custom_to_pil")

                except Exception as as_image_error:
                    # Fallback: try to get data from inline_data
                    logger.warning("nano_banana_as_image_failed", error=str(as_image_error))

                    if image_part.inline_data:
                        # Check if data is base64-encoded or raw bytes
                        import base64
                        data = image_part.inline_data.data

                        logger.info("nano_banana_using_inline_data",
                                  data_type=type(data).__name__,
                                  data_size=len(data))

                        # Try to decode if it's base64
                        try:
                            if isinstance(data, str):
                                # It's a base64 string
                                decoded_data = base64.b64decode(data)
                            elif isinstance(data, bytes):
                                # It might be already decoded or might be base64 bytes
                                # Try to decode first
                                try:
                                    decoded_data = base64.b64decode(data)
                                    logger.info("nano_banana_decoded_base64", size=len(decoded_data))
                                except Exception:
                                    # Not base64, use as is
                                    decoded_data = data
                                    logger.info("nano_banana_using_raw_bytes", size=len(decoded_data))
                            else:
                                decoded_data = data

                            # Write decoded data
                            with open(image_path, 'wb') as f:
                                f.write(decoded_data)

                        except Exception as decode_error:
                            logger.error("nano_banana_decode_failed", error=str(decode_error))
                            raise
                    else:
                        raise ValueError("No valid image data found in response")

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

            # Generate image in executor
            image_path = await loop.run_in_executor(None, _generate)

            return image_path

        except Exception as e:
            logger.error("nano_banana_executor_error", error=str(e))
            raise
