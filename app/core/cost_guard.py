"""
Cost Guard System - защита от чрезмерных расходов на дорогие AI модели.

Функционал:
- Подтверждение перед дорогими запросами
- Rate limiting на пользователя и глобально
- Защита от двойных кликов
- Кэширование запросов
- Логирование реальной стоимости
"""
import time
import hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.logger import get_logger
from app.core.redis_client import redis_client
from app.core.billing_config import get_video_model_billing

logger = get_logger(__name__)


veo_billing = get_video_model_billing("veo-3.1-fast")
sora_billing = get_video_model_billing("sora2")
luma_billing = get_video_model_billing("luma")
hailuo_billing = get_video_model_billing("hailuo")
kling_billing = get_video_model_billing("kling-video")

# Стоимость моделей в токенах (единый источник правды)
MODEL_COSTS = {
    "veo-3.1": {
        "base_cost": veo_billing.tokens_per_generation,
        "default_duration": 8,
        "requires_confirmation": True,
        "description": "Veo 3.1 Fast"
    },
    "sora-2": {
        "base_cost": sora_billing.tokens_per_generation,
        "default_duration": 10,
        "requires_confirmation": True,
        "description": "Sora 2"
    },
    "luma": {
        "base_cost": luma_billing.tokens_per_generation,
        "requires_confirmation": False,
        "description": "Luma Dream Machine"
    },
    "hailuo": {
        "base_cost": hailuo_billing.tokens_per_generation,
        "requires_confirmation": False,
        "description": "Hailuo MiniMax"
    },
    "kling": {
        "base_cost": kling_billing.tokens_per_generation,
        "requires_confirmation": False,
        "description": "Kling AI"
    }
}


# Rate limits (запросы в минуту)
RATE_LIMITS = {
    "veo-3.1": {
        "per_user": 2,  # 2 запроса в час на пользователя
        "global": 10,    # 10 запросов в час глобально
        "window": 3600   # 1 час
    },
    "sora-2": {
        "per_user": 5,
        "global": 20,
        "window": 3600
    },
    "default": {
        "per_user": 10,
        "global": 50,
        "window": 3600
    }
}


@dataclass
class CostEstimate:
    """Оценка стоимости запроса."""
    model: str
    estimated_tokens: int
    estimated_cost_usd: float
    duration_seconds: Optional[int] = None
    requires_confirmation: bool = False
    warning_message: Optional[str] = None


