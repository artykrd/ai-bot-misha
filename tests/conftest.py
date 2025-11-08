"""
Pytest configuration and fixtures.
"""
import pytest


# Configure pytest-asyncio to use session scope
def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )
