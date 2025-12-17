"""
Temporary file cache for download functionality.
Stores file paths associated with message IDs for a limited time.
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
import asyncio

class FileCache:
    """In-memory cache for temporary file storage."""

    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize file cache.

        Args:
            ttl_minutes: Time to live in minutes (default 60)
        """
        self._cache: Dict[str, tuple[str, datetime]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def store(self, key: str, file_path: str) -> None:
        """
        Store a file path with a key.

        Args:
            key: Unique identifier (usually message_id or user_id:timestamp)
            file_path: Path to the file
        """
        self._cache[key] = (file_path, datetime.now())
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
            return None

        file_path, timestamp = self._cache[key]

        # Check if expired
        if datetime.now() - timestamp > self._ttl:
            del self._cache[key]
            return None

        return file_path

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self._ttl
        ]

        for key in expired_keys:
            del self._cache[key]


# Global file cache instance
file_cache = FileCache(ttl_minutes=60)
