"""
Navigation handlers for all menu buttons.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

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
    eternal_tokens_keyboard
)
from app.database.models.user import User

router = Router(name="navigation")


# TODO: Move to database - Dialog states storage
# Format: {user_id: {dialog_id: {"history": bool, "show_costs": bool}}}
DIALOG_STATES = {}


# Model names mapping
MODEL_NAMES = {
    324: ("4️⃣ GPT 4.1 Mini", "gpt-4.1-mini"),
    325: ("4️⃣ GPT 4o", "gpt-4o"),
    326: ("💫 O3 Mini", "o3-mini"),
    327: ("🐳 Deepseek Чат", "deepseek-chat"),
    328: ("🐳 Deepseek R1", "deepseek-r1"),
    329: ("⚡ Gemini Flash 2.0", "gemini-flash-2.0"),
    330: ("🛡 Gemini Pro 2.5", "google/gemini-2.5-pro-preview"),
    331: ("🌐 Sonar с поиском", "perplexity/sonar-search"),
    332: ("💻 Sonar Pro", "perplexity/sonar-pro"),
    333: ("📔 Claude 4", "anthropic/claude-3.7"),
    334: ("📘 Claude 3.5 Haiku", "anthropic/claude-3.5"),
    338: ("🤖 GPT 4o-mini", "gpt-4o-mini"),
    335: ("🔍 Анализ текста", "gpt-4-mini-analysis"),
    336: ("🌆 Генератор промптов", "gpt-4-mini-prompts"),
    337: ("🔥 GPT 5 Mini", "gpt-5-mini"),
}


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
async def back_to_main(callback: CallbackQuery, user: User):
    """Return to main menu."""
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_user_total_tokens(user.id)

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

    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.llm_models")
async def show_models(callback: CallbackQuery):
    """Show AI models selection."""
    text = """🤖 **Языковые модели**

**GPT Models:**
• **GPT 4.1 Mini** – быстрая модель с отличным качеством (500 токенов)
• **GPT 4o** – самая продвинутая модель (1000 токенов)
• **GPT 5 Mini** – новейшая модель OpenAI (600 токенов)
• **O3 Mini** – модель для сложных рассуждений (700 токенов)

**Claude Models:**
• **Claude 3.7** – новая версия с улучшенными возможностями (1200 токенов)
• **Claude 3.5** – проверенная модель от Anthropic (1000 токенов)

**Google Models:**
• **Gemini Flash 2.0** – быстрая и эффективная модель (400 токенов)
• **Gemini Pro 2.5** – продвинутая модель для сложных задач (900 токенов)

**DeepSeek Models:**
• **Deepseek Чат** – отличная альтернатива для диалогов (600 токенов)
• **Deepseek R1** – модель с расширенными возможностями (800 токенов)

**Perplexity Models:**
• **Sonar с поиском** – модель с доступом к интернету (700 токенов)
• **Sonar Pro** – продвинутая версия с поиском (1000 токенов)"""

    await callback.message.edit_text(
        text,
        reply_markup=ai_models_keyboard()
    )
    await callback.answer()


# Dialog management
@router.callback_query(F.data.startswith("bot.start_chatgpt_dialog_"))
async def start_dialog(callback: CallbackQuery, user: User):
    """Start or continue a dialog with specific model."""
    from app.bot.handlers.dialog_context import set_active_dialog

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

    # Get model info
    model_name, model_id = MODEL_NAMES.get(dialog_id, ("Unknown Model", "unknown"))

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

    await callback.message.edit_text(
        text,
        reply_markup=dialog_keyboard(dialog_id, history_enabled, show_costs, from_home)
    )
    await callback.answer()


@router.callback_query(F.data == "bot.dialogs_chatgpt")
async def show_dialogs(callback: CallbackQuery):
    """Show user dialogs."""
    text = """💬 **Диалоги**

Диалоги нужны для хранения истории и роли (промпта). Каждый новый диалог — это отдельная ветка для общения с заранее заданной ролью с выбранной нейросетью. Вы можете выбрать подготовленные диалоги ниже или создать свой.

