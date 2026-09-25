from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.base import StrictInputModel


class ProductBase(StrictInputModel):
    name: str = Field(min_length=2, max_length=150)
    sku: str = Field(min_length=1, max_length=80)
    validity: datetime
    description: str | None = None
    quantity: int = Field(ge=0)
    min_quantity: int = Field(ge=0)
    price: float = Field(ge=0)
    sold_by_weight: bool = False
    weight_stock_kg: float | None = Field(default=None, ge=0)
    min_weight_kg: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_weight_fields(self) -> ProductBase:
        if self.sold_by_weight:
            if self.weight_stock_kg is None:
                raise ValueError("Informe o estoque em kg para produtos vendidos por peso")
            if self.min_weight_kg is None:
                raise ValueError("Informe o estoque mínimo em kg para produtos vendidos por peso")
        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(StrictInputModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    sku: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    validity: datetime | None = None
    quantity: int | None = Field(default=None, ge=0)
    min_quantity: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, ge=0)
    sold_by_weight: bool | None = None
    weight_stock_kg: float | None = Field(default=None, ge=0)
    min_weight_kg: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_weight_fields(self) -> ProductUpdate:
        if self.sold_by_weight is True:
            if self.weight_stock_kg is None:
                raise ValueError("Informe o estoque em kg para produtos vendidos por peso")
            if self.min_weight_kg is None:
                raise ValueError("Informe o estoque mínimo em kg para produtos vendidos por peso")
        return self


class ProductOut(BaseModel):
    id: int
    company_id: int
    name: str
    sku: str
    description: str | None
    quantity: int
    validity: datetime
    min_quantity: int
    price: float
    sold_by_weight: bool
    weight_stock_kg: float | None
    min_weight_kg: float | None
    created_at: datetime
    updated_at: datetime | None

    @field_validator("weight_stock_kg", "min_weight_kg", mode="before")
    @classmethod
    def decimal_to_float(cls, value: object) -> float | None:
        if value is None:
            return None
        return float(value)

    class Config:
        from_attributes = True


class StockChartItem(BaseModel):
    name: str
    quantity: int
    validity: datetime
