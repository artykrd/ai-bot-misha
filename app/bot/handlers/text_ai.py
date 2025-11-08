"""
Text AI handlers (ChatGPT, Claude, etc.).
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.inline import ai_models_keyboard, back_to_main_keyboard
from app.bot.states.dialog import DialogStates, AIGenerationStates
from app.database.models.user import User
from app.database.database import async_session_maker
from app.services.subscription.subscription_service import SubscriptionService
from app.services.ai.openai_service import OpenAIService
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError

logger = get_logger(__name__)

router = Router(name="text_ai")


@router.callback_query(F.data == "chatgpt")
async def start_chatgpt(callback: CallbackQuery, state: FSMContext):
    """Start ChatGPT dialog."""

    text = """🗯 **ChatGPT**

Отправьте ваш запрос текстом или голосовым сообщением.

Вы также можете прикрепить до 10 изображений для анализа.

**Стоимость:** 1,000 токенов за запрос"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

    # Set state
    await state.set_state(AIGenerationStates.waiting_for_prompt)
    await state.update_data(ai_model="gpt-4", tokens_cost=1000)


@router.callback_query(F.data == "select_model")
async def select_ai_model(callback: CallbackQuery):
    """Show AI model selection."""

    text = """🤖 **Выбор AI модели**

Выберите модель для диалога:

**GPT-4 Omni** - самая продвинутая модель OpenAI (1000 токенов)
**GPT-4 Mini** - быстрая и доступная модель (250 токенов)
**Claude 3.5** - модель от Anthropic (1200 токенов)
**Gemini Pro** - модель от Google (900 токенов)
**DeepSeek** - отличная альтернатива (800 токенов)"""

    await callback.message.edit_text(
        text,
        reply_markup=ai_models_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("model:"))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    """Choose AI model and start dialog."""

    model = callback.data.split(":")[1]

    # Model costs
    costs = {
        "gpt-4": 1000,
        "gpt-4-mini": 250,
        "claude": 1200,
        "gemini": 900,
        "deepseek": 800
    }

    model_names = {
        "gpt-4": "GPT-4 Omni",
        "gpt-4-mini": "GPT-4 Omni Mini",
        "claude": "Claude 3.5 Sonnet",
        "gemini": "Gemini Pro",
        "deepseek": "DeepSeek V2"
    }

    text = f"""✅ **Выбрана модель: {model_names[model]}**

Отправьте ваш запрос.

**Стоимость:** {costs[model]:,} токенов за запрос"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

    # Set state
    await state.set_state(AIGenerationStates.waiting_for_prompt)
    await state.update_data(ai_model=model, tokens_cost=costs[model])


@router.message(AIGenerationStates.waiting_for_prompt)
async def process_ai_request(message: Message, user: User, state: FSMContext):
    """Process AI request."""

    # Get state data
    data = await state.get_data()
    ai_model = data.get("ai_model", "gpt-4")
    tokens_cost = data.get("tokens_cost", 1000)

    # Check tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, tokens_cost)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {tokens_cost:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Process with AI
    processing_msg = await message.answer("⏳ Обрабатываю запрос...")

    try:
        ai_service = OpenAIService()
        response = await ai_service.generate_text(
            prompt=message.text,
            model=ai_model
        )

        if response.success:
            await processing_msg.edit_text(response.content)

            logger.info(
                "ai_request_completed",
                user_id=user.id,
                model=ai_model,
                tokens=tokens_cost
            )
        else:
            await processing_msg.edit_text(
                f"❌ Ошибка при генерации:\n{response.error}"
            )

            logger.error(
                "ai_request_failed",
                user_id=user.id,
                model=ai_model,
                error=response.error
            )

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Произошла ошибка: {str(e)}"
        )
        logger.error("ai_request_exception", user_id=user.id, error=str(e))

    await state.clear()
