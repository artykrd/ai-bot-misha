#!/usr/bin/env python3
# coding: utf-8
"""
Text AI handlers (ChatGPT, Claude, etc.) - Updated with new billing system.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.inline import ai_models_keyboard, back_to_main_keyboard
from app.bot.states.dialog import AIGenerationStates
from app.database.models.user import User
from app.database.database import async_session_maker
from app.services.billing.billing_service import BillingService
from app.services.subscription.subscription_service import SubscriptionService
from app.core.billing_config import ModelType, get_text_model_billing
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError

logger = get_logger(__name__)

router = Router(name="text_ai")


# Model configurations with new billing
MODEL_CONFIGS = {
    "gpt-4o": {
        "display_name": "GPT-4o",
        "description": "Самая продвинутая модель OpenAI",
        "billing_id": "gpt-4o",
    },
    "gpt-4.1-mini": {
        "display_name": "GPT-4.1 Mini",
        "description": "Быстрая и доступная модель",
        "billing_id": "gpt-4.1-mini",
    },
    "gpt-5-mini": {
        "display_name": "GPT-5 Mini",
        "description": "Новейшая мини-модель OpenAI",
        "billing_id": "gpt-5-mini",
    },
    "claude-4": {
        "display_name": "Claude 4",
        "description": "Модель от Anthropic",
        "billing_id": "claude-4",
    },
    "gemini-flash-2.0": {
        "display_name": "Gemini Flash 2.0",
        "description": "Быстрая модель от Google",
        "billing_id": "gemini-flash-2.0",
    },
    "deepseek-chat": {
        "display_name": "DeepSeek Chat",
        "description": "Отличная альтернатива",
        "billing_id": "deepseek-chat",
    },
    "deepseek-r1": {
        "display_name": "DeepSeek R1",
        "description": "Reasoning модель DeepSeek",
        "billing_id": "deepseek-r1",
    },
    "o3-mini": {
        "display_name": "O3 Mini",
        "description": "OpenAI Reasoning модель",
        "billing_id": "o3-mini",
    },
    "sonar": {
        "display_name": "Sonar (with search)",
        "description": "Модель с поиском в интернете",
        "billing_id": "sonar",
    },
    "sonar-pro": {
        "display_name": "Sonar Pro",
        "description": "Продвинутая модель с поиском",
        "billing_id": "sonar-pro",
    },
    # Legacy model mappings
    "gpt-4": "gpt-4o",
    "gpt-4-mini": "gpt-4.1-mini",
    "claude": "claude-4",
    "gemini": "gemini-flash-2.0",
    "deepseek": "deepseek-chat",
}


def get_model_config(model_id: str) -> dict:
    """Get model configuration, resolving legacy IDs."""
    config = MODEL_CONFIGS.get(model_id)
    if isinstance(config, str):
        # It's a legacy mapping, resolve it
        return MODEL_CONFIGS[config]
    return config


@router.callback_query(F.data == "chatgpt")
async def start_chatgpt(callback: CallbackQuery, state: FSMContext):
    """Start ChatGPT dialog."""
    model_id = "gpt-4o"
    billing = get_text_model_billing(model_id)

    text = f"""🗯 **ChatGPT (GPT-4o)**

Отправьте ваш запрос текстом или голосовым сообщением.

Вы также можете прикрепить до 10 изображений для анализа.

ℹ️ **Динамическое списание токенов**
Точная стоимость запроса зависит от длины вашего сообщения и ответа модели.
• Базовая стоимость: {billing.base_tokens:,} токенов
• За каждый токен AI: {billing.per_gpt_token} внутренних токенов"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

    # Set state
    await state.set_state(AIGenerationStates.waiting_for_prompt)
    await state.update_data(ai_model=model_id)


