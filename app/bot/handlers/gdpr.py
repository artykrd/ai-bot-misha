"""
GDPR / 152-ФЗ user-facing commands:
  /export_me   — download a JSON snapshot of personal data we hold
  /delete_me   — start the account-deletion flow (with confirmation)
"""
from io import BytesIO

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.core.logger import get_logger
from app.database.database import async_session_maker
from app.database.models.user import User
from app.services.user.gdpr_service import GDPRService

logger = get_logger(__name__)

router = Router(name="gdpr")


class GDPRStates(StatesGroup):
    waiting_for_delete_confirmation = State()


@router.message(Command("export_me"))
async def cmd_export_me(message: Message, user: User):
    """Send the requesting user a JSON file with all data we hold about them."""
    async with async_session_maker() as session:
        service = GDPRService(session)
        payload = await service.export_user_data_json(user.telegram_id)

    if not payload:
        await message.answer("Не удалось собрать данные. Попробуйте позже.")
        return

    file = BufferedInputFile(payload.encode("utf-8"), filename="my_data.json")
    await message.answer_document(
        file,
        caption=(
            "📦 Это все данные, которые мы храним о вашем аккаунте.\n\n"
            "Если хотите удалить аккаунт и все связанные данные — отправьте /delete_me."
        ),
    )

    logger.info(
        "gdpr_data_exported",
        user_id=user.id,
        telegram_id=user.telegram_id,
    )


def _delete_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить удаление", callback_data="gdpr:delete:confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="gdpr:delete:cancel"),
        ],
    ])


@router.message(Command("delete_me"))
async def cmd_delete_me(message: Message, user: User, state: FSMContext):
    """Ask the user to confirm full-account deletion."""
    await state.set_state(GDPRStates.waiting_for_delete_confirmation)
    await message.answer(
        "⚠️ <b>Удаление аккаунта</b>\n\n"
        "Будут безвозвратно удалены:\n"
        "• профиль и история активности\n"
        "• подписки и неиспользованные токены\n"
        "• диалоги с моделями и AI-запросы\n"
        "• очередь видео-задач\n"
        "• рефералы\n\n"
        "Платежи (для целей бухгалтерского учёта) сохраняются в обезличенном виде "
        "согласно требованиям 54-ФЗ.\n\n"
        "Эту операцию нельзя отменить. Подтвердите ваш выбор:",
        parse_mode="HTML",
        reply_markup=_delete_confirmation_keyboard(),
    )


@router.callback_query(F.data == "gdpr:delete:cancel")
async def cb_delete_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Удаление отменено.")
    await callback.answer()


@router.callback_query(F.data == "gdpr:delete:confirm")
async def cb_delete_confirm(callback: CallbackQuery, user: User, state: FSMContext):
    async with async_session_maker() as session:
        service = GDPRService(session)
        try:
            deleted = await service.delete_user(user.telegram_id)
        except Exception:
            await callback.message.edit_text(
                "Не удалось завершить удаление. Свяжитесь с поддержкой."
            )
            await callback.answer()
            return

    await state.clear()

    if not deleted:
        await callback.message.edit_text("Аккаунт не найден — удалять нечего.")
        await callback.answer()
        return

    logger.info(
        "gdpr_delete_completed",
        telegram_id=user.telegram_id,
    )

    await callback.message.edit_text(
        "✅ Ваши данные удалены.\n\nЕсли хотите снова пользоваться ботом — отправьте /start."
    )
    await callback.answer()
