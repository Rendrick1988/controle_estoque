from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.plans import normalize_plan, plan_capabilities, plan_caps, plan_supports
from app.models.company import Company
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User


def company_plan(db: Session, company_id: int) -> str:
    company = db.get(Company, company_id)
    return normalize_plan(company.plan if company else None)


def company_cap_value(db: Session, company_id: int, cap_key: str) -> int | None:
    return plan_caps(company_plan(db, company_id)).get(cap_key)


def company_supports(db: Session, company_id: int, capability: str) -> bool:
    return plan_supports(company_plan(db, company_id), capability)


def ensure_premium_exports(db: Session, company_id: int) -> None:
    if not company_supports(db, company_id, "exports"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Exportação em PDF e relatório para impressão não estão liberados para o plano atual.",
        )


def _count_products(db: Session, company_id: int) -> int:
    return int(db.scalar(select(func.count(Product.id)).where(Product.company_id == company_id)) or 0)


def _count_customers(db: Session, company_id: int) -> int:
    return int(db.scalar(select(func.count(Customer.id)).where(Customer.company_id == company_id)) or 0)


def _count_users(db: Session, company_id: int) -> int:
    return int(db.scalar(select(func.count(User.id)).where(User.company_id == company_id)) or 0)


def _count_sales(db: Session, company_id: int) -> int:
    return int(db.scalar(select(func.count(Sale.id)).where(Sale.company_id == company_id)) or 0)


def usage_counts(db: Session, company_id: int) -> dict[str, int]:
    return {
        "products": _count_products(db, company_id),
        "customers": _count_customers(db, company_id),
        "users": _count_users(db, company_id),
        "sales": _count_sales(db, company_id),
    }


def plan_usage_public(db: Session, company_id: int) -> dict:
    plan = company_plan(db, company_id)
    return {
        "plan": plan,
        "exports_enabled": plan_supports(plan, "exports"),
        "capabilities": plan_capabilities(plan),
        "caps": {
            "products": plan_caps(plan).get("products"),
            "customers": plan_caps(plan).get("customers"),
            "users": plan_caps(plan).get("users"),
            "sales": plan_caps(plan).get("sales"),
            "report_history": plan_caps(plan).get("report_history"),
            "audit_logs": plan_caps(plan).get("audit_logs"),
            "sales_list": plan_caps(plan).get("sales_list"),
            "report_days": plan_caps(plan).get("report_days"),
            "report_months": plan_caps(plan).get("report_months"),
            "top_products": plan_caps(plan).get("top_products"),
        },
        "used": usage_counts(db, company_id),
    }


def _enforce_count_cap(
    *,
    current: int,
    limit: int | None,
    detail_unavailable: str,
    detail_limited: str,
) -> None:
    if limit is None:
        return
    if limit <= 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail_unavailable)
    if current >= limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail_limited)


def enforce_product_cap(db: Session, company_id: int) -> None:
    limit = company_cap_value(db, company_id, "products")
    _enforce_count_cap(
        current=_count_products(db, company_id),
        limit=limit,
        detail_unavailable="Seu plano atual não permite cadastrar produtos.",
        detail_limited=f"Plano atual: limite de {limit} produtos. Faça upgrade para continuar cadastrando.",
    )


def enforce_customer_cap(db: Session, company_id: int) -> None:
    limit = company_cap_value(db, company_id, "customers")
    _enforce_count_cap(
        current=_count_customers(db, company_id),
        limit=limit,
        detail_unavailable="Seu plano atual não inclui o módulo de clientes.",
        detail_limited=f"Plano atual: limite de {limit} clientes. Faça upgrade para continuar cadastrando.",
    )


def enforce_user_cap(db: Session, company_id: int) -> None:
    limit = company_cap_value(db, company_id, "users")
    _enforce_count_cap(
        current=_count_users(db, company_id),
        limit=limit,
        detail_unavailable="Seu plano atual não permite múltiplos usuários.",
        detail_limited=f"Plano atual: até {limit} usuários na empresa. Faça upgrade para liberar mais acessos.",
    )


def enforce_sale_cap(db: Session, company_id: int) -> None:
    limit = company_cap_value(db, company_id, "sales")
    _enforce_count_cap(
        current=_count_sales(db, company_id),
        limit=limit,
        detail_unavailable="Seu plano atual não permite registrar vendas.",
        detail_limited=f"Plano atual: limite de {limit} vendas registradas. Faça upgrade para continuar operando.",
    )


def effective_int_cap(
    db: Session,
    company_id: int,
    requested: int,
    *,
    cap_key: str,
    absolute_max: int,
) -> int:
    resolved = max(1, min(requested, absolute_max))
    limit = company_cap_value(db, company_id, cap_key)
    if limit is None:
        return resolved
    if limit <= 0:
        return 1
    return min(resolved, limit)
