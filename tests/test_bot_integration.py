"""
Integration tests for bot functionality.
Tests button clicks and AI model selection flow.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot
from aiogram.types import Update, Message, CallbackQuery, User as TelegramUser
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from app.database.models.user import User
from app.services.ai.ai_factory import AIServiceFactory
from app.services.ai.mock_service import MockAIService


@pytest.fixture
def mock_telegram_user():
    """Create mock Telegram user."""
    return TelegramUser(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser"
    )


@pytest.fixture
def mock_db_user():
    """Create mock database user."""
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    user.id = 1
    # full_name is a computed property, will be "Test User"
    return user


@pytest.fixture
def mock_message(mock_telegram_user):
    """Create mock message."""
    msg = AsyncMock(spec=Message)
    msg.from_user = mock_telegram_user
    msg.text = "Test message"
    msg.answer = AsyncMock()
    msg.edit_text = AsyncMock()
    return msg


@pytest.fixture
def mock_callback(mock_telegram_user, mock_message):
    """Create mock callback query."""
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = mock_telegram_user
    callback.data = "test_data"
    callback.message = mock_message
    callback.answer = AsyncMock()
    return callback


@pytest.mark.asyncio
class TestAIModelSelection:
    """Test AI model selection and processing."""

    async def test_ai_factory_returns_mock_without_api_keys(self):
        """Test that AI factory returns mock service when no API keys configured."""
        service = AIServiceFactory.create_service("gpt-4", use_mock=True)
        assert isinstance(service, MockAIService)

    async def test_ai_factory_supports_all_models(self):
        """Test that AI factory supports all advertised models."""
        models = ["gpt-4", "gpt-4-mini", "claude", "gemini", "deepseek"]

        for model in models:
            service = AIServiceFactory.create_service(model, use_mock=True)
            assert service is not None
            assert isinstance(service, MockAIService)

    async def test_mock_service_generates_text(self):
        """Test that mock service can generate text responses."""
        service = MockAIService()
        response = await service.generate_text(
            prompt="Hello, how are you?",
            model="gpt-4"
        )

        assert response.success is True
        assert response.content is not None
        assert len(response.content) > 0
        assert response.metadata.get("mock") is True

    async def test_mock_service_different_models(self):
        """Test that mock service returns different responses for different models."""
        service = MockAIService()

        models = ["gpt-4", "gpt-4-mini", "claude", "gemini", "deepseek"]
        responses = []

        for model in models:
            response = await service.generate_text(
                prompt="Test prompt",
                model=model
            )
            responses.append(response.content)

        # Check that responses are different for different models
        assert len(set(responses)) == len(models)

    async def test_ai_factory_generate_text_convenience(self):
        """Test AI factory convenience method."""
        response = await AIServiceFactory.generate_text(
            model="gpt-4",
            prompt="Test prompt",
            use_mock=True
        )

        assert response.success is True
        assert response.content is not None


@pytest.mark.asyncio
class TestBotHandlers:
    """Test bot handlers with mocked dependencies."""

    @patch("app.bot.handlers.text_ai.async_session_maker")
    async def test_select_model_button(self, mock_session_maker, mock_callback):
        """Test AI model selection button handler."""
        from app.bot.handlers.text_ai import select_ai_model

        mock_callback.data = "select_model"

        await select_ai_model(mock_callback)

        # Check that message was edited
        mock_callback.message.edit_text.assert_called_once()

        # Check that callback was answered
        mock_callback.answer.assert_called_once()

        # Verify message contains model information
        call_args = mock_callback.message.edit_text.call_args
        text = call_args[0][0] if call_args[0] else call_args.kwargs.get("text", "")
        assert "GPT-4" in text
        assert "Claude" in text
        assert "Gemini" in text

    @patch("app.bot.handlers.text_ai.async_session_maker")
    async def test_choose_model_button(self, mock_session_maker, mock_callback):
        """Test choosing specific AI model."""
        from app.bot.handlers.text_ai import choose_model

        # Mock FSM context
        storage = MemoryStorage()
        state = FSMContext(
            storage=storage,
            key=MagicMock()
        )

        models = ["gpt-4", "gpt-4-mini", "claude", "gemini", "deepseek"]

        for model in models:
            mock_callback.data = f"model:{model}"

            await choose_model(mock_callback, state)

            # Verify message was edited
            assert mock_callback.message.edit_text.called

            # Verify state was set
            data = await state.get_data()
            assert data.get("ai_model") == model
            assert data.get("tokens_cost") > 0


@pytest.mark.asyncio
class TestSubscriptionFlow:
    """Test subscription and token management."""

    async def test_subscription_button_displays_plans(
        self,
        mock_callback,
        mock_db_user
    ):
        """Test that subscription button shows available plans."""
        from app.bot.handlers.subscription import show_subscriptions

        await show_subscriptions(mock_callback, mock_db_user)

        # Check message was edited
        mock_callback.message.edit_text.assert_called_once()

        # Verify subscription plans are shown
        call_args = mock_callback.message.edit_text.call_args
        text = call_args[0][0] if call_args[0] else call_args.kwargs.get("text", "")

        # Check that subscription info is displayed
        assert "подписк" in text.lower()
        assert "gpt-4" in text.lower() or "claude" in text.lower()


def test_model_provider_mapping():
    """Test that model to provider mapping is correct."""
    from app.services.ai.ai_factory import AIServiceFactory

    expected_mapping = {
        "gpt-4": "openai",
        "gpt-4-mini": "openai",
        "claude": "anthropic",
        "gemini": "google",
        "deepseek": "deepseek",
    }

    for model, expected_provider in expected_mapping.items():
        provider = AIServiceFactory.get_provider_name(model)
        assert provider == expected_provider, f"Model {model} should use {expected_provider}"


def test_real_model_names():
    """Test that model names are correctly mapped to API names."""
    from app.services.ai.ai_factory import AIServiceFactory

    # Test that we get valid model names
    models = ["gpt-4", "claude", "gemini", "deepseek"]

    for model in models:
        real_name = AIServiceFactory.get_real_model_name(model)
        assert real_name is not None
        assert len(real_name) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
