"""admin access, company status and full audit

Revision ID: 0003_access_admin_audit
Revises: 0002_mini_erp
Create Date: 2026-03-23

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_access_admin_audit"
down_revision = "0002_mini_erp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "companies", sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'"))
    )
    op.add_column(
        "companies", sa.Column("plan", sa.String(length=20), nullable=False, server_default=sa.text("'free'"))
    )
    op.create_index("ix_companies_status", "companies", ["status"])
    op.create_index("ix_companies_plan", "companies", ["plan"])
    op.execute("UPDATE companies SET status = 'active'")

    op.add_column(
        "users", sa.Column("role", sa.String(length=20), nullable=False, server_default=sa.text("'user'"))
    )
    op.create_index("ix_users_role", "users", ["role"])
    op.execute("UPDATE users SET role = 'user'")

    op.alter_column("audit_logs", "company_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("audit_logs", sa.Column("ip_address", sa.String(length=64), nullable=True))
    op.add_column("audit_logs", sa.Column("user_agent", sa.String(length=500), nullable=True))
    op.add_column("audit_logs", sa.Column("before_data", sa.JSON(), nullable=True))
    op.add_column("audit_logs", sa.Column("after_data", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_logs", "after_data")
    op.drop_column("audit_logs", "before_data")
    op.drop_column("audit_logs", "user_agent")
    op.drop_column("audit_logs", "ip_address")
    op.alter_column("audit_logs", "company_id", existing_type=sa.Integer(), nullable=False)

    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")

    op.drop_index("ix_companies_plan", table_name="companies")
    op.drop_index("ix_companies_status", table_name="companies")
    op.drop_column("companies", "plan")
    op.drop_column("companies", "status")
