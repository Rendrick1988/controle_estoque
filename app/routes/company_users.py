from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.authorization import effective_company_role_from_values
from app.core.db import get_db
from app.core.security import hash_password
from app.dependencies.auth import get_current_company_owner
from app.dependencies.plan_access import require_plan_capability
from app.models.user import User
from app.schemas.company_user import CompanyUserCreate, CompanyUserOut, CompanyUserUpdate
from app.services.audit_service import log_action
from app.services.plan_limits_service import enforce_user_cap
from app.services.company_user_service import (
    count_active_company_owners,
    get_company_user_or_404,
    list_company_users,
    serialize_company_user,
    user_profile,
)

router = APIRouter(
    prefix="/api/company-users",
    tags=["company-users"],
    dependencies=[Depends(require_plan_capability("multi_users"))],
)


@router.get("", response_model=list[CompanyUserOut])
def list_company_users_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_owner),
):
    users = list_company_users(db, current_user.company_id)
    return [serialize_company_user(user, current_user_id=current_user.id) for user in users]


@router.post("", response_model=CompanyUserOut, status_code=status.HTTP_201_CREATED)
def create_company_user_route(
    payload: CompanyUserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_owner),
):
    enforce_user_cap(db, current_user.company_id)
    next_is_owner = payload.profile == "owner"
    company_user = User(
        company_id=current_user.company_id,
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=effective_company_role_from_values(None, is_company_owner=next_is_owner),
        is_company_owner=next_is_owner,
        is_active=payload.is_active,
    )
    db.add(company_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já está em uso")
    db.refresh(company_user)
    serialized_company_user = serialize_company_user(company_user, current_user_id=current_user.id)
    log_action(
        db,
        action="CREATE",
        entity="company_user",
        entity_id=company_user.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        after_data=serialized_company_user,
        description=f"Usuário da empresa criado: {company_user.email} ({user_profile(company_user)})",
    )
    return serialized_company_user


@router.put("/{user_id}", response_model=CompanyUserOut)
def update_company_user_route(
    user_id: int,
    payload: CompanyUserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_owner),
):
    company_user = get_company_user_or_404(db, current_user.company_id, user_id)
    before_data = serialize_company_user(company_user, current_user_id=current_user.id)

    if company_user.id == current_user.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="Você não pode desativar seu próprio acesso")

    if (
        payload.profile is not None
        and company_user.id == current_user.id
        and payload.profile != user_profile(company_user)
    ):
        raise HTTPException(status_code=400, detail="Você não pode alterar o próprio perfil por esta tela")

    next_is_owner = company_user.is_company_owner if payload.profile is None else payload.profile == "owner"
    next_is_active = company_user.is_active if payload.is_active is None else payload.is_active

    if company_user.is_company_owner and company_user.is_active and (not next_is_owner or not next_is_active):
        if count_active_company_owners(db, current_user.company_id) <= 1:
            raise HTTPException(status_code=400, detail="A empresa precisa manter ao menos um dono ativo")

    if payload.email is not None:
        company_user.email = payload.email.lower()
    if payload.full_name is not None:
        company_user.full_name = payload.full_name
    if payload.password:
        company_user.hashed_password = hash_password(payload.password)
    company_user.role = effective_company_role_from_values(company_user.role, is_company_owner=next_is_owner)
    company_user.is_company_owner = next_is_owner
    company_user.is_active = next_is_active

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já está em uso")
    db.refresh(company_user)

    serialized_company_user = serialize_company_user(company_user, current_user_id=current_user.id)
    log_action(
        db,
        action="UPDATE",
        entity="company_user",
        entity_id=company_user.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        after_data=serialized_company_user,
        description=f"Usuário da empresa atualizado: {company_user.email} ({user_profile(company_user)})",
    )
    return serialized_company_user
