#!/usr/bin/env python3
# coding: utf-8
"""
Navigation handlers for all menu buttons.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from app.bot.keyboards.inline import (
    main_menu_keyboard,
    ai_models_keyboard,
    dialogs_keyboard,
    create_photo_keyboard,
    create_video_keyboard,
    photo_tools_keyboard,
    audio_tools_keyboard,
    nano_banana_keyboard,
    nano_format_keyboard,
    dialog_keyboard,
    referral_keyboard,
    subscription_keyboard,
    eternal_tokens_keyboard,
    back_to_main_keyboard,
    help_keyboard
)
from app.database.models.user import User

router = Router(name="navigation")


# TODO: Move to database - Dialog states storage
# Format: {user_id: {dialog_id: {"history": bool, "show_costs": bool}}}
DIALOG_STATES = {}



def get_dialog_state(user_id: int, dialog_id: int) -> dict:
    """Get dialog state for user."""
    if user_id not in DIALOG_STATES:
        DIALOG_STATES[user_id] = {}
    if dialog_id not in DIALOG_STATES[user_id]:
        DIALOG_STATES[user_id][dialog_id] = {"history": False, "show_costs": False}
    return DIALOG_STATES[user_id][dialog_id]


def set_dialog_state(user_id: int, dialog_id: int, history: bool = None, show_costs: bool = None):
    """Set dialog state for user."""
    state = get_dialog_state(user_id, dialog_id)
    if history is not None:
        state["history"] = history
    if show_costs is not None:
        state["show_costs"] = show_costs


# Main navigation
@router.callback_query(F.data == "bot.back")
async def back_to_main(callback: CallbackQuery, user: User, state: FSMContext):
    """Return to main menu."""
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService
    import os
    from pathlib import Path

    # Clean up any temporary files before returning to main menu
    data = await state.get_data()
    for key in ["image_path", "reference_image_path"]:
        file_path = data.get(key)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    # Clear state
    await state.clear()

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_available_tokens(user.id)

    text = f"""👋🏻 **Привет!** У тебя на балансе **{total_tokens:,} токенов** ** **– используй их для запросов к нейросетям.

💬 **Языковые модели:**
– **ChatGPT:** работает с текстом, голосом, может принимать до 10 картинок и документы любого формата;
– **Claude** и **Gemini:** отлично работают с текстом и документами;
– **DeepSeek:** отличная альтернатива для сложных задач;
– **Sonar:** модели с доступом к поиску в интернете.

🌄 **Создание изображений:**
– **Midjourney, DALL·E, Stable Diffusion, Recraft** – генерация изображений по описанию;
– **Nano Banana** – создаёт фото по промпту и вашим изображениям;
– **GPT Image** – генерация от OpenAI.

🎬 **Создание видео:**
– **Sora 2, Veo 3.1** – новейшие модели видеогенерации;
– **Midjourney Video, Hailuo, Luma, Kling** – создание видео по описанию.

