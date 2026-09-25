from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import StrictInputModel


def _empty_str_to_none(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


class CustomerBase(StrictInputModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr | None = None
    cpf: str | None = None
    phone: str = Field(min_length=8, max_length=30)

    @field_validator("email", "cpf", mode="before")
    @classmethod
    def optional_strings(cls, value: object) -> object:
        return _empty_str_to_none(value)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(StrictInputModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    cpf: str | None = None
    phone: str | None = Field(default=None, min_length=8, max_length=30)

    @field_validator("email", "cpf", mode="before")
    @classmethod
    def optional_strings(cls, value: object) -> object:
        return _empty_str_to_none(value)


class CustomerOut(BaseModel):
    id: int
    company_id: int
    name: str
    email: EmailStr | None = None
    cpf: str | None = None
    phone: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
