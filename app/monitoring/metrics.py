"""
System metrics collection using psutil.
Monitors CPU, RAM, Swap, and Disk usage.
"""
import psutil
from typing import Dict, Any
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects system metrics using psutil."""

    @staticmethod
    def get_cpu_metrics() -> Dict[str, Any]:
        """
        Get CPU metrics.

        Returns:
            Dict with cpu_percent, load_average, cpu_count
        """
        try:
            # Get load average (1, 5, 15 minutes)
            load_avg = psutil.getloadavg()
            cpu_count = psutil.cpu_count()

            # Normalize load average by CPU count
            load_avg_normalized = load_avg[0] / cpu_count if cpu_count else load_avg[0]

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "load_average": load_avg[0],
                "load_average_5min": load_avg[1],
                "load_average_15min": load_avg[2],
                "load_average_normalized": load_avg_normalized,
                "cpu_count": cpu_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("cpu_metrics_collection_failed", error=str(e))
            return {}

    @staticmethod
    def get_memory_metrics() -> Dict[str, Any]:
        """
        Get memory (RAM) metrics.

        Returns:
            Dict with total, available, used, percent, available_mb
        """
        try:
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)

            return {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": available_mb,
                "used_mb": memory.used / (1024 * 1024),
                "percent": memory.percent,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("memory_metrics_collection_failed", error=str(e))
            return {}

    @staticmethod
    def get_swap_metrics() -> Dict[str, Any]:
        """
        Get swap memory metrics.

        Returns:
            Dict with total, used, free, percent, used_mb
        """
        try:
            swap = psutil.swap_memory()
            used_mb = swap.used / (1024 * 1024)

            return {
                "total_mb": swap.total / (1024 * 1024),
                "used_mb": used_mb,
                "free_mb": swap.free / (1024 * 1024),
                "percent": swap.percent,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("swap_metrics_collection_failed", error=str(e))
            return {}

    @staticmethod
    def get_disk_metrics() -> Dict[str, Any]:
        """
        Get disk usage metrics for root partition.

        Returns:
            Dict with total, used, free, percent
        """
        try:
            disk = psutil.disk_usage('/')

            return {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent": disk.percent,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("disk_metrics_collection_failed", error=str(e))
            return {}

    @staticmethod
    def get_uptime() -> Dict[str, Any]:
        """
        Get system uptime.

        Returns:
            Dict with boot_time, uptime_seconds, uptime_hours, uptime_days
        """
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = (datetime.now() - boot_time).total_seconds()

            return {
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime_seconds,
                "uptime_hours": uptime_seconds / 3600,
                "uptime_days": uptime_seconds / 86400,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("uptime_metrics_collection_failed", error=str(e))
            return {}

    @classmethod
    def get_all_metrics(cls) -> Dict[str, Any]:
        """
        Get all system metrics.

        Returns:
            Dict with all metrics
        """
        return {
            "cpu": cls.get_cpu_metrics(),
            "memory": cls.get_memory_metrics(),
            "swap": cls.get_swap_metrics(),
            "disk": cls.get_disk_metrics(),
            "uptime": cls.get_uptime(),
            "collected_at": datetime.utcnow().isoformat()
        }
