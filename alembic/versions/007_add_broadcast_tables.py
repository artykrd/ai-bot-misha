"""add broadcast tables

Revision ID: 007
Revises: 006
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_broadcast_tables'
down_revision = '006_add_video_jobs_and_feature_flags'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create broadcast_messages table
    op.create_table(
        'broadcast_messages',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('admin_id', sa.BigInteger(), nullable=True, comment='Admin user who created the broadcast'),
        sa.Column('text', sa.Text(), nullable=False, comment='Message text content'),
        sa.Column('image_file_id', sa.String(length=255), nullable=True, comment='Telegram file_id for attached photo'),
        sa.Column('buttons', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='List of inline buttons'),
        sa.Column('filter_type', sa.String(length=50), nullable=False, comment='Filter: all, subscribed, free'),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0', comment='Number of successfully sent messages'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0', comment='Number of failed deliveries'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_broadcast_messages_admin_id', 'broadcast_messages', ['admin_id'])
    op.create_index('ix_broadcast_messages_filter_type', 'broadcast_messages', ['filter_type'])

    # Create broadcast_clicks table
    op.create_table(
        'broadcast_clicks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('broadcast_id', sa.BigInteger(), nullable=False, comment='Reference to broadcast message'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who clicked the button'),
        sa.Column('button_index', sa.Integer(), nullable=False, comment='0-based index of button in buttons array'),
        sa.Column('button_text', sa.String(length=255), nullable=False, comment='Button text for convenient querying'),
        sa.Column('button_callback_data', sa.String(length=255), nullable=False, comment='Full callback_data'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['broadcast_id'], ['broadcast_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_broadcast_clicks_broadcast_id', 'broadcast_clicks', ['broadcast_id'])
    op.create_index('ix_broadcast_clicks_user_id', 'broadcast_clicks', ['user_id'])
    op.create_index('ix_broadcast_clicks_button_callback_data', 'broadcast_clicks', ['button_callback_data'])
    op.create_index('idx_broadcast_clicks_broadcast_user', 'broadcast_clicks', ['broadcast_id', 'user_id'])
    op.create_index('idx_broadcast_clicks_created', 'broadcast_clicks', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_broadcast_clicks_created', table_name='broadcast_clicks')
    op.drop_index('idx_broadcast_clicks_broadcast_user', table_name='broadcast_clicks')
    op.drop_index('ix_broadcast_clicks_button_callback_data', table_name='broadcast_clicks')
    op.drop_index('ix_broadcast_clicks_user_id', table_name='broadcast_clicks')
    op.drop_index('ix_broadcast_clicks_broadcast_id', table_name='broadcast_clicks')
    op.drop_table('broadcast_clicks')

    op.drop_index('ix_broadcast_messages_filter_type', table_name='broadcast_messages')
    op.drop_index('ix_broadcast_messages_admin_id', table_name='broadcast_messages')
    op.drop_table('broadcast_messages')
