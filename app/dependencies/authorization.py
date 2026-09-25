from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.core.authorization import permission_label, user_has_permission
from app.dependencies.auth import get_current_user
from app.models.user import User


def require_company_permission(permission: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not user_has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você não tem permissão para {permission_label(permission)}.",
            )
        return current_user

    return dependency
