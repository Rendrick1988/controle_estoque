from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.core.plans import BillingCycle, PaymentStatus, PlanCode
from app.schemas.base import StrictInputModel


class BillingCheckoutRequest(StrictInputModel):
    plan: PlanCode
    billing_cycle: BillingCycle = "monthly"
    billing_access_token: str = Field(min_length=20, max_length=2048)
    company_name: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None


class BillingCheckoutOut(BaseModel):
    provider: str = "mercado_pago"
    checkout_url: str
    sandbox_checkout_url: str | None = None
    plan: PlanCode
    billing_cycle: BillingCycle


class BillingCheckoutConfirmOut(BaseModel):
    provider: str = "mercado_pago"
    provider_status: str | None = None
    company_id: int | None = None
    status: str | None = None
    payment_status: PaymentStatus | None = None
    plan: PlanCode | None = None
    billing_cycle: BillingCycle | None = None
    access_released: bool = False
    message: str


class PublicPlanOfferOut(BaseModel):
    code: PlanCode
    name: str
    badge: str
    monthly_price: float
    annual_price: float
    audience: list[str]
    includes: list[str]
    why: str


class PublicPlanCatalogOut(BaseModel):
    payment_provider: str = "mercado_pago"
    annual_discount_copy: str
    offers: list[PublicPlanOfferOut]
