"""
Daily monitoring report generation.
Collects and aggregates metrics over 24 hours.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import statistics

from app.core.redis_client import redis_client
from app.core.logger import get_logger
from app.monitoring.metrics import MetricsCollector
from app.monitoring.health_checks import HealthChecker
from app.monitoring.notifier import monitoring_notifier

logger = get_logger(__name__)


class DailyReportGenerator:
    """
    Generates daily monitoring reports.
    Stores metrics in Redis for aggregation.
    """

    METRICS_KEY_PREFIX = "monitoring:metrics:"
    ERROR_COUNT_KEY = "monitoring:errors:daily"
    METRICS_RETENTION_HOURS = 48  # Keep metrics for 48 hours

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()

    async def store_metrics(self):
        """
        Collect and store current metrics in Redis.
        Called periodically (e.g., every 5 minutes).
        """
        try:
            metrics = self.metrics_collector.get_all_metrics()
            timestamp = datetime.utcnow().isoformat()
            key = f"{self.METRICS_KEY_PREFIX}{timestamp}"

            # Store metrics in Redis with expiration
            await redis_client.set_json(
                key,
                metrics,
                expire=self.METRICS_RETENTION_HOURS * 3600
            )

            logger.debug("metrics_stored", timestamp=timestamp)
        except Exception as e:
            logger.error("metrics_storage_failed", error=str(e))

    async def increment_error_count(self):
        """
        Increment daily error counter.
        Called by error handler.
        """
        try:
            # Increment counter
            await redis_client.increment(self.ERROR_COUNT_KEY)

            # Set expiration to end of day + 1 hour
            now = datetime.utcnow()
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            expire_seconds = int((end_of_day - now).total_seconds()) + 3600

            await redis_client.expire(self.ERROR_COUNT_KEY, expire_seconds)

        except Exception as e:
            logger.error("error_count_increment_failed", error=str(e))

    async def get_stored_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Retrieve stored metrics from Redis.

        Args:
            hours: Number of hours to retrieve

        Returns:
            List of metrics dictionaries
        """
        try:
            # Get all keys matching pattern
            pattern = f"{self.METRICS_KEY_PREFIX}*"
            keys = []

            # Redis scan to get all matching keys
            cursor = 0
            while True:
                cursor, partial_keys = await redis_client.client.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                keys.extend(partial_keys)
                if cursor == 0:
                    break

            # Filter keys by time range
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_keys = []

            for key in keys:
                # Extract timestamp from key
                timestamp_str = key.replace(self.METRICS_KEY_PREFIX, "")
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp >= cutoff_time:
                        recent_keys.append(key)
                except ValueError:
                    continue

            # Retrieve metrics
            metrics_list = []
            for key in recent_keys:
                metrics = await redis_client.get_json(key)
                if metrics:
                    metrics_list.append(metrics)

            return metrics_list

        except Exception as e:
            logger.error("stored_metrics_retrieval_failed", error=str(e))
            return []

    async def generate_daily_report(self) -> Dict[str, Any]:
        """
        Generate daily report from stored metrics.

        Returns:
            Report data dictionary
        """
        try:
            # Get metrics for last 24 hours
            metrics_list = await self.get_stored_metrics(hours=24)

            if not metrics_list:
                logger.warning("no_metrics_for_daily_report")
                # Fallback to current metrics
                current_metrics = self.metrics_collector.get_all_metrics()
                return await self._generate_report_from_current(current_metrics)

            # Aggregate metrics
            cpu_loads = [
                m.get("cpu", {}).get("load_average_normalized", 0)
                for m in metrics_list
                if m.get("cpu", {}).get("load_average_normalized")
            ]

            memory_available = [
                m.get("memory", {}).get("available_mb", 0)
                for m in metrics_list
                if m.get("memory", {}).get("available_mb")
            ]

            memory_percents = [
                m.get("memory", {}).get("percent", 0)
                for m in metrics_list
                if m.get("memory", {}).get("percent")
            ]

            swap_used = [
                m.get("swap", {}).get("used_mb", 0)
                for m in metrics_list
                if m.get("swap", {}).get("used_mb")
            ]

            # Get current metrics for disk and uptime
            current_metrics = self.metrics_collector.get_all_metrics()

            # Get error count
            error_count_str = await redis_client.get(self.ERROR_COUNT_KEY)
            error_count = int(error_count_str) if error_count_str else 0

            # Check services health
            services_health = await self.health_checker.check_all_services()

            # Build report
            report = {
                "avg_cpu_load": statistics.mean(cpu_loads) if cpu_loads else 0,
                "peak_cpu_load": max(cpu_loads) if cpu_loads else 0,
                "min_available_ram_mb": min(memory_available) if memory_available else 0,
                "avg_memory_percent": statistics.mean(memory_percents) if memory_percents else 0,
                "max_swap_used_mb": max(swap_used) if swap_used else 0,
                "disk_used_percent": current_metrics.get("disk", {}).get("percent", 0),
                "disk_free_gb": current_metrics.get("disk", {}).get("free_gb", 0),
                "error_count": error_count,
                "uptime_hours": current_metrics.get("uptime", {}).get("uptime_hours", 0),
                "redis_status": services_health.get("redis", {}).get("status", "unknown"),
                "postgresql_status": services_health.get("postgresql", {}).get("status", "unknown"),
                "generated_at": datetime.utcnow().isoformat()
            }

            return report

        except Exception as e:
            logger.error("daily_report_generation_failed", error=str(e))
            return {}

    async def _generate_report_from_current(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate report from current metrics only (fallback).

        Args:
            current_metrics: Current system metrics

        Returns:
            Report data dictionary
        """
        try:
            # Check services health
            services_health = await self.health_checker.check_all_services()

            # Get error count
            error_count_str = await redis_client.get(self.ERROR_COUNT_KEY)
            error_count = int(error_count_str) if error_count_str else 0

            report = {
                "avg_cpu_load": current_metrics.get("cpu", {}).get("load_average_normalized", 0),
                "peak_cpu_load": current_metrics.get("cpu", {}).get("load_average_normalized", 0),
                "min_available_ram_mb": current_metrics.get("memory", {}).get("available_mb", 0),
                "avg_memory_percent": current_metrics.get("memory", {}).get("percent", 0),
                "max_swap_used_mb": current_metrics.get("swap", {}).get("used_mb", 0),
                "disk_used_percent": current_metrics.get("disk", {}).get("percent", 0),
                "disk_free_gb": current_metrics.get("disk", {}).get("free_gb", 0),
                "error_count": error_count,
                "uptime_hours": current_metrics.get("uptime", {}).get("uptime_hours", 0),
                "redis_status": services_health.get("redis", {}).get("status", "unknown"),
                "postgresql_status": services_health.get("postgresql", {}).get("status", "unknown"),
                "generated_at": datetime.utcnow().isoformat()
            }

            return report

        except Exception as e:
            logger.error("fallback_report_generation_failed", error=str(e))
            return {}

    async def send_daily_report(self):
        """
        Generate and send daily report.
        Should be called once per day by scheduler.
        """
        try:
            logger.info("generating_daily_report")

            # Generate report
            report = await self.generate_daily_report()

            if report:
                # Send report
                await monitoring_notifier.send_daily_report(report)
                logger.info("daily_report_sent_successfully")

                # Reset daily error counter
                await redis_client.delete(self.ERROR_COUNT_KEY)
            else:
                logger.warning("daily_report_empty")

        except Exception as e:
            logger.error("daily_report_send_failed", error=str(e))


# Global instance
daily_report_generator = DailyReportGenerator()
