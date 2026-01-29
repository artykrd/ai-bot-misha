"""add video jobs and feature flags

Revision ID: 006
Revises: 005
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create video_generation_jobs table
    op.create_table(
        'video_generation_jobs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('ai_request_id', sa.BigInteger(), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='Provider: kling, sora, veo, luma, hailuo'),
        sa.Column('model_id', sa.String(length=100), nullable=False, comment='Model identifier (e.g., kling-2.5)'),
        sa.Column('task_id', sa.String(length=255), nullable=True, comment="Provider's task ID for status polling"),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='Status: pending, processing, timeout_waiting, completed, failed'),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='Generation parameters (images, duration, aspect_ratio, etc.)'),
        sa.Column('video_path', sa.Text(), nullable=True, comment='Path to generated video file'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if failed'),
        sa.Column('chat_id', sa.BigInteger(), nullable=False, comment='Telegram chat ID to send result to'),
        sa.Column('progress_message_id', sa.BigInteger(), nullable=True, comment='Telegram message ID for progress updates'),
        sa.Column('tokens_cost', sa.BigInteger(), nullable=False, server_default='0', comment='Token cost for this job'),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0', comment='Number of processing attempts'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3', comment='Maximum number of retry attempts'),
        sa.Column('started_processing_at', sa.DateTime(timezone=True), nullable=True, comment='When worker started processing this job'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='When job was completed or failed'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, comment='Job expiration time (for cleanup)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ai_request_id'], ['ai_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_video_generation_jobs_user_id', 'video_generation_jobs', ['user_id'])
    op.create_index('ix_video_generation_jobs_ai_request_id', 'video_generation_jobs', ['ai_request_id'])
    op.create_index('ix_video_generation_jobs_provider', 'video_generation_jobs', ['provider'])
    op.create_index('ix_video_generation_jobs_task_id', 'video_generation_jobs', ['task_id'])
    op.create_index('ix_video_generation_jobs_status', 'video_generation_jobs', ['status'])
    op.create_index('ix_video_generation_jobs_completed_at', 'video_generation_jobs', ['completed_at'])
    op.create_index('ix_video_generation_jobs_expires_at', 'video_generation_jobs', ['expires_at'])

    # Add feature flags to system_settings if not exist
    op.execute("""
        INSERT INTO system_settings (key, value, value_type, description, created_at, updated_at)
        VALUES
            ('unlimited_limits_enabled', 'true', 'bool', 'Enable unlimited subscription limits enforcement', now(), now()),
            ('async_video_enabled', 'true', 'bool', 'Enable async video generation with job queue', now(), now()),
            ('ai_logging_enabled', 'true', 'bool', 'Enable comprehensive AI operations logging', now(), now())
        ON CONFLICT (key) DO NOTHING;
    """)


def downgrade() -> None:
    # Drop feature flags
    op.execute("""
        DELETE FROM system_settings
        WHERE key IN ('unlimited_limits_enabled', 'async_video_enabled', 'ai_logging_enabled');
    """)

    # Drop video_generation_jobs table
    op.drop_index('ix_video_generation_jobs_expires_at', 'video_generation_jobs')
    op.drop_index('ix_video_generation_jobs_completed_at', 'video_generation_jobs')
    op.drop_index('ix_video_generation_jobs_status', 'video_generation_jobs')
    op.drop_index('ix_video_generation_jobs_task_id', 'video_generation_jobs')
    op.drop_index('ix_video_generation_jobs_provider', 'video_generation_jobs')
    op.drop_index('ix_video_generation_jobs_ai_request_id', 'video_generation_jobs')
    op.drop_index('ix_video_generation_jobs_user_id', 'video_generation_jobs')
    op.drop_table('video_generation_jobs')
