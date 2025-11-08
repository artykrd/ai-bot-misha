"""
Script to check which buttons have handlers by analyzing the code.

Usage:
    python scripts/check_buttons.py
"""
import re
from pathlib import Path


# All callback patterns from bot_structure.md
ALL_BUTTONS = {
    # Main menu
    "bot.back": "Return to main menu",
    "bot.start_chatgpt_dialog_324#home": "Start ChatGPT from home",
    "bot.nano": "Nano Banana",
    "bot.llm_models": "Show all AI models",
    "bot.dialogs_chatgpt": "Show dialogs list",
    "bot.create_photo": "Photo creation menu",
    "bot.create_video": "Video creation menu",
    "bot.pi": "Photo tools menu",
    "bot.audio_instruments": "Audio tools menu",
    "bot.profile": "User profile",
    "bot#shop": "Subscription shop",
    "bot.refferal_program": "Referral program",

    # Model selection (all 12+ models)
    "bot.start_chatgpt_dialog_324": "GPT 4.1 Mini",
    "bot.start_chatgpt_dialog_325": "GPT 4o",
    "bot.start_chatgpt_dialog_326": "O3 Mini",
    "bot.start_chatgpt_dialog_327": "Deepseek Chat",
    "bot.start_chatgpt_dialog_328": "Deepseek R1",
    "bot.start_chatgpt_dialog_329": "Gemini Flash 2.0",
    "bot.start_chatgpt_dialog_330": "Gemini Pro 2.5",
    "bot.start_chatgpt_dialog_331": "Sonar с поиском",
    "bot.start_chatgpt_dialog_332": "Sonar Pro",
    "bot.start_chatgpt_dialog_333": "Claude 3.7",
    "bot.start_chatgpt_dialog_334": "Claude 3.5",
    "bot.start_chatgpt_dialog_335": "Анализ текста (dialog)",
    "bot.start_chatgpt_dialog_336": "Генератор промптов (dialog)",
    "bot.start_chatgpt_dialog_337": "GPT 5 Mini",

    # Dialog state toggles (tested with one model)
    "bot.start_chatgpt_dialog_324#sh_0": "Toggle history off",
    "bot.start_chatgpt_dialog_324#sh_1": "Toggle history on",
    "bot.start_chatgpt_dialog_324#bi_0": "Toggle costs off",
    "bot.start_chatgpt_dialog_324#bi_1": "Toggle costs on",

    # Dialogs
    "bot.create_chatgpt_dialog": "Create new dialog",

    # Photo creation
    "bot.gpt_image": "GPT Image",
    "bot.midjourney": "Midjourney",
    "bot_stable_diffusion": "Stable Diffusion",
    "bot.recraft": "Recraft",
    "bot.faceswap": "Face swap",

    # Nano Banana
    "bot.nb.prms:ratio": "Nano format selection menu",
    "bot.nb.prms.chs:ratio|1:1": "Nano format 1:1",
    "bot.nb.prms.chs:ratio|2:3": "Nano format 2:3",
    "bot.nb.prms.chs:ratio|3:2": "Nano format 3:2",
    "bot.nb.prms.chs:ratio|16:9": "Nano format 16:9",
    "bot.nb.prms.chs:ratio|9:16": "Nano format 9:16",
    "bot.nb.prms.chs:ratio|auto": "Nano format auto",

    # Video creation
    "bot.sora": "Sora 2",
    "bot.veo": "Veo 3.1",
    "bot.mjvideo": "Midjourney Video",
    "bot.hailuo": "Hailuo",
    "bot.luma": "Luma Dream Machine",
    "bot.kling": "Kling",
    "bot.kling_effects": "Kling Effects",

    # Photo tools
    "bot.pi_upscale": "Upscale photo",
    "bot.pi_repb": "Replace background",
    "bot.pi_remb": "Remove background",
    "bot.pi_vect": "Vectorize photo",

    # Audio tools
    "bot.suno": "Suno music creation",
    "bot.whisper": "Whisper transcription",
    "bot.whisper_tts": "Text to speech",

    # Subscription
    "bot#shop_tokens": "Eternal tokens shop",
    "shop_select_tariff_1": "7 days tariff",
    "shop_select_tariff_2": "14 days tariff",
    "shop_select_tariff_3": "21 days tariff",
    "shop_select_tariff_6": "30 days 1M tariff",
    "shop_select_tariff_21": "30 days 5M tariff",
    "shop_select_tariff_22": "Unlimited 1 day",
    "activate_promocode": "Activate promocode",

    # Eternal tokens
    "buy:eternal_150k": "Buy 150k eternal",
    "buy:eternal_250k": "Buy 250k eternal",
    "buy:eternal_500k": "Buy 500k eternal",
    "buy:eternal_1m": "Buy 1M eternal",

    # Profile
    "bot.change_language": "Change language",
    "bot.profile_payments": "Payment history",
    "page#faq": "FAQ/Help",

    # Referral
    "bot.refferal_withdraw": "Withdraw referral earnings",

    # Legacy
    "main_menu": "Main menu (legacy)",
}


