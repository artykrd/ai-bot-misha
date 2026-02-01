"""
Inline keyboards for the bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


MENU_BUTTONS = [
    ("Главное меню", "bot.back"),
    ("Мой профиль", "bot.profile"),
    ("Оформить подписку", "bot#shop"),
    ("Пригласи друга", "bot.refferal_program"),
    ("Выбрать модель", "bot.llm_models"),
    ("Nano Banana", "bot.nano"),
    ("Midjourney", "bot.midjourney"),
    ("DALL·E 3", "bot.gpt_image"),
    ("Gpt image 1", "bot.gpt_image"),
    ("Veo 3.1", "bot.veo"),
    ("Kling", "bot.kling_main"),
    ("Sora", "bot.sora"),
    ("Hailuo", "bot.hailuo"),
    ("Midjourney Video", "bot.mjvideo"),
    ("Luma", "bot.luma"),
    ("Suno", "bot.suno"),
    ("Расшифровка голоса", "bot.whisper"),
    ("Работа с фото", "bot.pi"),
    ("Recraft", "bot.recraft"),
    ("Замена лица на фото", "bot.faceswap"),
    ("Активировать промокод", "activate_promocode"),
    ("Помощь", "help"),
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Full menu keyboard."""
    builder = InlineKeyboardBuilder()

    for text, callback in MENU_BUTTONS:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback))

    return builder.as_markup()


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Меню", callback_data="bot.menu"))
    return builder.as_markup()


