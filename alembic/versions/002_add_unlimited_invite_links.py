"""Add unlimited invite links tables

Revision ID: 002_add_unlimited_invite_links
Revises: 001_initial
Create Date: 2025-12-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_unlimited_invite_links'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create unlimited_invite_links table
    op.create_table('unlimited_invite_links',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('invite_code', sa.String(length=50), nullable=False),
    sa.Column('duration_days', sa.Integer(), nullable=False),
    sa.Column('max_uses', sa.Integer(), nullable=True),
    sa.Column('current_uses', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unlimited_invite_links_invite_code'), 'unlimited_invite_links', ['invite_code'], unique=True)
    op.create_index(op.f('ix_unlimited_invite_links_is_active'), 'unlimited_invite_links', ['is_active'], unique=False)

    # Create unlimited_invite_uses table
    op.create_table('unlimited_invite_uses',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('invite_link_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('subscription_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['invite_link_id'], ['unlimited_invite_links.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unlimited_invite_uses_invite_link_id'), 'unlimited_invite_uses', ['invite_link_id'], unique=False)
    op.create_index(op.f('ix_unlimited_invite_uses_user_id'), 'unlimited_invite_uses', ['user_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_unlimited_invite_uses_user_id'), table_name='unlimited_invite_uses')
    op.drop_index(op.f('ix_unlimited_invite_uses_invite_link_id'), table_name='unlimited_invite_uses')
    op.drop_table('unlimited_invite_uses')

    op.drop_index(op.f('ix_unlimited_invite_links_is_active'), table_name='unlimited_invite_links')
    op.drop_index(op.f('ix_unlimited_invite_links_invite_code'), table_name='unlimited_invite_links')
    op.drop_table('unlimited_invite_links')
