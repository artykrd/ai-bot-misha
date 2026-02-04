"""
Kling AI Video Effects service.

Supports 199 video effects including single-image and dual-image effects.
"""
import time
import asyncio
import base64
import jwt
from typing import Optional, Callable, Awaitable, List, Dict
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


# Effect categories for user-friendly selection
EFFECT_CATEGORIES: Dict[str, Dict] = {
    "popular": {
        "name": "⭐ Популярные",
        "effects": [
            ("hug_pro", "🤗 Объятия (2 фото)", True),
            ("kiss_pro", "💋 Поцелуй (2 фото)", True),
            ("heart_gesture_pro", "💕 Сердечко (2 фото)", True),
            ("bullet_time", "🎬 Bullet Time"),
            ("anime_figure", "🎌 Аниме фигурка"),
            ("japanese_anime_1", "🇯🇵 Японское аниме"),
            ("3d_cartoon_1_pro", "🎨 3D мультфильм"),
            ("glamour_photo_shoot", "📸 Гламурная фотосессия"),
        ]
    },
    "dance": {
        "name": "💃 Танцы",
        "effects": [
            ("heart_gesture_dance", "💕 Танец с сердечком"),
            ("poping", "🕺 Поппинг"),
            ("motorcycle_dance", "🏍️ Мотоциклетный танец"),
            ("subject_3_dance", "🎵 Subject 3 Dance"),
            ("ghost_step_dance", "👻 Ghost Step"),
            ("drunk_dance", "🍺 Пьяный танец"),
            ("bouncy_dance", "🦘 Прыгучий танец"),
            ("jazz_jazz", "🎷 Джаз"),
            ("swing_swing", "🎶 Свинг"),
            ("smooth_sailing_dance", "⛵ Плавный танец"),
        ]
    },
    "pets": {
        "name": "🐾 Питомцы",
        "effects": [
            ("pet_vlogger", "📱 Питомец-блогер"),
            ("pet_dance", "💃 Танцующий питомец"),
            ("pet_bee", "🐝 Питомец-пчела"),
            ("pet_chef", "👨‍🍳 Питомец-шеф"),
            ("pet_wizard", "🧙 Питомец-волшебник"),
            ("pet_warrior", "⚔️ Питомец-воин"),
            ("pet_lion_pro", "🦁 Питомец-лев"),
            ("pet_moto_rider", "🏍️ Питомец на мото"),
            ("muscle_pet", "💪 Мускулистый питомец"),
            ("pet_delivery", "📦 Питомец-курьер"),
        ]
    },
    "transform": {
        "name": "🦸 Трансформации",
        "effects": [
            ("witch_transform", "🧙‍♀️ Ведьма"),
            ("vampire_transform", "🧛 Вампир"),
            ("demon_transform", "😈 Демон"),
            ("zombie_transform", "🧟 Зомби"),
            ("mummy_transform", "🪦 Мумия"),
            ("piggy_morph", "🐷 Свинка"),
            ("nezha", "⚡ Нэчжа"),
            ("guardian_spirit", "👼 Дух-хранитель"),
        ]
    },
    "wings": {
        "name": "🪽 Крылья и магия",
        "effects": [
            ("pure_white_wings", "🕊️ Белые крылья"),
            ("black_wings", "🦇 Чёрные крылья"),
            ("golden_wing", "✨ Золотые крылья"),
            ("pink_pink_wings", "💗 Розовые крылья"),
            ("fairy_wing", "🧚 Крылья феи"),
            ("angel_wing", "😇 Крылья ангела"),
            ("dark_wing", "🖤 Тёмные крылья"),
            ("magic_fireball", "🔥 Магический огненный шар"),
            ("magic_cloak", "🧥 Магический плащ"),
            ("magic_broom", "🧹 Магическая метла"),
            ("lightning_power", "⚡ Сила молнии"),
        ]
    },
    "cinema": {
        "name": "🎬 Кино эффекты",
        "effects": [
            ("bullet_time", "⏱️ Bullet Time"),
            ("bullet_time_360", "🔄 Bullet Time 360"),
            ("bullet_time_lite", "💫 Bullet Time Lite"),
            ("zoom_out", "🔭 Zoom Out"),
            ("disappear", "💨 Исчезновение"),
            ("media_interview", "🎤 Интервью"),
            ("a_list_look", "🌟 Звёздный образ"),
            ("memory_alive", "💭 Ожившие воспоминания"),
            ("phantom_jewel", "💎 Фантомный драгоценный камень"),
        ]
    },
    "duo": {
        "name": "👫 Для двоих (2 фото)",
        "effects": [
            ("hug_pro", "🤗 Объятия"),
            ("kiss_pro", "💋 Поцелуй"),
            ("fight_pro", "🥊 Драка"),
            ("cheers_2026", "🥂 Чокаемся"),
            ("heart_gesture_pro", "💕 Сердечко руками"),
        ]
    },
    "styles": {
        "name": "🎨 Стили и аниме",
        "effects": [
            ("japanese_anime_1", "🇯🇵 Японское аниме"),
            ("american_comics", "🦸 Американские комиксы"),
            ("3d_cartoon_1_pro", "🎨 3D мультфильм"),
            ("3d_cartoon_2", "🎬 3D мультфильм 2"),
            ("c4d_cartoon_pro", "🖥️ C4D мультфильм"),
            ("mythic_style", "🏛️ Мифический стиль"),
            ("steampunk", "⚙️ Стимпанк"),
            ("felt_felt", "🧶 Войлочный"),
            ("plushcut", "🧸 Плюшевый"),
            ("pixelpixel", "👾 Пиксельный"),
            ("yearbook", "📚 Выпускной альбом"),
            ("instant_film", "📷 Моментальное фото"),
            ("anime_figure", "🎌 Аниме фигурка"),
        ]
    },
    "funny": {
        "name": "😂 Забавные",
        "effects": [
            ("pucker_up", "😘 Поцелуйчик"),
            ("guess_what", "🤔 Угадай что"),
            ("inner_voice", "🗣️ Внутренний голос"),
            ("squeeze_scream", "😱 Крик"),
            ("cry_cry", "😭 Плач"),
            ("boss_coming", "👔 Босс идёт"),
            ("office_escape_plow", "🏃 Побег из офиса"),
            ("wig_out", "🦱 Парик"),
            ("dizzydizzy", "😵 Головокружение"),
            ("squish", "🫠 Сжатие"),
            ("expansion", "💥 Расширение"),
            ("emoji", "😀 Эмодзи"),
            ("wool_curly", "🐑 Кудряшки"),
            ("long_hair", "💇 Длинные волосы"),
        ]
    },
    "holiday": {
        "name": "🎉 Праздники",
        "effects": [
            ("happy_birthday", "🎂 С днём рождения"),
            ("birthday_star", "⭐ Именинник"),
            ("firework", "🎆 Фейерверк"),
            ("firework_2026", "🎇 Фейерверк 2026"),
            ("dollar_rain", "💵 Дождь из денег"),
            ("dollar_rain_pro", "💰 Дождь из денег PRO"),
            ("marry_me", "💍 Выходи за меня"),
            ("surprise_bouquet", "💐 Букет-сюрприз"),
            ("bouquet_drop", "🌹 Падающий букет"),
            ("balloon_parade", "🎈 Парад шаров"),
        ]
    },
    "christmas": {
        "name": "🎄 Рождество и Зима",
        "effects": [
            ("santa_gift", "🎅 Подарок от Санты"),
            ("santa_hug", "🤗 Объятия Санты"),
            ("santa_random_surprise", "🎁 Сюрприз Санты"),
            ("my_santa_pic", "📸 Фото с Сантой"),
            ("christmas_photo_shoot", "🎄 Рождественская фотосессия"),
            ("snowglobe", "🔮 Снежный шар"),
            ("steampunk_christmas", "⚙️ Стимпанк Рождество"),
            ("instant_christmas", "✨ Мгновенное Рождество"),
            ("snowboarding", "🏂 Сноуборд"),
            ("ski_ski", "⛷️ Лыжи"),
            ("coronation_of_frost", "❄️ Коронация мороза"),
            ("spark_in_the_snow", "✨ Искры в снегу"),
        ]
    },
    "action": {
        "name": "🎬 Действия",
        "effects": [
            ("running", "🏃 Бег"),
            ("running_man", "🏃‍♂️ Бегущий человек"),
            ("fly_fly", "🦅 Полёт"),
            ("jumpdrop", "⬇️ Прыжок"),
            ("splashsplash", "💦 Всплеск"),
            ("surfsurf", "🏄 Сёрфинг"),
            ("skateskate", "🛹 Скейт"),
            ("trampoline", "🤸 Батут"),
            ("trampoline_night", "🌙 Ночной батут"),
            ("baseball", "⚾ Бейсбол"),
            ("flyer", "✈️ Летун"),
            ("rampage_ape", "🦍 Буйствующая обезьяна"),
        ]
    },
}

