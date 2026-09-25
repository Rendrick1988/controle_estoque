"""add company owner flag to users

Revision ID: 0005_company_owner
Revises: 0004_customer_optional
Create Date: 2026-03-23

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_company_owner"
down_revision = "0004_customer_optional"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_company_owner", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.alter_column(
        "users",
        "is_company_owner",
        existing_type=sa.Boolean(),
        existing_nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    op.drop_column("users", "is_company_owner")
