from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.base import StrictInputModel


class SaleItemCreate(StrictInputModel):
    product_id: int = Field(gt=0)
    quantity: int | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def quantity_or_weight(self) -> SaleItemCreate:
        has_qty = self.quantity is not None and self.quantity > 0
        has_weight = self.weight_kg is not None and self.weight_kg > 0
        if has_qty == has_weight:
            raise ValueError("Informe quantidade (unidades) ou peso (kg), apenas um dos dois")
        return self


class SaleCreate(StrictInputModel):
    customer_id: int | None = Field(default=None, gt=0)
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleItemOut(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: int | None
    weight_kg: float | None
    price: float
    product_name: str | None = None
    sale_unit: Literal["quantity", "weight"] = "quantity"

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    customer_id: int | None
    customer_name: str | None = None
    total_value: float
    created_at: datetime
    company_id: int
    items: list[SaleItemOut]

    class Config:
        from_attributes = True


class SaleListItem(BaseModel):
    id: int
    customer_id: int | None
    customer_name: str
    total_value: float
    created_at: datetime
    items_count: int