class CostGuard:
    """
    Система защиты от чрезмерных расходов.
    """

    def __init__(self):
        self.redis = redis_client
        # Локальный кэш для защиты от двойных кликов (в памяти)
        self._processing_requests: Dict[str, float] = {}
        # Кэш запросов по hash промпта
        self._request_cache: Dict[str, Dict[str, Any]] = {}

    def estimate_cost(
        self,
        model: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> CostEstimate:
        """
        Оценить стоимость запроса.

        Args:
            model: Название модели (veo-3.1, sora-2, etc.)
            duration: Длительность видео в секундах
            **kwargs: Дополнительные параметры

        Returns:
            CostEstimate с детальной информацией
        """
        model_key = model.lower()
        config = MODEL_COSTS.get(model_key, {})

        if not config:
            # Неизвестная модель, используем базовую оценку
            return CostEstimate(
                model=model,
                estimated_tokens=1000,
                estimated_cost_usd=0.01,
                requires_confirmation=False
            )

        # Для видео-моделей рассчитываем по длительности
        if "base_cost_per_second" in config:
            # Применяем эконом-режим: используем минимальную длительность если не указано
            if duration is None:
                duration = config.get("default_duration", config.get("min_duration", 4))

            # Валидация длительности
            min_dur = config.get("min_duration", 1)
            max_dur = config.get("max_duration", 60)
            if duration < min_dur:
                duration = min_dur
            if duration > max_dur:
                duration = max_dur

            cost_per_sec = config["base_cost_per_second"]
            estimated_tokens = cost_per_sec * duration

            warning = None
            if duration > config.get("default_duration", 4):
                warning = (
                    f"⚠️ Вы выбрали {duration} секунд. "
                    f"Рекомендуем {config.get('default_duration', 4)} сек для экономии."
                )
        else:
            # Фиксированная стоимость
            estimated_tokens = config.get("base_cost", 1000)
            duration = duration or config.get("default_duration")
            warning = None

        # Конвертируем в USD (условно $0.01 за 1000 токенов)
        estimated_cost_usd = (estimated_tokens / 1000) * 0.01

        return CostEstimate(
            model=model,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=estimated_cost_usd,
            duration_seconds=duration,
            requires_confirmation=config.get("requires_confirmation", False),
            warning_message=warning
        )

    async def check_rate_limit(
        self,
        user_id: int,
        model: str
    ) -> tuple[bool, Optional[str]]:
        """
        Проверить rate limit для пользователя и модели.

        Returns:
            (allowed, error_message)
        """
        model_key = model.lower()
        limits = RATE_LIMITS.get(model_key, RATE_LIMITS["default"])

        window = limits["window"]
        now = int(time.time())

        # Проверяем per-user limit
        user_key = f"cost_guard:rate:{model_key}:user:{user_id}"

        if self.redis:
            try:
                # Используем Redis для rate limiting
                count = await self.redis.increment(user_key)
                if count == 1:
                    await self.redis.expire(user_key, window)

                ttl = await self.redis.get_ttl(user_key)

                if count > limits["per_user"]:
                    hours = ttl // 3600
                    minutes = (ttl % 3600) // 60
                    time_str = f"{hours}ч {minutes}мин" if hours > 0 else f"{minutes}мин"

                    return False, (
                        f"⛔️ Превышен лимит запросов для {model}!\n\n"
                        f"Лимит: {limits['per_user']} запросов в час\n"
                        f"Попробуйте через: {time_str}"
                    )

                # Проверяем global limit
                global_key = f"cost_guard:rate:{model_key}:global"
                global_count = await self.redis.increment(global_key)
                if global_count == 1:
                    await self.redis.expire(global_key, window)

                if global_count > limits["global"]:
                    return False, (
                        f"⛔️ Превышен глобальный лимит для {model}!\n\n"
                        f"Сервис временно перегружен. Попробуйте позже."
                    )

                return True, None

            except Exception as e:
                logger.error("rate_limit_check_failed", error=str(e))
                # Если Redis недоступен, разрешаем запрос
                return True, None
        else:
            # Без Redis используем простой in-memory счётчик (не персистентный)
            return True, None

    def check_duplicate_request(
        self,
        user_id: int,
        request_id: str,
        timeout: int = 30
    ) -> bool:
        """
        Проверить, не обрабатывается ли уже этот запрос (защита от двойного клика).

        Args:
            user_id: ID пользователя
            request_id: Уникальный ID запроса (обычно callback_query.id)
            timeout: Таймаут защиты в секундах

        Returns:
            True если запрос уже обрабатывается
        """
        key = f"{user_id}:{request_id}"
        now = time.time()

        # Очистка старых записей
        expired_keys = [k for k, t in self._processing_requests.items() if now - t > timeout]
        for k in expired_keys:
            del self._processing_requests[k]

        if key in self._processing_requests:
            logger.warning(
                "duplicate_request_detected",
                user_id=user_id,
                request_id=request_id
            )
            return True

        # Помечаем как обрабатываемый
        self._processing_requests[key] = now
        return False

    def release_request(self, user_id: int, request_id: str):
        """Освободить запрос после обработки."""
        key = f"{user_id}:{request_id}"
        if key in self._processing_requests:
            del self._processing_requests[key]

    def generate_request_hash(self, user_id: int, model: str, prompt: str, **params) -> str:
        """
        Сгенерировать хеш запроса для дедупликации.

        Args:
            user_id: ID пользователя
            model: Модель
            prompt: Промпт
            **params: Дополнительные параметры (duration, aspect_ratio, etc.)

        Returns:
            SHA256 хеш запроса
        """
        # Создаём строку из параметров
        params_str = "|".join([
            str(user_id),
            model,
            prompt,
            "|".join(f"{k}={v}" for k, v in sorted(params.items()))
        ])
        return hashlib.sha256(params_str.encode()).hexdigest()

    async def check_cached_result(
        self,
        request_hash: str,
        max_age: int = 3600
    ) -> Optional[Dict[str, Any]]:
        """
        Проверить, есть ли закэшированный результат для этого запроса.

        Args:
            request_hash: Хеш запроса
            max_age: Максимальный возраст кэша в секундах

        Returns:
            Кэшированный результат или None
        """
        if self.redis:
            try:
                key = f"cost_guard:cache:{request_hash}"
                cached = await self.redis.get(key)
                if cached:
                    import json
                    return json.loads(cached)
            except Exception as e:
                logger.error("cache_check_failed", error=str(e))

        return None

    async def cache_result(
        self,
        request_hash: str,
        result: Dict[str, Any],
        ttl: int = 3600
    ):
        """
        Закэшировать результат запроса.

        Args:
            request_hash: Хеш запроса
            result: Результат для кэширования
            ttl: Время жизни кэша в секундах
        """
        if self.redis:
            try:
                import json
                key = f"cost_guard:cache:{request_hash}"
                await self.redis.set(key, json.dumps(result), ex=ttl)
            except Exception as e:
                logger.error("cache_save_failed", error=str(e))

    async def log_generation(
        self,
        user_id: int,
        model: str,
        prompt: str,
        estimated_tokens: int,
        actual_tokens: int,
        estimated_cost_usd: float,
        actual_cost_usd: float,
        duration_seconds: Optional[int],
        status: str,
        error: Optional[str] = None,
        **metadata
    ):
        """
        Логировать генерацию для аналитики.

        Args:
            user_id: ID пользователя
            model: Модель
            prompt: Промпт (первые 200 символов)
            estimated_tokens: Оценка токенов
            actual_tokens: Фактические токены
            estimated_cost_usd: Оценка стоимости
            actual_cost_usd: Фактическая стоимость
            duration_seconds: Длительность (для видео)
            status: success/error/cancelled
            error: Сообщение об ошибке
            **metadata: Дополнительные данные
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "model": model,
            "prompt": prompt[:200],
            "estimated_tokens": estimated_tokens,
            "actual_tokens": actual_tokens,
            "estimated_cost_usd": round(estimated_cost_usd, 4),
            "actual_cost_usd": round(actual_cost_usd, 4),
            "cost_difference": round(actual_cost_usd - estimated_cost_usd, 4),
            "duration_seconds": duration_seconds,
            "status": status,
            "error": error,
            **metadata
        }

        logger.info("generation_logged", **log_data)

        # Также можем сохранить в БД для детальной аналитики (TODO)
        # await save_to_analytics_db(log_data)


# Глобальный инстанс
cost_guard = CostGuard()
