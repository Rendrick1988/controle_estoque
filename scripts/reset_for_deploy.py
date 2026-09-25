from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.audit_log import AuditLog
from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.user import User


TABLE_LABELS = {
    "companies": "Empresas",
    "users": "Usuarios",
    "company_settings": "Configuracoes da empresa",
    "products": "Produtos",
    "customers": "Clientes",
    "sales": "Vendas",
    "sale_items": "Itens de venda",
    "audit_logs": "Auditoria",
}


@dataclass
class ResetSummary:
    preserved_admin_user_ids: list[int]
    preserved_admin_company_ids: list[int]
    deleted_counts: dict[str, int]
    remaining_counts: dict[str, int]


def count_rows(db: Session) -> dict[str, int]:
    return {
        "companies": int(db.scalar(select(func.count(Company.id))) or 0),
        "users": int(db.scalar(select(func.count(User.id))) or 0),
        "company_settings": int(db.scalar(select(func.count(CompanySettings.id))) or 0),
        "products": int(db.scalar(select(func.count(Product.id))) or 0),
        "customers": int(db.scalar(select(func.count(Customer.id))) or 0),
        "sales": int(db.scalar(select(func.count(Sale.id))) or 0),
        "sale_items": int(db.scalar(select(func.count(SaleItem.id))) or 0),
        "audit_logs": int(db.scalar(select(func.count(AuditLog.id))) or 0),
    }


def admin_scope(db: Session) -> tuple[list[int], list[int]]:
    admin_users = list(
        db.scalars(select(User).where(User.role == "admin").order_by(User.id.asc())).all()
    )
    admin_user_ids = [user.id for user in admin_users]
    admin_company_ids = sorted({user.company_id for user in admin_users})
    return admin_user_ids, admin_company_ids


def delete_non_admin_rows(db: Session, admin_company_ids: list[int], admin_user_ids: list[int]) -> dict[str, int]:
    deleted_counts: dict[str, int] = {}

    deleted_counts["audit_logs"] = db.execute(delete(AuditLog)).rowcount or 0
    deleted_counts["sale_items"] = db.execute(delete(SaleItem)).rowcount or 0
    deleted_counts["sales"] = db.execute(delete(Sale)).rowcount or 0
    deleted_counts["customers"] = db.execute(delete(Customer)).rowcount or 0
    deleted_counts["products"] = db.execute(delete(Product)).rowcount or 0

    if admin_user_ids:
        deleted_counts["users"] = (
            db.execute(delete(User).where(User.id.not_in(admin_user_ids))).rowcount or 0
        )
    else:
        deleted_counts["users"] = db.execute(delete(User)).rowcount or 0

    if admin_company_ids:
        deleted_counts["company_settings"] = (
            db.execute(delete(CompanySettings).where(CompanySettings.company_id.not_in(admin_company_ids))).rowcount
            or 0
        )
        deleted_counts["companies"] = (
            db.execute(delete(Company).where(Company.id.not_in(admin_company_ids))).rowcount or 0
        )
    else:
        deleted_counts["company_settings"] = db.execute(delete(CompanySettings)).rowcount or 0
        deleted_counts["companies"] = db.execute(delete(Company)).rowcount or 0

    return deleted_counts


def build_summary(
    before_counts: dict[str, int],
    after_counts: dict[str, int],
    admin_user_ids: list[int],
    admin_company_ids: list[int],
) -> ResetSummary:
    deleted_counts = {
        table_name: before_counts[table_name] - after_counts[table_name]
        for table_name in before_counts
    }
    return ResetSummary(
        preserved_admin_user_ids=admin_user_ids,
        preserved_admin_company_ids=admin_company_ids,
        deleted_counts=deleted_counts,
        remaining_counts=after_counts,
    )


def print_summary(summary: ResetSummary, *, applied: bool) -> None:
    title = "Limpeza aplicada" if applied else "Previa da limpeza"
    print(title)
    print(f"Admins preservados (usuarios): {summary.preserved_admin_user_ids or 'nenhum'}")
    print(f"Admins preservados (empresas): {summary.preserved_admin_company_ids or 'nenhuma'}")
    for table_name in TABLE_LABELS:
        label = TABLE_LABELS[table_name]
        print(
            f"- {label}: removidos={summary.deleted_counts[table_name]} "
            f"restantes={summary.remaining_counts[table_name]}"
        )


def run_reset(*, apply_changes: bool) -> ResetSummary:
    db = SessionLocal()
    try:
        before_counts = count_rows(db)
        admin_user_ids, admin_company_ids = admin_scope(db)
        delete_non_admin_rows(db, admin_company_ids, admin_user_ids)
        after_counts = count_rows(db)
        summary = build_summary(before_counts, after_counts, admin_user_ids, admin_company_ids)
        if apply_changes:
            db.commit()
        else:
            db.rollback()
        return summary
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Limpa a base local para deploy, preservando apenas usuarios admin "
            "e as empresas desses admins."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica a limpeza. Sem essa flag, executa apenas uma previa sem alterar os dados.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_reset(apply_changes=args.apply)
    print_summary(summary, applied=args.apply)
    if not args.apply:
        print("Nenhum dado foi alterado. Rode novamente com --apply para executar a limpeza.")


if __name__ == "__main__":
    main()
