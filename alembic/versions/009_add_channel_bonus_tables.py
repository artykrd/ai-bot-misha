"""add channel subscription bonus tables

Revision ID: 009
Revises: 008
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009_add_channel_bonus_tables'
down_revision = '008_add_blocked_users_and_expiry_notifications'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create channel_subscription_bonuses table
    op.create_table(
        'channel_subscription_bonuses',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=False, comment='Telegram channel/chat numeric ID'),
        sa.Column('channel_username', sa.String(255), nullable=True, comment='Channel @username (without @) for display'),
        sa.Column('channel_title', sa.String(255), nullable=True, comment='Channel display title'),
        sa.Column('bonus_tokens', sa.Integer(), nullable=False, server_default='1000', comment='Number of tokens to award for subscription'),
        sa.Column('welcome_message', sa.Text(), nullable=True, comment='Custom message shown when bonus is awarded'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether this bonus is currently active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_channel_subscription_bonuses_channel_id', 'channel_subscription_bonuses', ['channel_id'])
    op.create_index('ix_channel_subscription_bonuses_is_active', 'channel_subscription_bonuses', ['is_active'])

    # Create channel_bonus_claims table
    op.create_table(
        'channel_bonus_claims',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who claimed the bonus'),
        sa.Column('bonus_id', sa.BigInteger(), nullable=False, comment='Reference to the bonus configuration'),
        sa.Column('tokens_awarded', sa.Integer(), nullable=False, comment='Actual tokens awarded at the time of claim'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bonus_id'], ['channel_subscription_bonuses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_channel_bonus_claims_user_id', 'channel_bonus_claims', ['user_id'])
    op.create_index('ix_channel_bonus_claims_bonus_id', 'channel_bonus_claims', ['bonus_id'])
    op.create_index('idx_channel_bonus_claims_user_bonus', 'channel_bonus_claims', ['user_id', 'bonus_id'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_channel_bonus_claims_user_bonus', table_name='channel_bonus_claims')
    op.drop_index('ix_channel_bonus_claims_bonus_id', table_name='channel_bonus_claims')
    op.drop_index('ix_channel_bonus_claims_user_id', table_name='channel_bonus_claims')
    op.drop_table('channel_bonus_claims')

    op.drop_index('ix_channel_subscription_bonuses_is_active', table_name='channel_subscription_bonuses')
    op.drop_index('ix_channel_subscription_bonuses_channel_id', table_name='channel_subscription_bonuses')
    op.drop_table('channel_subscription_bonuses')