def ai_models_keyboard() -> InlineKeyboardMarkup:
    """AI models selection keyboard with groups: ChatGPT, Deepseek, Gemini, Others."""
    builder = InlineKeyboardBuilder()

    # ChatGPT
    builder.row(
        InlineKeyboardButton(text="4️⃣ GPT 4.1 Mini", callback_data="bot.start_chatgpt_dialog_324"),
        InlineKeyboardButton(text="4️⃣ GPT 4o", callback_data="bot.start_chatgpt_dialog_325")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 GPT 5 Mini", callback_data="bot.start_chatgpt_dialog_337"),
        InlineKeyboardButton(text="💫 O3 Mini", callback_data="bot.start_chatgpt_dialog_326")
    )

    # Deepseek
    builder.row(
        InlineKeyboardButton(text="🐳 Deepseek Чат", callback_data="bot.start_chatgpt_dialog_327"),
        InlineKeyboardButton(text="🐳 Deepseek R1", callback_data="bot.start_chatgpt_dialog_328")
    )

    # Gemini
    builder.row(
        InlineKeyboardButton(text="⚡ Gemini Flash 2.0", callback_data="bot.start_chatgpt_dialog_329")
    )

    # Другие модели
    builder.row(
        InlineKeyboardButton(text="📔 Claude 4", callback_data="bot.start_chatgpt_dialog_333"),
        InlineKeyboardButton(text="🌐 Sonar с поиском", callback_data="bot.start_chatgpt_dialog_331")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Sonar Pro", callback_data="bot.start_chatgpt_dialog_332")
    )

    # Инструменты
    builder.row(
        InlineKeyboardButton(text="💬 Выбрать диалог", callback_data="bot.dialogs_chatgpt")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def dialog_keyboard(dialog_id: int, history_enabled: bool = False, show_costs: bool = False, from_home: bool = False) -> InlineKeyboardMarkup:
    """Dialog keyboard with history and cost toggles."""
    builder = InlineKeyboardBuilder()

    # History toggle
    if history_enabled:
        builder.row(
            InlineKeyboardButton(
                text="🟢 История включена",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#sh_1"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔴 История отключена",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#sh_0"
            )
        )

    # Show costs toggle
    if show_costs:
        builder.row(
            InlineKeyboardButton(
                text="🟢 Показ затрат включен",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#bi_1"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔴 Показ затрат отключен",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#bi_0"
            )
        )

    # Change model
    builder.row(
        InlineKeyboardButton(text="🤖 Изменить модель", callback_data="bot.llm_models")
    )

    # Back button
    if from_home:
        builder.row(
            InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад к моделям", callback_data="bot.llm_models")
        )

    return builder.as_markup()


def nano_banana_keyboard(is_pro: bool = False) -> InlineKeyboardMarkup:
    """Nano Banana keyboard with version toggle."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📐 Изменить формат", callback_data="bot.nb.prms:ratio")
    )

    # New button for multiple images generation
    builder.row(
        InlineKeyboardButton(text="🎨 Создать несколько изображений", callback_data="bot.nb.multi")
    )

    # Version toggle button
    if is_pro:
        builder.row(
            InlineKeyboardButton(text="🍌 Переключить на обычную версию", callback_data="bot.nano")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="✨ Переключить на PRO версию", callback_data="bot.nano_pro")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def nano_format_keyboard(current_ratio: str = "auto") -> InlineKeyboardMarkup:
    """Nano Banana format selection keyboard with current selection marked."""
    builder = InlineKeyboardBuilder()

    # Define all available ratios
    ratios = ["1:1", "2:3", "3:2", "16:9", "9:16", "auto"]

    # Add checkmark to selected ratio
    def format_button_text(ratio: str) -> str:
        return f"✅ {ratio}" if ratio == current_ratio else ratio

    builder.row(
        InlineKeyboardButton(text=format_button_text("1:1"), callback_data="bot.nb.prms.chs:ratio|1:1"),
        InlineKeyboardButton(text=format_button_text("2:3"), callback_data="bot.nb.prms.chs:ratio|2:3"),
        InlineKeyboardButton(text=format_button_text("3:2"), callback_data="bot.nb.prms.chs:ratio|3:2")
    )
    builder.row(
        InlineKeyboardButton(text=format_button_text("16:9"), callback_data="bot.nb.prms.chs:ratio|16:9"),
        InlineKeyboardButton(text=format_button_text("9:16"), callback_data="bot.nb.prms.chs:ratio|9:16"),
        InlineKeyboardButton(text=format_button_text("auto"), callback_data="bot.nb.prms.chs:ratio|auto")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться в Nano Banana", callback_data="bot.nano")
    )

    return builder.as_markup()


def nano_multi_images_keyboard() -> InlineKeyboardMarkup:
    """Nano Banana multiple images count selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="2️⃣ изображения", callback_data="bot.nb.multi.cnt:2"),
        InlineKeyboardButton(text="3️⃣ изображения", callback_data="bot.nb.multi.cnt:3")
    )
    builder.row(
        InlineKeyboardButton(text="4️⃣ изображения", callback_data="bot.nb.multi.cnt:4"),
        InlineKeyboardButton(text="5️⃣ изображений", callback_data="bot.nb.multi.cnt:5")
    )
    builder.row(
        InlineKeyboardButton(text="6️⃣ изображений", callback_data="bot.nb.multi.cnt:6"),
        InlineKeyboardButton(text="🔟 изображений", callback_data="bot.nb.multi.cnt:10")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться в Nano Banana", callback_data="bot.nano")
    )

    return builder.as_markup()


