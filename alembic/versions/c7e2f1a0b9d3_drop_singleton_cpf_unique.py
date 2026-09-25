"""remove global unique on customers.cpf (keep company_id+cpf)

Revision ID: c7e2f1a0b9d3
Revises: 5b8a849fe51b
Create Date: 2026-05-13

"""
from __future__ import annotations

from alembic import op
from sqlalchemy import inspect


revision = "c7e2f1a0b9d3"
down_revision = "5b8a849fe51b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    for uc in insp.get_unique_constraints("customers"):
        cols = tuple(uc.get("column_names") or ())
        if cols == ("cpf",):
            op.drop_constraint(uc["name"], "customers", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(None, "customers", ["cpf"])
