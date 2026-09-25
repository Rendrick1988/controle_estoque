from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.core.plans import BillingCycle, PaymentStatus, PlanCode, normalize_billing_cycle, normalize_payment_status, normalize_plan
from app.schemas.base import StrictInputModel


class CompanyCreate(StrictInputModel):
    name: str = Field(min_length=2, max_length=150)


class CompanyOut(BaseModel):
    id: int
    name: str
    status: Literal["pending", "active", "blocked"]
    plan: PlanCode
    billing_cycle: BillingCycle
    payment_status: PaymentStatus
    mercado_pago_reference: str | None = None
    paid_until: datetime | None = None
    created_at: datetime

    @field_validator("plan", mode="before")
    @classmethod
    def normalize_plan_value(cls, value: str) -> PlanCode:
        return normalize_plan(value)

    @field_validator("billing_cycle", mode="before")
    @classmethod
    def normalize_billing_cycle_value(cls, value: str) -> BillingCycle:
        return normalize_billing_cycle(value)

    @field_validator("payment_status", mode="before")
    @classmethod
    def normalize_payment_status_value(cls, value: str) -> PaymentStatus:
        return normalize_payment_status(value)

    class Config:
        from_attributes = True

