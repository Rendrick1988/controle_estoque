"""add billing fields to companies

Revision ID: 0006_company_billing_fields
Revises: 0005_company_owner
Create Date: 2026-04-01

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_company_billing_fields"
down_revision = "0005_company_owner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("billing_cycle", sa.String(length=20), nullable=False, server_default=sa.text("'monthly'")),
    )
    op.add_column(
        "companies",
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
    )
    op.add_column("companies", sa.Column("mercado_pago_reference", sa.String(length=120), nullable=True))
    op.add_column("companies", sa.Column("paid_until", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_companies_billing_cycle"), "companies", ["billing_cycle"], unique=False)
    op.create_index(op.f("ix_companies_payment_status"), "companies", ["payment_status"], unique=False)
    op.create_index(op.f("ix_companies_mercado_pago_reference"), "companies", ["mercado_pago_reference"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_mercado_pago_reference"), table_name="companies")
    op.drop_index(op.f("ix_companies_payment_status"), table_name="companies")
    op.drop_index(op.f("ix_companies_billing_cycle"), table_name="companies")
    op.drop_column("companies", "paid_until")
    op.drop_column("companies", "mercado_pago_reference")
    op.drop_column("companies", "payment_status")
    op.drop_column("companies", "billing_cycle")
