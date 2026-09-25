from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.authorization import require_company_permission
from app.models.user import User
from app.schemas.company_settings import CompanySettingsOut, CompanySettingsUpdate
from app.services.audit_service import log_action, serialize_instance
from app.services.settings_service import get_or_create_company_settings, save_company_logo, update_company_settings

router = APIRouter(prefix="/api/settings", tags=["company-settings"])
ALLOWED_COMPANY_LOGO_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_COMPANY_LOGO_BYTES = 2 * 1024 * 1024


@router.get("/company", response_model=CompanySettingsOut)
def get_company_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("settings:read")),
):
    return get_or_create_company_settings(db, current_user.company_id)


@router.put("/company", response_model=CompanySettingsOut)
def update_company_settings_route(
    payload: CompanySettingsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("settings:write")),
):
    submitted_fields = payload.model_dump(exclude_unset=True)
    current_settings = get_or_create_company_settings(db, current_user.company_id)
    before_data = serialize_instance(current_settings)
    updated_fields: dict[str, object] = {}
    for field_name in ("theme", "logo_url", "primary_color", "features"):
        if field_name in submitted_fields:
            updated_fields[field_name] = submitted_fields[field_name]
    updated = update_company_settings(
        db,
        current_user.company_id,
        **updated_fields,
    )
    log_action(
        db,
        action="UPDATE",
        entity="company_settings",
        entity_id=updated.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        after_data=serialize_instance(updated),
        description="Configurações da empresa atualizadas",
    )
    return updated


@router.post("/company/logo", response_model=CompanySettingsOut)
async def upload_company_logo(
    request: Request,
    logo_file: UploadFile | None = File(None),
    legacy_logo: UploadFile | None = File(None, alias="logo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("settings:write")),
):
    uploaded_logo = logo_file or legacy_logo
    if not uploaded_logo:
        raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado.")

    file_extension = ALLOWED_COMPANY_LOGO_TYPES.get((uploaded_logo.content_type or "").strip().lower())
    if not file_extension:
        raise HTTPException(status_code=400, detail="Envie uma imagem PNG, JPG, WEBP ou GIF.")

    logo_bytes = await uploaded_logo.read()
    if not logo_bytes:
        raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado.")
    if len(logo_bytes) > MAX_COMPANY_LOGO_BYTES:
        raise HTTPException(status_code=400, detail="A logo deve ter no maximo 2 MB.")

    current_settings = get_or_create_company_settings(db, current_user.company_id)
    before_data = serialize_instance(current_settings)
    updated = save_company_logo(
        db,
        current_user.company_id,
        logo_bytes=logo_bytes,
        file_extension=file_extension,
    )
    log_action(
        db,
        action="UPDATE",
        entity="company_settings",
        entity_id=updated.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        after_data=serialize_instance(updated),
        description="Logo da empresa atualizada",
    )
    return updated
