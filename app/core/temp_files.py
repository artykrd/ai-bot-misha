"""
Утилиты для работы с временными файлами.

Исправляет проблемы:
- Двойной .resolve()
- Использование file_id как имени (конфликты при повторной загрузке)
- Утечка временных файлов
"""
import os
import uuid
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class TempFileManager:
    """Менеджер временных файлов с автоматической очисткой."""

    def __init__(self, base_dir: str = "./storage/temp"):
        """
        Инициализировать менеджер.

        Args:
            base_dir: Базовая директория для временных файлов
        """
        # ИСПРАВЛЕНО: убран двойной .resolve()
        self.base_path = Path(base_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def generate_unique_filename(
        self,
        prefix: str = "temp",
        suffix: str = ".jpg",
        user_id: Optional[int] = None
    ) -> Path:
        """
        Сгенерировать уникальное имя файла.

        ИСПРАВЛЕНО: Вместо file_id используем UUID + timestamp
        для гарантированной уникальности.

        Args:
            prefix: Префикс имени файла
            suffix: Расширение файла (с точкой)
            user_id: ID пользователя (опционально)

        Returns:
            Path к уникальному файлу
        """
        # Генерируем UUID для уникальности
        unique_id = uuid.uuid4().hex[:12]
        timestamp = int(time.time())

        # Формируем имя файла
        if user_id:
            filename = f"{prefix}_u{user_id}_{timestamp}_{unique_id}{suffix}"
        else:
            filename = f"{prefix}_{timestamp}_{unique_id}{suffix}"

        return self.base_path / filename

    def cleanup_file(self, file_path: Optional[str | Path]) -> bool:
        """
        Безопасно удалить файл.

        Args:
            file_path: Путь к файлу

        Returns:
            True если файл был удалён, False иначе
        """
        if not file_path:
            return False

        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                # Проверяем что файл находится в temp директории
                # для безопасности
                if self.base_path in path.parents or path.parent == self.base_path:
                    path.unlink()
                    logger.info("temp_file_cleaned", path=str(path))
                    return True
                else:
                    logger.warning(
                        "attempt_to_delete_non_temp_file",
                        path=str(path),
                        base_path=str(self.base_path)
                    )
        except Exception as e:
            logger.error(
                "temp_file_cleanup_failed",
                path=str(file_path),
                error=str(e)
            )

        return False

    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Очистить старые временные файлы.

        Args:
            max_age_hours: Максимальный возраст файлов в часах
        """
        try:
            now = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0

            for file_path in self.base_path.iterdir():
                if file_path.is_file():
                    # Проверяем возраст файла
                    file_age = now - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.error(
                                "old_file_cleanup_failed",
                                path=str(file_path),
                                error=str(e)
                            )

            if deleted_count > 0:
                logger.info(
                    "old_files_cleaned",
                    count=deleted_count,
                    max_age_hours=max_age_hours
                )

        except Exception as e:
            logger.error("cleanup_old_files_failed", error=str(e))

    def get_storage_stats(self) -> dict:
        """
        Получить статистику использования storage.

        Returns:
            Словарь со статистикой
        """
        try:
            total_size = 0
            file_count = 0

            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1

            return {
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "base_path": str(self.base_path)
            }
        except Exception as e:
            logger.error("get_storage_stats_failed", error=str(e))
            return {"error": str(e)}


# Глобальный инстанс
temp_file_manager = TempFileManager()


def get_temp_file_path(
    prefix: str = "temp",
    suffix: str = ".jpg",
    user_id: Optional[int] = None
) -> Path:
    """
    Быстрый способ получить путь к уникальному временному файлу.

    Args:
        prefix: Префикс имени файла
        suffix: Расширение файла
        user_id: ID пользователя

    Returns:
        Path к файлу
    """
    return temp_file_manager.generate_unique_filename(prefix, suffix, user_id)


def cleanup_temp_file(file_path: Optional[str | Path]) -> bool:
    """
    Быстрый способ удалить временный файл.

    Args:
        file_path: Путь к файлу

    Returns:
        True если удалён
    """
    return temp_file_manager.cleanup_file(file_path)


async def cleanup_multiple_files(*file_paths: Optional[str | Path]):
    """
    Удалить несколько временных файлов.

    Args:
        *file_paths: Пути к файлам
    """
    for path in file_paths:
        if path:
            cleanup_temp_file(path)
