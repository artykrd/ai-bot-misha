"""
Monitoring notification system.
Sends alerts to admin bot with throttling to prevent spam.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import Bot

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class MonitoringNotifier:
    """
    Sends monitoring alerts to admin bot.
    Includes throttling to prevent spam.
    """

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.last_notification_time = defaultdict(lambda: datetime.min)
        self.warning_cooldown = timedelta(minutes=15)  # 15 minutes for warnings
        self.critical_cooldown = timedelta(minutes=1)  # 1 minute for critical - near instant
        self._initialize_bot()

    def _initialize_bot(self):
        """Initialize admin bot using admin bot token from settings."""
        try:
            if settings.telegram_admin_bot_token:
                self.bot = Bot(token=settings.telegram_admin_bot_token)
                logger.info("monitoring_notifier_initialized")
        except Exception as e:
            logger.error("monitoring_notifier_init_failed", error=str(e))

    def _escape_markdown(self, text: str) -> str:
        """Escape markdown special characters."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    def _should_send_notification(self, alert_key: str, severity: str) -> bool:
        """
        Check if notification should be sent based on throttling rules.

        Args:
            alert_key: Unique key for this alert
            severity: 'warning' or 'critical'

        Returns:
            True if notification should be sent
        """
        if not self.bot or not settings.admin_user_ids:
            return False

        now = datetime.utcnow()
        last_time = self.last_notification_time[alert_key]

        # Critical alerts have shorter cooldown
        cooldown = self.critical_cooldown if severity == "critical" else self.warning_cooldown

        if now - last_time < cooldown:
            return False

        self.last_notification_time[alert_key] = now
        return True

    async def send_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send monitoring alert to admins.

        Args:
            alert_type: Type of alert (e.g., "CPU", "Memory", "Service")
            severity: 'warning' or 'critical'
            message: Alert message
            details: Additional details
        """
        alert_key = f"{alert_type}:{severity}"

        # Check throttling (critical alerts bypass for first occurrence)
        if not self._should_send_notification(alert_key, severity):
            return

        # Format message
        emoji = "⚠️" if severity == "warning" else "🔴"
        severity_text = "WARNING" if severity == "warning" else "CRITICAL"

        safe_alert_type = self._escape_markdown(alert_type)
        safe_message = self._escape_markdown(message)

        notification = f"""{emoji} *MONITORING {severity_text}*

📊 *Тип:* {safe_alert_type}
📝 *Сообщение:* {safe_message}

🕐 *Время:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"""

        # Add details if provided
        if details:
            notification += "\n\n📋 *Детали:*"
            for key, value in details.items():
                safe_key = self._escape_markdown(str(key))
                safe_value = self._escape_markdown(str(value))
                notification += f"\n  • {safe_key}: {safe_value}"

        # Send to all admins
        for admin_id in settings.admin_user_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=notification,
                    parse_mode="Markdown"
                )
                logger.info(
                    "monitoring_alert_sent",
                    admin_id=admin_id,
                    alert_type=alert_type,
                    severity=severity
                )
            except Exception as e:
                logger.error(
                    "monitoring_alert_send_failed",
                    admin_id=admin_id,
                    error=str(e)
                )

    async def send_daily_report(
        self,
        report_data: Dict[str, Any]
    ):
        """
        Send daily monitoring report to admins.

        Args:
            report_data: Report data with metrics
        """
        if not self.bot or not settings.admin_user_ids:
            return

        try:
            # Format report
            report = f"""📊 *ЕЖЕДНЕВНЫЙ ОТЧЁТ МОНИТОРИНГА*

📅 *Дата:* {datetime.utcnow().strftime('%Y-%m-%d')}

🔄 *CPU*
  • Средний load: {report_data.get('avg_cpu_load', 0):.2f}
  • Пиковый load: {report_data.get('peak_cpu_load', 0):.2f}

💾 *Память*
  • Минимум доступно: {report_data.get('min_available_ram_mb', 0):.0f} MB
  • Средний процент использования: {report_data.get('avg_memory_percent', 0):.1f}%

💿 *Swap*
  • Максимум использовано: {report_data.get('max_swap_used_mb', 0):.0f} MB

📦 *Диск*
  • Использовано: {report_data.get('disk_used_percent', 0):.1f}%
  • Свободно: {report_data.get('disk_free_gb', 0):.1f} GB

❌ *Ошибки*
  • Всего за сутки: {report_data.get('error_count', 0)}

⏱ *Uptime*
  • Время работы: {report_data.get('uptime_hours', 0):.1f} часов

✅ *Статус сервисов*
  • Redis: {report_data.get('redis_status', 'unknown')}
  • PostgreSQL: {report_data.get('postgresql_status', 'unknown')}

🕐 *Сгенерировано:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

            # Send to all admins
            for admin_id in settings.admin_user_ids:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=report,
                        parse_mode="Markdown"
                    )
                    logger.info("daily_report_sent", admin_id=admin_id)
                except Exception as e:
                    logger.error(
                        "daily_report_send_failed",
                        admin_id=admin_id,
                        error=str(e)
                    )

        except Exception as e:
            logger.error("daily_report_format_failed", error=str(e))


# Global instance
monitoring_notifier = MonitoringNotifier()