def dialogs_keyboard() -> InlineKeyboardMarkup:
    """Dialogs list keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔍 Анализ текста", callback_data="bot.start_chatgpt_dialog_335"),
        InlineKeyboardButton(text="🌆 Генератор промптов", callback_data="bot.start_chatgpt_dialog_336")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Выбрать модель", callback_data="bot.llm_models"),
        InlineKeyboardButton(text="🆕 Создать диалог", callback_data="bot.create_chatgpt_dialog")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def create_photo_keyboard() -> InlineKeyboardMarkup:
    """Photo creation keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🖼 DALL-E 3", callback_data="bot.gpt_image"),
        InlineKeyboardButton(text="👁 GPT Vision", callback_data="bot.gpt_vision")
    )
    builder.row(
        InlineKeyboardButton(text="🍌 Nano Banana", callback_data="bot.nano"),
        InlineKeyboardButton(text="🍌✨ Banana PRO", callback_data="bot.nano_pro")
    )
    builder.row(
        InlineKeyboardButton(text="🌆 Midjourney", callback_data="bot.midjourney"),
        InlineKeyboardButton(text="🎨 Recraft", callback_data="bot.recraft")
    )
    builder.row(
        InlineKeyboardButton(text="✨ Seedream 4.5", callback_data="bot.seedream_4.5"),
        InlineKeyboardButton(text="🌟 Seedream 4.0", callback_data="bot.seedream_4.0")
    )
    builder.row(
        InlineKeyboardButton(text="🖌 Stable Diffusion", callback_data="bot_stable_diffusion"),
        InlineKeyboardButton(text="🎞 Kling AI", callback_data="bot.kling_image")
    )
    builder.row(
        InlineKeyboardButton(text="🎭 Замена лиц", callback_data="bot.faceswap")
    )
    builder.row(
        InlineKeyboardButton(text="🛠 Редактировать фото", callback_data="bot.pi")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def create_video_keyboard() -> InlineKeyboardMarkup:
    """Video creation keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎞 Kling", callback_data="bot.kling_video"),
        InlineKeyboardButton(text="🎥 Hailuo", callback_data="bot.hailuo")
    )
    builder.row(
        InlineKeyboardButton(text="🌊 Veo 3.1", callback_data="bot.veo"),
        InlineKeyboardButton(text="📹 Luma", callback_data="bot.luma")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def photo_tools_keyboard() -> InlineKeyboardMarkup:
    """Photo tools keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔎 Улучшить качество", callback_data="bot.pi_upscale")
    )
    builder.row(
        InlineKeyboardButton(text="🪄 Заменить фон", callback_data="bot.pi_repb")
    )
    builder.row(
        InlineKeyboardButton(text="🪞 Удалить фон", callback_data="bot.pi_remb")
    )
    builder.row(
        InlineKeyboardButton(text="📐 Векторизация", callback_data="bot.pi_vect")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def audio_tools_keyboard() -> InlineKeyboardMarkup:
    """Audio tools keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎧 Создать песню", callback_data="bot.suno")
    )
    builder.row(
        InlineKeyboardButton(text="🎙 Расшифровка голоса", callback_data="bot.whisper")
    )
    builder.row(
        InlineKeyboardButton(text="🗣 Озвучка текста", callback_data="bot.whisper_tts")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def subscription_keyboard() -> InlineKeyboardMarkup:
    """Subscription selection keyboard with new billing prices."""
    from app.core.subscription_plans import list_subscription_plans

    builder = InlineKeyboardBuilder()

    for plan in list_subscription_plans():
        builder.row(
            InlineKeyboardButton(
                text=(
                    f"{plan.display_name} — {plan.price} руб."
                ),
                callback_data=f"shop_select_tariff_{plan.plan_id}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="🔥 Безлимит на 1 день",
            callback_data="shop_select_tariff_22"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔹 Купить вечные токены",
            callback_data="bot#shop_tokens"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔢 Активировать промокод",
            callback_data="activate_promocode"
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.back")
    )

    return builder.as_markup()


def eternal_tokens_keyboard() -> InlineKeyboardMarkup:
    """Eternal tokens selection keyboard."""
    from app.core.subscription_plans import ETERNAL_PLANS
    from app.core.billing_config import format_token_amount

    builder = InlineKeyboardBuilder()

    for plan in ETERNAL_PLANS.values():
        builder.row(
            InlineKeyboardButton(
                text=f"{format_token_amount(plan.tokens)} токенов — {plan.price} руб.",
                callback_data=f"buy:{plan.subscription_type}"
            )
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot#shop")
    )

    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    """Profile keyboard with additional options."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💎 Токены", callback_data="bot.profile_tokens")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои платежи", callback_data="bot.profile_payments"),
        InlineKeyboardButton(text="📦 Мои подписки", callback_data="bot.profile_subscriptions")
    )
    builder.row(
        InlineKeyboardButton(text="🤝 Партнерство", callback_data="bot.refferal_program")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Поддержка", callback_data="page#faq")
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Активировать промокод", callback_data="activate_promocode")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def referral_keyboard(user_telegram_id: int = None) -> InlineKeyboardMarkup:
    """Referral program keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🏦 Вывести средства", callback_data="bot.refferal_withdraw")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Обменять на токены", callback_data="bot.refferal_exchange")
    )

    # Share button with dynamic referral link
    if user_telegram_id:
        bot_username = "assistantvirtualsbot"
        referral_link = f"https://t.me/{bot_username}?start=ref{user_telegram_id}"
        share_url = f"https://t.me/share/url?url={referral_link}"
        builder.row(
            InlineKeyboardButton(
                text="🔗 Поделиться ссылкой",
                url=share_url
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.profile")
    )

    return builder.as_markup()


def help_keyboard() -> InlineKeyboardMarkup:
    """Help menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💎 Токены", callback_data="help.tokens")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Платежи", callback_data="help.payments")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.profile")
    )

    return builder.as_markup()


