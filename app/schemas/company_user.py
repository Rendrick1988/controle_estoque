from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import StrictInputModel


class CompanyUserCreate(StrictInputModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=150)
    password: str = Field(min_length=6, max_length=128)
    profile: Literal["owner", "collaborator"] = "collaborator"
    is_active: bool = True


class CompanyUserUpdate(StrictInputModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=150)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    profile: Literal["owner", "collaborator"] | None = None
    is_active: bool | None = None


class CompanyUserOut(BaseModel):
    id: int
    company_id: int
    email: EmailStr
    full_name: str | None
    profile: Literal["owner", "collaborator"]
    is_company_owner: bool
    is_active: bool
    is_current_user: bool
    created_at: datetime
