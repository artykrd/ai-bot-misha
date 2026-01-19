"""Add referral balances table

Revision ID: 004_add_referral_balances
Revises: 003_populate_ai_models
Create Date: 2025-02-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_referral_balances'
down_revision = '003_populate_ai_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'referral_balances',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('tokens_balance', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('money_balance', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_referral_balances_user_id'), 'referral_balances', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_referral_balances_user_id'), table_name='referral_balances')
    op.drop_table('referral_balances')