def subscription_manage_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    """Keyboard for managing an active subscription."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="❌ Отменить подписку", callback_data=f"cancel_subscription_{subscription_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="bot.profile")
    )

    return builder.as_markup()


def kling_choice_keyboard() -> InlineKeyboardMarkup:
    """Kling AI choice keyboard for photo or video generation."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🌄 Создать фото", callback_data="bot.kling_image"),
        InlineKeyboardButton(text="🎬 Создать видео", callback_data="bot.kling_video")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


# ======================
# KLING VIDEO KEYBOARDS
# ======================

def kling_main_keyboard() -> InlineKeyboardMarkup:
    """Main Kling video keyboard with settings button."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="kling.settings")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def kling_settings_keyboard() -> InlineKeyboardMarkup:
    """Kling settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📐 Формат видео", callback_data="kling.settings.aspect_ratio")
    )
    builder.row(
        InlineKeyboardButton(text="🕓 Длительность", callback_data="kling.settings.duration")
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Версия", callback_data="kling.settings.version")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Автоперевод", callback_data="kling.settings.auto_translate")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_aspect_ratio_keyboard(current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """Kling aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "16:9", "9:16"]

    for ratio in ratios:
        text = f"✅ {ratio}" if ratio == current_ratio else ratio
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling.set.aspect_ratio:{ratio}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_duration_keyboard(current_duration: int = 5) -> InlineKeyboardMarkup:
    """Kling duration selection keyboard."""
    builder = InlineKeyboardBuilder()

    durations = [5, 10]

    for duration in durations:
        text = f"✅ {duration} секунд" if duration == current_duration else f"{duration} секунд"
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling.set.duration:{duration}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_version_keyboard(current_version: str = "2.5") -> InlineKeyboardMarkup:
    """Kling version selection keyboard."""
    builder = InlineKeyboardBuilder()

    versions = ["2.1", "2.1 Pro", "2.5", "2.6"]

    for version in versions:
        text = f"✅ {version}" if version == current_version else version
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling.set.version:{version}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_auto_translate_keyboard(current_value: bool = True) -> InlineKeyboardMarkup:
    """Kling auto-translate toggle keyboard."""
    builder = InlineKeyboardBuilder()

    yes_text = "✅ Да" if current_value else "Да"
    no_text = "✅ Нет" if not current_value else "Нет"

    builder.row(
        InlineKeyboardButton(text=yes_text, callback_data="kling.set.auto_translate:yes")
    )
    builder.row(
        InlineKeyboardButton(text=no_text, callback_data="kling.set.auto_translate:no")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


# ======================
# SUNO KEYBOARDS
# ======================

def suno_main_keyboard(model_version: str = "V5", is_instrumental: bool = False, style: str = "техно, хип-хоп", balance_songs: int = 0, tokens_per_song: int = 17600) -> InlineKeyboardMarkup:
    """Main Suno keyboard with current settings."""
    builder = InlineKeyboardBuilder()

    # Type button
    type_text = "инструментал (без слов)" if is_instrumental else "с текстом песни"

    builder.row(
        InlineKeyboardButton(text="⚙️ Параметры", callback_data="suno.settings")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Создать песню пошагово", callback_data="suno.step_by_step")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def suno_settings_keyboard(model_version: str = "V5", is_instrumental: bool = False, style: str = "техно, хип-хоп") -> InlineKeyboardMarkup:
    """Suno settings keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📀 Изменить версию", callback_data="suno.change_version")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Изменить тип", callback_data="suno.change_type")
    )
    builder.row(
        InlineKeyboardButton(text="🎨 Изменить стиль", callback_data="suno.change_style")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_version_keyboard() -> InlineKeyboardMarkup:
    """Suno model version selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎵 V5 (лучшее)", callback_data="suno.set_version_V5")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 V4.5 Plus", callback_data="suno.set_version_V4_5PLUS"),
        InlineKeyboardButton(text="🎵 V4.5 All", callback_data="suno.set_version_V4_5ALL")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 V4.5", callback_data="suno.set_version_V4_5"),
        InlineKeyboardButton(text="🎵 V4", callback_data="suno.set_version_V4")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="suno.settings")
    )

    return builder.as_markup()


def suno_type_keyboard() -> InlineKeyboardMarkup:
    """Suno type selection keyboard (instrumental or with lyrics)."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎤 С текстом песни", callback_data="suno.set_type_lyrics")
    )
    builder.row(
        InlineKeyboardButton(text="🎹 Инструментал (без слов)", callback_data="suno.set_type_instrumental")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="suno.settings")
    )

    return builder.as_markup()


