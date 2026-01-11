"""
Structured logging configuration using structlog.
Provides JSON-formatted logs for production and human-readable logs for development.
"""
import logging
import sys
from pathlib import Path
from typing import Any
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log entries."""
    event_dict["app"] = "ai-bot-misha"
    event_dict["environment"] = settings.environment
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Shared processors (no rendering yet)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_context,
        structlog.processors.StackInfoRenderer(),
    ]

    # Create formatters for different outputs
    if settings.is_development:
        # Console: colored output
        console_processors = shared_processors + [structlog.dev.ConsoleRenderer()]
        # Files: plain key-value output without colors
        file_processors = shared_processors + [structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event"])]
    else:
        # Production: JSON everywhere
        console_processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
        file_processors = console_processors

    # Create handlers
    # Console handler (stdout) with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer() if settings.is_development else structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
    )

    # File handler with daily rotation - NO COLORS
    file_handler = TimedRotatingFileHandler(
        filename=log_dir / "bot.txt",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.suffix = "%Y-%m-%d.txt"
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event"]),
            foreign_pre_chain=shared_processors,
        )
    )

    # ERROR ONLY handler - NO COLORS, simple format
    error_handler = logging.FileHandler(
        filename=log_dir / "error.log",
        mode='a',
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event"]),
            foreign_pre_chain=shared_processors,
        )
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[console_handler, file_handler, error_handler],
    )

    # Configure structlog with minimal processors (formatting happens in handlers)
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Initialize logging on module import
setup_logging()
