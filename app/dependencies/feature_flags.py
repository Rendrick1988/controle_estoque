from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.auth import get_current_user
from app.models.company_settings import CompanySettings
from app.models.user import User
from app.services.settings_service import get_or_create_company_settings, has_feature


def get_company_settings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> CompanySettings:
    return get_or_create_company_settings(db, current_user.company_id)


def require_feature(feature_name: str):
    def dependency(settings: CompanySettings = Depends(get_company_settings)) -> None:
        if not has_feature(settings, feature_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Funcionalidade '{feature_name}' desativada para esta empresa",
            )

    return dependency
