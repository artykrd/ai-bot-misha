"""
File download API for serving large files that exceed Telegram's 50MB limit.
Uses temporary tokens for secure access.
"""
import os
import time
import secrets
from typing import Dict, Tuple

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["files"])

# In-memory store: token -> (file_path, expires_at, filename)
_download_tokens: Dict[str, Tuple[str, float, str]] = {}

# Token lifetime in seconds (1 hour)
TOKEN_LIFETIME = 3600


def create_download_token(file_path: str, filename: str = None) -> str:
    """
    Create a temporary download token for a file.

    Args:
        file_path: Absolute or relative path to the file.
        filename: Optional display filename for the download.

    Returns:
        Token string to use in download URL.
    """
    _cleanup_expired_tokens()

    token = secrets.token_urlsafe(32)
    expires_at = time.time() + TOKEN_LIFETIME

    if not filename:
        filename = os.path.basename(file_path)

    _download_tokens[token] = (file_path, expires_at, filename)

    logger.info(
        "download_token_created",
        token=token[:8] + "...",
        filename=filename,
        file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
    )

    return token


def get_download_url(token: str) -> str:
    """Get the full download URL for a token."""
    return f"https://mikhail-bot.archy-tech.ru/api/download/{token}"


def _cleanup_expired_tokens():
    """Remove expired tokens."""
    now = time.time()
    expired = [t for t, (_, exp, _) in _download_tokens.items() if exp < now]
    for t in expired:
        del _download_tokens[t]


@router.get("/download/{token}")
async def download_file(token: str):
    """Download a file using a temporary token."""
    _cleanup_expired_tokens()

    if token not in _download_tokens:
        raise HTTPException(status_code=404, detail="Ссылка недействительна или истекла")

    file_path, expires_at, filename = _download_tokens[token]

    if time.time() > expires_at:
        del _download_tokens[token]
        raise HTTPException(status_code=410, detail="Ссылка истекла")

    if not os.path.exists(file_path):
        del _download_tokens[token]
        raise HTTPException(status_code=404, detail="Файл не найден")

    logger.info("file_downloaded", token=token[:8] + "...", filename=filename)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
