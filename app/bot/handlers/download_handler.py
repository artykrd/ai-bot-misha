"""
Handler for downloading original files as documents.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.enums import ParseMode

from app.bot.utils.file_cache import file_cache
from app.core.logger import get_logger
import os

router = Router(name="download")
logger = get_logger(__name__)


@router.callback_query(F.data.startswith("download:"))
async def download_file(callback: CallbackQuery):
    """
    Handle file download requests.

    Downloads the original file as a document (no compression).
    """
    try:
        # Extract cache key from callback data
        cache_key = callback.data.replace("download:", "")

        # Retrieve file path from cache
        file_path = file_cache.get(cache_key)

        if not file_path or not os.path.exists(file_path):
            await callback.answer(
                "⚠️ Файл недоступен. Возможно, время хранения истекло.",
                show_alert=True
            )
            return

        # Determine file type from cache key
        file_type = cache_key.split(":")[0] if ":" in cache_key else "file"

        # Send file as document (uncompressed)
        file = FSInputFile(file_path)

        # Get file name from path
        file_name = os.path.basename(file_path)

        await callback.message.answer_document(
            document=file,
            caption=f"📥 Оригинальный файл ({file_type})\n\nФайл отправлен без сжатия."
        )

        await callback.answer("✅ Файл отправлен!")

        logger.info("file_downloaded", cache_key=cache_key, file_type=file_type)

    except Exception as e:
        logger.error("download_error", error=str(e), exc_info=True)
        await callback.answer(
            "❌ Ошибка при загрузке файла. Попробуйте позже.",
            show_alert=True
        )