def find_callback_handlers(handlers_dir: Path):
    """Find all callback handlers in the handlers directory."""

    handlers_found = {}

    for handler_file in handlers_dir.glob("*.py"):
        if handler_file.name.startswith("__"):
            continue

        content = handler_file.read_text()

        # Find all @router.callback_query decorators
        # Patterns to match:
        # @router.callback_query(F.data == "bot.back")
        # @router.callback_query(F.data.in_(["bot.sora", "bot.veo"]))
        # @router.callback_query(F.data.startswith("bot.start_chatgpt_dialog_"))

        # Simple pattern match
        single_pattern = r'@router\.callback_query\(F\.data\s*==\s*["\']([^"\']+)["\']\)'
        for match in re.finditer(single_pattern, content):
            callback_data = match.group(1)
            if callback_data not in handlers_found:
                handlers_found[callback_data] = []
            handlers_found[callback_data].append(str(handler_file.name))

        # Pattern for F.data.in_([...])
        in_pattern = r'@router\.callback_query\(F\.data\.in_\(\[([^\]]+)\]\)\)'
        for match in re.finditer(in_pattern, content):
            callbacks_str = match.group(1)
            # Extract each callback from the list
            callback_list = re.findall(r'["\']([^"\']+)["\']', callbacks_str)
            for callback_data in callback_list:
                if callback_data not in handlers_found:
                    handlers_found[callback_data] = []
                handlers_found[callback_data].append(str(handler_file.name))

        # Pattern for F.data.startswith("...")
        startswith_pattern = r'@router\.callback_query\(F\.data\.startswith\(["\']([^"\']+)["\']\)\)'
        for match in re.finditer(startswith_pattern, content):
            prefix = match.group(1)
            # Mark all buttons that start with this prefix as handled
            for callback_data in ALL_BUTTONS.keys():
                if callback_data.startswith(prefix):
                    if callback_data not in handlers_found:
                        handlers_found[callback_data] = []
                    handlers_found[callback_data].append(f"{handler_file.name} (startswith)")

    return handlers_found


def main():
    """Main function."""

    print("=" * 80)
    print("BOT BUTTON COVERAGE REPORT")
    print("=" * 80)
    print()

    # Find all handlers
    handlers_dir = Path(__file__).parent.parent / "app" / "bot" / "handlers"
    handlers_found = find_callback_handlers(handlers_dir)

    # Check coverage
    active_buttons = []
    inactive_buttons = []

    for callback_data, description in ALL_BUTTONS.items():
        if callback_data in handlers_found:
            active_buttons.append({
                "callback": callback_data,
                "description": description,
                "handlers": handlers_found[callback_data]
            })
        else:
            inactive_buttons.append({
                "callback": callback_data,
                "description": description
            })

    # Print summary
    total = len(ALL_BUTTONS)
    active_count = len(active_buttons)
    inactive_count = len(inactive_buttons)
    coverage = (active_count / total) * 100

    print("SUMMARY")
    print("-" * 80)
    print(f"Total buttons defined:     {total}")
    print(f"✅ Buttons with handlers:  {active_count} ({coverage:.1f}%)")
    print(f"❌ Buttons without handlers: {inactive_count} ({100-coverage:.1f}%)")
    print()

    # Print active buttons
    if active_buttons:
        print("=" * 80)
        print(f"ACTIVE BUTTONS ({active_count})")
        print("=" * 80)
        for btn in sorted(active_buttons, key=lambda x: x["callback"]):
            print(f"✅ {btn['callback']}")
            print(f"   → {btn['description']}")
            print(f"   → Handlers: {', '.join(btn['handlers'])}")
            print()

    # Print inactive buttons
    if inactive_buttons:
        print("=" * 80)
        print(f"INACTIVE BUTTONS ({inactive_count})")
        print("=" * 80)
        for btn in sorted(inactive_buttons, key=lambda x: x["callback"]):
            print(f"❌ {btn['callback']}")
            print(f"   → {btn['description']}")
            print()

        print("=" * 80)
        print("ACTION ITEMS")
        print("=" * 80)
        print()
        print("The following buttons need handlers:")
        print()

        # Group by category
        categories = {}
        for btn in inactive_buttons:
            callback = btn['callback']
            if callback.startswith("bot.start_chatgpt_dialog_"):
                category = "Dialog start buttons"
            elif callback.startswith("bot."):
                category = "Navigation buttons"
            elif callback.startswith("shop_") or callback.startswith("buy:"):
                category = "Payment buttons"
            else:
                category = "Other buttons"

            if category not in categories:
                categories[category] = []
            categories[category].append(btn)

        for category, buttons in categories.items():
            print(f"{category}:")
            for btn in buttons:
                print(f"  • {btn['callback']}: {btn['description']}")
            print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    return 0 if inactive_count == 0 else 1


if __name__ == "__main__":
    exit(main())
