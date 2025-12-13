#!/usr/bin/env python3
# coding: utf-8
"""
Universal message handler for active dialogs.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

from app.bot.handlers.dialog_context import (
    get_active_dialog,
    clear_active_dialog,
    has_active_dialog
)
from app.database.models.user import User
from app.database.database import async_session_maker
from app.services.subscription.subscription_service import SubscriptionService
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError

logger = get_logger(__name__)

router = Router(name="dialog_handler")


def split_long_message(text: str, max_length: int = 4000) -> list[str]:
    """
    Split long message into chunks that fit Telegram's message limit.
    Telegram has a 4096 character limit, but we use 4000 to leave room for formatting.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    # Split by paragraphs first
    paragraphs = text.split('\n\n')

    for paragraph in paragraphs:
        # If adding this paragraph exceeds limit, save current chunk
        if len(current_chunk) + len(paragraph) + 2 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # If single paragraph is too long, split by sentences
            if len(paragraph) > max_length:
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 2 > max_length:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + '. '
                    else:
                        current_chunk += sentence + '. '
            else:
                current_chunk = paragraph + '\n\n'
        else:
            current_chunk += paragraph + '\n\n'

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


@router.message(Command("end"))
async def cmd_end_dialog(message: Message, user: User):
    """End current dialog."""
    if not has_active_dialog(user.telegram_id):
        await message.answer("У вас нет активного диалога.")
        return

    dialog = get_active_dialog(user.telegram_id)
    clear_active_dialog(user.telegram_id)

    await message.answer(
        f"✅ Диалог с {dialog['model_name']} завершен.\n\n"
        f"Используйте /start для возврата в главное меню."
    )


@router.message(Command("clear"))
async def cmd_clear_history(message: Message, user: User):
    """Clear dialog history."""
    if not has_active_dialog(user.telegram_id):
        await message.answer("У вас нет активного диалога.")
        return

    dialog = get_active_dialog(user.telegram_id)

    # TODO: Clear dialog history in database
    # For now just send confirmation

    await message.answer(
        f"✅ История диалога с {dialog['model_name']} очищена.\n\n"
        f"Можете продолжать общение с чистой историей."
    )


@router.message(F.text)
async def handle_text_message(message: Message, user: User):
    """Handle text messages in active dialog."""
    # Check if user has active dialog
    dialog = get_active_dialog(user.telegram_id)
    if not dialog:
        # No active dialog - ignore message
        logger.debug(f"User {user.telegram_id} sent message but no active dialog")
        return

    # Process text message
    await process_dialog_message(
        message=message,
        user=user,
        dialog=dialog,
        message_type="text",
        content=message.text
    )


@router.message(F.voice)
async def handle_voice_message(message: Message, user: User):
    """Handle voice messages in active dialog."""
    dialog = get_active_dialog(user.telegram_id)
    if not dialog:
        return

    if not dialog["supports_voice"]:
        await message.answer(
            f"⚠️ Модель {dialog['model_name']} не поддерживает голосовые сообщения.\n\n"
            f"Пожалуйста, отправьте текстовое сообщение."
        )
        return

    # Process voice message
    await process_dialog_message(
        message=message,
        user=user,
        dialog=dialog,
        message_type="voice",
        content=message.voice
    )


@router.message(F.photo)
async def handle_photo_message(message: Message, user: User):
    """Handle photo messages in active dialog."""
    dialog = get_active_dialog(user.telegram_id)
    if not dialog:
        return

    if not dialog["supports_vision"]:
        await message.answer(
            f"⚠️ Модель {dialog['model_name']} не поддерживает анализ изображений.\n\n"
            f"Пожалуйста, отправьте текстовое сообщение."
        )
        return

    # Process photo message
    await process_dialog_message(
        message=message,
        user=user,
        dialog=dialog,
        message_type="photo",
        content=message.photo[-1]  # Get highest resolution photo
    )


