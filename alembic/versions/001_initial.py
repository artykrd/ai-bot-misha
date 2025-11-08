"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2025-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('language_code', sa.String(length=10), nullable=True),
    sa.Column('is_banned', sa.Boolean(), nullable=False),
    sa.Column('ban_reason', sa.Text(), nullable=True),
    sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_is_banned'), 'users', ['is_banned'], unique=False)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)

    # Create subscriptions table
    op.create_table('subscriptions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('subscription_type', sa.String(length=50), nullable=False),
    sa.Column('tokens_amount', sa.BigInteger(), nullable=False),
    sa.Column('tokens_used', sa.BigInteger(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_is_active'), 'subscriptions', ['is_active'], unique=False)
    op.create_index(op.f('ix_subscriptions_tokens_used'), 'subscriptions', ['tokens_used'], unique=False)
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)

    # Create payments table
    op.create_table('payments',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('subscription_id', sa.BigInteger(), nullable=True),
    sa.Column('payment_id', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('payment_method', sa.String(length=100), nullable=True),
    sa.Column('yukassa_payment_id', sa.String(length=255), nullable=True),
    sa.Column('yukassa_response', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_payment_id'), 'payments', ['payment_id'], unique=True)
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'], unique=False)
    op.create_index(op.f('ix_payments_subscription_id'), 'payments', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_payments_user_id'), 'payments', ['user_id'], unique=False)
    op.create_index(op.f('ix_payments_yukassa_payment_id'), 'payments', ['yukassa_payment_id'], unique=False)

    # Create ai_requests table
    op.create_table('ai_requests',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('request_type', sa.String(length=50), nullable=False),
    sa.Column('ai_model', sa.String(length=100), nullable=False),
    sa.Column('prompt', sa.Text(), nullable=True),
    sa.Column('tokens_cost', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('response_file_path', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('processing_time_seconds', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_requests_ai_model'), 'ai_requests', ['ai_model'], unique=False)
    op.create_index(op.f('ix_ai_requests_request_type'), 'ai_requests', ['request_type'], unique=False)
    op.create_index(op.f('ix_ai_requests_status'), 'ai_requests', ['status'], unique=False)
    op.create_index(op.f('ix_ai_requests_user_id'), 'ai_requests', ['user_id'], unique=False)

    # Create dialogs table
    op.create_table('dialogs',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('ai_model', sa.String(length=100), nullable=False),
    sa.Column('system_prompt', sa.Text(), nullable=True),
    sa.Column('is_history_enabled', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialogs_user_id'), 'dialogs', ['user_id'], unique=False)

    # Create dialog_messages table
    op.create_table('dialog_messages',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('dialog_id', sa.BigInteger(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('tokens_used', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['dialog_id'], ['dialogs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dialog_messages_dialog_id'), 'dialog_messages', ['dialog_id'], unique=False)

    # Create referrals table
    op.create_table('referrals',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('referrer_id', sa.BigInteger(), nullable=False),
    sa.Column('referred_id', sa.BigInteger(), nullable=False),
    sa.Column('referral_code', sa.String(length=50), nullable=False),
    sa.Column('referral_type', sa.String(length=20), nullable=False),
    sa.Column('tokens_earned', sa.BigInteger(), nullable=False),
    sa.Column('money_earned', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['referred_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['referrer_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referrals_is_active'), 'referrals', ['is_active'], unique=False)
    op.create_index(op.f('ix_referrals_referral_code'), 'referrals', ['referral_code'], unique=False)
    op.create_index(op.f('ix_referrals_referred_id'), 'referrals', ['referred_id'], unique=True)
    op.create_index(op.f('ix_referrals_referrer_id'), 'referrals', ['referrer_id'], unique=False)

    # Create files table
    op.create_table('files',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('ai_request_id', sa.BigInteger(), nullable=True),
    sa.Column('file_type', sa.String(length=50), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('file_size', sa.BigInteger(), nullable=False),
    sa.Column('mime_type', sa.String(length=100), nullable=False),
    sa.Column('is_compressed', sa.Boolean(), nullable=False),
    sa.Column('original_file_path', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['ai_request_id'], ['ai_requests.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_ai_request_id'), 'files', ['ai_request_id'], unique=False)
    op.create_index(op.f('ix_files_expires_at'), 'files', ['expires_at'], unique=False)
    op.create_index(op.f('ix_files_file_type'), 'files', ['file_type'], unique=False)
    op.create_index(op.f('ix_files_user_id'), 'files', ['user_id'], unique=False)

    # Create promocodes table
    op.create_table('promocodes',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('bonus_type', sa.String(length=20), nullable=False),
    sa.Column('bonus_value', sa.Integer(), nullable=False),
    sa.Column('max_uses', sa.Integer(), nullable=True),
    sa.Column('current_uses', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promocodes_code'), 'promocodes', ['code'], unique=True)
    op.create_index(op.f('ix_promocodes_is_active'), 'promocodes', ['is_active'], unique=False)

    # Create promocode_uses table
    op.create_table('promocode_uses',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('promocode_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('bonus_received', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['promocode_id'], ['promocodes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promocode_uses_promocode_id'), 'promocode_uses', ['promocode_id'], unique=False)
    op.create_index(op.f('ix_promocode_uses_user_id'), 'promocode_uses', ['user_id'], unique=False)

    # Create ai_models table
    op.create_table('ai_models',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('display_name', sa.String(length=255), nullable=False),
    sa.Column('model_type', sa.String(length=50), nullable=False),
    sa.Column('provider', sa.String(length=100), nullable=False),
    sa.Column('api_endpoint', sa.Text(), nullable=True),
    sa.Column('tokens_per_request', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
    sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_models_is_active'), 'ai_models', ['is_active'], unique=False)
    op.create_index(op.f('ix_ai_models_model_type'), 'ai_models', ['model_type'], unique=False)
    op.create_index(op.f('ix_ai_models_name'), 'ai_models', ['name'], unique=True)

    # Create ai_cache table
    op.create_table('ai_cache',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('request_hash', sa.String(length=64), nullable=False),
    sa.Column('model_name', sa.String(length=100), nullable=False),
    sa.Column('prompt_hash', sa.String(length=64), nullable=False),
    sa.Column('response_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=True),
    sa.Column('access_count', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_cache_expires_at'), 'ai_cache', ['expires_at'], unique=False)
    op.create_index(op.f('ix_ai_cache_model_name'), 'ai_cache', ['model_name'], unique=False)
    op.create_index(op.f('ix_ai_cache_prompt_hash'), 'ai_cache', ['prompt_hash'], unique=False)
    op.create_index(op.f('ix_ai_cache_request_hash'), 'ai_cache', ['request_hash'], unique=True)

    # Create system_settings table
    op.create_table('system_settings',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('key', sa.String(length=100), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('value_type', sa.String(length=20), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)

    # Create admin_logs table
    op.create_table('admin_logs',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('admin_id', sa.BigInteger(), nullable=True),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('target_type', sa.String(length=50), nullable=True),
    sa.Column('target_id', sa.BigInteger(), nullable=True),
    sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_logs_action'), 'admin_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_logs_admin_id'), 'admin_logs', ['admin_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_admin_logs_admin_id'), table_name='admin_logs')
    op.drop_index(op.f('ix_admin_logs_action'), table_name='admin_logs')
    op.drop_table('admin_logs')
    op.drop_index(op.f('ix_system_settings_key'), table_name='system_settings')
    op.drop_table('system_settings')
    op.drop_index(op.f('ix_ai_cache_request_hash'), table_name='ai_cache')
    op.drop_index(op.f('ix_ai_cache_prompt_hash'), table_name='ai_cache')
    op.drop_index(op.f('ix_ai_cache_model_name'), table_name='ai_cache')
    op.drop_index(op.f('ix_ai_cache_expires_at'), table_name='ai_cache')
    op.drop_table('ai_cache')
    op.drop_index(op.f('ix_ai_models_name'), table_name='ai_models')
    op.drop_index(op.f('ix_ai_models_model_type'), table_name='ai_models')
    op.drop_index(op.f('ix_ai_models_is_active'), table_name='ai_models')
    op.drop_table('ai_models')
    op.drop_index(op.f('ix_promocode_uses_user_id'), table_name='promocode_uses')
    op.drop_index(op.f('ix_promocode_uses_promocode_id'), table_name='promocode_uses')
    op.drop_table('promocode_uses')
    op.drop_index(op.f('ix_promocodes_is_active'), table_name='promocodes')
    op.drop_index(op.f('ix_promocodes_code'), table_name='promocodes')
    op.drop_table('promocodes')
    op.drop_index(op.f('ix_files_user_id'), table_name='files')
    op.drop_index(op.f('ix_files_file_type'), table_name='files')
    op.drop_index(op.f('ix_files_expires_at'), table_name='files')
    op.drop_index(op.f('ix_files_ai_request_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_referrals_referrer_id'), table_name='referrals')
    op.drop_index(op.f('ix_referrals_referred_id'), table_name='referrals')
    op.drop_index(op.f('ix_referrals_referral_code'), table_name='referrals')
    op.drop_index(op.f('ix_referrals_is_active'), table_name='referrals')
    op.drop_table('referrals')
    op.drop_index(op.f('ix_dialog_messages_dialog_id'), table_name='dialog_messages')
    op.drop_table('dialog_messages')
    op.drop_index(op.f('ix_dialogs_user_id'), table_name='dialogs')
    op.drop_table('dialogs')
    op.drop_index(op.f('ix_ai_requests_user_id'), table_name='ai_requests')
    op.drop_index(op.f('ix_ai_requests_status'), table_name='ai_requests')
    op.drop_index(op.f('ix_ai_requests_request_type'), table_name='ai_requests')
    op.drop_index(op.f('ix_ai_requests_ai_model'), table_name='ai_requests')
    op.drop_table('ai_requests')
    op.drop_index(op.f('ix_payments_yukassa_payment_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_user_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_subscription_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_status'), table_name='payments')
    op.drop_index(op.f('ix_payments_payment_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_tokens_used'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_is_active'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_is_banned'), table_name='users')
    op.drop_table('users')
