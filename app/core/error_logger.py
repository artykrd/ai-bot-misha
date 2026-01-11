"""
Error logging utilities with automatic classification.
Use these utilities to log errors that should trigger admin notifications.
"""
from functools import wraps
from typing import Callable, Any
import logging

from app.core.logger import get_logger


def log_service_error(service_name: str):
    """
    Decorator to automatically log and classify errors from services.

    Usage:
        @log_service_error("Nano Banana")
        async def generate_image(...):
            ...

    Args:
        service_name: Human-readable service name (e.g., "Nano Banana", "DALL-E")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(f"service.{service_name.lower().replace(' ', '_')}")
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Log error with service context
                logger.error(
                    f"error_in_{service_name.lower().replace(' ', '_')}",
                    error=str(e),
                    function=func.__name__,
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_handler_error(handler_name: str):
    """
    Decorator to automatically log and classify errors from handlers.

    Usage:
        @log_handler_error("Image Generation")
        async def process_image(message: Message, ...):
            ...

    Args:
        handler_name: Human-readable handler name
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(f"handler.{handler_name.lower().replace(' ', '_')}")
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Log error with handler context
                logger.error(
                    f"error_in_{handler_name.lower().replace(' ', '_')}_handler",
                    error=str(e),
                    function=func.__name__,
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


class ErrorLogger:
    """
    Context manager for error logging.

    Usage:
        with ErrorLogger("Database Operation", "user_creation"):
            # your code here
            pass
    """

    def __init__(self, service_name: str, operation: str):
        self.service_name = service_name
        self.operation = operation
        self.logger = get_logger(f"service.{service_name.lower().replace(' ', '_')}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error(
                f"error_in_{self.service_name.lower().replace(' ', '_')}",
                operation=self.operation,
                error=str(exc_val),
                exc_info=(exc_type, exc_val, exc_tb)
            )
        return False  # Don't suppress exception


def log_critical_error(service_name: str, error_message: str, details: dict = None):
    """
    Manually log a critical error that should immediately notify admins.

    Args:
        service_name: Service name (e.g., "Nano Banana", "Payment System")
        error_message: Short error description
        details: Additional context dictionary
    """
    logger = get_logger(f"service.{service_name.lower().replace(' ', '_')}")
    logger.error(
        f"critical_error_in_{service_name.lower().replace(' ', '_')}",
        error=error_message,
        details=details or {},
        exc_info=True
    )
