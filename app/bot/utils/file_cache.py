"""
Temporary file cache for download functionality.
Stores file paths associated with message IDs for a limited time.
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.core.logger import get_logger
import os

logger = get_logger(__name__)


class FileCache:
    """In-memory cache for temporary file storage (singleton)."""

    _instance: Optional['FileCache'] = None
    _cache: Dict[str, tuple[str, datetime, Optional[int]]] = {}
    _ttl: timedelta = timedelta(minutes=60)

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("file_cache_initialized", ttl_minutes=60)
        return cls._instance

    def store(self, key: str, file_path: str, user_id: Optional[int] = None) -> None:
        """
        Store a file path with a key.

        Args:
            key: Unique identifier (usually message_id or user_id:timestamp)
            file_path: Path to the file
            user_id: Owner user ID for access control
        """
        self._cache[key] = (file_path, datetime.now(), user_id)
        logger.info("file_cached", key=key, path=file_path[:50], cache_size=len(self._cache), user_id=user_id)
        self._cleanup_expired()

    def get(self, key: str, user_id: Optional[int] = None) -> Optional[str]:
        """
        Retrieve a file path by key.

        Args:
            key: The key to retrieve
            user_id: Requesting user ID for access control

        Returns:
            File path if found, not expired, and user has access; None otherwise
        """
        if key not in self._cache:
            logger.warning("file_not_in_cache", key=key, cache_size=len(self._cache))
            return None

        entry = self._cache[key]
        # Support both old (2-tuple) and new (3-tuple) format
        if len(entry) == 2:
            file_path, timestamp = entry
            owner_id = None
        else:
            file_path, timestamp, owner_id = entry

        # Check if expired
        age = datetime.now() - timestamp
        if age > self._ttl:
            del self._cache[key]
            logger.warning("file_expired", key=key, age_seconds=age.total_seconds())
            return None

        # Check ownership if both user_id and owner_id are present
        if user_id is not None and owner_id is not None and user_id != owner_id:
            logger.warning(
                "file_access_denied",
                key=key,
                requesting_user=user_id,
                owner_user=owner_id,
            )
            return None

        logger.info("file_retrieved", key=key, age_seconds=age.total_seconds())
        return file_path

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache and delete physical files."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now - entry[1] > self._ttl
        ]

        if expired_keys:
            files_deleted = 0
            for key in expired_keys:
                entry = self._cache[key]
                file_path = entry[0]
                # Try to delete physical file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        files_deleted += 1
                        logger.info("expired_file_deleted", path=file_path, key=key)
                except Exception as e:
                    logger.warning("failed_to_delete_expired_file", path=file_path, error=str(e))

                del self._cache[key]
            logger.info("cache_cleaned", expired_count=len(expired_keys), files_deleted=files_deleted)


# Global file cache instance (singleton)
file_cache = FileCache()
