from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.plan_limits_service import company_plan, company_supports

CAPABILITY_LABELS = {
    "clientes": "módulo de clientes",
    "relatorio": "relatórios",
    "dashboard_avancado": "dashboard avançado",
    "multi_users": "múltiplos usuários",
    "audit": "auditoria da empresa",
    "exports": "exportações",
    "vendas": "vendas",
}


def require_plan_capability(capability: str):
    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> None:
        if company_supports(db, current_user.company_id, capability):
            return
        plan = company_plan(db, current_user.company_id)
        label = CAPABILITY_LABELS.get(capability, capability)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"O plano {plan} não inclui {label}.",
        )

    return dependency
