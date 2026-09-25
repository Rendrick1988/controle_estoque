from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.plans import BillingCycle, PlanCode, normalize_billing_cycle, normalize_plan
from app.schemas.base import StrictInputModel
from app.schemas.company import CompanyCreate, CompanyOut


class PlanUsageOut(BaseModel):
    """Limites e capacidades do plano atual da empresa do usuario."""

    plan: PlanCode
    exports_enabled: bool
    capabilities: list[str]
    caps: dict[str, int | None]
    used: dict[str, int]

    @field_validator("plan", mode="before")
    @classmethod
    def normalize_plan_value(cls, value: str) -> PlanCode:
        return normalize_plan(value)


class UserCreate(StrictInputModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=150)
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    company_id: int
    email: EmailStr
    full_name: str | None
    role: Literal["admin", "user"]
    is_company_owner: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserMeOut(UserOut):
    company_plan: PlanCode
    plan_usage: PlanUsageOut


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(StrictInputModel):
    company: CompanyCreate
    admin: UserCreate
    plan: PlanCode = "professional"
    billing_cycle: BillingCycle = "monthly"

    @field_validator("billing_cycle", mode="before")
    @classmethod
    def normalize_billing_cycle_value(cls, value: str) -> BillingCycle:
        return normalize_billing_cycle(value)


class RegisterResponse(BaseModel):
    company: CompanyOut
    admin: UserOut
    billing_access_token: str | None = None


class ForgotPasswordRequest(StrictInputModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Mensagem sempre similar (evita revelar se o e-mail existe). reset_token só vem preenchido quando habilitado."""

    detail: str
    reset_token: str | None = None


class ResetPasswordRequest(StrictInputModel):
    reset_token: str = Field(min_length=10, max_length=2048)
    new_password: str = Field(min_length=6, max_length=128)

