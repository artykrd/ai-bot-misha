"""
Temporary file cache for download functionality.
Stores file paths associated with message IDs for a limited time.
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.core.logger import get_logger

logger = get_logger(__name__)


class FileCache:
    """In-memory cache for temporary file storage (singleton)."""

    _instance: Optional['FileCache'] = None
    _cache: Dict[str, tuple[str, datetime]] = {}
    _ttl: timedelta = timedelta(minutes=60)

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("file_cache_initialized", ttl_minutes=60)
        return cls._instance

    def store(self, key: str, file_path: str) -> None:
        """
        Store a file path with a key.

        Args:
            key: Unique identifier (usually message_id or user_id:timestamp)
            file_path: Path to the file
        """
        self._cache[key] = (file_path, datetime.now())
        logger.info("file_cached", key=key, path=file_path[:50], cache_size=len(self._cache))
        self._cleanup_expired()

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a file path by key.

        Args:
            key: The key to retrieve

        Returns:
            File path if found and not expired, None otherwise
        """
        if key not in self._cache:
            logger.warning("file_not_in_cache", key=key, cache_size=len(self._cache))
            return None

        file_path, timestamp = self._cache[key]

        # Check if expired
        age = datetime.now() - timestamp
        if age > self._ttl:
            del self._cache[key]
            logger.warning("file_expired", key=key, age_seconds=age.total_seconds())
            return None

        logger.info("file_retrieved", key=key, age_seconds=age.total_seconds())
        return file_path

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self._ttl
        ]

        if expired_keys:
            for key in expired_keys:
                del self._cache[key]
            logger.info("cache_cleaned", expired_count=len(expired_keys))


# Global file cache instance (singleton)
file_cache = FileCache()
