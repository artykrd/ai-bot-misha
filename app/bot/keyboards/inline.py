"""
Inline keyboards for the bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard matching bot_structure.md."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🗯 ChatGPT", callback_data="bot.start_chatgpt_dialog_324#home")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Выбрать модель", callback_data="bot.llm_models"),
        InlineKeyboardButton(text="💬 Диалоги", callback_data="bot.dialogs_chatgpt")
    )
    builder.row(
        InlineKeyboardButton(text="🌄 Создать фото", callback_data="bot.create_photo"),
        InlineKeyboardButton(text="🎞 Создать видео", callback_data="bot.create_video")
    )
    builder.row(
        InlineKeyboardButton(text="✂️ Работа с фото", callback_data="bot.pi"),
        InlineKeyboardButton(text="🎙 Работа с аудио", callback_data="bot.audio_instruments")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="bot.profile"),
        InlineKeyboardButton(text="💎 Подписка", callback_data="bot#shop")
    )
    builder.row(
        InlineKeyboardButton(text="🤝🏼 Партнерство", callback_data="bot.refferal_program"),
        InlineKeyboardButton(text="🆘 Поддержка", url="https://t.me/gigavidacha")
    )

    return builder.as_markup()


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Back to main menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back"))
    return builder.as_markup()


def ai_models_keyboard() -> InlineKeyboardMarkup:
    """AI models selection keyboard with all 12 models."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="4️⃣ GPT 4.1 Mini", callback_data="bot.start_chatgpt_dialog_324"),
        InlineKeyboardButton(text="4️⃣ GPT 4o", callback_data="bot.start_chatgpt_dialog_325")
    )
    builder.row(
        InlineKeyboardButton(text="💫 O3 Mini", callback_data="bot.start_chatgpt_dialog_326"),
        InlineKeyboardButton(text="🐳 Deepseek Чат", callback_data="bot.start_chatgpt_dialog_327")
    )
    builder.row(
        InlineKeyboardButton(text="🐳 Deepseek R1", callback_data="bot.start_chatgpt_dialog_328"),
        InlineKeyboardButton(text="⚡ Gemini Flash 2.0", callback_data="bot.start_chatgpt_dialog_329")
    )
    builder.row(
        InlineKeyboardButton(text="🛡 nano Banana", callback_data="bot.start_chatgpt_dialog_330"),
        InlineKeyboardButton(text="🌐 Sonar с поиском", callback_data="bot.start_chatgpt_dialog_331")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Sonar Pro", callback_data="bot.start_chatgpt_dialog_332"),
        InlineKeyboardButton(text="📔 Claude 4", callback_data="bot.start_chatgpt_dialog_333")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 GPT 5 Mini", callback_data="bot.start_chatgpt_dialog_337")
    )
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


