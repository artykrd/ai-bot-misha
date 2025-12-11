"""
Google Veo 3.1 video generation service via Gemini API.
Updated for 2025 API - uses google-generativeai library.
"""
import time
import os
from typing import Optional, Callable, Awaitable
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

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


class VeoService(BaseVideoProvider):
    """Google Veo 3.1 API integration via Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        # Veo 3.1 uses Gemini API key (not Vertex AI credentials)
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        super().__init__(api_key=self.api_key or "")

        self.client = None
        self._genai = None

        # Don't import on init, wait until first use
        if self.api_key:
            self._genai = _get_genai()
            if self._genai:
                try:
                    # Initialize Gemini client with API key
                    # Set the API key as environment variable for the library
                    os.environ["GEMINI_API_KEY"] = self.api_key
                    self.client = self._genai.Client(api_key=self.api_key)
                    logger.info("veo_initialized", api_key_present=bool(self.api_key))
                except Exception as e:
                    logger.error("veo_init_failed", error=str(e))
                    self.client = None

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Google Veo 3.1.

        Args:
            prompt: Text description for video generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - duration: Video duration in seconds (4, 6, 8, default: 8)
                - aspect_ratio: Video aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, default: 16:9)
                - negative_prompt: Things to avoid in the video
                - resolution: Video resolution (720p, 1080p, default: 720p)
                - image_path: Path to first frame image for image-to-video (optional)
                - last_frame_path: Path to last frame image for interpolation (optional, requires image_path)
                - reference_images: List of up to 3 reference image paths (optional, Veo 3.1 only)
                - video_path: Path to Veo-generated video for extension (optional, Veo 3.1 only)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.client or not self.api_key:
            return VideoResponse(
                success=False,
                error="Google Gemini API key not configured. Set GOOGLE_GEMINI_API_KEY in .env. Get your key at: https://aistudio.google.com/apikey",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Инициализация Veo 3.1...")

            if not self._genai:
                self._genai = _get_genai()

            if not self._genai:
                return VideoResponse(
                    success=False,
                    error="google-generativeai library not available. Install with: pip install google-generativeai>=0.8.3",
                    processing_time=time.time() - start_time
                )

            # Get parameters
            duration = kwargs.get("duration", 8)  # Default 8 seconds
            aspect_ratio = kwargs.get("aspect_ratio", "16:9")
            negative_prompt = kwargs.get("negative_prompt", None)
            resolution = kwargs.get("resolution", "720p")
            image_path = kwargs.get("image_path", None)
            last_frame_path = kwargs.get("last_frame_path", None)
            reference_images = kwargs.get("reference_images", None)
            input_video_path = kwargs.get("video_path", None)

            # Determine mode
            mode = "text-to-video"
            if input_video_path:
                mode = "video-extension"
            elif image_path and last_frame_path:
                mode = "interpolation"
            elif image_path:
                mode = "image-to-video"
            elif reference_images:
                mode = "reference-images"

            if progress_callback:
                await progress_callback(f"🎥 Генерирую видео ({mode}) {duration}с, {aspect_ratio}, {resolution}...")

            # Generate video using Veo model
            output_video_path = await self._generate_veo_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt,
                resolution=resolution,
                image_path=image_path,
                last_frame_path=last_frame_path,
                reference_images=reference_images,
                input_video_path=input_video_path,
                progress_callback=progress_callback
            )

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "veo_video_generated",
                prompt=prompt[:100],
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                mode=mode,
                time=processing_time
            )

            # Token usage for Veo 3.1: approximately 15,000 tokens per 8-second video
            tokens_used = 15000

            return VideoResponse(
                success=True,
                video_path=output_video_path,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={
                    "provider": "veo",
                    "model": "veo-3.1-generate-preview",
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "mode": mode,
                    "prompt": prompt
                }
            )

        except Exception as e:
            error_msg = str(e)

            # Special handling for quota/rate limit errors
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                error_msg = (
                    "❌ Превышена квота API или требуется платная подписка.\n\n"
                    "Veo 3.1 требует:\n"
                    "1. Активную оплату в Google AI Studio\n"
                    "2. Tier 1 или выше API ключ\n\n"
                    "Проверьте:\n"
                    "• https://aistudio.google.com/apikey (ваш API ключ)\n"
                    "• https://ai.dev/usage?tab=rate-limit (использование)\n"
                    "• https://ai.google.dev/pricing (цены и лимиты)\n\n"
                    f"Оригинальная ошибка: {error_msg}"
                )

            logger.error("veo_video_generation_failed", error=error_msg, prompt=prompt[:100])

            if progress_callback:
                await progress_callback(f"❌ Ошибка: см. сообщение ниже")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _generate_veo_video(
        self,
        prompt: str,
        duration: int,
        aspect_ratio: str,
        negative_prompt: Optional[str],
        resolution: str,
        image_path: Optional[str] = None,
        last_frame_path: Optional[str] = None,
        reference_images: Optional[list] = None,
        input_video_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate video using Veo 3.1 model via Gemini API."""

        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # Prepare generation config according to official docs
                config_params = {}

                # Add aspect ratio
                if aspect_ratio:
                    config_params["aspect_ratio"] = aspect_ratio

                # Add negative prompt if provided
                if negative_prompt:
                    config_params["negative_prompt"] = negative_prompt

                # Add resolution if not default
                if resolution:
                    config_params["resolution"] = resolution

                # Add duration
                if duration:
                    config_params["duration_seconds"] = str(duration)

                # Prepare image parameter if provided
                # For Veo, we need to upload the file and use its URI
                image_obj = None
                uploaded_image_file = None
                if image_path:
                    try:
                        from google.genai import types
                        import mimetypes

                        # Upload image file to Google using Files API
                        uploaded_image_file = self.client.files.upload(file=image_path)

                        # Detect mime type
                        mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'

                        # Create Image object with the uploaded file URI
                        # According to Veo docs, Image accepts gcs_uri or file_uri
                        image_obj = types.Image(
                            gcs_uri=uploaded_image_file.uri,
                            mime_type=mime_type
                        )

                        logger.info("veo_image_uploaded_and_prepared",
                                  path=image_path,
                                  file_uri=uploaded_image_file.uri,
                                  mime_type=mime_type)
                    except Exception as img_error:
                        logger.error("veo_image_prepare_failed", error=str(img_error))
                        raise Exception(f"Failed to prepare image: {img_error}")

                # Prepare reference images if provided (Veo 3.1 only)
                ref_images_objs = None
                uploaded_ref_files = []
                if reference_images and len(reference_images) > 0:
                    try:
                        from google.genai import types
                        import mimetypes

                        ref_images_objs = []
                        for idx, ref_img_path in enumerate(reference_images[:3]):  # Max 3 images
                            # Upload reference image
                            uploaded_ref_file = self.client.files.upload(file=ref_img_path)
                            uploaded_ref_files.append(uploaded_ref_file)

                            ref_mime_type = mimetypes.guess_type(ref_img_path)[0] or 'image/jpeg'

                            # Create Image object with uploaded file URI
                            ref_image_obj = types.Image(
                                gcs_uri=uploaded_ref_file.uri,
                                mime_type=ref_mime_type
                            )

                            # Create VideoGenerationReferenceImage
                            ref_img = types.VideoGenerationReferenceImage(
                                image=ref_image_obj,
                                reference_type="asset"  # asset or style
                            )
                            ref_images_objs.append(ref_img)
                            logger.info("veo_reference_image_uploaded_and_prepared",
                                      index=idx,
                                      path=ref_img_path,
                                      file_uri=uploaded_ref_file.uri,
                                      mime_type=ref_mime_type)

                        # Add reference images to config
                        config_params["reference_images"] = ref_images_objs
                    except Exception as ref_error:
                        logger.error("veo_reference_images_prepare_failed", error=str(ref_error))
                        raise Exception(f"Failed to prepare reference images: {ref_error}")

                # Prepare last frame for interpolation (Veo 3.1 only)
                # Requires both image_path and last_frame_path
                last_frame_obj = None
                uploaded_last_frame_file = None
                if last_frame_path and image_path:
                    try:
                        from google.genai import types
                        import mimetypes

                        # Upload last frame file
                        uploaded_last_frame_file = self.client.files.upload(file=last_frame_path)

                        last_frame_mime = mimetypes.guess_type(last_frame_path)[0] or 'image/jpeg'

                        # Create Image object for last frame with uploaded file URI
                        last_frame_obj = types.Image(
                            gcs_uri=uploaded_last_frame_file.uri,
                            mime_type=last_frame_mime
                        )

                        # Add last_frame to config
                        config_params["last_frame"] = last_frame_obj

                        logger.info("veo_last_frame_uploaded_and_prepared",
                                  path=last_frame_path,
                                  file_uri=uploaded_last_frame_file.uri,
                                  mime_type=last_frame_mime)
                    except Exception as last_error:
                        logger.error("veo_last_frame_prepare_failed", error=str(last_error))
                        raise Exception(f"Failed to prepare last frame: {last_error}")

                # Prepare video for extension (Veo 3.1 only)
                # Must be a video from a previous Veo generation
                video_obj = None
                if input_video_path:
                    try:
                        # For video extension, we need to upload the video file
                        # The video must be from a previous Veo generation
                        uploaded_video_file = self.client.files.upload(file=input_video_path)
                        video_obj = uploaded_video_file

                        logger.info("veo_input_video_uploaded", path=input_video_path, file_uri=uploaded_video_file.name)
                    except Exception as vid_error:
                        logger.error("veo_input_video_upload_failed", error=str(vid_error))
                        raise Exception(f"Failed to upload input video: {vid_error}")

                # Generate video using Veo 3.1 according to official Python example
                # from google import genai
                # client = genai.Client()
                # Different parameters depending on mode:
                # - Text-to-Video: prompt + config
                # - Image-to-Video: prompt + image + config
                # - Interpolation: prompt + image + config (with last_frame)
                # - Reference Images: prompt + config (with reference_images)
                # - Video Extension: prompt + video + config

                if video_obj:
                    # Video extension mode
                    operation = self.client.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=prompt,
                        video=video_obj,
                        config=config_params if config_params else None,
                    )
                else:
                    # All other modes (text, image, interpolation, reference)
                    operation = self.client.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=prompt,
                        image=image_obj if image_obj else None,
                        config=config_params if config_params else None,
                    )

                # Wait for the video to be generated (polling)
                # According to docs: poll until operation.done is True
                max_wait_time = 360  # 6 minutes max (docs say up to 6 min during peak)
                start = time.time()
                poll_interval = 10  # Poll every 10 seconds

                while not operation.done:
                    if time.time() - start > max_wait_time:
                        raise TimeoutError("Video generation timed out after 6 minutes")

                    time.sleep(poll_interval)
                    # Refresh operation status
                    operation = self.client.operations.get(operation)

                # Get the generated video from response
                # According to docs: operation.response.generated_videos[0]
                generated_video = operation.response.generated_videos[0]

                # Save video to storage
                filename = self._generate_filename("mp4")
                video_path = self.storage_path / filename

                # Download and save video file
                # According to docs: client.files.download(file=video.video)
                self.client.files.download(file=generated_video.video)
                generated_video.video.save(str(video_path))

                logger.info(
                    "veo_video_saved",
                    path=str(video_path),
                    size=video_path.stat().st_size
                )

                return str(video_path)

            except Exception as e:
                logger.error("veo_generation_error", error=str(e))
                raise

        try:
            if progress_callback:
                await progress_callback("⏳ Обработка запроса... это может занять 1-6 минут")

            # Generate video in executor to not block async event loop
            video_path = await loop.run_in_executor(None, _generate)

            return video_path

        except Exception as e:
            logger.error("veo_executor_error", error=str(e))
            raise