**Доступные диалоги:**"""

    await callback.message.edit_text(
        text,
        reply_markup=dialogs_keyboard()
    )
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

    await callback.message.edit_text(
        text,
        reply_markup=create_photo_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.create_video")
async def show_create_video(callback: CallbackQuery):
    """Show video creation options."""
    text = """🎞 **Создание видео**

__ℹ️ Выберите нейросеть для генерации видео по кнопке ниже. После выбора – можете сразу отправлять запрос.__"""

    await callback.message.edit_text(
        text,
        reply_markup=create_video_keyboard()
    )
    await callback.answer()


# Nano Banana
@router.callback_query(F.data == "bot.nano")
async def show_nano_banana(callback: CallbackQuery):
    """Show Nano Banana interface."""
    text = """🍌 **Nano Banana · твори и экспериментируй**

📖 **Создавайте:**
– Создает фотографии по промпту и по вашим изображениям;
– Она отлично наследует исходное фото и может работать с ним. Попросите её, например, "перенести этот стиль на новое изображение".

**Стоимость:** 8,000 токенов за запрос

⚠️ Отправьте текстовый запрос или изображение для генерации"""

    await callback.message.edit_text(
        text,
        reply_markup=nano_banana_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.nb.prms:ratio")
async def nano_format_select(callback: CallbackQuery):
    """Show Nano Banana format selection."""
    text = """📐 **Выберите формат создаваемого фото в Nano Banana**

**1:1:** идеально подходит для профильных фото в соцсетях, таких как VK, Telegram и т.д

**2:3:** хорошо подходит для печатных фотографий, но также подходит для создания контента

**3:2:** аналогичен 2:3, только в горизонтальной ориентации

**16:9:** идеально подходит для создания обложек на YouTube и других видеоплатформ

**9:16:** идеально подходит для создания сторис в Instagram, TikTok и других

**auto:** бот автоматически определит формат изображения"""

    await callback.message.edit_text(
        text,
        reply_markup=nano_format_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot.nb.prms.chs:ratio|"))
async def nano_format_selected(callback: CallbackQuery):
    """Handle Nano Banana format selection."""
    format_value = callback.data.split("|")[1]
    await callback.answer(f"✅ Формат установлен: {format_value}")
    # Save to user state/database
    # Return to Nano Banana menu
    await show_nano_banana(callback)


# Photo tools
@router.callback_query(F.data == "bot.pi")
async def show_photo_tools(callback: CallbackQuery):
    """Show photo tools."""
    text = """✂️  **Инструменты для работы с фото**

ℹ️ __В этот раздел мы добавили инструменты, которые помогут вам эффективно работать с вашими фотографиями. Выберите интересующий вас инструмент по кнопке ниже.__"""

    await callback.message.edit_text(
        text,
        reply_markup=photo_tools_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.in_(["bot.pi_upscale", "bot.pi_repb", "bot.pi_remb", "bot.pi_vect"]))
async def photo_tool_selected(callback: CallbackQuery):
    """Handle photo tool selection."""
    tool_names = {
        "bot.pi_upscale": "🔎 Улучшение качества фото",
        "bot.pi_repb": "🪄 Замена фона",
        "bot.pi_remb": "🪞 Удаление фона",
        "bot.pi_vect": "📐 Векторизация фото"
    }
    tool_name = tool_names.get(callback.data, "Инструмент")

    await callback.answer(
        f"⚠️ {tool_name} будет доступно в следующей версии",
        show_alert=True
    )


# Audio tools
@router.callback_query(F.data == "bot.audio_instruments")
async def show_audio_tools(callback: CallbackQuery):
    """Show audio tools."""
    text = """🎙 **Работа с аудио**

