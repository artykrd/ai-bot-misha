"""make payments.yukassa_payment_id unique (idempotent crediting)

Defence-in-depth against double-crediting the same payment (YooKassa webhook
retries / Telegram Stars successful_payment redelivery). Verified there are no
existing duplicates before adding the constraint.

Revision ID: 011_unique_yukassa_payment_id
Revises: 010_add_welcome_bonus_tables
Create Date: 2026-06-19

"""
from alembic import op


revision = '011_unique_yukassa_payment_id'
down_revision = '010_add_welcome_bonus_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Replace the existing non-unique index with a unique one. NULLs remain
    # distinct in Postgres, so legacy rows without an external id are unaffected.
    op.drop_index('ix_payments_yukassa_payment_id', table_name='payments')
    op.create_index(
        'ix_payments_yukassa_payment_id',
        'payments',
        ['yukassa_payment_id'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_payments_yukassa_payment_id', table_name='payments')
    op.create_index(
        'ix_payments_yukassa_payment_id',
        'payments',
        ['yukassa_payment_id'],
        unique=False,
    )
