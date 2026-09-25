from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class DashboardSaleByDay(BaseModel):
    day: date
    total: float


class DashboardSaleByMonth(BaseModel):
    month: str
    total: float


class DashboardProductSeries(BaseModel):
    product_name: str
    quantity_sold: float


class DashboardRecentSale(BaseModel):
    sale_id: int
    customer_name: str
    total_value: float
    created_at: datetime


class DashboardAlert(BaseModel):
    level: str
    category: str
    message: str


class DashboardSummaryOut(BaseModel):
    sales_today: float
    total_revenue: float
    total_sales_count: int
    total_products: int
    recent_sales: list[DashboardRecentSale]
    alerts: list[DashboardAlert]
    sales_by_day: list[DashboardSaleByDay]
    sales_by_month: list[DashboardSaleByMonth]
    sales_by_product: list[DashboardProductSeries]
