"""
Main monitoring system.
Coordinates metrics collection, health checks, and alerting.
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.logger import get_logger
from app.core.scheduler import scheduler
from app.monitoring.metrics import MetricsCollector
from app.monitoring.health_checks import HealthChecker
from app.monitoring.notifier import monitoring_notifier
from app.monitoring.daily_report import daily_report_generator

logger = get_logger(__name__)


class SystemMonitor:
    """
    Main monitoring system.
    Coordinates all monitoring activities.
    """

    # Threshold values
    CPU_WARNING_THRESHOLD = 0.8
    CPU_CRITICAL_THRESHOLD = 1.2
    RAM_WARNING_THRESHOLD_MB = 300
    RAM_CRITICAL_THRESHOLD_MB = 150
    SWAP_WARNING_THRESHOLD_MB = 200

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._started = False

    async def check_and_alert(self):
        """
        Check metrics and send alerts if thresholds are exceeded.
        Called periodically by monitoring loop.
        """
        try:
            # Collect metrics
            metrics = self.metrics_collector.get_all_metrics()

            # Check CPU
            cpu_load = metrics.get("cpu", {}).get("load_average_normalized", 0)
            if cpu_load > self.CPU_CRITICAL_THRESHOLD:
                await monitoring_notifier.send_alert(
                    alert_type="CPU Load",
                    severity="critical",
                    message=f"CPU load is critically high: {cpu_load:.2f}",
                    details={
                        "load_average": cpu_load,
                        "threshold": self.CPU_CRITICAL_THRESHOLD,
                        "cpu_percent": metrics.get("cpu", {}).get("cpu_percent", 0)
                    }
                )
            elif cpu_load > self.CPU_WARNING_THRESHOLD:
                await monitoring_notifier.send_alert(
                    alert_type="CPU Load",
                    severity="warning",
                    message=f"CPU load is high: {cpu_load:.2f}",
                    details={
                        "load_average": cpu_load,
                        "threshold": self.CPU_WARNING_THRESHOLD,
                        "cpu_percent": metrics.get("cpu", {}).get("cpu_percent", 0)
                    }
                )

            # Check RAM
            ram_available = metrics.get("memory", {}).get("available_mb", 0)
            if ram_available < self.RAM_CRITICAL_THRESHOLD_MB:
                await monitoring_notifier.send_alert(
                    alert_type="Memory",
                    severity="critical",
                    message=f"Available RAM is critically low: {ram_available:.0f} MB",
                    details={
                        "available_mb": ram_available,
                        "threshold_mb": self.RAM_CRITICAL_THRESHOLD_MB,
                        "used_percent": metrics.get("memory", {}).get("percent", 0)
                    }
                )
            elif ram_available < self.RAM_WARNING_THRESHOLD_MB:
                await monitoring_notifier.send_alert(
                    alert_type="Memory",
                    severity="warning",
                    message=f"Available RAM is low: {ram_available:.0f} MB",
                    details={
                        "available_mb": ram_available,
                        "threshold_mb": self.RAM_WARNING_THRESHOLD_MB,
                        "used_percent": metrics.get("memory", {}).get("percent", 0)
                    }
                )

            # Check Swap
            swap_used = metrics.get("swap", {}).get("used_mb", 0)
            if swap_used > self.SWAP_WARNING_THRESHOLD_MB:
                await monitoring_notifier.send_alert(
                    alert_type="Swap Memory",
                    severity="warning",
                    message=f"Swap usage is high: {swap_used:.0f} MB",
                    details={
                        "used_mb": swap_used,
                        "threshold_mb": self.SWAP_WARNING_THRESHOLD_MB,
                        "percent": metrics.get("swap", {}).get("percent", 0)
                    }
                )

            # Check services health
            services = await self.health_checker.check_all_services()

            # Alert on unhealthy services
            # Note: Webhook check removed - runs in same process as bot

            if services.get("redis", {}).get("status") != "healthy":
                await monitoring_notifier.send_alert(
                    alert_type="Redis Service",
                    severity="critical",
                    message="Redis service is unavailable",
                    details={
                        "error": services.get("redis", {}).get("error", "Unknown")
                    }
                )

            if services.get("postgresql", {}).get("status") != "healthy":
                await monitoring_notifier.send_alert(
                    alert_type="PostgreSQL Service",
                    severity="critical",
                    message="PostgreSQL service is unavailable",
                    details={
                        "error": services.get("postgresql", {}).get("error", "Unknown")
                    }
                )

            logger.debug("monitoring_check_completed")

        except Exception as e:
            logger.error("monitoring_check_failed", error=str(e))

    async def monitoring_loop(self):
        """
        Main monitoring loop.
        Runs continuously in the background.
        """
        logger.info("monitoring_loop_started")

        while self._started:
            try:
                # Check metrics and alert
                await self.check_and_alert()

                # Store metrics for daily report
                await daily_report_generator.store_metrics()

                # Wait 1 minute before next check (for near-instant critical alerts)
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                logger.info("monitoring_loop_cancelled")
                break
            except Exception as e:
                logger.error("monitoring_loop_error", error=str(e))
                # Wait a bit before retrying
                await asyncio.sleep(60)

        logger.info("monitoring_loop_stopped")

    def start(self):
        """
        Start monitoring system.
        Called during bot startup.
        """
        if self._started:
            logger.warning("monitoring_already_started")
            return

        self._started = True

        # Start monitoring loop in background
        self._monitoring_task = asyncio.create_task(self.monitoring_loop())

        # Daily report disabled - only critical alerts are sent instantly
        # scheduler.add_daily_job(
        #     daily_report_generator.send_daily_report,
        #     time_str="03:00"
        # )

        logger.info("monitoring_started")

    async def stop(self):
        """
        Stop monitoring system.
        Called during bot shutdown.
        """
        if not self._started:
            return

        self._started = False

        # Cancel monitoring task
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("monitoring_stopped")

    async def get_current_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        Useful for manual checks or API endpoints.

        Returns:
            Dict with current metrics and services status
        """
        try:
            metrics = self.metrics_collector.get_all_metrics()
            services = await self.health_checker.check_all_services()

            return {
                "metrics": metrics,
                "services": services,
                "thresholds": {
                    "cpu_warning": self.CPU_WARNING_THRESHOLD,
                    "cpu_critical": self.CPU_CRITICAL_THRESHOLD,
                    "ram_warning_mb": self.RAM_WARNING_THRESHOLD_MB,
                    "ram_critical_mb": self.RAM_CRITICAL_THRESHOLD_MB,
                    "swap_warning_mb": self.SWAP_WARNING_THRESHOLD_MB
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("get_current_status_failed", error=str(e))
            return {}


# Global instance
system_monitor = SystemMonitor()