__ℹ️ Выберите нейросеть для работы с аудио по кнопке ниже. После выбора – можете сразу отправлять запрос.__"""

    await callback.message.edit_text(
        text,
        reply_markup=audio_tools_keyboard()
    )
    await callback.answer()


# Service handlers (all return "in development" message)
@router.callback_query(F.data.in_([
    "bot.gpt_image", "bot.midjourney", "bot_stable_diffusion", "bot.recraft", "bot.faceswap",
    "bot.sora", "bot.veo", "bot.mjvideo", "bot.hailuo", "bot.luma", "bot.kling", "bot.kling_effects",
    "bot.suno", "bot.whisper", "bot.whisper_tts"
]))
async def service_not_implemented(callback: CallbackQuery):
    """Handler for services not yet implemented."""
    service_info = {
        "bot.gpt_image": ("💥 GPT Image", "Генерация изображений от OpenAI"),
        "bot.midjourney": ("🌆 Midjourney", "Создание изображений с помощью Midjourney"),
        "bot_stable_diffusion": ("🖌 Stable Diffusion", "Генерация изображений с помощью Stable Diffusion"),
        "bot.recraft": ("🎨 Recraft", "Создание дизайнов и иллюстраций"),
        "bot.faceswap": ("🎭 Замена лиц", "Замена лиц на фотографиях"),
        "bot.sora": ("☁️ Sora 2", "Создание видео с помощью Sora"),
        "bot.veo": ("🌊 Veo 3.1", "Генерация видео от Google"),
        "bot.mjvideo": ("🗾 Midjourney Video", "Создание видео с Midjourney"),
        "bot.hailuo": ("🎥 Hailuo", "Генерация видео"),
        "bot.luma": ("📹 Luma", "Создание видео с Luma Dream Machine"),
        "bot.kling": ("🎞 Kling", "Генерация видео с Kling"),
        "bot.kling_effects": ("🧙 Kling Эффекты", "Видеоэффекты от Kling"),
        "bot.suno": ("🎧 Suno", "Создание музыки и песен"),
        "bot.whisper": ("🎙 Whisper", "Расшифровка голосовых сообщений"),
        "bot.whisper_tts": ("🗣 TTS", "Озвучка текста")
    }
    service_name, service_desc = service_info.get(callback.data, ("Сервис", "Описание"))

    text = f"""⚠️ **{service_name}**

{service_desc}

🔧 **Статус:** В разработке

Этот функционал будет доступен в следующей версии бота. Следите за обновлениями!"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