🎙 **Работа с аудио:**
– **Suno** – создание музыки и песен;
– **Whisper** – расшифровка голосовых сообщений;
– **TTS** – озвучка текста."""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=main_menu_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.llm_models")
async def show_models(callback: CallbackQuery):
    """Show AI models selection."""
    from app.core.billing_config import format_text_model_pricing

    text = (
        "🤖 **Языковые модели**\n\n"
        "**GPT Models:**\n"
        f"• {format_text_model_pricing('gpt-4.1-mini')}\n"
        f"• {format_text_model_pricing('gpt-4o')}\n"
        f"• {format_text_model_pricing('gpt-5-mini')}\n"
        f"• {format_text_model_pricing('o3-mini')}\n\n"
        "**Claude Models:**\n"
        f"• {format_text_model_pricing('claude-4')}\n\n"
        "**Google Models:**\n"
        f"• {format_text_model_pricing('gemini-flash-2.0')}\n"
        f"• {format_text_model_pricing('nano-banana-text')}\n\n"
        "**DeepSeek Models:**\n"
        f"• {format_text_model_pricing('deepseek-chat')}\n"
        f"• {format_text_model_pricing('deepseek-r1')}\n\n"
        "**Perplexity Models:**\n"
        f"• {format_text_model_pricing('sonar')}\n"
        f"• {format_text_model_pricing('sonar-pro')}"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=ai_models_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


# Dialog management
@router.callback_query(F.data.startswith("bot.start_chatgpt_dialog_"))
async def start_dialog(callback: CallbackQuery, user: User):
    """Start or continue a dialog with specific model."""
    from app.bot.handlers.dialog_context import set_active_dialog, MODEL_MAPPINGS

    # Parse callback data
    callback_parts = callback.data.split("#")
    dialog_part = callback_parts[0]
    dialog_id = int(dialog_part.split("_")[-1])

    # Check if coming from home
    from_home = len(callback_parts) > 1 and callback_parts[1] == "home"

    # Get current dialog state
    state = get_dialog_state(user.telegram_id, dialog_id)
    history_enabled = state["history"]
    show_costs = state["show_costs"]

    # Check for state changes in callback
    if len(callback_parts) > 1 and callback_parts[1].startswith("sh_"):
        # Toggle history
        current_value = callback_parts[1] == "sh_1"
        history_enabled = not current_value  # Toggle to opposite
        set_dialog_state(user.telegram_id, dialog_id, history=history_enabled)
    elif len(callback_parts) > 1 and callback_parts[1].startswith("bi_"):
        # Toggle show costs
        current_value = callback_parts[1] == "bi_1"
        show_costs = not current_value  # Toggle to opposite
        set_dialog_state(user.telegram_id, dialog_id, show_costs=show_costs)

    # Set active dialog in context
    set_active_dialog(user.telegram_id, dialog_id, history_enabled, show_costs)

    model_config = MODEL_MAPPINGS.get(dialog_id)
    if not model_config:
        await callback.answer("❌ Неизвестная модель", show_alert=True)
        return
    model_name = model_config["name"]
    model_id = model_config["model_id"]

    # Build history status text
    history_status = "сохраняется (📈)" if history_enabled else "не сохраняется"

    text = f"""💬 **Диалог начался**

Для ввода используй:
└ 📝 текст;
└ 🎤 голосовое сообщение;
└ 📸 фотографии (до 10 шт.);
└ 📎 файл: любой текстовый формат (txt, .py и т.п).

**Название:** {model_name}
**Модель:** {model_id}
**История:** {history_status}

/end — завершит этот диалог
/clear — очистит историю в этом диалоге"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=dialog_keyboard(dialog_id, history_enabled, show_costs, from_home)
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.dialogs_chatgpt")
async def show_dialogs(callback: CallbackQuery):
    """Show user dialogs."""
    text = """💬 **Диалоги**

Диалоги нужны для хранения истории и роли (промпта). Каждый новый диалог — это отдельная ветка для общения с заранее заданной ролью с выбранной нейросетью. Вы можете выбрать подготовленные диалоги ниже или создать свой.

**Доступные диалоги:**"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=dialogs_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.create_chatgpt_dialog")
async def create_dialog(callback: CallbackQuery):
    """Create new dialog."""
    await callback.answer(
        "⚠️ Создание диалога будет доступно в следующей версии",
        show_alert=True
    )


# Photo and Video creation
@router.callback_query(F.data == "bot.create_photo")
async def show_create_photo(callback: CallbackQuery):
    """Show photo creation options."""
    text = """🌄 **Создание фото**

