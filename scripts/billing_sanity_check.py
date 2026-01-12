#!/usr/bin/env python3
"""
Sanity checks for billing configuration.
"""
from __future__ import annotations

from pathlib import Path
import re

from app.core.billing_config import (
    TOKEN_PRICE_RUB,
    TOKEN_PACKAGES,
    IMAGE_MODELS,
    VIDEO_MODELS,
    format_token_amount,
)
from app.core.subscription_plans import list_subscription_plans, UNLIMITED_PLAN, ETERNAL_PLANS


OLD_VALUE_PATTERNS = [
    r"(?<!\d)98(\.00)?(?!\d|\s*000)",
    r"(?<!\d)196(\.00)?(?!\d)",
    r"(?<!\d)289(\.00)?(?!\d)",
    r"(?<!\d)597(\.00)?(?!\d)",
    r"(?<!\d)2790(\.00)?(?!\d)",
    r"0\.000653",
    r"(?<!\d)3000(?!\d)",
]


def print_subscription_plans() -> None:
    print("== Subscription plans ==")
    for plan in list_subscription_plans():
        print(
            f"{plan.plan_id}: {plan.display_name} | "
            f"{format_token_amount(plan.tokens)} tokens | "
            f"{plan.price} RUB | {plan.days} days"
        )
    print(
        f"unlimited: {UNLIMITED_PLAN.subscription_type} | "
        f"{UNLIMITED_PLAN.price} RUB | {UNLIMITED_PLAN.days} days"
    )
    print("== Eternal plans ==")
    for plan in ETERNAL_PLANS.values():
        print(
            f"{plan.subscription_type}: {format_token_amount(plan.tokens)} tokens | "
            f"{plan.price} RUB"
        )


def print_token_price() -> None:
    print("== Token price ==")
    print(f"1 token = {TOKEN_PRICE_RUB} RUB")


def print_media_costs() -> None:
    print("== Image model costs ==")
    for model_id, billing in IMAGE_MODELS.items():
        print(
            f"{model_id}: {format_token_amount(billing.tokens_per_generation)} tokens"
        )
    print("== Video model costs ==")
    for model_id, billing in VIDEO_MODELS.items():
        print(
            f"{model_id}: {format_token_amount(billing.tokens_per_generation)} tokens"
        )


def scan_for_old_values(root: Path) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    self_path = Path(__file__).resolve()
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part.startswith(".") for part in path.parts):
            continue
        if path.suffix not in {".py", ".sql"}:
            continue
        if path.resolve() == self_path:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in OLD_VALUE_PATTERNS:
            if re.search(pattern, content):
                matches.setdefault(pattern, []).append(str(path))
    return matches


def main() -> None:
    print_subscription_plans()
    print_token_price()
    print_media_costs()
    print("== Scan for old values ==")
    matches = scan_for_old_values(Path("."))
    if not matches:
        print("No old values found.")
        return
    for pattern, files in matches.items():
        print(f"Found '{pattern}' in {len(files)} files:")
        for file_path in sorted(files):
            print(f"  - {file_path}")


if __name__ == "__main__":
    main()