@router.callback_query(F.data == "select_model")
async def select_ai_model(callback: CallbackQuery):
    """Show AI model selection."""

    text = """🤖 **Выбор AI модели**

Выберите модель для диалога.

ℹ️ **О стоимости:**
Для текстовых моделей стоимость рассчитывается динамически на основе реального использования.
Стоимость = базовая стоимость + (ваши токены + токены ответа) × множитель

**Доступные модели:**
• GPT-4o - универсальная мощная модель
• GPT-4.1 Mini - быстрая и экономичная
• Claude 4 - отличное понимание контекста
• Gemini Flash 2.0 - самая быстрая
• DeepSeek Chat / R1 - специализированные модели
• O3 Mini - reasoning модель
• Sonar / Sonar Pro - с поиском в интернете"""

    await callback.message.edit_text(
        text,
        reply_markup=ai_models_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("model:"))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    """Choose AI model and start dialog."""

    model_id = callback.data.split(":")[1]
    config = get_model_config(model_id)

    if not config:
        await callback.answer("❌ Неизвестная модель", show_alert=True)
        return

    billing = get_text_model_billing(config["billing_id"])

    text = f"""✅ **Выбрана модель: {config['display_name']}**

{config['description']}

Отправьте ваш запрос.

ℹ️ **Динамическое списание:**
• Базовая стоимость: {billing.base_tokens:,} токенов
• За токен AI: {billing.per_gpt_token}x
• Точная стоимость зависит от длины запроса и ответа"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

    # Set state
    await state.set_state(AIGenerationStates.waiting_for_prompt)
    await state.update_data(ai_model=config["billing_id"])


@router.message(AIGenerationStates.waiting_for_prompt)
async def process_ai_request(message: Message, user: User, state: FSMContext):
    """Process AI request with new billing system."""

    # Check message length (max 2000 characters)
    if message.text and len(message.text) > 2000:
        await message.answer(
            "⚠️ Сообщение слишком длинное!\n\n"
            f"Максимальная длина: 2000 символов\n"
            f"Ваше сообщение: {len(message.text)} символов\n\n"
            "Пожалуйста, сократите ваш запрос и попробуйте снова."
        )
        return

    # Get state data
    data = await state.get_data()
    model_id = data.get("ai_model", "gpt-4o")

    # Get billing configuration
    billing = get_text_model_billing(model_id)
    if not billing:
        await message.answer("❌ Ошибка конфигурации модели")
        await state.clear()
        return

    # Estimate minimum cost (base_tokens + estimated avg usage)
    # Estimate ~500 prompt tokens + ~1000 completion tokens for avg request
    estimated_tokens = billing.calculate_cost(500, 1000)

    # Check if user has enough tokens for estimated cost
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        has_balance = await sub_service.check_token_balance(user.id, estimated_tokens)

        if not has_balance:
            total_tokens = await sub_service.get_available_tokens(user.id)
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Примерная стоимость запроса: {estimated_tokens:,} токенов\n"
                f"Ваш баланс: {total_tokens:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Process with AI using factory
    processing_msg = await message.answer("⏳ Обрабатываю запрос...")

    try:
        from app.services.ai.ai_factory import AIServiceFactory

        # Factory will auto-detect if API keys are available or use mock
        response = await AIServiceFactory.generate_text(
            model=model_id,
            prompt=message.text
        )

        if not response.success:
            await processing_msg.edit_text(
                f"❌ Ошибка при генерации:\n{response.error}"
            )
            logger.error(
                "ai_request_failed",
                user_id=user.id,
                model=model_id,
                error=response.error
            )
            await state.clear()
            return

        # Calculate actual cost based on real usage
        async with async_session_maker() as session:
            billing_service = BillingService(session)

            # If we have token information from API, use it
            if response.prompt_tokens > 0 and response.completion_tokens > 0:
                prompt_tokens = response.prompt_tokens
                completion_tokens = response.completion_tokens
            else:
                # Fallback: estimate based on text length
                # Rough estimate: ~4 characters per token
                prompt_tokens = max(len(message.text) // 4, 100)
                completion_tokens = max(len(response.content) // 4, 100)

            try:
                actual_cost, ai_request = await billing_service.calculate_and_charge_text(
                    user_id=user.id,
                    model_id=model_id,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    prompt=message.text,
                )

                # Mark request as completed
                await billing_service.mark_request_completed(ai_request.id)

                # Format response
                content = response.content
                if response.metadata.get("mock"):
                    content += "\n\n⚠️ _Используется тестовый режим (API ключи не настроены)_"

                # Add cost information
                content += f"\n\n💰 Списано: {actual_cost:,} токенов"

                await processing_msg.edit_text(content)

                logger.info(
                    "ai_request_completed",
                    user_id=user.id,
                    model=model_id,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost=actual_cost,
                    is_mock=response.metadata.get("mock", False)
                )

            except InsufficientTokensError as e:
                await processing_msg.edit_text(
                    f"❌ Недостаточно токенов для оплаты запроса!\n\n"
                    f"Требуется: {actual_cost:,} токенов\n"
                    f"Доступно: {e.details.get('available', 0):,} токенов\n\n"
                    f"Купите подписку: /start → 💎 Подписка"
                )
                logger.warning(
                    "ai_request_insufficient_tokens",
                    user_id=user.id,
                    model=model_id,
                    required=actual_cost
                )

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Произошла ошибка: {str(e)}"
        )
        logger.error("ai_request_exception", user_id=user.id, model=model_id, error=str(e))

    await state.clear()
