"""
Script to test all bot buttons and find inactive ones.

Usage:
    python scripts/test_buttons.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiogram import Dispatcher
from aiogram.types import CallbackQuery, User as TgUser, Chat, Message
from unittest.mock import AsyncMock, MagicMock

from app.bot.bot_instance import bot
from app.database.models.user import User


# All callback patterns from bot_structure.md
ALL_BUTTONS = [
    # Main menu
    "bot.back",
    "bot.start_chatgpt_dialog_324#home",
    "bot.nano",
    "bot.llm_models",
    "bot.dialogs_chatgpt",
    "bot.create_photo",
    "bot.create_video",
    "bot.pi",
    "bot.audio_instruments",
    "bot.profile",
    "bot#shop",
    "bot.refferal_program",

    # Model selection (all 12 models)
    "bot.start_chatgpt_dialog_324",
    "bot.start_chatgpt_dialog_325",
    "bot.start_chatgpt_dialog_326",
    "bot.start_chatgpt_dialog_327",
    "bot.start_chatgpt_dialog_328",
    "bot.start_chatgpt_dialog_329",
    "bot.start_chatgpt_dialog_330",
    "bot.start_chatgpt_dialog_331",
    "bot.start_chatgpt_dialog_332",
    "bot.start_chatgpt_dialog_333",
    "bot.start_chatgpt_dialog_334",
    "bot.start_chatgpt_dialog_335",
    "bot.start_chatgpt_dialog_336",
    "bot.start_chatgpt_dialog_337",

    # Dialog state toggles
    "bot.start_chatgpt_dialog_324#sh_0",
    "bot.start_chatgpt_dialog_324#sh_1",
    "bot.start_chatgpt_dialog_324#bi_0",
    "bot.start_chatgpt_dialog_324#bi_1",

    # Dialogs
    "bot.create_chatgpt_dialog",

    # Photo creation
    "bot.gpt_image",
    "bot.midjourney",
    "bot_stable_diffusion",
    "bot.recraft",
    "bot.faceswap",

    # Nano Banana
    "bot.nb.prms:ratio",
    "bot.nb.prms.chs:ratio|1:1",
    "bot.nb.prms.chs:ratio|2:3",
    "bot.nb.prms.chs:ratio|3:2",
    "bot.nb.prms.chs:ratio|16:9",
    "bot.nb.prms.chs:ratio|9:16",
    "bot.nb.prms.chs:ratio|auto",

    # Video creation
    "bot.sora",
    "bot.veo",
    "bot.mjvideo",
    "bot.hailuo",
    "bot.luma",
    "bot.kling",
    "bot.kling_effects",

    # Photo tools
    "bot.pi_upscale",
    "bot.pi_repb",
    "bot.pi_remb",
    "bot.pi_vect",

    # Audio tools
    "bot.suno",
    "bot.whisper",
    "bot.whisper_tts",

    # Subscription
    "bot#shop_tokens",
    "shop_select_tariff_1",
    "shop_select_tariff_2",
    "shop_select_tariff_3",
    "shop_select_tariff_6",
    "shop_select_tariff_21",
    "shop_select_tariff_22",
    "activate_promocode",

    # Eternal tokens
    "buy:eternal_150k",
    "buy:eternal_250k",
    "buy:eternal_500k",
    "buy:eternal_1m",

    # Profile
    "bot.change_language",
    "bot.profile_payments",
    "page#faq",

    # Referral
    "bot.refferal_withdraw",

    # Legacy/fallback
    "main_menu",
]


async def create_mock_callback(callback_data: str) -> CallbackQuery:
    """Create a mock CallbackQuery for testing."""

    # Create mock user
    tg_user = TgUser(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser"
    )

    # Create mock chat
    chat = Chat(
        id=123456789,
        type="private"
    )

    # Create mock message
    message = MagicMock(spec=Message)
    message.chat = chat
    message.from_user = tg_user
    message.message_id = 1
    message.edit_text = AsyncMock()
    message.answer = AsyncMock()
    message.delete = AsyncMock()

    # Create mock callback query
    callback = MagicMock(spec=CallbackQuery)
    callback.id = "test_callback_id"
    callback.from_user = tg_user
    callback.message = message
    callback.data = callback_data
    callback.answer = AsyncMock()

    return callback


async def create_mock_user() -> User:
    """Create a mock User for testing."""
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    user.id = 1
    return user


async def test_button(dp: Dispatcher, callback_data: str) -> dict:
    """Test a single button callback."""

    # Create mock callback
    callback = await create_mock_callback(callback_data)
    user = await create_mock_user()

    # Add user to callback context
    callback.bot = bot

    try:
        # Try to find handler
        handlers_found = False

        for observer in dp.callback_query.observers.values():
            for handler in observer:
                # Check if handler matches this callback
                filters_check = await handler.check(callback)
                if filters_check:
                    handlers_found = True
                    break
            if handlers_found:
                break

        if handlers_found:
            return {
                "callback_data": callback_data,
                "status": "✅ ACTIVE",
                "has_handler": True
            }
        else:
            return {
                "callback_data": callback_data,
                "status": "❌ NO HANDLER",
                "has_handler": False
            }

    except Exception as e:
        return {
            "callback_data": callback_data,
            "status": f"⚠️ ERROR: {str(e)}",
            "has_handler": False,
            "error": str(e)
        }


async def test_all_buttons():
    """Test all buttons and generate report."""

    print("=" * 80)
    print("BOT BUTTON TEST REPORT")
    print("=" * 80)
    print()

    # Setup bot
    from app.bot.bot_instance import setup_bot
    dp = await setup_bot()

    print(f"Testing {len(ALL_BUTTONS)} button callbacks...")
    print()

    results = []

    for callback_data in ALL_BUTTONS:
        result = await test_button(dp, callback_data)
        results.append(result)

    # Categorize results
    active_buttons = [r for r in results if r["has_handler"]]
    inactive_buttons = [r for r in results if not r["has_handler"]]

    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total buttons tested: {len(ALL_BUTTONS)}")
    print(f"✅ Active (with handlers): {len(active_buttons)}")
    print(f"❌ Inactive (no handlers): {len(inactive_buttons)}")
    print()

    # Print active buttons
    if active_buttons:
        print("=" * 80)
        print("ACTIVE BUTTONS (✅)")
        print("=" * 80)
        for result in active_buttons:
            print(f"  {result['status']} {result['callback_data']}")
        print()

    # Print inactive buttons
    if inactive_buttons:
        print("=" * 80)
        print("INACTIVE BUTTONS (❌)")
        print("=" * 80)
        for result in inactive_buttons:
            print(f"  {result['status']} {result['callback_data']}")
            if "error" in result:
                print(f"      Error: {result['error']}")
        print()

    # Print detailed recommendations
    if inactive_buttons:
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print()
        print("The following buttons need handlers:")
        print()

        for result in inactive_buttons:
            callback_data = result['callback_data']
            print(f"• {callback_data}")

            # Suggest where to add handler
            if callback_data.startswith("bot.start_chatgpt_dialog_"):
                print(f"  → Should be handled in: app/bot/handlers/navigation.py")
                print(f"  → Handler: start_dialog()")
            elif callback_data.startswith("bot."):
                print(f"  → Should be handled in: app/bot/handlers/navigation.py")
            elif callback_data.startswith("shop_"):
                print(f"  → Should be handled in: app/bot/handlers/navigation.py")
                print(f"  → Handler: tariff_selected()")
            elif callback_data.startswith("buy:"):
                print(f"  → Should be handled in: app/bot/handlers/navigation.py")
            elif callback_data.startswith("page#"):
                print(f"  → Should be handled in: app/bot/handlers/navigation.py")
            else:
                print(f"  → Needs new handler")
            print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    # Return exit code
    return 0 if len(inactive_buttons) == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_all_buttons())
    sys.exit(exit_code)
