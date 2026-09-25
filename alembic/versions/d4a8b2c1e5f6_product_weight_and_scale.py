"""product weight fields and sale item weight

Revision ID: d4a8b2c1e5f6
Revises: c7e2f1a0b9d3
Create Date: 2026-05-18

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d4a8b2c1e5f6"
down_revision = "c7e2f1a0b9d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("sold_by_weight", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "products",
        sa.Column("weight_stock_kg", sa.Numeric(12, 3), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("min_weight_kg", sa.Numeric(12, 3), nullable=True),
    )
    op.add_column(
        "sale_items",
        sa.Column("weight_kg", sa.Numeric(12, 3), nullable=True),
    )
    op.alter_column("sale_items", "quantity", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.execute(sa.text("UPDATE sale_items SET quantity = 1 WHERE quantity IS NULL"))
    op.alter_column("sale_items", "quantity", existing_type=sa.Integer(), nullable=False)
    op.drop_column("sale_items", "weight_kg")
    op.drop_column("products", "min_weight_kg")
    op.drop_column("products", "weight_stock_kg")
    op.drop_column("products", "sold_by_weight")
