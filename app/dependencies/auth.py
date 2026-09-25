from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.authorization import user_has_permission
from app.core.db import get_db
from app.core.security import decode_token
from app.models.company import Company
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _company_access_detail(company: Company) -> str:
    if company.status == "pending":
        if company.payment_status == "canceled":
            return "Pagamento não concluído. Finalize o checkout para liberar o acesso."
        if company.payment_status == "past_due":
            return "Pagamento em atraso. Regularize a cobrança para liberar o acesso."
        if company.payment_status == "paid":
            return "Pagamento recebido. A liberação automática do acesso ainda está em processamento."
        return "A empresa ainda não teve o pagamento confirmado. Conclua o checkout para liberar o acesso."
    if company.status == "blocked":
        return "Empresa com acesso bloqueado. Regularize a cobrança para continuar."
    return "Empresa sem acesso liberado"


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado"
        )
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")
    company = db.get(Company, user.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empresa inválida")
    if company.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_company_access_detail(company))
    return user


def get_current_company_owner(current_user: User = Depends(get_current_user)) -> User:
    if not user_has_permission(current_user, "company:admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para administradores da empresa",
        )
    return current_user

