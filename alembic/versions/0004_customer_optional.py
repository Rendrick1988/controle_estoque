"""allow sales without customer

Revision ID: 0004_customer_optional
Revises: 0003_access_admin_audit
Create Date: 2026-03-23

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_customer_optional"
down_revision = "0003_access_admin_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("sales", "customer_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("sales", "customer_id", existing_type=sa.Integer(), nullable=False)
