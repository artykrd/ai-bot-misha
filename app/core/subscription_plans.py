"""
Subscription plans and token packages.

Single source of truth for subscription pricing/tokens/duration and shop plan IDs.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, Optional

from app.core.billing_config import TOKEN_PACKAGES, TokenPackage, format_token_amount


@dataclass(frozen=True)
class SubscriptionPlan:
    """Time-limited subscription plan tied to a token package."""

    plan_id: str
    subscription_type: str
    display_name: str
    package: TokenPackage

    @property
    def days(self) -> int:
        return self.package.days

    @property
    def tokens(self) -> int:
        return self.package.tokens

    @property
    def price(self) -> Decimal:
        return Decimal(str(self.package.price))


@dataclass(frozen=True)
class Tariff:
    """Generic tariff definition used by billing and subscription service."""

    subscription_type: str
    days: Optional[int]
    tokens: Optional[int]
    price: Decimal

    @property
    def is_unlimited(self) -> bool:
        return self.tokens is None or self.tokens < 0


@dataclass(frozen=True)
class EternalTokenPlan:
    """Eternal token purchase plan."""

    subscription_type: str
    tokens: int
    price: Decimal
    display_name: str


def _build_display_name(package: TokenPackage) -> str:
    day_label = "день" if package.days in (1, 21, 31) else "дней"
    return f"{package.days} {day_label} — {format_token_amount(package.tokens)} токенов"


SUBSCRIPTION_PLANS: Dict[str, SubscriptionPlan] = {
    "1": SubscriptionPlan(
        plan_id="1",
        subscription_type="7days",
        display_name=_build_display_name(TOKEN_PACKAGES["7days"]),
        package=TOKEN_PACKAGES["7days"],
    ),
    "2": SubscriptionPlan(
        plan_id="2",
        subscription_type="14days",
        display_name=_build_display_name(TOKEN_PACKAGES["14days"]),
        package=TOKEN_PACKAGES["14days"],
    ),
    "3": SubscriptionPlan(
        plan_id="3",
        subscription_type="21days",
        display_name=_build_display_name(TOKEN_PACKAGES["21days"]),
        package=TOKEN_PACKAGES["21days"],
    ),
    "6": SubscriptionPlan(
        plan_id="6",
        subscription_type="30days_1m",
        display_name=_build_display_name(TOKEN_PACKAGES["30days_1m"]),
        package=TOKEN_PACKAGES["30days_1m"],
    ),
    "21": SubscriptionPlan(
        plan_id="21",
        subscription_type="30days_5m",
        display_name=_build_display_name(TOKEN_PACKAGES["30days_5m"]),
        package=TOKEN_PACKAGES["30days_5m"],
    ),
}


UNLIMITED_PLAN = Tariff(
    subscription_type="unlimited_1day",
    days=1,
    tokens=None,
    price=Decimal("649.00"),
)


ETERNAL_PLANS: Dict[str, EternalTokenPlan] = {
    "eternal_150k": EternalTokenPlan(
        subscription_type="eternal_150k",
        tokens=150_000,
        price=Decimal("149.00"),
        display_name="150,000 токенов",
    ),
    "eternal_250k": EternalTokenPlan(
        subscription_type="eternal_250k",
        tokens=250_000,
        price=Decimal("279.00"),
        display_name="250,000 токенов",
    ),
    "eternal_500k": EternalTokenPlan(
        subscription_type="eternal_500k",
        tokens=500_000,
        price=Decimal("519.00"),
        display_name="500,000 токенов",
    ),
    "eternal_1m": EternalTokenPlan(
        subscription_type="eternal_1m",
        tokens=1_000_000,
        price=Decimal("999.00"),
        display_name="1,000,000 токенов",
    ),
}


# Subscription types that represent actual paid purchases.
# Used for statistics filtering to exclude bonuses, promos, gifts, etc.
PAID_SUBSCRIPTION_TYPES = [
    # Eternal token purchases (payment_service default)
    "eternal_purchase",
    # Time-limited subscriptions (payment_service default)
    "premium_subscription",
    # Unlimited daily plan
    "unlimited_1day",
]


def list_subscription_plans() -> Iterable[SubscriptionPlan]:
    return SUBSCRIPTION_PLANS.values()


def get_subscription_plan(plan_id: str) -> Optional[SubscriptionPlan]:
    return SUBSCRIPTION_PLANS.get(plan_id)


def get_subscription_tariff(subscription_type: str) -> Optional[Tariff]:
    if subscription_type in ETERNAL_PLANS:
        plan = ETERNAL_PLANS[subscription_type]
        return Tariff(
            subscription_type=plan.subscription_type,
            days=None,
            tokens=plan.tokens,
            price=plan.price,
        )

    if subscription_type == UNLIMITED_PLAN.subscription_type:
        return UNLIMITED_PLAN

    package = TOKEN_PACKAGES.get(subscription_type)
    if not package:
        return None
    return Tariff(
        subscription_type=subscription_type,
        days=package.days,
        tokens=package.tokens,
        price=Decimal(str(package.price)),
    )


def get_all_tariffs() -> Dict[str, Tariff]:
    tariffs = {key: get_subscription_tariff(key) for key in TOKEN_PACKAGES.keys()}
    tariffs[UNLIMITED_PLAN.subscription_type] = UNLIMITED_PLAN
    for key, plan in ETERNAL_PLANS.items():
        tariffs[key] = Tariff(
            subscription_type=plan.subscription_type,
            days=None,
            tokens=plan.tokens,
            price=plan.price,
        )
    return {k: v for k, v in tariffs.items() if v is not None}
