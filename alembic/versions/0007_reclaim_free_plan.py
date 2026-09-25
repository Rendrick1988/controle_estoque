"""normalize legacy free plans before reclaiming free tier

Revision ID: 0007_reclaim_free_plan
Revises: 0006_company_billing_fields
Create Date: 2026-04-01

"""

from __future__ import annotations

from alembic import op


revision = "0007_reclaim_free_plan"
down_revision = "0006_company_billing_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE companies SET plan = 'basic' WHERE plan = 'free'")


def downgrade() -> None:
    # Nao ha como distinguir com seguranca quais registros eram legacy alias.
    pass