def nano_banana_keyboard() -> InlineKeyboardMarkup:
    """Nano Banana keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📐 Изменить формат", callback_data="bot.nb.prms:ratio")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def nano_format_keyboard() -> InlineKeyboardMarkup:
    """Nano Banana format selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="1:1", callback_data="bot.nb.prms.chs:ratio|1:1"),
        InlineKeyboardButton(text="2:3", callback_data="bot.nb.prms.chs:ratio|2:3"),
        InlineKeyboardButton(text="3:2", callback_data="bot.nb.prms.chs:ratio|3:2")
    )
    builder.row(
        InlineKeyboardButton(text="16:9", callback_data="bot.nb.prms.chs:ratio|16:9"),
        InlineKeyboardButton(text="9:16", callback_data="bot.nb.prms.chs:ratio|9:16"),
        InlineKeyboardButton(text="✅ auto", callback_data="bot.nb.prms.chs:ratio|auto")
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
        InlineKeyboardButton(text="🌆 Midjourney", callback_data="bot.midjourney")
    )
    builder.row(
        InlineKeyboardButton(text="🖌 Stable Diffusion", callback_data="bot_stable_diffusion"),
        InlineKeyboardButton(text="🎨 Recraft", callback_data="bot.recraft")
    )
    builder.row(
        InlineKeyboardButton(text="🎞 Kling AI", callback_data="bot.kling_image"),
        InlineKeyboardButton(text="🎭 Замена лиц", callback_data="bot.faceswap")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def create_video_keyboard() -> InlineKeyboardMarkup:
    """Video creation keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="☁️ Sora 2", callback_data="bot.sora"),
        InlineKeyboardButton(text="🌊 Veo 3.1", callback_data="bot.veo")
    )
    builder.row(
        InlineKeyboardButton(text="🗾 Midjourney Video", callback_data="bot.mjvideo"),
        InlineKeyboardButton(text="🎥 Hailuo", callback_data="bot.hailuo")
    )
    builder.row(
        InlineKeyboardButton(text="📹 Luma", callback_data="bot.luma"),
        InlineKeyboardButton(text="🎞 Kling", callback_data="bot.kling_video")
    )
    builder.row(
        InlineKeyboardButton(text="🧙 Kling Эффекты", callback_data="bot.kling_effects")
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
    """Subscription selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="7 дней — 150,000 токенов — 98 руб.",
            callback_data="shop_select_tariff_1"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="14 дней — 250,000 токенов — 196 руб.",
            callback_data="shop_select_tariff_2"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="21 день — 500,000 токенов — 289 руб.",
            callback_data="shop_select_tariff_3"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="30 дней — 1,000,000 токенов — 597 руб.",
            callback_data="shop_select_tariff_6"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="30 дней — 5,000,000 токенов — 2790 руб.",
            callback_data="shop_select_tariff_21"
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
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="150,000 токенов — 149 руб.",
            callback_data="buy:eternal_150k"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="250,000 токенов — 279 руб.",
            callback_data="buy:eternal_250k"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="500,000 токенов — 519 руб.",
            callback_data="buy:eternal_500k"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="1,000,000 токенов — 999 руб.",
            callback_data="buy:eternal_1m"
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
        InlineKeyboardButton(text="🌎 Изменить язык", callback_data="bot.change_language")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои платежи", callback_data="bot.profile_payments")
    )
    builder.row(
        InlineKeyboardButton(text="🤝🏼 Партнерство", callback_data="bot.refferal_program")
    )
    builder.row(
        InlineKeyboardButton(text="🤔 Помощь", callback_data="page#faq")
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

    # Share button with dynamic referral link
    if user_telegram_id:
        bot_username = "GPTchatneiroseti_BOT"  # TODO: Get from config
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


def suno_style_keyboard() -> InlineKeyboardMarkup:
    """Suno style selection keyboard."""
    builder = InlineKeyboardBuilder()

    styles = [
        ("🎸 Рок", "рок"),
        ("🎹 Поп", "поп"),
        ("🎺 Джаз", "джаз"),
        ("🎵 Классика", "классическая музыка"),
        ("🎧 Электроника", "электроника, техно"),
        ("🎤 Хип-хоп", "хип-хоп, рэп"),
        ("🎻 Блюз", "блюз"),
        ("🎼 Кантри", "кантри"),
        ("🎪 Фолк", "фолк"),
        ("🎭 Металл", "металл"),
    ]

    for i in range(0, len(styles), 2):
        if i + 1 < len(styles):
            builder.row(
                InlineKeyboardButton(text=styles[i][0], callback_data=f"suno.set_style_{styles[i][1]}"),
                InlineKeyboardButton(text=styles[i+1][0], callback_data=f"suno.set_style_{styles[i+1][1]}")
            )
        else:
            builder.row(
                InlineKeyboardButton(text=styles[i][0], callback_data=f"suno.set_style_{styles[i][1]}")
            )

    builder.row(
        InlineKeyboardButton(text="✏️ Ввести свой стиль", callback_data="suno.custom_style")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Создать песню", callback_data="suno.generate_song")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="suno.settings")
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
