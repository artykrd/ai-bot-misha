"""add blocked users flag and expiry notification tables

Revision ID: 008
Revises: 007
Create Date: 2026-02-22

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_add_blocked_users_and_expiry_notifications'
down_revision = '007_add_broadcast_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_bot_blocked column to users table
    op.add_column(
        'users',
        sa.Column(
            'is_bot_blocked',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='Whether user has blocked the bot'
        )
    )
    op.create_index('ix_users_is_bot_blocked', 'users', ['is_bot_blocked'])

def downgrade() -> None:
    # Drop expiry notification tables
    op.drop_index('ix_expiry_notification_logs_subscription_id', table_name='expiry_notification_logs')
    op.drop_index('ix_expiry_notification_logs_user_id', table_name='expiry_notification_logs')
    op.drop_table('expiry_notification_logs')

    op.drop_index('ix_expiry_notification_settings_is_active', table_name='expiry_notification_settings')
    op.drop_table('expiry_notification_settings')

    # Remove is_bot_blocked column from users
    op.drop_index('ix_users_is_bot_blocked', table_name='users')
    op.drop_column('users', 'is_bot_blocked')