def suno_style_keyboard(selected_styles: list = None) -> InlineKeyboardMarkup:
    """Suno style selection keyboard with multiple selection support."""
    builder = InlineKeyboardBuilder()

    if selected_styles is None:
        selected_styles = []

    # All 21 styles from the image (7 rows x 3 columns)
    styles = [
        ("🎤 Рэп", "рэп"),
        ("🎧 Хип-хоп", "хип-хоп"),
        ("🎸 Рок", "рок"),

        ("🎹 Поп", "поп"),
        ("🎵 R&B", "r&b"),
        ("⚡ Электроника", "электроника"),

        ("🪩 Диско", "диско"),
        ("🔊 Техно", "техно"),
        ("🏠 Хаус", "хаус"),

        ("💃 Танцевальная", "танцевальная"),
        ("🎛 Дабстеп", "дабстеп"),
        ("🎺 Джаз", "джаз"),

        ("🤠 Кантри", "кантри"),
        ("🌴 Регги", "регги"),
        ("🎻 Фолк", "фолк"),

        ("🎷 Блюз", "блюз"),
        ("🎼 Классика", "классическая"),
        ("🎸 Фанк", "фанк"),

        ("🎭 Панк", "панк"),
        ("🌊 Эмбиент", "эмбиент"),
        ("📻 Lo-Fi", "lo-fi"),
    ]

    # Build keyboard in rows of 3
    for i in range(0, len(styles), 3):
        row_buttons = []
        for j in range(3):
            if i + j < len(styles):
                style_name, style_value = styles[i + j]
                # Add checkmark if selected
                if style_value in selected_styles:
                    style_name = f"✅ {style_name}"
                row_buttons.append(
                    InlineKeyboardButton(
                        text=style_name,
                        callback_data=f"suno.toggle_style_{style_value}"
                    )
                )
        builder.row(*row_buttons)

    # Show selected styles count and confirm button
    selected_count = len(selected_styles)
    if selected_count > 0:
        builder.row(
            InlineKeyboardButton(
                text=f"👍 Я выбрал(а) стили ({selected_count}/3)",
                callback_data="suno.confirm_styles"
            )
        )

    builder.row(
        InlineKeyboardButton(text="✏️ Ввести свой стиль", callback_data="suno.custom_style")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Вернуться в Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_lyrics_choice_keyboard(song_title: str) -> InlineKeyboardMarkup:
    """Keyboard for choosing how to create lyrics."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🤖 Создать по названию", callback_data="suno.lyrics_by_title")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Создать по описанию", callback_data="suno.lyrics_by_description")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Написать свой текст", callback_data="suno.lyrics_custom")
    )
    builder.row(
        InlineKeyboardButton(text="🎹 Создать без слов", callback_data="suno.lyrics_instrumental")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back to Suno keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )
    return builder.as_markup()


def suno_vocal_keyboard(selected_vocal: str = "m") -> InlineKeyboardMarkup:
    """Keyboard for selecting vocal type."""
    builder = InlineKeyboardBuilder()

    # Vocal type buttons with checkmark for selected
    # API supports: 'm' (male), 'f' (female)
    vocals = [
        ("👨 Мужской голос", "m"),
        ("👩 Женский голос", "f"),
    ]

    for text, vocal_type in vocals:
        if vocal_type == selected_vocal:
            text = f"✅ {text}"
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"suno.set_vocal_{vocal_type}")
        )

    builder.row(
        InlineKeyboardButton(text="👍 Подтвердить", callback_data="suno.confirm_vocal")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_final_keyboard() -> InlineKeyboardMarkup:
    """Final screen keyboard with generate button."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎵 Создать песню", callback_data="suno.generate_song")
    )
    builder.row(
        InlineKeyboardButton(text="↻ Начать заново", callback_data="suno.step_by_step")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )
    return builder.as_markup()


