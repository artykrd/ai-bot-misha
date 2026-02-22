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

    # Create expiry_notification_settings table
    op.create_table(
        'expiry_notification_settings',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('delay_days', sa.Integer(), nullable=False, comment='Days after expiry to send notification'),
        sa.Column('message_text', sa.Text(), nullable=False, comment='Notification message text'),
        sa.Column('has_discount', sa.Boolean(), nullable=False, server_default='false', comment='Whether to include a discount'),
        sa.Column('discount_percent', sa.Integer(), nullable=False, server_default='0', comment='Discount percentage (0-100)'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether this notification rule is active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_expiry_notification_settings_is_active', 'expiry_notification_settings', ['is_active'])

    # Create expiry_notification_logs table
    op.create_table(
        'expiry_notification_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who received the notification'),
        sa.Column('subscription_id', sa.BigInteger(), nullable=False, comment='Expired subscription that triggered this notification'),
        sa.Column('settings_id', sa.BigInteger(), nullable=False, comment='Settings rule that triggered this notification'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False, comment='When the notification was sent'),
        sa.Column('delivered', sa.Boolean(), nullable=False, server_default='true', comment='Whether the notification was successfully delivered'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['settings_id'], ['expiry_notification_settings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_expiry_notification_logs_user_id', 'expiry_notification_logs', ['user_id'])
    op.create_index('ix_expiry_notification_logs_subscription_id', 'expiry_notification_logs', ['subscription_id'])


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