# Subscription
@router.callback_query(F.data == "bot#shop")
async def show_subscription(callback: CallbackQuery):
    """Show subscription options."""
    text = """💎 **Оформить подписку**

🤩 **Наш бот предоставляет вам лучший сервис** без каких либо ограничений и продолжает это делать ежедневно 24/7. **Подписка позволит вам получить больше возможностей**, чем если использовать бот бесплатно.

**Выберите подходящий тариф:**"""

    await callback.message.edit_text(
        text,
        reply_markup=subscription_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    await callback.answer()


@router.callback_query(F.data == "bot#shop_tokens")
async def show_eternal_tokens(callback: CallbackQuery):
    """Show eternal tokens options."""
    text = """🔹 **Вечные токены**

Купите токены, которые никогда не сгорят. Используйте их в любое время без ограничений по дате."""

    await callback.message.edit_text(
        text,
        reply_markup=eternal_tokens_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("shop_select_tariff_"))
async def tariff_selected(callback: CallbackQuery):
    """Handle tariff selection."""
    await callback.answer(
        "⚠️ Оплата будет доступна в следующей версии",
        show_alert=True
    )


@router.callback_query(F.data.startswith("buy:eternal_"))
async def eternal_token_selected(callback: CallbackQuery):
    """Handle eternal token purchase."""
    await callback.answer(
        "⚠️ Оплата будет доступна в следующей версии",
        show_alert=True
    )


@router.callback_query(F.data == "activate_promocode")
async def activate_promocode(callback: CallbackQuery):
    """Activate promocode."""
    await callback.answer(
        "⚠️ Активация промокодов будет доступна в следующей версии",
        show_alert=True
    )


# Profile and Referral
@router.callback_query(F.data == "bot.refferal_program")
async def show_referral(callback: CallbackQuery, user: User):
    """Show referral program with real statistics."""
    from app.database.database import async_session_maker
    from sqlalchemy import select, func
    from app.database.models.referral import Referral

    async with async_session_maker() as session:
        # Count referrals
        referral_count_result = await session.execute(
            select(func.count(Referral.id)).where(
                Referral.referrer_id == user.id,
                Referral.is_active == True
            )
        )
        referral_count = referral_count_result.scalar() or 0

        # Sum tokens earned
        tokens_earned_result = await session.execute(
            select(func.sum(Referral.tokens_earned)).where(
                Referral.referrer_id == user.id,
                Referral.is_active == True
            )
        )
        tokens_earned = tokens_earned_result.scalar() or 0

        # Sum money earned
        money_earned_result = await session.execute(
            select(func.sum(Referral.money_earned)).where(
                Referral.referrer_id == user.id,
                Referral.is_active == True
            )
        )
        money_earned = float(money_earned_result.scalar() or 0)

    # Build referral link for bot
    # TODO: Get bot username from config
    bot_username = "GPTchatneiroseti_BOT"
    referral_link = f"https://t.me/{bot_username}?start=ref{user.telegram_id}"

    text = f"""🔹 **Реферальная программа**

Получайте **100 токенов** за приглашенного пользователя и **10%** деньгами от каждой его покупки в боте.

👥 Приглашено пользователей: **{referral_count}**
🔶 Получено: **{tokens_earned:,} токенов**
💸 Минимальная сумма вывода: **500 руб.**
💰 Доступно для вывода: **{money_earned:.2f} руб.**

Ваша реферальная ссылка:
`{referral_link}`

Поделитесь этой ссылкой с друзьями и получайте бонусы!"""

    await callback.message.edit_text(
        text,
        reply_markup=referral_keyboard(user.telegram_id)
    )
    await callback.answer()


@router.callback_query(F.data == "bot.refferal_withdraw")
async def referral_withdraw(callback: CallbackQuery, user: User):
    """Withdraw referral earnings."""
    from app.database.database import async_session_maker
    from sqlalchemy import select, func
    from app.database.models.referral import Referral

    async with async_session_maker() as session:
        # Sum money earned
        money_earned_result = await session.execute(
            select(func.sum(Referral.money_earned)).where(
                Referral.referrer_id == user.id,
                Referral.is_active == True
            )
        )
        money_earned = float(money_earned_result.scalar() or 0)

    min_withdrawal = 500.0

    if money_earned < min_withdrawal:
        await callback.answer(
            f"⚠️ Недостаточно средств для вывода\n\n"
            f"Минимум: {min_withdrawal:.0f} руб.\n"
            f"Доступно: {money_earned:.2f} руб.",
            show_alert=True
        )
    else:
        text = f"""💰 **Вывод средств**

Доступно для вывода: **{money_earned:.2f} руб.**

Для вывода средств обратитесь в поддержку: @gigavidacha

Укажите:
• Ваш Telegram ID: `{user.telegram_id}`
• Сумму для вывода
• Реквизиты для перевода"""

        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data.in_(["bot.change_language", "bot.profile_payments"]))
async def profile_feature_not_implemented(callback: CallbackQuery):
    """Profile features not implemented."""
    features = {
        "bot.change_language": "Изменение языка",
        "bot.profile_payments": "История платежей"
    }
    feature = features.get(callback.data, "Функционал")

    await callback.answer(
        f"⚠️ {feature} будет доступно в следующей версии",
        show_alert=True
    )


@router.callback_query(F.data == "page#faq")
async def show_faq(callback: CallbackQuery):
    """Show FAQ/Help."""
    text = """🆘 <b>Помощь</b>

<b>Как пользоваться ботом:</b>
1️⃣ Выберите AI модель через /models
2️⃣ Отправьте текстовый запрос
3️⃣ Получите ответ от AI

<b>Токены:</b>
• Каждый запрос стоит определенное количество токенов
• Пополнить баланс: /shop
• Посмотреть баланс: /profile

<b>Поддержка:</b>
Если возникли вопросы, напишите @gigavidacha"""

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()