# =============================================
# SEEDREAM KEYBOARDS
# =============================================

def seedream_keyboard(model_version: str = "4.5", current_size: str = "2K", batch_mode: bool = False) -> InlineKeyboardMarkup:
    """Seedream main keyboard with settings."""
    builder = InlineKeyboardBuilder()

    # Size selection
    builder.row(
        InlineKeyboardButton(
            text=f"📐 Разрешение: {current_size}",
            callback_data=f"seedream.settings.size|{model_version}"
        )
    )

    # Batch mode toggle
    if batch_mode:
        builder.row(
            InlineKeyboardButton(
                text="📦 Пакетная генерация: ВКЛ",
                callback_data=f"seedream.toggle.batch|{model_version}|off"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="🔢 Количество изображений",
                callback_data=f"seedream.settings.batch_count|{model_version}"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="📦 Пакетная генерация: ВЫКЛ",
                callback_data=f"seedream.toggle.batch|{model_version}|on"
            )
        )

    # Switch version
    if model_version == "4.5":
        builder.row(
            InlineKeyboardButton(
                text="🔄 Переключить на Seedream 4.0",
                callback_data="bot.seedream_4.0"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔄 Переключить на Seedream 4.5",
                callback_data="bot.seedream_4.5"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def seedream_size_keyboard(model_version: str = "4.5", current_size: str = "2K") -> InlineKeyboardMarkup:
    """Seedream size selection keyboard."""
    builder = InlineKeyboardBuilder()

    # Different sizes for different models
    if model_version == "4.5":
        sizes = [
            ("2K", "2K"),
            ("4K", "4K"),
            ("1:1", "1:1"),
            ("4:3", "4:3"),
            ("3:4", "3:4"),
            ("16:9", "16:9"),
            ("9:16", "9:16"),
        ]
    else:  # 4.0
        sizes = [
            ("1K", "1K"),
            ("2K", "2K"),
            ("4K", "4K"),
            ("1:1", "1:1"),
            ("4:3", "4:3"),
            ("3:4", "3:4"),
            ("16:9", "16:9"),
            ("9:16", "9:16"),
        ]

    # Add checkmark to current size
    def format_button_text(size: str) -> str:
        return f"✅ {size}" if size == current_size else size

    # Build in rows of 3
    for i in range(0, len(sizes), 3):
        row_buttons = []
        for j in range(3):
            if i + j < len(sizes):
                size_name, size_value = sizes[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=format_button_text(size_name),
                        callback_data=f"seedream.set.size|{model_version}|{size_value}"
                    )
                )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data=f"bot.seedream_{model_version}"
        )
    )

    return builder.as_markup()


def seedream_batch_count_keyboard(model_version: str = "4.5", current_count: int = 3) -> InlineKeyboardMarkup:
    """Seedream batch image count selection keyboard."""
    builder = InlineKeyboardBuilder()

    counts = [2, 3, 4, 5, 6, 8, 10, 15]

    def format_button_text(count: int) -> str:
        text = f"{count} шт."
        return f"✅ {text}" if count == current_count else text

    # Build in rows of 4
    for i in range(0, len(counts), 4):
        row_buttons = []
        for j in range(4):
            if i + j < len(counts):
                count = counts[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=format_button_text(count),
                        callback_data=f"seedream.set.batch_count|{model_version}|{count}"
                    )
                )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data=f"bot.seedream_{model_version}"
        )
    )

    return builder.as_markup()


def seedream_back_keyboard(model_version: str = "4.5") -> InlineKeyboardMarkup:
    """Simple back to Seedream keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data=f"bot.seedream_{model_version}"
        )
    )
    return builder.as_markup()
