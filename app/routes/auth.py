from __future__ import annotations

from time import sleep

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.authorization import effective_company_role
from app.core.config import settings
from app.core.db import get_db
from app.core.plans import PlanCode, default_features_for_plan
from app.core.security import (
    create_access_token,
    create_billing_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)
from app.dependencies.auth import _company_access_detail, get_current_user
from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.user import User
from app.schemas.company import CompanyOut
from app.schemas.user import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    PlanUsageOut,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    Token,
    UserMeOut,
    UserOut,
)
from app.services.audit_service import log_action
from app.services.plan_limits_service import plan_usage_public

router = APIRouter(prefix="/api/auth", tags=["auth"])


_FORGOT_PASSWORD_MESSAGE = (
    "Solicitação recebida. Se o e-mail estiver cadastrado em uma empresa com acesso liberado, "
    "use o código exibido nesta tela (quando disponível) ou recebido por e-mail para criar uma nova senha."
)

def _serialize_user_out(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "company_id": user.company_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": effective_company_role(user),
        "is_company_owner": user.is_company_owner,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


def _apply_registration_plan(company: Company, plan: PlanCode, billing_cycle: str) -> None:
    company.plan = plan
    company.billing_cycle = billing_cycle
    company.mercado_pago_reference = None
    company.paid_until = None
    if plan == "free":
        company.status = "active"
        company.payment_status = "paid"
        return
    company.status = "pending"
    company.payment_status = "pending"


def _build_register_response(company: Company, user: User) -> RegisterResponse:
    billing_access_token = None
    if company.status != "active":
        billing_access_token = create_billing_access_token(user_id=user.id, company_id=company.id)
    return RegisterResponse(
        company=CompanyOut.model_validate(company),
        admin=UserOut(**_serialize_user_out(user)),
        billing_access_token=billing_access_token,
    )


def _resume_existing_registration(
    register_request: RegisterRequest,
    request: Request,
    db: Session,
) -> RegisterResponse | None:
    email = register_request.admin.email.lower().strip()
    existing_user = db.scalar(select(User).where(User.email == email))
    existing_company = db.scalar(select(Company).where(Company.name == register_request.company.name))

    if not existing_user and not existing_company:
        return None
    if not existing_user or not existing_company or existing_user.company_id != existing_company.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já existe ou email já está em uso",
        )
    if not verify_password(register_request.admin.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já existe ou email já está em uso",
        )
    if existing_company.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já está ativa. Faça login para acessar.",
        )

    old_plan = existing_company.plan
    before_data = {
        "company": CompanyOut.model_validate(existing_company).model_dump(),
        "user": _serialize_user_out(existing_user),
    }

    _apply_registration_plan(existing_company, register_request.plan, register_request.billing_cycle)
    if register_request.admin.full_name:
        existing_user.full_name = register_request.admin.full_name
    if existing_user.is_company_owner:
        existing_user.role = "admin"

    company_settings = db.scalar(select(CompanySettings).where(CompanySettings.company_id == existing_company.id))
    if company_settings:
        if existing_company.plan != old_plan:
            company_settings.features = default_features_for_plan(register_request.plan)
    else:
        db.add(
            CompanySettings(
                company_id=existing_company.id,
                theme="light",
                primary_color="#7c5cff",
                features=default_features_for_plan(register_request.plan),
            )
        )

    db.commit()
    db.refresh(existing_company)
    db.refresh(existing_user)

    log_action(
        db,
        action="REGISTER_RESUME",
        entity="company",
        entity_id=existing_company.id,
        user_id=existing_user.id,
        company_id=existing_company.id,
        request=request,
        before_data=before_data,
        after_data={
            "company": CompanyOut.model_validate(existing_company).model_dump(),
            "user": _serialize_user_out(existing_user),
        },
        description=(
            f"Cadastro retomado com acesso imediato no plano Free: {existing_company.name}"
            if existing_company.plan == "free"
            else f"Cadastro retomado para pagamento automático: {existing_company.name}"
        ),
    )
    return _build_register_response(existing_company, existing_user)


