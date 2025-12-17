"""Populate AI models with correct token costs

Revision ID: 003_populate_ai_models
Revises: 002_add_unlimited_invite_links
Create Date: 2025-12-17 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision: str = '003_populate_ai_models'
down_revision: Union[str, None] = '002_add_unlimited_invite_links'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Populate ai_models table with correct token costs.
    This is the SINGLE SOURCE OF TRUTH for all model pricing.
    """

    # Create metadata and table reference
    meta = sa.MetaData()
    ai_models = sa.Table(
        'ai_models',
        meta,
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('tokens_per_request', sa.BigInteger, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('settings', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    now = datetime.now(timezone.utc)

    # Define all models with their costs
    models_data = [
        # Image Generation Models
        {
            'name': 'nano-banana',
            'display_name': 'Nano Banana (Gemini 2.5 Flash)',
            'model_type': 'image',
            'provider': 'google',
            'tokens_per_request': 6380,
            'is_active': True,
            'settings': {'formats': ['1:1', '16:9', '9:16', '3:4', '4:3']},
        },
        {
            'name': 'gpt-image',
            'display_name': 'GPT Image 1 (DALL-E)',
            'model_type': 'image',
            'provider': 'openai',
            'tokens_per_request': 5300,
            'is_active': True,
            'settings': {'sizes': ['1024x1024', '1792x1024', '1024x1792']},
        },
        {
            'name': 'midjourney',
            'display_name': 'Midjourney',
            'model_type': 'image',
            'provider': 'midjourney',
            'tokens_per_request': 15000,
            'is_active': False,  # Not yet connected
            'settings': {},
        },
        {
            'name': 'stable-diffusion-core',
            'display_name': 'Stable Diffusion Core',
            'model_type': 'image',
            'provider': 'stability',
            'tokens_per_request': 85000,
            'is_active': False,  # Not yet connected
            'settings': {},
        },
        {
            'name': 'recraft',
            'display_name': 'Recraft AI',
            'model_type': 'image',
            'provider': 'recraft',
            'tokens_per_request': 20000,
            'is_active': True,
            'settings': {'styles': ['realistic', 'digital', 'vector', 'icon']},
        },
        {
            'name': 'dalle',
            'display_name': 'DALL-E 3',
            'model_type': 'image',
            'provider': 'openai',
            'tokens_per_request': 5300,
            'is_active': True,
            'settings': {'quality': ['standard', 'hd']},
        },
        {
            'name': 'kling-image',
            'display_name': 'Kling AI Image',
            'model_type': 'image',
            'provider': 'kling',
            'tokens_per_request': 6380,
            'is_active': True,
            'settings': {'formats': ['1:1', '16:9', '9:16', '4:3', '3:4']},
        },
        # Video Generation Models
        {
            'name': 'sora-2',
            'display_name': 'Sora 2',
            'model_type': 'video',
            'provider': 'openai',
            'tokens_per_request': 50600,
            'is_active': True,
            'settings': {'max_duration': 20, 'resolution': '1080p'},
        },
        {
            'name': 'veo-3.1',
            'display_name': 'Veo 3.1',
            'model_type': 'video',
            'provider': 'google',
            'tokens_per_request': 116000,
            'is_active': True,
            'settings': {'duration': 8, 'resolution': '720p', 'formats': ['16:9', '9:16', '1:1', '4:3', '3:4']},
        },
        {
            'name': 'hailuo',
            'display_name': 'Hailuo (MiniMax)',
            'model_type': 'video',
            'provider': 'minimax',
            'tokens_per_request': 90000,
            'is_active': True,
            'settings': {'duration': '6-10', 'resolution': ['768P', '1080P']},
        },
        {
            'name': 'luma',
            'display_name': 'Luma Dream Machine',
            'model_type': 'video',
            'provider': 'luma',
            'tokens_per_request': 90000,
            'is_active': True,
            'settings': {},
        },
        {
            'name': 'kling',
            'display_name': 'Kling AI Video',
            'model_type': 'video',
            'provider': 'kling',
            'tokens_per_request': 80000,
            'is_active': True,
            'settings': {'version': ['2.5', '2.5-turbo']},
        },
        {
            'name': 'kling-effects',
            'display_name': 'Kling Effects',
            'model_type': 'video',
            'provider': 'kling',
            'tokens_per_request': 80000,
            'is_active': True,
            'settings': {'duration': [5, 10], 'format': '1:1'},
        },
        {
            'name': 'mjvideo',
            'display_name': 'Midjourney Video',
            'model_type': 'video',
            'provider': 'midjourney',
            'tokens_per_request': 90000,
            'is_active': False,  # Not yet connected
            'settings': {},
        },
        # Photo Tools
        {
            'name': 'photo-enhance',
            'display_name': 'Улучшение качества',
            'model_type': 'tool',
            'provider': 'internal',
            'tokens_per_request': 2000,
            'is_active': True,
            'settings': {},
        },
        {
            'name': 'bg-replace',
            'display_name': 'Замена фона',
            'model_type': 'tool',
            'provider': 'internal',
            'tokens_per_request': 15000,
            'is_active': True,
            'settings': {},
        },
        {
            'name': 'bg-remove',
            'display_name': 'Удаление фона',
            'model_type': 'tool',
            'provider': 'removebg',
            'tokens_per_request': 5000,
            'is_active': True,
            'settings': {},
        },
        {
            'name': 'vectorize',
            'display_name': 'Векторизация',
            'model_type': 'tool',
            'provider': 'internal',
            'tokens_per_request': 5000,
            'is_active': True,
            'settings': {},
        },
        # Audio Models
        {
            'name': 'suno',
            'display_name': 'Suno Music',
            'model_type': 'audio',
            'provider': 'suno',
            'tokens_per_request': 17600,
            'is_active': True,
            'settings': {'versions': ['V5', 'V4.5', 'V4']},
        },
        {
            'name': 'whisper',
            'display_name': 'Whisper (расшифровка)',
            'model_type': 'audio',
            'provider': 'openai',
            'tokens_per_request': 1200,  # per minute
            'is_active': True,
            'settings': {'unit': 'per_minute'},
        },
        {
            'name': 'tts',
            'display_name': 'OpenAI TTS (озвучка)',
            'model_type': 'audio',
            'provider': 'openai',
            'tokens_per_request': 1,  # per character
            'is_active': True,
            'settings': {'unit': 'per_character', 'voices': ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']},
        },
    ]

    # Insert or update models
    conn = op.get_bind()

    for model_data in models_data:
        model_data['created_at'] = now
        model_data['updated_at'] = now

        # Check if model exists
        existing = conn.execute(
            sa.select(ai_models.c.id).where(ai_models.c.name == model_data['name'])
        ).fetchone()

        if existing:
            # Update existing
            conn.execute(
                ai_models.update().where(ai_models.c.name == model_data['name']).values(**model_data)
            )
        else:
            # Insert new
            conn.execute(ai_models.insert().values(**model_data))


def downgrade() -> None:
    """Remove populated models."""
    # We don't delete data on downgrade to preserve user history
    pass