ℹ️ __Выберите нейросеть для генерации фото по кнопке ниже. После выбора – можете сразу отправлять запрос.__"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=create_photo_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.create_video")
async def show_create_video(callback: CallbackQuery):
    """Show video creation options."""
    text = """🎞 **Создание видео**

__ℹ️ Выберите нейросеть для генерации видео по кнопке ниже. После выбора – можете сразу отправлять запрос.__"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=create_video_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


# Nano Banana
@router.callback_query(F.data == "bot.nano")
async def show_nano_banana(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Nano Banana interface."""
    from app.bot.handlers.media_handler import MediaState
    from app.core.billing_config import get_image_model_billing, format_token_amount
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService

    async def get_available_tokens(user_id: int) -> int:
        """Get available tokens for user."""
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            return await sub_service.get_available_tokens(user_id)

    nano_billing = get_image_model_billing("nano-banana-image")
    total_tokens = await get_available_tokens(user.id)
    requests_available = int(total_tokens / nano_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = f"""🍌 **Nano Banana · твори и экспериментируй**

📖 **Создавайте:**
– Создает фотографии по промпту и по вашим изображениям;
– Она отлично наследует исходное фото и может работать с ним. Попросите её, например, отредактировать ваши фото (добавлять, удалять, менять объекты и всё, что угодно).

📷 **Добавляйте до 5 картинок в одном сообщении c промптом:**
– Добавьте к запросу одно или несколько фото с разными объектами и укажите что с ними сделать: соединить в какой-то объект, заменить что-то, отредактировать и т.д.

⚙️ **Настройки**
Формат фото: автоматический
PRO-режим: отключен

🔹 Баланса хватит на {requests_available} запросов. 1 генерация = {format_token_amount(nano_billing.tokens_per_generation)} токенов

✏️ **Отправьте текстовый запрос для генерации изображения**"""

    # Set FSM state to wait for prompt
    await state.set_state(MediaState.waiting_for_image_prompt)

    # Get existing data or set defaults
    data = await state.get_data()
    current_ratio = data.get("nano_aspect_ratio", "auto")

    await state.update_data(
        service="nano_banana",
        nano_aspect_ratio=current_ratio,  # Preserve existing format or set default
        nano_is_pro=False
    )

    # Use answer() instead of edit_text() because callback may come from media message
    await callback.message.answer(
        text,
        reply_markup=nano_banana_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.nb.prms:ratio")
async def nano_format_select(callback: CallbackQuery, state: FSMContext):
    """Show Nano Banana format selection."""
    # Get current format from state
    data = await state.get_data()
    current_ratio = data.get("nano_aspect_ratio", "auto")

    text = f"""📐 **Выберите формат создаваемого фото в Nano Banana**

**Текущий формат:** {current_ratio}

**1:1:** идеально подходит для профильных фото в соцсетях, таких как VK, Telegram и т.д

**2:3:** хорошо подходит для печатных фотографий, но также подходит для создания контента

**3:2:** аналогичен 2:3, только в горизонтальной ориентации

**16:9:** идеально подходит для создания обложек на YouTube и других видеоплатформ

**9:16:** идеально подходит для создания сторис в Instagram, TikTok и других

**auto:** бот автоматически определит формат изображения"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=nano_format_keyboard(current_ratio)
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("bot.nb.prms.chs:ratio|"))
async def nano_format_selected(callback: CallbackQuery, state: FSMContext):
    """Handle Nano Banana format selection."""
    format_value = callback.data.split("|")[1]

    # Save format to state
    await state.update_data(nano_aspect_ratio=format_value)

    await callback.answer(f"✅ Формат установлен: {format_value}")

    # Show updated format selection menu with checkmark on selected format
    await nano_format_select(callback, state)


@router.callback_query(F.data == "bot.nb.multi")
async def nano_multi_images(callback: CallbackQuery, state: FSMContext):
    """Show Nano Banana multiple images generation menu."""
    from app.bot.keyboards.inline import nano_multi_images_keyboard
    from app.core.billing_config import get_image_model_billing, format_token_amount

    # Get current PRO status
    data = await state.get_data()
    nano_is_pro = data.get("nano_is_pro", False)
    model_display = "Gemini 3 Pro" if nano_is_pro else "Gemini 2.5 Flash"

    cost_per_image = get_image_model_billing(
        "banana-pro" if nano_is_pro else "nano-banana-image"
    ).tokens_per_generation

    text = f"""🎨 **Создание нескольких изображений ({model_display})**

📊 **Как это работает:**
• Вы выбираете количество изображений (2-10)
• Можете загрузить одно или несколько референсных фото (опционально)
• Отправляете промпт с описанием
• Бот создает указанное количество изображений параллельно

💡 **Примеры использования:**
• Загрузите несколько фото людей → получите варианты с каждым в разных стилях
• Загрузите одно фото → получите несколько вариаций одной сцены
• Без фото → получите несколько разных изображений по промпту

💰 **Стоимость:** {format_token_amount(cost_per_image)} токенов × количество изображений

📌 **Выберите количество изображений для генерации:**"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=nano_multi_images_keyboard(),
            parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("bot.nb.multi.cnt:"))
async def nano_multi_count_selected(callback: CallbackQuery, state: FSMContext):
    """Handle multiple images count selection."""
    from app.bot.handlers.media_handler import MediaState
    from app.bot.keyboards.inline import back_to_main_keyboard
    from app.core.billing_config import get_image_model_billing, format_token_amount

    count = int(callback.data.split(":")[1])

    # Get current PRO status
    data = await state.get_data()
    nano_is_pro = data.get("nano_is_pro", False)
    model_display = "Nano Banana PRO (Gemini 3)" if nano_is_pro else "Nano Banana (Gemini 2.5)"

    # Calculate cost
    cost_per_image = get_image_model_billing(
        "banana-pro" if nano_is_pro else "nano-banana-image"
    ).tokens_per_generation
    total_cost = cost_per_image * count

    text = f"""✅ **Выбрано: {count} изображений**

🍌 **Модель:** {model_display}
💰 **Стоимость:** {format_token_amount(total_cost)} токенов

📸 **Инструкция:**

**Шаг 1 (опционально):** Загрузите фотографии
• Можете загрузить **одно или несколько** фото как референс
• Если загрузите несколько фото, бот будет использовать их для создания вариаций
• Если не хотите использовать фото, сразу переходите к Шагу 2

**Шаг 2:** Отправьте текстовый промпт
• Опишите, что вы хотите создать
• Если загрузили фото: опишите, как их трансформировать
• Без фото: опишите желаемое изображение

**Примеры промптов:**
*С несколькими фото людей:*
"Создай портрет каждого человека в стиле аниме"

*С одним фото (разные сцены):*
"1. Флакон на кафеле, 2. На ванной, 3. С каплями воды, 4. В руке с маникюром, 5. Рядом с полотенцем"

*Без фото (разные виды):*
"Футуристический город: 1. с высоты птичьего полета, 2. на уровне улицы, 3. ночной вид, 4. панорама"

💡 **Совет:** Для получения разных сцен описывайте каждую через запятую или используйте нумерацию (1. сцена1, 2. сцена2)

✏️ **Загрузите фото (одно или несколько) или сразу отправьте промпт**"""

    # Set state and save count
    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(
        service="nano_banana",
        multi_images_count=count,
        reference_image_paths=[],  # List for multiple reference images
        photo_caption_prompt=None
    )

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


# Photo tools
@router.callback_query(F.data == "bot.pi")
async def show_photo_tools(callback: CallbackQuery):
    """Show photo tools."""
    text = """✂️  **Инструменты для работы с фото**

ℹ️ __В этот раздел мы добавили инструменты, которые помогут вам эффективно работать с вашими фотографиями. Выберите интересующий вас инструмент по кнопке ниже.__"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=photo_tools_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.in_(["bot.pi_upscale", "bot.pi_repb", "bot.pi_remb", "bot.pi_vect"]))
async def photo_tool_selected(callback: CallbackQuery, state: FSMContext):
    """Handle photo tool selection."""
    from app.bot.handlers.media_handler import MediaState

    tool_info = {
        "bot.pi_upscale": {
            "name": "🔎 Улучшение качества фото",
            "state": MediaState.waiting_for_photo_upscale,
            "description": "Загрузите фото, качество которого вы хотите улучшить.\n\n"
                          "Бот использует GPT Vision для анализа и улучшения качества изображения."
        },
        "bot.pi_repb": {
            "name": "🪄 Замена фона",
            "state": MediaState.waiting_for_photo_replace_bg,
            "description": "Загрузите фото и опишите, какой фон вы хотите.\n\n"
                          "Пример: 'Замени фон на горный пейзаж' или 'Поставь меня на пляж'.\n\n"
                          "Сначала загрузите фото, затем опишите желаемый фон."
        },
        "bot.pi_remb": {
            "name": "🪞 Удаление фона",
            "state": MediaState.waiting_for_photo_remove_bg,
            "description": "Загрузите фото, с которого нужно удалить фон.\n\n"
                          "Бот создаст изображение с прозрачным или белым фоном."
        },
        "bot.pi_vect": {
            "name": "📐 Векторизация фото",
            "state": MediaState.waiting_for_photo_vectorize,
            "description": "Загрузите фото для векторизации.\n\n"
                          "Бот создаст векторную версию вашего изображения."
        }
    }

    tool = tool_info.get(callback.data)
    if not tool:
        await callback.answer("⚠️ Неизвестный инструмент", show_alert=True)
        return

    # Set state and save tool type
    await state.set_state(tool["state"])
    await state.update_data(photo_tool=callback.data)

    text = f"{tool['name']}\n\n{tool['description']}\n\n📤 **Загрузите фотографию**"

    try:
        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


# Audio tools
@router.callback_query(F.data == "bot.audio_instruments")
async def show_audio_tools(callback: CallbackQuery):
    """Show audio tools."""
    text = """🎙 **Работа с аудио**

__ℹ️ Выберите нейросеть для работы с аудио по кнопке ниже. После выбора – можете сразу отправлять запрос.__"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=audio_tools_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


# Media service handlers moved to media_handler.py
# All video, audio, and image processing handlers are now implemented there


# Subscription
@router.callback_query(F.data == "bot#shop")
async def show_subscription(callback: CallbackQuery):
    """Show subscription options."""
    text = """💎 **Оформить подписку**

🤩 **Наш бот предоставляет вам лучший сервис** без каких либо ограничений и продолжает это делать ежедневно 24/7. **Подписка позволит вам получить больше возможностей**, чем если использовать бот бесплатно.

**Выберите подходящий тариф:**"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=subscription_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot#shop_tokens")
async def show_eternal_tokens(callback: CallbackQuery):
    """Show eternal tokens options."""
    text = """🔹 **Вечные токены**

Купите токены, которые никогда не сгорят. Используйте их в любое время без ограничений по дате."""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=eternal_tokens_keyboard()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("shop_select_tariff_"))
async def tariff_selected(callback: CallbackQuery, user: User):
    """Handle tariff selection."""
    from app.database.database import async_session_maker
    from app.services.payment import PaymentService
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    from app.core.subscription_plans import get_subscription_plan, UNLIMITED_PLAN
    from app.core.logger import get_logger

    logger = get_logger(__name__)

    # Extract tariff ID
    tariff_id = callback.data.split("_")[-1]

    plan = get_subscription_plan(tariff_id)
    if tariff_id == "22":
        tariff = UNLIMITED_PLAN
        tariff_name = "Безлимит на 1 день"
        tariff_tokens = None
    else:
        if not plan:
            await callback.answer("❌ Неизвестный тариф", show_alert=True)
            return
        tariff = plan
        tariff_name = plan.display_name
        tariff_tokens = plan.tokens

    # Create payment
    async with async_session_maker() as session:
        payment_service = PaymentService(session)

        payment = await payment_service.create_payment(
            user_id=user.id,
            amount=tariff.price,
            description=f"Подписка: {tariff_name}",
            metadata={
                "tariff_id": tariff_id,
                "days": tariff.days,
                "tokens": tariff_tokens,
                "type": "subscription"
            }
        )

        if not payment:
            await callback.answer("❌ Ошибка создания платежа. Попробуйте позже.", show_alert=True)
            return

        # Get payment URL
        confirmation_url = payment.yukassa_response.get("confirmation_url")

        if not confirmation_url:
            await callback.answer("❌ Ошибка получения ссылки на оплату", show_alert=True)
            return

    logger.info(
        "subscription_payment_created",
        plan_id=tariff_id,
        amount_rub=float(tariff.price),
        tokens_granted=tariff_tokens,
        duration_days=tariff.days,
        user_id=user.id,
        payment_id=payment.payment_id,
    )

    # Build payment message
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Оплатить", url=confirmation_url)
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot#shop")
    )

    tokens_text = f"{tariff_tokens:,} токенов" if tariff_tokens else "Безлимит"

    # Special detailed description for unlimited tariff
    if tariff_id == "22":
        from app.core.billing_config import (
            get_text_model_billing,
            get_image_model_billing,
            get_video_model_billing,
            format_token_amount,
        )
        gpt_billing = get_text_model_billing("gpt-4.1-mini")
        nano_billing = get_image_model_billing("nano-banana-image")
        dalle_billing = get_image_model_billing("dalle3")
        sora_billing = get_video_model_billing("sora2")
        veo_billing = get_video_model_billing("veo-3.1-fast")
        hailuo_billing = get_video_model_billing("hailuo")
        kling_billing = get_video_model_billing("kling-video")

        text = f"""💳 **Оплата подписки**

📦 **Тариф:** {tariff_name}
💰 **Стоимость:** {tariff.price} руб.
⏰ **Срок:** {tariff.days} день

🎯 **Что вы получаете:**

**💬 Чат с ChatGPT:**
• Базовая стоимость: {format_token_amount(gpt_billing.base_tokens)} токенов
• За каждый токен AI: {gpt_billing.per_gpt_token} внутренних токенов

**🖼 Генерация изображений:**
• Nano Banana: {format_token_amount(nano_billing.tokens_per_generation)} токенов за изображение
• DALL-E 3: {format_token_amount(dalle_billing.tokens_per_generation)} токенов за изображение

**🎬 Генерация видео:**
• Sora 2: {format_token_amount(sora_billing.tokens_per_generation)} токенов за видео
• Veo 3.1 Fast: {format_token_amount(veo_billing.tokens_per_generation)} токенов за видео
• Hailuo: {format_token_amount(hailuo_billing.tokens_per_generation)} токенов за видео
• Kling: {format_token_amount(kling_billing.tokens_per_generation)} токенов за видео

**🎵 Генерация аудио:**
• Suno: ~85 песен (по 2 мин)
• Транскрибация: ~1250 минут аудио

После оплаты подписка будет автоматически активирована.

Нажмите кнопку "Оплатить" для перехода к оплате."""
    else:
        text = f"""💳 **Оплата подписки**

📦 **Тариф:** {tariff_name}
💰 **Стоимость:** {tariff.price} руб.
⏰ **Срок:** {tariff.days} дней
🎁 **Токены:** {tokens_text}

После оплаты подписка будет автоматически активирована.

Нажмите кнопку "Оплатить" для перехода к оплате."""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("buy:eternal_"))
async def eternal_token_selected(callback: CallbackQuery, user: User):
    """Handle eternal token purchase - redirect to subscription handler."""
    # This will be handled by the subscription.py handler
    from app.bot.handlers.subscription import process_subscription_purchase
    await process_subscription_purchase(callback, user)


# Promocode activation is handled in subscription.py


# Profile and Referral
@router.callback_query(F.data == "bot.refferal_program")
async def show_referral(callback: CallbackQuery, user: User):
    """Show referral program with real statistics."""
    from app.database.database import async_session_maker

    # Get referral statistics using ReferralService
    async with async_session_maker() as session:
        from app.services.referral import ReferralService

        referral_service = ReferralService(session)
        stats = await referral_service.get_referral_stats(user.id)

        referral_count = stats["referral_count"]
        tokens_earned = stats["tokens_earned"]
        tokens_balance = stats["tokens_balance"]
        money_balance = stats["money_balance"]

    # Build referral link for bot
    bot_username = "assistantvirtualsbot"
    referral_link = f"https://t.me/{bot_username}?start=ref{user.telegram_id}"

    text = f"""🔹 **Реферальная программа**

Приглашайте друзей и получайте награды:

🎁 **+50 токенов** вам и другу при первом запуске
💰 **10% деньгами** от каждой покупки приглашенного

👥 Приглашено пользователей: **{referral_count}**
🔶 Заработано токенов: **{tokens_earned:,}**
💎 Баланс токенов: **{tokens_balance:,}**
💸 Минимальная сумма вывода: **1 500 руб.**
💰 Доступно для вывода: **{money_balance:.2f} руб.**

🔗 Моя реферальная ссылка:
`{referral_link}`

Поделитесь этой ссылкой с друзьями и получайте бонусы!"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=referral_keyboard(user.telegram_id)
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.refferal_withdraw")
async def referral_withdraw(callback: CallbackQuery, user: User):
    """Withdraw referral earnings."""
    from app.database.database import async_session_maker
    from sqlalchemy import select
    from app.database.models.referral_balance import ReferralBalance

    async with async_session_maker() as session:
        balance_result = await session.execute(
            select(ReferralBalance).where(ReferralBalance.user_id == user.id)
        )
        balance = balance_result.scalar_one_or_none()
        money_balance = float(balance.money_balance) if balance else 0.0

    min_withdrawal = 1500.0

    if money_balance < min_withdrawal:
        await callback.answer(
            f"⚠️ Недостаточно средств для вывода\n\n"
            f"Минимум: {min_withdrawal:.0f} руб.\n"
            f"Доступно: {money_balance:.2f} руб.",
            show_alert=True
        )
    else:
        text = f"""💰 **Вывод средств**

Доступно для вывода: **{money_balance:.2f} руб.**

Для вывода средств обратитесь в поддержку: @gigavidacha

Укажите:
• Ваш Telegram ID: `{user.telegram_id}`
• Сумму для вывода
• Реквизиты для перевода"""

        try:
            await callback.message.edit_text(
                text,
                reply_markup=back_to_main_keyboard()
            )
        except TelegramBadRequest as e:
            # Ignore error if message content hasn't changed
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


@router.callback_query(F.data == "bot.refferal_exchange")
async def referral_exchange(callback: CallbackQuery, user: User):
    """Exchange referral money balance to tokens."""
    from app.database.database import async_session_maker
    from app.services.referral import ReferralService
    from decimal import Decimal

    tokens_per_ruble = 1700

    async with async_session_maker() as session:
        referral_service = ReferralService(session)
        stats = await referral_service.get_referral_stats(user.id)
        money_balance = Decimal(str(stats["money_balance"]))

        if money_balance <= 0:
            await callback.answer("⚠️ У вас нет средств для обмена.", show_alert=True)
            return

        tokens_added = await referral_service.exchange_money_to_tokens(
            user_id=user.id,
            money_amount=money_balance,
            tokens_per_ruble=tokens_per_ruble
        )

    if not tokens_added:
        await callback.answer("⚠️ Не удалось выполнить обмен.", show_alert=True)
        return

    text = f"""🔄 **Обмен выполнен**

Сумма обмена: **{money_balance:.2f} руб.**
Начислено: **{tokens_added:,} токенов**
Курс: **1 руб. = {tokens_per_ruble} токенов**"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard()
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.profile_payments")
async def show_profile_payments(callback: CallbackQuery, user: User):
    """Show user's payment history."""
    from app.database.database import async_session_maker
    from sqlalchemy import select, desc
    from app.database.models.payment import Payment
    from datetime import datetime

    async with async_session_maker() as session:
        # Get user payments
        result = await session.execute(
            select(Payment)
            .where(Payment.user_id == user.id)
            .order_by(desc(Payment.created_at))
            .limit(10)
        )
        payments = result.scalars().all()

    if not payments:
        text = """📋 <b>Мои платежи</b>

У вас пока нет платежей.

Оформите подписку через /shop, чтобы начать использовать все возможности бота!"""
    else:
        payment_lines = []
        status_emoji = {
            "success": "✅",
            "pending": "⏳",
            "failed": "❌",
            "refunded": "↩️"
        }
        status_text = {
            "success": "Успешно",
            "pending": "В обработке",
            "failed": "Неудачно",
            "refunded": "Возврат"
        }

        for payment in payments:
            date_str = payment.created_at.strftime("%d.%m.%Y %H:%M")
            emoji = status_emoji.get(payment.status, "❓")
            status = status_text.get(payment.status, payment.status)
            payment_lines.append(
                f"{emoji} <b>{payment.amount} {payment.currency}</b> — {status}\n"
                f"   {date_str}"
            )

        payments_text = "\n\n".join(payment_lines)
        text = f"""📋 <b>Мои платежи</b>

Последние 10 платежей:

{payments_text}

Всего платежей: {len(payments)}"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "bot.change_language")
async def profile_feature_not_implemented(callback: CallbackQuery):
    """Profile features not implemented."""
    await callback.answer(
        "⚠️ Изменение языка будет доступно в следующей версии",
        show_alert=True
    )


@router.callback_query(F.data == "page#faq")
async def show_faq(callback: CallbackQuery):
    """Show FAQ/Help."""
    text = """🆘 <b>Помощь</b>

Добро пожаловать в раздел помощи!

Выберите интересующую вас тему:

💎 <b>Токены</b> — что это и как их получить
📋 <b>Платежи</b> — информация о платежах
🔒 <b>Политика хранения данных</b> — как мы храним ваши данные

<b>Поддержка:</b>
Если возникли вопросы, напишите @gigavidacha"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=help_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "help.tokens")
async def show_help_tokens(callback: CallbackQuery):
    """Show help about tokens."""
    from app.core.billing_config import (
        format_token_amount,
        get_text_model_billing,
        get_image_model_billing,
        get_video_model_billing,
    )
    gpt_billing = get_text_model_billing("gpt-4.1-mini")

    text = f"""💎 <b>Токены</b>

<b>Что такое токены?</b>
Токены — это внутренняя валюта бота. За токены вы можете использовать все AI-модели: ChatGPT, генерацию изображений, видео, музыки и многое другое.

<b>Как получить токены?</b>
• Купить подписку через /shop
• Пригласить друзей (реферальная программа)
• Активировать промокод

<b>Стоимость запросов:</b>
• ChatGPT 4.1 Mini — база {format_token_amount(gpt_billing.base_tokens)} + {gpt_billing.per_gpt_token} за токен AI
• Nano Banana (фото) — {format_token_amount(get_image_model_billing("nano-banana-image").tokens_per_generation)} токенов
• Banana PRO (фото) — {format_token_amount(get_image_model_billing("banana-pro").tokens_per_generation)} токенов
• DALL-E 3 — {format_token_amount(get_image_model_billing("dalle3").tokens_per_generation)} токенов
• Sora 2 (видео) — {format_token_amount(get_video_model_billing("sora2").tokens_per_generation)} токенов
• Veo 3.1 Fast (видео) — {format_token_amount(get_video_model_billing("veo-3.1-fast").tokens_per_generation)} токенов
• Midjourney Video SD (видео) — {format_token_amount(get_video_model_billing("midjourney-video-sd").tokens_per_generation)} токенов
• Midjourney Video HD (видео) — {format_token_amount(get_video_model_billing("midjourney-video-hd").tokens_per_generation)} токенов
• Hailuo (видео) — {format_token_amount(get_video_model_billing("hailuo").tokens_per_generation)} токенов
• Kling (видео) — {format_token_amount(get_video_model_billing("kling-video").tokens_per_generation)} токенов
• Kling Effects (видео) — {format_token_amount(get_video_model_billing("kling-effects").tokens_per_generation)} токенов
• Suno (музыка) — 17,600 токенов
• Whisper (расшифровка) — 1,200 токенов/мин

<b>Токены не сгорают</b> и доступны бессрочно (для вечных токенов)."""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=help_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "help.payments")
async def show_help_payments(callback: CallbackQuery):
    """Show help about payments."""
    text = """📋 <b>Платежи</b>

<b>Как оплатить подписку?</b>
1. Перейдите в раздел /shop
2. Выберите подходящий тариф
3. Нажмите кнопку "Оплатить"
4. Введите данные карты
5. Подтвердите платеж

<b>Способы оплаты:</b>
• Банковская карта (Visa, MasterCard, МИР)
• ЮMoney
• QIWI
• Другие методы через ЮKassa

<b>История платежей:</b>
Посмотреть все ваши платежи можно в разделе "Мой профиль" → "Мои платежи"

<b>Возврат средств:</b>
Если у вас возникли проблемы с платежом, обратитесь в поддержку @gigavidacha"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=help_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "help.privacy")
async def show_help_privacy(callback: CallbackQuery):
    """Show privacy policy."""
    text = """📖 <b>Политика хранения данных</b>

