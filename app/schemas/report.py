from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class SalesByDayItem(BaseModel):
    day: date
    total: float


class SalesByMonthItem(BaseModel):
    month: str
    total: float


class RevenueSummary(BaseModel):
    total_revenue: float


class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: float
    revenue: float


class SaleHistoryItem(BaseModel):
    sale_id: int
    customer_name: str
    total_value: float
    created_at: datetime


class PrintExportResponse(BaseModel):
    html: str
