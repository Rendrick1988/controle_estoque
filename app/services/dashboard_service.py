from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.services.plan_limits_service import effective_int_cap
from app.services.reports_service import sales_by_day, sales_by_month, top_products, total_revenue


def get_total_sales_count(db: Session, company_id: int) -> int:
    return int(db.scalar(select(func.count(Sale.id)).where(Sale.company_id == company_id)) or 0)


def get_total_products(db: Session, company_id: int) -> int:
    return int(db.scalar(select(func.count(Product.id)).where(Product.company_id == company_id)) or 0)


def get_sales_today(db: Session, company_id: int) -> float:
    today = datetime.now(timezone.utc).date()
    query = select(func.coalesce(func.sum(Sale.total_value), 0)).where(
        and_(Sale.company_id == company_id, func.date(Sale.created_at) == today)
    )
    total_sales_today = db.scalar(query) or 0
    return float(total_sales_today)


def get_recent_sales(db: Session, company_id: int, *, limit: int = 8) -> list[dict]:
    query = (
        select(Sale.id, Sale.total_value, Sale.created_at, Sale.customer_id)
        .where(Sale.company_id == company_id)
        .order_by(Sale.created_at.desc())
        .limit(limit)
    )
    sale_rows = db.execute(query).all()
    if not sale_rows:
        return []

    customer_ids = [row.customer_id for row in sale_rows if row.customer_id is not None]
    from app.models.customer import Customer

    customer_map: dict[int, str] = {}
    if customer_ids:
        customer_query = select(Customer.id, Customer.name).where(
            and_(Customer.company_id == company_id, Customer.id.in_(customer_ids))
        )
        customer_map = {row.id: row.name for row in db.execute(customer_query).all()}
    return [
        {
            "sale_id": row.id,
            "customer_name": customer_map.get(row.customer_id, "Sem cliente cadastrado"),
            "total_value": float(row.total_value),
            "created_at": row.created_at,
        }
        for row in sale_rows
    ]


def get_alerts(db: Session, company_id: int, *, high_sales_threshold: float = 10000.0) -> list[dict]:
    alerts: list[dict] = []

    low_stock_count = db.scalar(
        select(func.count(Product.id)).where(
            and_(
                Product.company_id == company_id,
                Product.quantity > 0,
                Product.quantity <= Product.min_quantity,
            )
        )
    )
    zero_stock_count = db.scalar(
        select(func.count(Product.id)).where(and_(Product.company_id == company_id, Product.quantity == 0))
    )

    sales_today = get_sales_today(db, company_id)
    if (low_stock_count or 0) > 0:
        alerts.append(
            {
                "level": "warning",
                "category": "estoque_baixo",
                "message": f"{low_stock_count} produto(s) com estoque baixo",
            }
        )
    if (zero_stock_count or 0) > 0:
        alerts.append(
            {
                "level": "critical",
                "category": "estoque_zerado",
                "message": f"{zero_stock_count} produto(s) com estoque zerado",
            }
        )
    if sales_today >= high_sales_threshold:
        alerts.append(
            {
                "level": "info",
                "category": "venda_alta",
                "message": f"Meta de vendas altas atingida hoje (R$ {sales_today:.2f})",
            }
        )
    return alerts


def build_dashboard_payload(db: Session, company_id: int) -> dict:
    capped_day_window = effective_int_cap(db, company_id, 14, cap_key="dashboard_days", absolute_max=14)
    capped_month_window = effective_int_cap(db, company_id, 12, cap_key="dashboard_months", absolute_max=12)
    capped_top_products = effective_int_cap(db, company_id, 8, cap_key="dashboard_top", absolute_max=8)
    capped_recent_sales = effective_int_cap(db, company_id, 8, cap_key="dashboard_recent_sales", absolute_max=8)

    sales_by_day_items = sales_by_day(db, company_id, days=capped_day_window)
    sales_by_month_items = sales_by_month(db, company_id, months=capped_month_window)
    top_product_items = top_products(db, company_id, limit=capped_top_products)

    return {
        "sales_today": get_sales_today(db, company_id),
        "total_revenue": total_revenue(db, company_id),
        "total_sales_count": get_total_sales_count(db, company_id),
        "total_products": get_total_products(db, company_id),
        "recent_sales": get_recent_sales(db, company_id, limit=capped_recent_sales),
        "alerts": get_alerts(db, company_id),
        "sales_by_day": sales_by_day_items,
        "sales_by_month": sales_by_month_items,
        "sales_by_product": [
            {"product_name": top_product["product_name"], "quantity_sold": top_product["quantity_sold"]}
            for top_product in top_product_items
        ],
    }
