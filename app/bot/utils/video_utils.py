"""
Video utilities for compression and validation.
Uses ffmpeg/ffprobe when available.
"""
import os
import asyncio
import shutil
from typing import Optional, Tuple

from app.core.logger import get_logger

logger = get_logger(__name__)

# Telegram limits
TELEGRAM_FILE_SIZE_LIMIT = 50 * 1024 * 1024  # 50MB
TELEGRAM_SAFE_SIZE_LIMIT = 49 * 1024 * 1024  # 49MB with margin


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None


def is_ffprobe_available() -> bool:
    """Check if ffprobe is available in PATH."""
    return shutil.which("ffprobe") is not None


async def get_video_duration(video_path: str) -> Optional[float]:
    """Get video duration in seconds using ffprobe."""
    if not is_ffprobe_available():
        return None

    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0 and stdout.strip():
            return float(stdout.strip())
    except Exception as e:
        logger.warning("ffprobe_duration_failed", error=str(e), path=video_path)
    return None


async def compress_video_for_telegram(
    video_path: str,
    target_size_mb: float = 48.0,
) -> Tuple[bool, str]:
    """
    Compress video to fit within Telegram's file size limit.

    Returns:
        Tuple of (success, path_or_error_message).
        On success, path is the compressed file path.
        On failure, message describes why compression failed.
    """
    if not is_ffmpeg_available():
        return False, (
            "⚠️ Видео слишком большое для Telegram. "
            "Сжатие недоступно (ffmpeg не установлен на сервере)."
        )

    file_size = os.path.getsize(video_path)
    if file_size <= TELEGRAM_SAFE_SIZE_LIMIT:
        return True, video_path

    try:
        # Get video duration for bitrate calculation
        duration = await get_video_duration(video_path)
        if not duration or duration <= 0:
            return False, "⚠️ Не удалось определить длительность видео для сжатия."

        # Calculate target bitrate (bits/sec)
        # target_size in bits, minus ~128kbps for audio
        target_bits = target_size_mb * 8 * 1024 * 1024
        audio_bitrate = 128 * 1024  # 128kbps
        video_bitrate = int((target_bits / duration) - audio_bitrate)

        if video_bitrate < 200_000:  # Less than 200kbps - quality would be too bad
            return False, (
                f"⚠️ Видео слишком длинное ({int(duration)}с) для сжатия до 50 МБ "
                f"без критической потери качества."
            )

        # Compressed output path
        base, ext = os.path.splitext(video_path)
        compressed_path = f"{base}_compressed{ext}"

        logger.info(
            "video_compression_started",
            original_size=file_size,
            duration=duration,
            target_bitrate=video_bitrate,
        )

        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", video_path,
            "-c:v", "libx264", "-preset", "fast",
            "-b:v", str(video_bitrate),
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            compressed_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error("video_compression_failed", stderr=stderr.decode()[-500:])
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            return False, "⚠️ Ошибка при сжатии видео."

        compressed_size = os.path.getsize(compressed_path)
        logger.info(
            "video_compression_done",
            original_size=file_size,
            compressed_size=compressed_size,
            ratio=f"{compressed_size/file_size:.1%}",
        )

        if compressed_size > TELEGRAM_SAFE_SIZE_LIMIT:
            os.remove(compressed_path)
            return False, (
                f"⚠️ Даже после сжатия видео ({compressed_size // (1024*1024)} МБ) "
                f"превышает лимит Telegram (50 МБ)."
            )

        return True, compressed_path

    except Exception as e:
        logger.error("video_compression_error", error=str(e))
        return False, f"⚠️ Ошибка при сжатии видео: {str(e)}"
