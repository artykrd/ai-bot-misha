"""
Image utilities for processing and compressing images.
"""
import os
from PIL import Image
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger(__name__)


def compress_image_if_needed(
    image_path: str,
    max_size_mb: float = 4.0,
    max_dimension: int = 2048,
    output_format: str = "PNG",
    force_format: bool = False
) -> str:
    """
    Compress image if it exceeds size or dimension limits.

    Args:
        image_path: Path to the image file
        max_size_mb: Maximum file size in MB (default 4.0)
        max_dimension: Maximum width or height in pixels (default 2048)
        output_format: Output format (PNG or JPEG)
        force_format: If True, never convert to a different format (default False)

    Returns:
        Path to the compressed image (same path if no compression needed)
    """
    try:
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)

        logger.info(
            "checking_image_size",
            path=image_path,
            size_mb=round(file_size_mb, 2),
            max_size_mb=max_size_mb
        )

        # Check if compression is needed
        needs_compression = file_size_mb > max_size_mb

        # Open image to check dimensions
        img = Image.open(image_path)
        width, height = img.size

        # Check if resizing is needed
        needs_resize = width > max_dimension or height > max_dimension

        if not needs_compression and not needs_resize:
            logger.info("image_within_limits", size_mb=round(file_size_mb, 2))
            return image_path

        # Resize if needed
        if needs_resize:
            # Calculate new dimensions maintaining aspect ratio
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))

            logger.info(
                "resizing_image",
                original_size=f"{width}x{height}",
                new_size=f"{new_width}x{new_height}"
            )

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            width, height = new_width, new_height

        # Save with compression
        quality = 95  # Start with high quality
        temp_path = image_path + ".tmp"

        while quality > 10:
            if output_format.upper() == "PNG":
                # For PNG, optimize but don't use quality
                img.save(temp_path, "PNG", optimize=True)
            else:
                # For JPEG, use quality parameter
                img.save(temp_path, "JPEG", quality=quality, optimize=True)

            temp_size_mb = os.path.getsize(temp_path) / (1024 * 1024)

            if temp_size_mb <= max_size_mb:
                # Success - replace original
                os.replace(temp_path, image_path)
                logger.info(
                    "image_compressed",
                    original_size_mb=round(file_size_mb, 2),
                    new_size_mb=round(temp_size_mb, 2),
                    quality=quality if output_format.upper() != "PNG" else "optimized",
                    dimensions=f"{width}x{height}"
                )
                return image_path

            # Reduce quality and try again
            if output_format.upper() == "PNG":
                if force_format:
                    # For PNG with force_format, reduce dimensions instead of converting
                    # Reduce by 20% each iteration
                    new_width = int(width * 0.8)
                    new_height = int(height * 0.8)

                    if new_width < 256 or new_height < 256:
                        # Too small, can't compress further
                        break

                    logger.info(
                        "reducing_png_dimensions",
                        from_size=f"{width}x{height}",
                        to_size=f"{new_width}x{new_height}"
                    )

                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    width, height = new_width, new_height
                else:
                    # For PNG without force_format, convert to JPEG
                    output_format = "JPEG"
                    quality = 85
                    logger.info("converting_png_to_jpeg_for_compression")
            else:
                quality -= 10

        # If we get here, even lowest quality is too large
        # Replace anyway and warn
        if os.path.exists(temp_path):
            os.replace(temp_path, image_path)
            final_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            logger.warning(
                "image_compressed_but_large",
                size_mb=round(final_size_mb, 2),
                max_size_mb=max_size_mb
            )

        return image_path

    except Exception as e:
        logger.error("image_compression_error", error=str(e), path=image_path)
        # Return original path on error
        return image_path


def ensure_png_format(image_path: str) -> str:
    """
    Convert image to PNG format if it's not already.

    Args:
        image_path: Path to the image file

    Returns:
        Path to the PNG image
    """
    try:
        # Check if already PNG
        if image_path.lower().endswith('.png'):
            return image_path

        # Open and convert
        img = Image.open(image_path)

        # Create new path with .png extension
        png_path = str(Path(image_path).with_suffix('.png'))

        # Convert RGBA if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            # Already has alpha or palette
            img.save(png_path, 'PNG', optimize=True)
        else:
            # Convert to RGB first
            rgb_img = img.convert('RGB')
            rgb_img.save(png_path, 'PNG', optimize=True)

        # Remove original if different
        if png_path != image_path and os.path.exists(image_path):
            os.remove(image_path)

        logger.info("converted_to_png", original=image_path, new=png_path)
        return png_path

    except Exception as e:
        logger.error("png_conversion_error", error=str(e), path=image_path)
        return image_path
