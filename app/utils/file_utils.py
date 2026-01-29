"""
File utilities wrapper module.

This module provides a unified interface for file operations
by re-exporting functions from their actual locations.
"""
import os
from pathlib import Path
from typing import Optional
from PIL import Image

from app.core.temp_files import (
    get_temp_file_path,
    cleanup_temp_file,
    cleanup_multiple_files,
    temp_file_manager
)
from app.core.logger import get_logger

logger = get_logger(__name__)

# Re-export from temp_files for convenience
__all__ = [
    "get_temp_file_path",
    "cleanup_temp_file",
    "cleanup_multiple_files",
    "resize_image_if_needed",
]


def resize_image_if_needed(image_path: str, max_size_mb: float = 2.0, max_dimension: int = 2048) -> str:
    """
    Resize image if it's too large.

    Args:
        image_path: Path to the image file
        max_size_mb: Maximum file size in MB
        max_dimension: Maximum width or height in pixels

    Returns:
        Path to the resized image (same as input if no resize needed)
    """
    try:
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)

        img = Image.open(image_path)
        needs_resize = False

        # Check if file size is too large
        if file_size_mb > max_size_mb:
            needs_resize = True
            logger.info("image_too_large", size_mb=file_size_mb)

        # Check if dimensions are too large
        if img.width > max_dimension or img.height > max_dimension:
            needs_resize = True
            logger.info("image_dimensions_too_large", width=img.width, height=img.height)

        if not needs_resize:
            return image_path

        # Calculate new dimensions maintaining aspect ratio
        ratio = min(max_dimension / img.width, max_dimension / img.height, 1.0)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)

        # Convert RGBA to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(
                img,
                mask=img.split()[-1] if img.mode == "RGBA" else None
            )
            img = background

        # Resize image
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save with optimization
        img_resized.save(image_path, "JPEG", quality=85, optimize=True)

        new_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        logger.info(
            "image_resized",
            old_size_mb=file_size_mb,
            new_size_mb=new_size_mb,
            old_dimensions=f"{img.width}x{img.height}",
            new_dimensions=f"{new_width}x{new_height}"
        )

        return image_path

    except Exception as e:
        logger.error("image_resize_failed", error=str(e), image_path=image_path)
        return image_path  # Return original path on error
