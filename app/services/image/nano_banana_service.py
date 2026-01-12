"""
Nano Banana - Gemini 2.5 Flash Image generation service.
Uses the new Gemini API for fast image generation.
"""
import time
import os
import re
from typing import Optional, Callable, Awaitable
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
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


def _get_finish_reason_message(finish_reason: str) -> str:
    """Get user-friendly error message based on finish_reason."""
    reason_str = str(finish_reason).upper()

    # Map finish reasons to user-friendly messages
    reason_messages = {
        "SAFETY": "🛡️ Генерация заблокирована фильтром безопасности. Попробуйте изменить промпт.",
        "BLOCKED_REASON": "🛡️ Запрос заблокирован. Попробуйте изменить формулировку.",
        "RECITATION": "📋 Запрос содержит защищенный контент. Попробуйте другой промпт.",
        "IMAGE_OTHER": "⚠️ Не удалось сгенерировать изображение. Это может быть из-за:\n"
                       "• Сложности промпта или референсного изображения\n"
                       "• Технической проблемы на стороне API\n"
                       "• Несовместимости параметров\n\n"
                       "Попробуйте упростить промпт или использовать другое изображение.",
        "MAX_TOKENS": "📝 Превышен лимит токенов. Попробуйте короче промпт.",
        "OTHER": "⚠️ Генерация прервана. Попробуйте изменить параметры запроса."
    }

    # Check for specific reasons
    for key, message in reason_messages.items():
        if key in reason_str:
            return message

    # Default message with finish_reason for debugging
    return f"⚠️ Генерация прервана (причина: {finish_reason}). Попробуйте изменить промпт или изображение."


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
        Generate image using Nano Banana (Gemini 2.5 Flash Image or Gemini 3 Pro Image).

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - model: Model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview, default: gemini-2.5-flash-image)
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
            model = kwargs.get("model", "gemini-2.5-flash-image")
            aspect_ratio = kwargs.get("aspect_ratio", "1:1")
            number_of_images = kwargs.get("number_of_images", 1)
            reference_image_path = kwargs.get("reference_image_path", None)

            mode = "text-to-image"
            if reference_image_path:
                mode = "image-to-image"

            if progress_callback:
                model_display = "Gemini 3 Pro" if "3-pro" in model else "Gemini 2.5 Flash"
                await progress_callback(f"🎨 Генерирую изображение ({model_display}, {mode}, {aspect_ratio})...")

            # Generate image
            image_path = await self._generate_nano_image(
                prompt=prompt,
                model=model,
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

            billing_id = "banana-pro" if "3-pro" in model else "nano-banana-image"
            nano_billing = get_image_model_billing(billing_id)
            tokens_used = nano_billing.tokens_per_generation * number_of_images

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "nano_banana",
                    "model": model,
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

            logger.error("nano_banana_generation_failed", error=error_msg, prompt=prompt[:100] if prompt else "None")

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
        model: str,
        aspect_ratio: str,
        number_of_images: int,
        reference_image_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate image using Nano Banana model (Gemini 2.5 Flash Image or Gemini 3 Pro Image)."""

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

                # CRITICAL FIX: Translate Russian prompts to English
                # Gemini 2.5 Flash Image works better with English prompts
                def has_cyrillic(text):
                    """Check if text contains Cyrillic characters."""
                    if not text:
                        return False
                    return bool(re.search('[а-яА-ЯёЁ]', text))

                translated_prompt = prompt or ""
                if has_cyrillic(prompt):
                    # Simple translation approach: prefix with instruction
                    # For better results, we rely on Gemini's multilingual understanding
                    # with explicit English instruction
                    translated_prompt = f"Create an image: {prompt}. Interpret the description and generate accordingly."
                    logger.info("nano_banana_russian_prompt_detected", original=prompt[:50] if prompt else "None")

                # Prepare contents - can be text only or text + image
                if reference_image_path:
                    # Load reference image
                    ref_image = Image.open(reference_image_path)

                    # DETAILED LOGGING - Step 1: Original image info
                    logger.info(
                        "nano_banana_ref_image_loaded",
                        path=reference_image_path,
                        format=ref_image.format,
                        mode=ref_image.mode,
                        size=ref_image.size,
                        width=ref_image.width,
                        height=ref_image.height,
                        file_size=os.path.getsize(reference_image_path) if os.path.exists(reference_image_path) else 0
                    )

                    # Convert to RGB if needed
                    original_mode = ref_image.mode
                    if ref_image.mode != 'RGB':
                        ref_image = ref_image.convert('RGB')
                        logger.info(
                            "nano_banana_ref_image_converted",
                            from_mode=original_mode,
                            to_mode='RGB',
                            size_after=ref_image.size
                        )

                    # Enhance prompt for image-to-image to get better transformations
                    enhanced_prompt = (
                        f"Generate a NEW image based on this reference image with the following transformation: {translated_prompt}. "
                        f"Create a completely transformed version, not just minor adjustments. "
                        f"Make significant creative changes while following the instruction."
                    )
                    # Create multimodal content: image + enhanced text prompt
                    contents = [ref_image, enhanced_prompt]
                    logger.info("nano_banana_using_reference_image", path=reference_image_path, enhanced=True)
                else:
                    # Text-only generation
                    contents = translated_prompt

                # Use the specified model (gemini-2.5-flash-image or gemini-3-pro-image-preview)
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )

                logger.info("nano_banana_api_call", model=model, mode="image-to-image" if reference_image_path else "text-to-image")

                # DETAILED LOGGING - Step 2: Response structure
                logger.info(
                    "nano_banana_api_response_received",
                    has_parts=hasattr(response, 'parts') and response.parts is not None,
                    parts_count=len(response.parts) if hasattr(response, 'parts') and response.parts else 0,
                    has_candidates=hasattr(response, 'candidates') and response.candidates is not None,
                    candidates_count=len(response.candidates) if hasattr(response, 'candidates') and response.candidates else 0,
                    has_text=hasattr(response, 'text'),
                    response_type=type(response).__name__
                )

                # DETAILED LOGGING - Step 3: Candidates details (if available)
                if hasattr(response, 'candidates') and response.candidates:
                    for idx, candidate in enumerate(response.candidates):
                        # Basic candidate info
                        logger.info(
                            "nano_banana_candidate_basic",
                            index=idx,
                            finish_reason=str(candidate.finish_reason) if hasattr(candidate, 'finish_reason') else "NONE",
                            has_content=hasattr(candidate, 'content'),
                            has_safety_ratings=hasattr(candidate, 'safety_ratings')
                        )

                        # Log safety ratings SEPARATELY for better visibility
                        if hasattr(candidate, 'safety_ratings'):
                            if candidate.safety_ratings:
                                for rating in candidate.safety_ratings:
                                    logger.info(
                                        "nano_banana_safety_rating",
                                        candidate_index=idx,
                                        category=str(rating.category) if hasattr(rating, 'category') else "UNKNOWN",
                                        probability=str(rating.probability) if hasattr(rating, 'probability') else "UNKNOWN",
                                        blocked=rating.blocked if hasattr(rating, 'blocked') else False
                                    )
                            else:
                                # safety_ratings exists but is falsy - log details
                                logger.warning(
                                    "nano_banana_safety_ratings_empty",
                                    candidate_index=idx,
                                    safety_ratings_type=type(candidate.safety_ratings).__name__,
                                    safety_ratings_len=len(candidate.safety_ratings) if hasattr(candidate.safety_ratings, '__len__') else "NO_LEN",
                                    safety_ratings_is_none=candidate.safety_ratings is None
                                )
                        else:
                            logger.warning("nano_banana_no_safety_ratings_attribute", candidate_index=idx)

                        # Log content structure
                        if hasattr(candidate, 'content') and candidate.content:
                            content = candidate.content
                            parts_count = len(content.parts) if hasattr(content, 'parts') and content.parts else 0
                            logger.info(
                                "nano_banana_content_structure",
                                candidate_index=idx,
                                parts_count=parts_count,
                                has_parts_attr=hasattr(content, 'parts')
                            )

                            # Log each part separately
                            if hasattr(content, 'parts') and content.parts:
                                for part_idx, part in enumerate(content.parts[:3]):
                                    logger.info(
                                        "nano_banana_content_part",
                                        candidate_index=idx,
                                        part_index=part_idx,
                                        has_text=hasattr(part, 'text') and part.text is not None,
                                        text_length=len(part.text) if hasattr(part, 'text') and part.text else 0,
                                        has_inline_data=hasattr(part, 'inline_data') and part.inline_data is not None,
                                        has_as_image=hasattr(part, 'as_image')
                                    )
                        else:
                            # Content is missing or falsy - log details
                            content_val = candidate.content if hasattr(candidate, 'content') else "NO_ATTR"
                            logger.warning(
                                "nano_banana_no_content",
                                candidate_index=idx,
                                has_content_attr=hasattr(candidate, 'content'),
                                content_is_none=content_val is None if hasattr(candidate, 'content') else False,
                                content_type=type(content_val).__name__ if hasattr(candidate, 'content') and content_val is not None else "None",
                                content_bool=bool(content_val) if hasattr(candidate, 'content') else False
                            )

                # Delete reference image immediately after upload to prevent reuse
                if reference_image_path and os.path.exists(reference_image_path):
                    try:
                        os.remove(reference_image_path)
                        logger.info("reference_image_deleted_after_upload", path=reference_image_path)
                    except Exception as cleanup_error:
                        logger.warning("reference_image_deletion_failed", path=reference_image_path, error=str(cleanup_error))

                # Get the first generated image
                # Response contains parts with images
                if not response.parts or len(response.parts) == 0:
                    # Check if response was blocked by safety filters
                    # Try to get finish_reason from different locations
                    finish_reason = None

                    # Check direct attribute
                    if hasattr(response, 'finish_reason') and response.finish_reason:
                        finish_reason = response.finish_reason
                    # Check candidates
                    elif hasattr(response, 'candidates') and response.candidates:
                        if len(response.candidates) > 0 and hasattr(response.candidates[0], 'finish_reason'):
                            finish_reason = response.candidates[0].finish_reason

                    # Log response details for debugging
                    logger.warning(
                        "nano_banana_empty_response",
                        finish_reason=str(finish_reason),
                        has_parts=bool(response.parts),
                        parts_count=len(response.parts) if response.parts else 0,
                        has_candidates=hasattr(response, 'candidates'),
                        candidates_count=len(response.candidates) if hasattr(response, 'candidates') and response.candidates else 0
                    )

                    if finish_reason:
                        error_msg = _get_finish_reason_message(finish_reason)
                    else:
                        error_msg = "API не сгенерировал изображение. Попробуйте изменить промпт."
                    raise ValueError(error_msg)

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
                    # Check finish reason for more details
                    # Try to get finish_reason from different locations
                    finish_reason = None

                    # Check direct attribute
                    if hasattr(response, 'finish_reason') and response.finish_reason:
                        finish_reason = response.finish_reason
                    # Check candidates
                    elif hasattr(response, 'candidates') and response.candidates:
                        if len(response.candidates) > 0 and hasattr(response.candidates[0], 'finish_reason'):
                            finish_reason = response.candidates[0].finish_reason

                    # Log for debugging
                    logger.warning(
                        "nano_banana_no_image_part",
                        finish_reason=str(finish_reason),
                        parts_count=len(response.parts),
                        parts_types=[type(p).__name__ for p in response.parts[:3]]
                    )

                    if finish_reason:
                        error_msg = _get_finish_reason_message(finish_reason)
                    else:
                        error_msg = "API не вернул изображение. Попробуйте изменить промпт."
                    raise ValueError(error_msg)

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
                        pil_image.save(str(image_path), format='PNG')
                    else:
                        # Custom image object - convert to real PIL Image via buffer
                        # Try different methods to save custom image object
                        buffer = io.BytesIO()
                        saved = False

                        # Try different save methods in order of likelihood
                        try:
                            # Method 1: Try with positional argument (Gemini's custom Image)
                            pil_image.save(buffer, 'PNG')
                            saved = True
                        except (TypeError, AttributeError) as e:
                            logger.debug("nano_banana_save_method1_failed", error=str(e))

                        if not saved:
                            # Method 2: Try without format argument
                            buffer = io.BytesIO()
                            try:
                                pil_image.save(buffer)
                                saved = True
                            except Exception as e:
                                logger.debug("nano_banana_save_method2_failed", error=str(e))

                        if not saved:
                            # Method 3: Try to get _pil_image attribute (if it's a wrapper)
                            buffer = io.BytesIO()
                            try:
                                if hasattr(pil_image, '_pil_image'):
                                    pil_image._pil_image.save(buffer, 'PNG')
                                    saved = True
                            except Exception as e:
                                logger.debug("nano_banana_save_method3_failed", error=str(e))

                        if not saved:
                            # If all methods failed, raise the original error
                            raise Exception("Failed to save custom image object with any method")

                        buffer.seek(0)

                        # Load as real PIL Image
                        real_pil_image = Image.open(buffer)

                        # Save as PNG
                        real_pil_image.save(str(image_path), format='PNG')

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
