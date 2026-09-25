from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do repositorio (app/core/config.py -> parents[2] == raiz)
_ENV_DIR = Path(__file__).resolve().parents[2]


def _normalize_database_url(value: str | None) -> str:
    normalized = (value or "").strip()
    if not normalized:
        return normalized
    if normalized.startswith("postgresql+psycopg2://"):
        return normalized
    if normalized.startswith("postgres://"):
        return "postgresql+psycopg2://" + normalized[len("postgres://") :]
    if normalized.startswith("postgresql://"):
        return "postgresql+psycopg2://" + normalized[len("postgresql://") :]
    return normalized


def _default_app_base_url() -> str:
    render_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if render_url:
        return render_url.rstrip("/")

    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway_domain:
        if railway_domain.startswith(("http://", "https://")):
            return railway_domain.rstrip("/")
        return f"https://{railway_domain}".rstrip("/")

    return "http://localhost:8000"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = ""
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_IN_RESPONSE: bool = True
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    APP_BASE_URL: str = Field(default_factory=_default_app_base_url)
    MERCADO_PAGO_ACCESS_TOKEN: str | None = None
    MERCADO_PAGO_PUBLIC_KEY: str | None = None
    MERCADO_PAGO_API_BASE_URL: str = "https://api.mercadopago.com"
    MERCADO_PAGO_NOTIFICATION_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str | None) -> str:
        return _normalize_database_url(value)

    @field_validator("APP_BASE_URL", mode="before")
    @classmethod
    def normalize_app_base_url(cls, value: str | None) -> str:
        normalized = (value or "").strip()
        if not normalized:
            return _default_app_base_url()
        return normalized.rstrip("/")


settings = Settings()

