"""Add AI cost tracking tables and fields

Revision ID: 005_add_ai_cost_tracking
Revises: 004_add_referral_balances
Create Date: 2025-01-29 00:00:00.000000

This migration adds:
1. New fields to ai_requests for cost tracking
2. operation_categories table for categorization config
3. model_costs table for model pricing config

All changes are backward-compatible and additive.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_ai_cost_tracking'
down_revision = '004_add_referral_balances'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns to ai_requests
    # These are all nullable to maintain backward compatibility
    op.add_column(
        'ai_requests',
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=True,
                  comment='Real API cost in USD')
    )
    op.add_column(
        'ai_requests',
        sa.Column('cost_rub', sa.Numeric(precision=10, scale=2), nullable=True,
                  comment='Cost in RUB at request time')
    )
    op.add_column(
        'ai_requests',
        sa.Column('operation_category', sa.String(50), nullable=True,
                  comment='Category: text, image_gen, image_edit, video_gen, audio_gen, transcription, tts')
    )
    op.add_column(
        'ai_requests',
        sa.Column('subscription_id', sa.BigInteger(), nullable=True,
                  comment='Subscription used for this request')
    )
    op.add_column(
        'ai_requests',
        sa.Column('is_unlimited_subscription', sa.Boolean(), nullable=True,
                  server_default='false',
                  comment='Was this request made under unlimited subscription')
    )
    op.add_column(
        'ai_requests',
        sa.Column('input_data', sa.JSON(), nullable=True,
                  comment='Input parameters (dimensions, duration, etc.)')
    )

    # Add indexes for new columns
    op.create_index(
        'ix_ai_requests_operation_category',
        'ai_requests',
        ['operation_category']
    )
    op.create_index(
        'ix_ai_requests_subscription_id',
        'ai_requests',
        ['subscription_id']
    )
    op.create_index(
        'ix_ai_requests_is_unlimited',
        'ai_requests',
        ['is_unlimited_subscription']
    )
    op.create_index(
        'ix_ai_requests_created_at',
        'ai_requests',
        ['created_at']
    )

    # Add foreign key constraint for subscription_id
    op.create_foreign_key(
        'fk_ai_requests_subscription_id',
        'ai_requests',
        'subscriptions',
        ['subscription_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 2. Create operation_categories table
    op.create_table(
        'operation_categories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True,
                  comment='Category code: text, image_gen, video_gen, etc.'),
        sa.Column('name', sa.String(100), nullable=False,
                  comment='Display name'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('request_type', sa.String(50), nullable=False,
                  comment='Maps to ai_requests.request_type: text, image, video, audio'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_operation_categories_code', 'operation_categories', ['code'], unique=True)

    # 3. Create model_costs table
    op.create_table(
        'model_costs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('model_id', sa.String(100), nullable=False,
                  comment='Model identifier used in code'),
        sa.Column('provider', sa.String(50), nullable=False,
                  comment='Provider: openai, anthropic, google, kling, suno, etc.'),
        sa.Column('category_code', sa.String(50), nullable=False,
                  comment='FK to operation_categories.code'),
        sa.Column('display_name', sa.String(100), nullable=False,
                  comment='User-facing name'),

        # Cost configuration
        sa.Column('cost_usd_per_unit', sa.Numeric(precision=10, scale=6), nullable=False,
                  comment='Cost in USD per unit'),
        sa.Column('cost_unit', sa.String(50), nullable=False,
                  comment='Unit type: request, token, minute, character, second'),
        sa.Column('tokens_per_unit', sa.Integer(), nullable=False,
                  comment='Internal tokens charged per unit'),

        # Optional unit multipliers for variable costs
        sa.Column('unit_multipliers', sa.JSON(), nullable=True,
                  comment='Multipliers for different configurations (e.g., resolution, duration)'),

        # Unlimited subscription limits (nullable = no special limit)
        sa.Column('unlimited_daily_limit', sa.Integer(), nullable=True,
                  comment='Max requests per day for unlimited subscription'),
        sa.Column('unlimited_budget_tokens', sa.Integer(), nullable=True,
                  comment='Token budget for unlimited subscription'),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_model_costs_model_id', 'model_costs', ['model_id'], unique=True)
    op.create_index('ix_model_costs_category_code', 'model_costs', ['category_code'])
    op.create_index('ix_model_costs_provider', 'model_costs', ['provider'])

    # 4. Seed operation categories
    op.execute("""
        INSERT INTO operation_categories (code, name, description, request_type) VALUES
        ('text', 'Text Generation', 'Text chat, completion, reasoning', 'text'),
        ('text_with_image', 'Text with Image', 'Vision models, image analysis', 'text'),
        ('image_gen', 'Image Generation', 'Creating images from text/image', 'image'),
        ('image_edit', 'Image Editing', 'Upscale, background removal, face swap', 'image'),
        ('video_gen', 'Video Generation', 'Creating videos from text/image', 'video'),
        ('audio_gen', 'Audio/Music Generation', 'Creating music and sounds', 'audio'),
        ('transcription', 'Audio Transcription', 'Speech to text', 'audio'),
        ('tts', 'Text to Speech', 'Text to audio synthesis', 'audio')
    """)

    # 5. Seed model costs with realistic data
    # Note: costs are approximate and should be adjusted based on actual API pricing
    op.execute("""
        INSERT INTO model_costs (model_id, provider, category_code, display_name, cost_usd_per_unit, cost_unit, tokens_per_unit, unlimited_daily_limit) VALUES
        -- Text models (per 1K tokens, cost_usd is per token)
        ('gpt-4.1-mini', 'openai', 'text', 'GPT-4.1 Mini', 0.00000015, 'token', 2, NULL),
        ('gpt-4o', 'openai', 'text', 'GPT-4o', 0.000005, 'token', 7, NULL),
        ('gpt-4o-mini', 'openai', 'text', 'GPT-4o Mini', 0.00000015, 'token', 2, NULL),
        ('o1-mini', 'openai', 'text', 'O1 Mini', 0.000003, 'token', 3, NULL),
        ('o3-mini', 'openai', 'text', 'O3 Mini', 0.0000011, 'token', 3, NULL),
        ('claude-4', 'anthropic', 'text', 'Claude 4', 0.000003, 'token', 4, NULL),
        ('claude-3.5-sonnet', 'anthropic', 'text', 'Claude 3.5 Sonnet', 0.000003, 'token', 4, NULL),
        ('gemini-2.0-flash', 'google', 'text', 'Gemini 2.0 Flash', 0.0000001, 'token', 1, NULL),
        ('gemini-pro', 'google', 'text', 'Gemini Pro', 0.00000025, 'token', 2, NULL),
        ('deepseek-chat', 'deepseek', 'text', 'DeepSeek Chat', 0.00000014, 'token', 2, NULL),
        ('sonar', 'perplexity', 'text', 'Sonar (with search)', 0.000001, 'token', 3, NULL),

        -- Image generation (per request)
        ('dalle3', 'openai', 'image_gen', 'DALL-E 3', 0.04, 'request', 9500, 150),
        ('dalle3-hd', 'openai', 'image_gen', 'DALL-E 3 HD', 0.08, 'request', 19000, 75),
        ('midjourney', 'midjourney', 'image_gen', 'Midjourney', 0.06, 'request', 13000, 100),
        ('nano-banana', 'aimlapi', 'image_gen', 'Nano Banana', 0.025, 'request', 6000, 235),
        ('gpt-image-1', 'openai', 'image_gen', 'GPT Image 1', 0.08, 'request', 8000, 176),
        ('stability-sd3', 'stability', 'image_gen', 'Stable Diffusion 3', 0.35, 'request', 82000, 17),
        ('recraft', 'recraft', 'image_gen', 'Recraft', 0.04, 'request', 7000, 75),
        ('kling-image', 'kling', 'image_gen', 'Kling Image', 0.03, 'request', 2000, 200),

        -- Image editing (per request)
        ('face-swap', 'replicate', 'image_edit', 'Face Swap', 0.02, 'request', 4700, 300),
        ('upscale', 'replicate', 'image_edit', 'Image Upscale', 0.008, 'request', 1900, 750),
        ('remove-bg', 'removebg', 'image_edit', 'Background Removal', 0.02, 'request', 4700, 300),
        ('replace-bg', 'replicate', 'image_edit', 'Background Replace', 0.06, 'request', 14000, 100),
        ('vectorize', 'vectorizer', 'image_edit', 'Vectorization', 0.02, 'request', 4700, 300),

        -- Video generation (per request, varies by duration/resolution)
        ('sora2', 'openai', 'video_gen', 'Sora 2', 0.50, 'request', 50000, 29),
        ('veo-3.1', 'google', 'video_gen', 'Veo 3.1', 0.80, 'request', 115000, 12),
        ('midjourney-video', 'midjourney', 'video_gen', 'Midjourney Video', 0.55, 'request', 79000, 17),
        ('kling-1.6', 'kling', 'video_gen', 'Kling 1.6', 0.35, 'request', 58000, 18),
        ('kling-2.0', 'kling', 'video_gen', 'Kling 2.0', 0.35, 'request', 58000, 18),
        ('kling-2.5', 'kling', 'video_gen', 'Kling 2.5', 0.35, 'request', 58000, 18),
        ('kling-effects', 'kling', 'video_gen', 'Kling Effects', 0.20, 'request', 2500, 15),
        ('hailuo', 'minimax', 'video_gen', 'Hailuo', 0.55, 'request', 89500, 16),
        ('luma', 'luma', 'video_gen', 'Luma Dream Machine', 2.00, 'request', 85000, 3),

        -- Audio generation (per request)
        ('suno', 'suno', 'audio_gen', 'Suno Music', 0.10, 'request', 8000, 85),

        -- Transcription (per minute)
        ('whisper', 'openai', 'transcription', 'Whisper', 0.006, 'minute', 500, 1250),

        -- TTS (per character)
        ('openai-tts', 'openai', 'tts', 'OpenAI TTS', 0.000015, 'character', 1, 1500000),
        ('openai-tts-hd', 'openai', 'tts', 'OpenAI TTS HD', 0.00003, 'character', 2, 750000)
    """)


def downgrade() -> None:
    # Drop model_costs table
    op.drop_index('ix_model_costs_provider', table_name='model_costs')
    op.drop_index('ix_model_costs_category_code', table_name='model_costs')
    op.drop_index('ix_model_costs_model_id', table_name='model_costs')
    op.drop_table('model_costs')

    # Drop operation_categories table
    op.drop_index('ix_operation_categories_code', table_name='operation_categories')
    op.drop_table('operation_categories')

    # Remove foreign key and indexes from ai_requests
    op.drop_constraint('fk_ai_requests_subscription_id', 'ai_requests', type_='foreignkey')
    op.drop_index('ix_ai_requests_created_at', table_name='ai_requests')
    op.drop_index('ix_ai_requests_is_unlimited', table_name='ai_requests')
    op.drop_index('ix_ai_requests_subscription_id', table_name='ai_requests')
    op.drop_index('ix_ai_requests_operation_category', table_name='ai_requests')

    # Remove columns from ai_requests
    op.drop_column('ai_requests', 'input_data')
    op.drop_column('ai_requests', 'is_unlimited_subscription')
    op.drop_column('ai_requests', 'subscription_id')
    op.drop_column('ai_requests', 'operation_category')
    op.drop_column('ai_requests', 'cost_rub')
    op.drop_column('ai_requests', 'cost_usd')
