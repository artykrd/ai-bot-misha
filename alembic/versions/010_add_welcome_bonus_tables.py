"""add welcome bonus tables for advertising campaigns

Revision ID: 010
Revises: 009
Create Date: 2026-03-17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010_add_welcome_bonus_tables'
down_revision = '009_add_channel_bonus_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create welcome_bonuses table
    op.create_table(
        'welcome_bonuses',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('invite_code', sa.String(50), nullable=False, comment='Unique invite code for deep link'),
        sa.Column('bonus_tokens', sa.Integer(), nullable=False, comment='Number of tokens to award'),
        sa.Column('name', sa.String(255), nullable=True, comment='Campaign name for admin reference'),
        sa.Column('max_uses', sa.Integer(), nullable=True, comment='Maximum number of uses (NULL = unlimited)'),
        sa.Column('current_uses', sa.Integer(), nullable=False, server_default='0', comment='Current number of uses'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True, comment='Link expiration date (NULL = never expires)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_welcome_bonuses_invite_code', 'welcome_bonuses', ['invite_code'], unique=True)
    op.create_index('ix_welcome_bonuses_is_active', 'welcome_bonuses', ['is_active'])

    # Create welcome_bonus_uses table
    op.create_table(
        'welcome_bonus_uses',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('welcome_bonus_id', sa.BigInteger(), nullable=False, comment='ID of the welcome bonus link'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who used the link'),
        sa.Column('tokens_awarded', sa.Integer(), nullable=False, comment='Actual tokens awarded at the time of use'),
        sa.Column('subscription_id', sa.BigInteger(), nullable=True, comment='ID of created bonus subscription'),
        sa.Column('has_purchased', sa.Boolean(), nullable=False, server_default='false', comment='Whether user made a paid purchase after bonus'),
        sa.Column('first_purchase_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp of first paid purchase after bonus'),
        sa.Column('first_purchase_amount', sa.Float(), nullable=True, comment='Amount of first paid purchase'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['welcome_bonus_id'], ['welcome_bonuses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_welcome_bonus_uses_welcome_bonus_id', 'welcome_bonus_uses', ['welcome_bonus_id'])
    op.create_index('ix_welcome_bonus_uses_user_id', 'welcome_bonus_uses', ['user_id'])
    op.create_index('idx_welcome_bonus_uses_user_bonus', 'welcome_bonus_uses', ['user_id', 'welcome_bonus_id'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_welcome_bonus_uses_user_bonus', table_name='welcome_bonus_uses')
    op.drop_index('ix_welcome_bonus_uses_user_id', table_name='welcome_bonus_uses')
    op.drop_index('ix_welcome_bonus_uses_welcome_bonus_id', table_name='welcome_bonus_uses')
    op.drop_table('welcome_bonus_uses')

    op.drop_index('ix_welcome_bonuses_is_active', table_name='welcome_bonuses')
    op.drop_index('ix_welcome_bonuses_invite_code', table_name='welcome_bonuses')
    op.drop_table('welcome_bonuses')
