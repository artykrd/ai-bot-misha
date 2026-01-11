"""
Error notification system for admin bot.
Sends error notifications to administrators when critical errors occur.
"""
import logging
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import Bot

from app.core.config import settings


class ErrorNotifier:
    """
    Handles error notifications to admin bot.
    Includes throttling to prevent spam.
    """

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.last_notification_time = defaultdict(lambda: datetime.min)
        self.notification_cooldown = timedelta(minutes=5)  # 5 minutes between same error notifications
        self.error_counts = defaultdict(int)

    def set_bot(self, bot: Bot):
        """Set the bot instance for sending notifications."""
        self.bot = bot

    async def notify_admins(self, error_type: str, error_message: str, details: str = ""):
        """
        Send error notification to all admins.

        Args:
            error_type: Type of error (e.g., "Nano Banana", "Referral", "Database")
            error_message: Short error description
            details: Additional details about the error
        """
        if not self.bot or not settings.admin_user_ids:
            return

        # Create error key for throttling
        error_key = f"{error_type}:{error_message[:50]}"

        # Check if we should send notification (throttling)
        now = datetime.now()
        last_time = self.last_notification_time[error_key]

        if now - last_time < self.notification_cooldown:
            # Just increment counter, don't send
            self.error_counts[error_key] += 1
            return

        # Update last notification time
        self.last_notification_time[error_key] = now

        # Get accumulated count if any
        count = self.error_counts[error_key]
        count_text = f" (повторилось {count + 1} раз)" if count > 0 else ""
        self.error_counts[error_key] = 0  # Reset counter

        # Format message
        message = f"""🚨 **Ошибка в боте**{count_text}

📁 **Модуль:** {error_type}
❌ **Ошибка:** {error_message}

📝 **Подробности:**
{details if details else 'Нет дополнительных деталей'}

🕐 **Время:** {now.strftime('%Y-%m-%d %H:%M:%S')}

💡 **Действие:** Проверьте логи в logs/error.log"""

        # Send to all admins
        for admin_id in settings.admin_user_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Can't send notification, just log it
                logging.error(f"Failed to send error notification to admin {admin_id}: {e}")


# Global instance
error_notifier = ErrorNotifier()


class ErrorNotificationHandler(logging.Handler):
    """
    Custom logging handler that sends ERROR and CRITICAL level logs to admin bot.
    """

    def __init__(self, notifier: ErrorNotifier):
        super().__init__(level=logging.ERROR)
        self.notifier = notifier

    def emit(self, record: logging.LogRecord):
        """Handle log record and send notification if needed."""
        try:
            # Extract module information
            module_name = record.name.split('.')[-1] if record.name else "Unknown"

            # Map module names to user-friendly names
            module_mapping = {
                "nano_banana_service": "Nano Banana",
                "dalle_service": "DALL-E",
                "veo_service": "Veo",
                "sora_service": "Sora",
                "suno_service": "Suno",
                "referral": "Реферальная программа",
                "subscription_service": "Система подписок",
                "payment": "Платежная система",
                "database": "База данных",
            }

            error_type = module_mapping.get(module_name, module_name.title())

            # Get error message
            error_message = record.getMessage()

            # Get stack trace if available
            details = ""
            if record.exc_info:
                import traceback
                details = ''.join(traceback.format_exception(*record.exc_info))
                # Limit details to 500 characters
                if len(details) > 500:
                    details = details[:500] + "\n... (truncated)"

            # Send notification asynchronously
            # Create a task to avoid blocking
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(
                    self.notifier.notify_admins(error_type, error_message, details)
                )
            except RuntimeError:
                # No event loop running, skip notification
                pass

        except Exception:
            # Don't let handler errors break the application
            self.handleError(record)


def setup_error_notifications(bot: Bot):
    """
    Setup error notification system.

    Args:
        bot: Bot instance for sending notifications
    """
    error_notifier.set_bot(bot)

    # Add handler to root logger
    handler = ErrorNotificationHandler(error_notifier)
    logging.getLogger().addHandler(handler)