@router.post("/register", response_model=RegisterResponse)
def register_company(register_request: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    resumed_registration = _resume_existing_registration(register_request, request, db)
    if resumed_registration is not None:
        return resumed_registration

    company = Company(name=register_request.company.name)
    _apply_registration_plan(company, register_request.plan, register_request.billing_cycle)
    company_settings = CompanySettings(
        company=company,
        theme="light",
        primary_color="#7c5cff",
        features=default_features_for_plan(register_request.plan),
    )
    user = User(
        company=company,
        email=register_request.admin.email.lower(),
        full_name=register_request.admin.full_name,
        hashed_password=hash_password(register_request.admin.password),
        role="admin",
        is_company_owner=True,
    )
    db.add(company)
    db.add(company_settings)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já existe ou email já está em uso",
        )
    db.refresh(company)
    db.refresh(user)
    log_action(
        db,
        action="CREATE",
        entity="company",
        entity_id=company.id,
        user_id=user.id,
        company_id=company.id,
        request=request,
        after_data={
            "company": {"id": company.id, "name": company.name, "status": company.status, "plan": company.plan},
            "user": {
                "id": user.id,
                "email": user.email,
                "role": effective_company_role(user),
                "is_company_owner": user.is_company_owner,
            },
        },
        description=(
            f"Empresa criada com acesso imediato no plano Free: {company.name}"
            if company.plan == "free"
            else f"Empresa criada aguardando confirmação automática de pagamento no plano {company.plan}: {company.name}"
        ),
    )
    return _build_register_response(company, user)


@router.post("/login", response_model=Token)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm usa "username" como campo; aqui tratamos como email
    email = form.username.lower().strip()
    query = select(User).where(User.email == email)
    user = db.scalar(query)
    if not user or not verify_password(form.password, user.hashed_password):
        log_action(
            db,
            action="LOGIN_FAILURE",
            entity="auth",
            entity_id=user.id if user else None,
            user_id=user.id if user else None,
            company_id=user.company_id if user else None,
            request=request,
            before_data={"email": email},
            description=f"Falha de login para {email}",
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    company = db.get(Company, user.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empresa inválida")
    if company.status != "active":
        log_action(
            db,
            action="LOGIN_BLOCKED",
            entity="company",
            entity_id=company.id,
            user_id=user.id,
            company_id=company.id,
            request=request,
            before_data={"email": email, "company_status": company.status},
            description=f"Tentativa de acesso bloqueada para {email}",
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_company_access_detail(company))
    token = create_access_token(str(user.id))
    log_action(
        db,
        action="LOGIN_SUCCESS",
        entity="user",
        entity_id=user.id,
        user_id=user.id,
        company_id=user.company_id,
        request=request,
        after_data={"email": user.email, "role": effective_company_role(user), "is_company_owner": user.is_company_owner},
        description=f"Login realizado: {user.email}",
    )
    return Token(access_token=token)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    sleep(0.06)
    reset_token: str | None = None

    user = db.scalar(select(User).where(User.email == email))
    company = db.get(Company, user.company_id) if user else None
    eligible = bool(user and user.is_active and company and company.status == "active")

    if eligible:
        if settings.PASSWORD_RESET_TOKEN_IN_RESPONSE:
            reset_token = create_password_reset_token(user.id)
        log_action(
            db,
            action="PASSWORD_RESET_REQUEST",
            entity="user",
            entity_id=user.id,
            user_id=user.id,
            company_id=user.company_id,
            request=request,
            after_data={"email": email, "token_entregue_na_resposta": bool(reset_token)},
            description=f"Solicitação de recuperação de senha: {email}",
        )

    return ForgotPasswordResponse(detail=_FORGOT_PASSWORD_MESSAGE, reset_token=reset_token)


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    try:
        decoded = decode_password_reset_token(payload.reset_token.strip())
        user_id = int(decoded["sub"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido ou expirado. Solicite uma nova recuperação de senha.",
        ) from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível redefinir a senha para esta conta.",
        )
    company = db.get(Company, user.company_id)
    if not company or company.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível redefinir a senha enquanto a empresa não estiver com acesso liberado.",
        )

    before_data = {"id": user.id, "email": user.email}
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    db.refresh(user)

    log_action(
        db,
        action="PASSWORD_RESET_COMPLETE",
        entity="user",
        entity_id=user.id,
        user_id=user.id,
        company_id=user.company_id,
        request=request,
        before_data=before_data,
        after_data={**before_data, "password_updated": True},
        description=f"Senha redefinida após recuperação: {user.email}",
    )

    return {"detail": "Senha alterada com sucesso. Você já pode entrar com a nova senha."}


@router.get("/me", response_model=UserMeOut)
def get_current_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan_usage_data = plan_usage_public(db, current_user.company_id)
    usage = PlanUsageOut(**plan_usage_data)
    return UserMeOut(
        **_serialize_user_out(current_user),
        company_plan=usage.plan,
        plan_usage=usage,
    )