@router.message(F.document)
async def handle_document_message(message: Message, user: User):
    """Handle document/file messages in active dialog."""
    dialog = get_active_dialog(user.telegram_id)
    if not dialog:
        return

    if not dialog["supports_files"]:
        await message.answer(
            f"⚠️ Модель {dialog['model_name']} не поддерживает обработку файлов.\n\n"
            f"Пожалуйста, отправьте текстовое сообщение."
        )
        return

    # Process document message
    await process_dialog_message(
        message=message,
        user=user,
        dialog=dialog,
        message_type="document",
        content=message.document
    )


async def process_dialog_message(
    message: Message,
    user: User,
    dialog: dict,
    message_type: str,
    content: any
):
    """Process message with AI model."""

    # Get cost
    tokens_cost = dialog["cost_per_request"]

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
            return

    # Show processing message
    processing_msg = await message.answer("⏳ Обрабатываю запрос...")

    try:
        # Route to appropriate AI service based on provider
        provider = dialog["provider"]
        model_id = dialog["model_id"]

        if provider == "openai":
            response = await process_openai_message(
                message_type=message_type,
                content=content,
                model_id=model_id,
                caption=message.caption,
                history_enabled=dialog["history_enabled"],
                system_prompt=dialog.get("system_prompt")
            )
        elif provider == "google":
            response = await process_google_message(
                message_type=message_type,
                content=content,
                model_id=model_id,
                caption=message.caption,
                history_enabled=dialog["history_enabled"],
                system_prompt=dialog.get("system_prompt")
            )
        elif provider == "anthropic":
            response = await process_anthropic_message(
                message_type=message_type,
                content=content,
                model_id=model_id,
                caption=message.caption,
                history_enabled=dialog["history_enabled"],
                system_prompt=dialog.get("system_prompt")
            )
        elif provider == "deepseek":
            response = await process_deepseek_message(
                message_type=message_type,
                content=content,
                model_id=model_id,
                caption=message.caption,
                history_enabled=dialog["history_enabled"],
                system_prompt=dialog.get("system_prompt")
            )
        elif provider == "perplexity":
            response = await process_perplexity_message(
                message_type=message_type,
                content=content,
                model_id=model_id,
                caption=message.caption,
                history_enabled=dialog["history_enabled"],
                system_prompt=dialog.get("system_prompt")
            )
        else:
            response = {
                "success": False,
                "error": f"Unknown provider: {provider}"
            }

        # Send response
        if response["success"]:
            response_text = response["content"]

            # Add cost info if enabled
            if dialog["show_costs"]:
                response_text += f"\n\n💰 <i>Стоимость запроса: {tokens_cost:,} токенов</i>"

            # Add mock warning if using mock service
            if response.get("mock"):
                response_text += "\n\n⚠️ <i>Используется тестовый режим (API ключи не настроены)</i>"

            # Split long messages to fit Telegram's limit
            message_chunks = split_long_message(response_text)

            # Send first chunk as edit to processing message
            await processing_msg.edit_text(message_chunks[0], parse_mode=ParseMode.HTML)

            # Send remaining chunks as new messages
            for chunk in message_chunks[1:]:
                await message.answer(chunk, parse_mode=ParseMode.HTML)

            logger.info(
                "dialog_message_processed",
                user_id=user.id,
                dialog_id=dialog["dialog_id"],
                model=dialog["model_name"],
                message_type=message_type,
                tokens=tokens_cost,
                is_mock=response.get("mock", False)
            )
        else:
            await processing_msg.edit_text(
                f"❌ Ошибка при обработке:\n{response['error']}"
            )

            logger.error(
                "dialog_message_failed",
                user_id=user.id,
                dialog_id=dialog["dialog_id"],
                error=response["error"]
            )

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Произошла ошибка: {str(e)}"
        )
        logger.error("dialog_message_exception", user_id=user.id, error=str(e), exc_info=True)


