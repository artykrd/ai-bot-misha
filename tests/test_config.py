"""
Test configuration loading.
"""
import pytest
from app.core.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings is not None
    assert settings.telegram_bot_token is not None
    assert settings.database_url is not None


def test_environment():
    """Test environment configuration."""
    assert settings.environment in ["development", "production"]


def test_admin_ids():
    """Test admin IDs are parsed correctly."""
    assert isinstance(settings.admin_user_ids, list)
    assert len(settings.admin_user_ids) > 0


def test_properties():
    """Test computed properties."""
    if settings.environment == "development":
        assert settings.is_development is True
        assert settings.is_production is False
    else:
        assert settings.is_development is False
        assert settings.is_production is True
