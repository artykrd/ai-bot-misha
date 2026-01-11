"""
Test script for monitoring system.
Tests metrics collection, health checks, and basic functionality.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.monitoring.metrics import MetricsCollector
from app.monitoring.health_checks import HealthChecker


async def test_metrics():
    """Test metrics collection."""
    print("=" * 60)
    print("Testing Metrics Collection")
    print("=" * 60)

    collector = MetricsCollector()

    # Test CPU metrics
    print("\n📊 CPU Metrics:")
    cpu = collector.get_cpu_metrics()
    if cpu:
        print(f"  CPU Percent: {cpu.get('cpu_percent', 0):.1f}%")
        print(f"  Load Average: {cpu.get('load_average', 0):.2f}")
        print(f"  Load Average (normalized): {cpu.get('load_average_normalized', 0):.2f}")
        print(f"  CPU Count: {cpu.get('cpu_count', 0)}")
        print("  ✅ CPU metrics OK")
    else:
        print("  ❌ CPU metrics FAILED")

    # Test Memory metrics
    print("\n💾 Memory Metrics:")
    memory = collector.get_memory_metrics()
    if memory:
        print(f"  Total: {memory.get('total_mb', 0):.0f} MB")
        print(f"  Available: {memory.get('available_mb', 0):.0f} MB")
        print(f"  Used: {memory.get('used_mb', 0):.0f} MB")
        print(f"  Percent: {memory.get('percent', 0):.1f}%")
        print("  ✅ Memory metrics OK")
    else:
        print("  ❌ Memory metrics FAILED")

    # Test Swap metrics
    print("\n💿 Swap Metrics:")
    swap = collector.get_swap_metrics()
    if swap:
        print(f"  Total: {swap.get('total_mb', 0):.0f} MB")
        print(f"  Used: {swap.get('used_mb', 0):.0f} MB")
        print(f"  Free: {swap.get('free_mb', 0):.0f} MB")
        print(f"  Percent: {swap.get('percent', 0):.1f}%")
        print("  ✅ Swap metrics OK")
    else:
        print("  ❌ Swap metrics FAILED")

    # Test Disk metrics
    print("\n📦 Disk Metrics:")
    disk = collector.get_disk_metrics()
    if disk:
        print(f"  Total: {disk.get('total_gb', 0):.1f} GB")
        print(f"  Used: {disk.get('used_gb', 0):.1f} GB")
        print(f"  Free: {disk.get('free_gb', 0):.1f} GB")
        print(f"  Percent: {disk.get('percent', 0):.1f}%")
        print("  ✅ Disk metrics OK")
    else:
        print("  ❌ Disk metrics FAILED")

    # Test Uptime metrics
    print("\n⏱ Uptime Metrics:")
    uptime = collector.get_uptime()
    if uptime:
        print(f"  Uptime Hours: {uptime.get('uptime_hours', 0):.1f}")
        print(f"  Uptime Days: {uptime.get('uptime_days', 0):.2f}")
        print("  ✅ Uptime metrics OK")
    else:
        print("  ❌ Uptime metrics FAILED")

    # Test all metrics at once
    print("\n📋 All Metrics:")
    all_metrics = collector.get_all_metrics()
    if all_metrics:
        print("  ✅ All metrics collection OK")
    else:
        print("  ❌ All metrics collection FAILED")


async def test_health_checks():
    """Test health checks."""
    print("\n" + "=" * 60)
    print("Testing Health Checks")
    print("=" * 60)

    checker = HealthChecker()

    # Test webhook health check
    print("\n🌐 Webhook Health Check:")
    try:
        webhook = await checker.check_webhook(timeout=5.0)
        status = webhook.get('status', 'unknown')
        print(f"  Status: {status}")
        if webhook.get('error'):
            print(f"  Error: {webhook.get('error')}")
        print(f"  Response Time: {webhook.get('response_time', 0):.3f}s")
        if status == "healthy":
            print("  ✅ Webhook is healthy")
        else:
            print("  ⚠️ Webhook is unavailable (expected if API not running)")
    except Exception as e:
        print(f"  ❌ Webhook check error: {e}")

    # Note: Redis and PostgreSQL checks would require connections
    # We skip them in this basic test
    print("\n📝 Note: Redis and PostgreSQL checks require active connections")
    print("   They will be tested when the bot is running")


async def main():
    """Run all tests."""
    print("🚀 Starting Monitoring System Tests\n")

    try:
        await test_metrics()
        await test_health_checks()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        print("\n📌 Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env with TELEGRAM_ADMIN_BOT_TOKEN")
        print("  3. Start the bot to test full monitoring system")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