Мы трепетно относимся к данным наших пользователей и поэтому решили написать эту политику, чтобы вы были уведомлены, как мы храним данные.

Администрация бота имеет доступ только к управлению вашим аккаунтом (блокировка, выдача определённых прав и иные сервисные функции), но прав на доступ к истории ваших запросов у неё нет.

Ниже приведён перечь данных, которые мы временно храним на своих серверах.

<b>ChatGPT</b>
1. История ваших запросов в диалоге хранится на сервере до момента, пока вы не выполните очистку диалога по команде «/clear» или «Очистить историю».
2. История ваших запросов через команду «/gpt _вопрос_» хранится до конца суток и автоматически очищается системой.

<b>DALL-E</b>
История ваших запросов хранится до конца суток и автоматически очищается системой. Система хранит информацию запрос-ссылки (на сервере OpenAI).

❗️Система очищает только вопрос-ответ и хранит информацию о потраченных токенах за запрос для извлечения статистики по тратам.

<b>ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ:</b>
https://docs.google.com/document/d/10YyarEM8z4BNsqOnXoyjuMEP73WKqSY387wC3-FDgj8/edit?usp=drivesdk

<b>ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ:</b>
https://docs.google.com/document/d/177YiMyDvNPuvg3S-yR6tpqhnu4pn53YZ4X4EQWROQ_I/edit?usp=drivesdk"""

    try:
        await callback.message.edit_text(
            text,
            reply_markup=help_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()
