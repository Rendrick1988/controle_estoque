from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.authorization import require_company_permission
from app.dependencies.feature_flags import require_feature
from app.dependencies.plan_access import require_plan_capability
from app.models.company import Company
from app.models.user import User
from app.schemas.report import (
    PrintExportResponse,
    RevenueSummary,
    SaleHistoryItem,
    SalesByDayItem,
    SalesByMonthItem,
    TopProductItem,
)
from app.services.plan_limits_service import (
    effective_int_cap,
    ensure_premium_exports,
)
from app.services.reports_service import (
    build_printable_report_html,
    build_sales_report_pdf,
    sales_by_day,
    sales_by_month,
    sales_history,
    top_products,
    total_revenue,
)

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"],
    dependencies=[Depends(require_plan_capability("relatorio")), Depends(require_feature("relatorio"))],
)


def _get_company_name(db: Session, company_id: int) -> str:
    company = db.scalar(select(Company).where(Company.id == company_id))
    return company.name if company else f"Empresa {company_id}"


@router.get("/sales-by-day", response_model=list[SalesByDayItem])
def report_sales_by_day(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:read")),
):
    company_id = current_user.company_id
    capped_days = effective_int_cap(db, company_id, days, cap_key="report_days", absolute_max=365)
    return sales_by_day(db, company_id, days=capped_days)


@router.get("/sales-by-month", response_model=list[SalesByMonthItem])
def report_sales_by_month(
    months: int = Query(default=12, ge=1, le=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:read")),
):
    company_id = current_user.company_id
    capped_months = effective_int_cap(db, company_id, months, cap_key="report_months", absolute_max=36)
    return sales_by_month(db, company_id, months=capped_months)


@router.get("/total-revenue", response_model=RevenueSummary)
def report_total_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:read")),
):
    return {"total_revenue": total_revenue(db, current_user.company_id)}


@router.get("/top-products", response_model=list[TopProductItem])
def report_top_products(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:read")),
):
    company_id = current_user.company_id
    capped_limit = effective_int_cap(db, company_id, limit, cap_key="top_products", absolute_max=50)
    return top_products(db, company_id, limit=capped_limit)


@router.get("/history", response_model=list[SaleHistoryItem])
def report_history(
    limit: int = Query(default=300, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:read")),
):
    company_id = current_user.company_id
    capped_limit = effective_int_cap(db, company_id, limit, cap_key="report_history", absolute_max=1000)
    return sales_history(db, company_id, limit=capped_limit)


@router.get("/export/print", response_model=PrintExportResponse)
def export_print(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:export")),
):
    ensure_premium_exports(db, current_user.company_id)
    capped_days = effective_int_cap(db, current_user.company_id, 30, cap_key="report_days", absolute_max=365)
    capped_months = effective_int_cap(db, current_user.company_id, 12, cap_key="report_months", absolute_max=36)
    capped_top_limit = effective_int_cap(db, current_user.company_id, 10, cap_key="top_products", absolute_max=50)
    revenue = total_revenue(db, current_user.company_id)
    sales_by_day_items = sales_by_day(db, current_user.company_id, days=capped_days)
    sales_by_month_items = sales_by_month(db, current_user.company_id, months=capped_months)
    top_product_items = top_products(db, current_user.company_id, limit=capped_top_limit)
    html = build_printable_report_html(
        company_name=_get_company_name(db, current_user.company_id),
        revenue=revenue,
        sales_by_day_items=sales_by_day_items,
        sales_by_month_items=sales_by_month_items,
        top_products_items=top_product_items,
    )
    return {"html": html}


@router.get("/export/print/page", response_class=HTMLResponse)
def export_print_page(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:export")),
):
    ensure_premium_exports(db, current_user.company_id)
    capped_days = effective_int_cap(db, current_user.company_id, 30, cap_key="report_days", absolute_max=365)
    capped_months = effective_int_cap(db, current_user.company_id, 12, cap_key="report_months", absolute_max=36)
    capped_top_limit = effective_int_cap(db, current_user.company_id, 10, cap_key="top_products", absolute_max=50)
    revenue = total_revenue(db, current_user.company_id)
    sales_by_day_items = sales_by_day(db, current_user.company_id, days=capped_days)
    sales_by_month_items = sales_by_month(db, current_user.company_id, months=capped_months)
    top_product_items = top_products(db, current_user.company_id, limit=capped_top_limit)
    html = build_printable_report_html(
        company_name=_get_company_name(db, current_user.company_id),
        revenue=revenue,
        sales_by_day_items=sales_by_day_items,
        sales_by_month_items=sales_by_month_items,
        top_products_items=top_product_items,
    )
    return HTMLResponse(content=html)


@router.get("/export/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("reports:export")),
):
    ensure_premium_exports(db, current_user.company_id)
    capped_days = effective_int_cap(db, current_user.company_id, 30, cap_key="report_days", absolute_max=365)
    capped_months = effective_int_cap(db, current_user.company_id, 12, cap_key="report_months", absolute_max=36)
    capped_top_limit = effective_int_cap(db, current_user.company_id, 10, cap_key="top_products", absolute_max=50)
    revenue = total_revenue(db, current_user.company_id)
    sales_by_day_items = sales_by_day(db, current_user.company_id, days=capped_days)
    sales_by_month_items = sales_by_month(db, current_user.company_id, months=capped_months)
    top_product_items = top_products(db, current_user.company_id, limit=capped_top_limit)
    pdf_bytes = build_sales_report_pdf(
        company_name=_get_company_name(db, current_user.company_id),
        revenue=revenue,
        sales_by_day_items=sales_by_day_items,
        sales_by_month_items=sales_by_month_items,
        top_products_items=top_product_items,
    )
    headers = {"Content-Disposition": "attachment; filename=relatorio-vendas.pdf"}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
