from __future__ import annotations

from datetime import datetime
import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import StrictInputModel

_HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _normalize_features(values: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        value = (item or "").strip().lower()
        if not value or value in seen:
            continue
        normalized.append(value)
        seen.add(value)
    return normalized


class CompanySettingsBase(BaseModel):
    theme: Literal["light", "dark", "custom", "pink"] = "light"
    logo_url: str | None = Field(default=None, max_length=500)
    primary_color: str | None = Field(default=None, max_length=20)
    features: list[str] = Field(default_factory=list)

    @field_validator("features")
    @classmethod
    def normalize_features(cls, values: list[str]) -> list[str]:
        return _normalize_features(values)


class CompanySettingsUpdate(StrictInputModel):
    theme: Literal["light", "dark", "custom", "pink"] | None = None
    logo_url: str | None = Field(default=None, max_length=500)
    primary_color: str | None = Field(default=None, max_length=20)
    features: list[str] | None = None

    @field_validator("features")
    @classmethod
    def normalize_features(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        return _normalize_features(values)

    @field_validator("primary_color")
    @classmethod
    def validate_primary_color(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not _HEX_COLOR_PATTERN.fullmatch(value):
            raise ValueError("Informe uma cor hexadecimal válida, por exemplo #1f2937.")
        return value

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith("/uploads/logos/") or value.startswith("https://") or value.startswith("http://"):
            return value
        raise ValueError("A logo deve usar uma URL segura (http/https) ou um arquivo enviado pelo sistema.")


class CompanySettingsOut(CompanySettingsBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
