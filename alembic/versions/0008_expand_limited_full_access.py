"""expand free and basic defaults to full access with limits

Revision ID: 0008_expand_limited_full_access
Revises: 0007_reclaim_free_plan
Create Date: 2026-04-01

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0008_expand_limited_full_access"
down_revision = "0007_reclaim_free_plan"
branch_labels = None
depends_on = None

EXPANDED_FEATURES = ["vendas", "relatorio", "dashboard_avancado"]


def _normalize(features: object) -> list[str]:
    if not isinstance(features, list):
        return []
    normalized: list[str] = []
    for item in features:
        value = str(item or "").strip().lower()
        if value:
            normalized.append(value)
    return normalized


def upgrade() -> None:
    bind = op.get_bind()
    company_settings = sa.table(
        "company_settings",
        sa.column("id", sa.Integer()),
        sa.column("company_id", sa.Integer()),
        sa.column("features", sa.JSON()),
    )
    companies = sa.table(
        "companies",
        sa.column("id", sa.Integer()),
        sa.column("plan", sa.String()),
    )

    rows = bind.execute(
        sa.select(
            company_settings.c.id,
            company_settings.c.features,
            companies.c.plan,
        ).select_from(company_settings.join(companies, company_settings.c.company_id == companies.c.id))
    ).mappings()

    for row in rows:
        current = _normalize(row["features"])
        plan = str(row["plan"] or "").strip().lower()
        should_expand = (plan == "free" and current == []) or (plan == "basic" and current == ["vendas"])
        if not should_expand:
            continue
        bind.execute(
            company_settings.update()
            .where(company_settings.c.id == row["id"])
            .values(features=EXPANDED_FEATURES)
        )


def downgrade() -> None:
    bind = op.get_bind()
    company_settings = sa.table(
        "company_settings",
        sa.column("id", sa.Integer()),
        sa.column("company_id", sa.Integer()),
        sa.column("features", sa.JSON()),
    )
    companies = sa.table(
        "companies",
        sa.column("id", sa.Integer()),
        sa.column("plan", sa.String()),
    )

    rows = bind.execute(
        sa.select(
            company_settings.c.id,
            companies.c.plan,
            company_settings.c.features,
        ).select_from(company_settings.join(companies, company_settings.c.company_id == companies.c.id))
    ).mappings()

    for row in rows:
        if _normalize(row["features"]) != EXPANDED_FEATURES:
            continue
        plan = str(row["plan"] or "").strip().lower()
        fallback = [] if plan == "free" else ["vendas"] if plan == "basic" else None
        if fallback is None:
            continue
        bind.execute(
            company_settings.update()
            .where(company_settings.c.id == row["id"])
            .values(features=fallback)
        )
