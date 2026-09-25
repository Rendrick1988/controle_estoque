from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.plans import default_features_for_plan, sanitize_features_for_plan
from app.models.company import Company
from app.models.company_settings import CompanySettings

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WEB_DIR = _REPO_ROOT / "web"
_COMPANY_LOGO_UPLOAD_DIR = _WEB_DIR / "uploads" / "logos"
_COMPANY_LOGO_URL_PREFIX = "/uploads/logos/"
_SETTINGS_FIELD_UNSET = object()


def normalize_features(features: list[str] | None) -> list[str]:
    if not features:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for feature_name in features:
        normalized_feature = (feature_name or "").strip().lower()
        if not normalized_feature or normalized_feature in seen:
            continue
        normalized.append(normalized_feature)
        seen.add(normalized_feature)
    return normalized


def get_or_create_company_settings(db: Session, company_id: int) -> CompanySettings:
    company = db.get(Company, company_id)
    company_plan = company.plan if company else None
    query = select(CompanySettings).where(CompanySettings.company_id == company_id)
    settings = db.scalar(query)
    if settings:
        sanitized = sanitize_features_for_plan(company_plan, normalize_features(settings.features))
        if settings.features != sanitized:
            settings.features = sanitized
            db.commit()
            db.refresh(settings)
            return settings
        settings.features = sanitized
        return settings

    settings = CompanySettings(
        company_id=company_id,
        theme="light",
        primary_color="#7c5cff",
        features=default_features_for_plan(company_plan),
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_company_settings(
    db: Session,
    company_id: int,
    *,
    theme: str | object = _SETTINGS_FIELD_UNSET,
    logo_url: str | None | object = _SETTINGS_FIELD_UNSET,
    primary_color: str | None | object = _SETTINGS_FIELD_UNSET,
    features: list[str] | None | object = _SETTINGS_FIELD_UNSET,
) -> CompanySettings:
    settings = get_or_create_company_settings(db, company_id)
    company = db.get(Company, company_id)
    company_plan = company.plan if company else None
    if theme is not _SETTINGS_FIELD_UNSET:
        settings.theme = theme
    if logo_url is not _SETTINGS_FIELD_UNSET:
        if settings.logo_url != (logo_url or None):
            _delete_uploaded_company_logo(settings.logo_url)
        settings.logo_url = logo_url or None
    if primary_color is not _SETTINGS_FIELD_UNSET:
        settings.primary_color = primary_color or None
    if features is not _SETTINGS_FIELD_UNSET:
        settings.features = sanitize_features_for_plan(company_plan, normalize_features(features))

    db.commit()
    db.refresh(settings)
    return settings


def save_company_logo(
    db: Session,
    company_id: int,
    *,
    logo_bytes: bytes,
    file_extension: str,
) -> CompanySettings:
    settings = get_or_create_company_settings(db, company_id)
    _delete_uploaded_company_logo(settings.logo_url)

    _COMPANY_LOGO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logo_filename = f"company-{company_id}-{uuid4().hex}{file_extension}"
    logo_path = _COMPANY_LOGO_UPLOAD_DIR / logo_filename
    logo_path.write_bytes(logo_bytes)

    settings.logo_url = f"{_COMPANY_LOGO_URL_PREFIX}{logo_filename}"
    db.commit()
    db.refresh(settings)
    return settings


def _delete_uploaded_company_logo(logo_url: str | None) -> None:
    if not logo_url or not logo_url.startswith(_COMPANY_LOGO_URL_PREFIX):
        return

    relative_path = logo_url.removeprefix("/").strip()
    if not relative_path:
        return

    candidate = (_WEB_DIR / relative_path).resolve()
    uploads_dir = _COMPANY_LOGO_UPLOAD_DIR.resolve()
    if uploads_dir not in candidate.parents:
        return
    if candidate.is_file():
        candidate.unlink()


def has_feature(settings: CompanySettings, feature: str) -> bool:
    wanted = feature.strip().lower()
    active = set(normalize_features(settings.features))
    return wanted in active