async def process_openai_message(
    message_type: str,
    content: any,
    model_id: str,
    caption: str = None,
    history_enabled: bool = False,
    system_prompt: str = None
) -> dict:
    """Process message with OpenAI models."""
    from app.services.ai.openai_service import OpenAIService

    try:
        service = OpenAIService()

        if message_type == "text":
            result = await service.generate_text(
                model=model_id,
                prompt=content,
                system_prompt=system_prompt
            )
        elif message_type == "voice":
            # TODO: Transcribe voice first, then send to model
            return {"success": False, "error": "Voice processing not yet implemented"}
        elif message_type == "photo":
            # TODO: Process image with vision model
            return {"success": False, "error": "Image processing not yet implemented"}
        elif message_type == "document":
            # TODO: Process document
            return {"success": False, "error": "Document processing not yet implemented"}
        else:
            return {"success": False, "error": f"Unsupported message type: {message_type}"}

        return {
            "success": result.success,
            "content": result.content if result.success else result.error,
            "error": result.error if not result.success else None,
            "mock": result.metadata.get("mock", False)
        }
    except Exception as e:
        logger.error(f"OpenAI processing error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def process_google_message(
    message_type: str,
    content: any,
    model_id: str,
    caption: str = None,
    history_enabled: bool = False,
    system_prompt: str = None
) -> dict:
    """Process message with Google Gemini models."""
    from app.services.ai.google_service import GoogleService

    try:
        service = GoogleService()

        if message_type == "text":
            result = await service.generate_text(
                model=model_id,
                prompt=content,
                system_prompt=system_prompt
            )
        else:
            return {"success": False, "error": f"Message type {message_type} not yet implemented for Google"}

        return {
            "success": result.success,
            "content": result.content if result.success else result.error,
            "error": result.error if not result.success else None,
            "mock": result.metadata.get("mock", False)
        }
    except Exception as e:
        logger.error(f"Google processing error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def process_anthropic_message(
    message_type: str,
    content: any,
    model_id: str,
    caption: str = None,
    history_enabled: bool = False,
    system_prompt: str = None
) -> dict:
    """Process message with Anthropic Claude models."""
    from app.services.ai.anthropic_service import AnthropicService

    try:
        service = AnthropicService()

        if message_type == "text":
            result = await service.generate_text(
                model=model_id,
                prompt=content,
                system_prompt=system_prompt
            )
        else:
            return {"success": False, "error": f"Message type {message_type} not yet implemented for Anthropic"}

        return {
            "success": result.success,
            "content": result.content if result.success else result.error,
            "error": result.error if not result.success else None,
            "mock": result.metadata.get("mock", False)
        }
    except Exception as e:
        logger.error(f"Anthropic processing error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def process_deepseek_message(
    message_type: str,
    content: any,
    model_id: str,
    caption: str = None,
    history_enabled: bool = False,
    system_prompt: str = None
) -> dict:
    """Process message with DeepSeek models."""
    from app.services.ai.deepseek_service import DeepSeekService

    try:
        service = DeepSeekService()

        # Map model names to API model IDs
        model_map = {
            "deepseek-chat": "deepseek-chat",
            "deepseek-r1": "deepseek-reasoner"
        }

        api_model = model_map.get(model_id, "deepseek-chat")

        if message_type == "text":
            result = await service.generate_text(
                model=api_model,
                prompt=content,
                system_prompt=system_prompt
            )
        else:
            return {"success": False, "error": f"Message type {message_type} not yet implemented for DeepSeek"}

        return {
            "success": result.success,
            "content": result.content if result.success else result.error,
            "error": result.error if not result.success else None,
            "tokens_used": result.tokens_used if result.success else 0,
            "model": api_model
        }
    except Exception as e:
        logger.error(f"DeepSeek processing error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def process_perplexity_message(
    message_type: str,
    content: any,
    model_id: str,
    caption: str = None,
    history_enabled: bool = False,
    system_prompt: str = None
) -> dict:
    """Process message with Perplexity models."""
    from app.services.ai.perplexity_service import PerplexityService

    try:
        service = PerplexityService()

        if message_type == "text":
            result = await service.generate_text(
                model=model_id,
                prompt=content,
                system_prompt=system_prompt
            )
        else:
            return {"success": False, "error": f"Message type {message_type} not yet implemented for Perplexity"}

        return {
            "success": result.success,
            "content": result.content if result.success else result.error,
            "error": result.error if not result.success else None,
            "mock": result.metadata.get("mock", False)
        }
    except Exception as e:
        logger.error(f"Perplexity processing error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