# Dual-image effects (require 2 photos)
DUAL_IMAGE_EFFECTS = {"cheers_2026", "kiss_pro", "fight_pro", "hug_pro", "heart_gesture_pro"}


class KlingEffectsService(BaseVideoProvider):
    """
    Kling AI Video Effects API integration.

    Supports 199 video effects with single or dual image input.
    """

    OFFICIAL_API_URL = "https://api-singapore.klingai.com"

    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize Kling Effects service.

        Args:
            access_key: Kling API access key
            secret_key: Kling API secret key
        """
        self.access_key = access_key or getattr(settings, 'kling_access_key', None)
        self.secret_key = secret_key or getattr(settings, 'kling_secret_key', None)
        self.base_url = self.OFFICIAL_API_URL

        super().__init__(self.access_key or "")

        self._jwt_token = None
        self._jwt_expires_at = 0

        if not self.access_key or not self.secret_key:
            logger.warning("kling_effects_api_keys_missing")

    def _generate_jwt_token(self) -> str:
        """Generate JWT token for Kling API authentication."""
        if not self.access_key or not self.secret_key:
            raise ValueError("Kling access_key and secret_key are required")

        current_time = int(time.time())

        if self._jwt_token and current_time < (self._jwt_expires_at - 300):
            return self._jwt_token

        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": current_time + 1800,
            "nbf": current_time - 5
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)

        self._jwt_token = token
        self._jwt_expires_at = current_time + 1800

        return token

    def _get_auth_headers(self) -> dict:
        """Get authentication headers for API requests."""
        token = self._generate_jwt_token()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    async def _image_to_base64(self, image_path: str) -> str:
        """Convert local image file to base64 string."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(path, "rb") as f:
            image_data = f.read()

        return base64.b64encode(image_data).decode("utf-8")

    async def generate_effect_video(
        self,
        effect_scene: str,
        image_paths: List[str],
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    ) -> VideoResponse:
        """
        Generate video with effect.

        Args:
            effect_scene: Effect scene name (e.g., 'hug_pro', 'bullet_time')
            image_paths: List of image paths (1 for single-image, 2 for dual-image effects)
            progress_callback: Optional async callback for progress updates

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.access_key or not self.secret_key:
            return VideoResponse(
                success=False,
                error="Kling API ключи не настроены",
                processing_time=time.time() - start_time
            )

        is_dual = effect_scene in DUAL_IMAGE_EFFECTS

        if is_dual and len(image_paths) < 2:
            return VideoResponse(
                success=False,
                error=f"Эффект '{effect_scene}' требует 2 фотографии",
                processing_time=time.time() - start_time
            )

        if len(image_paths) < 1:
            return VideoResponse(
                success=False,
                error="Требуется минимум 1 фотография",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Создаю видео с эффектом...")

            # Create task
            task_id = await self._create_effect_task(effect_scene, image_paths, is_dual)
            logger.info("kling_effect_task_created", task_id=task_id, effect=effect_scene)

            if progress_callback:
                await progress_callback("⏳ Генерация видео... (до 2 минут)")

            # Poll for completion
            video_url = await self._poll_task_status(task_id, progress_callback)

            if progress_callback:
                await progress_callback("💾 Сохраняю видео...")

            # Download video
            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "kling_effect_video_generated",
                effect=effect_scene,
                path=video_path,
                time=processing_time
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                metadata={
                    "provider": "kling_effects",
                    "effect_scene": effect_scene,
                    "task_id": task_id,
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling_effect_generation_failed", error=error_msg, effect=effect_scene)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_effect_task(
        self,
        effect_scene: str,
        image_paths: List[str],
        is_dual: bool
    ) -> str:
        """Create video effect generation task."""
        url = f"{self.base_url}/v1/videos/effects"
        headers = self._get_auth_headers()

        # Convert images to base64
        if is_dual:
            images_base64 = [
                await self._image_to_base64(image_paths[0]),
                await self._image_to_base64(image_paths[1])
            ]
            payload = {
                "effect_scene": effect_scene,
                "input": {
                    "images": images_base64
                }
            }
        else:
            image_base64 = await self._image_to_base64(image_paths[0])
            payload = {
                "effect_scene": effect_scene,
                "input": {
                    "image": image_base64
                }
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Kling Effects API error: {response.status} - {error_text}")

                data = await response.json()

                if data.get("code") != 0:
                    raise Exception(f"API error: {data.get('message', 'Unknown error')}")

                return data["data"]["task_id"]

    async def _poll_task_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 300,
        poll_interval: int = 5
    ) -> str:
        """Poll task status until complete."""
        url = f"{self.base_url}/v1/videos/effects/{task_id}"
        headers = self._get_auth_headers()

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Превышено время ожидания генерации")

                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    data = await response.json()

                    if data.get("code") != 0:
                        raise Exception(f"API error: {data.get('message', 'Unknown error')}")

                    task_data = data.get("data", {})
                    status = task_data.get("task_status", "unknown")
                    status_msg = task_data.get("task_status_msg", "")

                    if status != last_status:
                        last_status = status
                        if progress_callback:
                            if status == "submitted":
                                await progress_callback("⏳ В очереди...")
                            elif status == "processing":
                                await progress_callback("⚙️ Генерация видео...")

                    if status == "succeed":
                        task_result = task_data.get("task_result", {})
                        videos = task_result.get("videos", [])
                        if videos:
                            return videos[0]["url"]
                        raise Exception("Нет URL видео в ответе")

                    elif status == "failed":
                        error = status_msg or "Генерация не удалась"
                        raise Exception(error)

                await asyncio.sleep(poll_interval)

    async def generate_video(
        self,
        prompt: str,
        model: str = "",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """Required by base class - redirects to generate_effect_video."""
        effect_scene = kwargs.get("effect_scene", "")
        image_paths = kwargs.get("images", [])

        if not effect_scene:
            return VideoResponse(
                success=False,
                error="effect_scene is required"
            )

        return await self.generate_effect_video(
            effect_scene=effect_scene,
            image_paths=image_paths,
            progress_callback=progress_callback
        )


def get_effect_categories() -> Dict[str, Dict]:
    """Get all effect categories."""
    return EFFECT_CATEGORIES


def get_effects_by_category(category: str) -> List[tuple]:
    """Get effects for a specific category."""
    cat = EFFECT_CATEGORIES.get(category, {})
    return cat.get("effects", [])


def is_dual_image_effect(effect_scene: str) -> bool:
    """Check if effect requires 2 images."""
    return effect_scene in DUAL_IMAGE_EFFECTS


def get_effect_display_name(effect_scene: str) -> str:
    """Get display name for an effect."""
    for category in EFFECT_CATEGORIES.values():
        for effect in category.get("effects", []):
            if len(effect) >= 2 and effect[0] == effect_scene:
                return effect[1]
    return effect_scene
