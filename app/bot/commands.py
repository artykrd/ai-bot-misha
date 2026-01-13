"""
Bot command menu configuration and setup.
"""
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.core.logger import get_logger

logger = get_logger(__name__)


# Define all bot commands
BOT_COMMANDS = [
    BotCommand(command="start", description="🦁 Главное меню"),
    BotCommand(command="shop", description="💎 Оформить подписку"),
    BotCommand(command="models", description="🤖 Выбрать модель"),
    BotCommand(command="sora", description="☁️ Sora 2"),
    BotCommand(command="veo", description="🌊 Veo 3.1"),
    BotCommand(command="nano", description="🍌 Nano Banana"),
    BotCommand(command="suno", description="🎵 Suno"),
    BotCommand(command="image", description="💥 GPT Image 1"),
    BotCommand(command="mj", description="🖼 Midjourney"),
    BotCommand(command="dalle", description="🖼 DALL-E 3"),
    BotCommand(command="recraft", description="🎨 Recraft"),
    BotCommand(command="faceswap", description="🎭 Замена лица на фото"),
    BotCommand(command="instruments", description="✂️ Работа с фото"),
    BotCommand(command="whisper", description="🎙 Расшифровка голоса"),
    BotCommand(command="mvideo", description="🎞 Midjourney Video"),
    BotCommand(command="luma", description="🎬 Luma Dream Machine"),
    BotCommand(command="kling", description="🎞 Kling"),
    BotCommand(command="hailuo", description="🎥 Hailuo"),
    BotCommand(command="profile", description="👤 Мой профиль"),
    BotCommand(command="ref", description="🤝 Пригласи друга"),
    BotCommand(command="promocode", description="🔢 Активировать промокод"),
    BotCommand(command="faq", description="❓ Помощь"),
]


async def setup_bot_commands(bot: Bot) -> None:
    """Setup bot commands menu."""
    await bot.set_my_commands(
        commands=BOT_COMMANDS,
        scope=BotCommandScopeDefault()
    )
    logger.info("bot_commands_set", count=len(BOT_COMMANDS))
