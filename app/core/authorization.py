from __future__ import annotations

from typing import Final, Literal

from app.models.user import User

CompanyRole = Literal["admin", "user"]

_ADMIN_ONLY_PERMISSIONS: Final[frozenset[str]] = frozenset(
    {
        "company:admin",
        "settings:write",
        "company_users:manage",
        "audit:read",
    }
)
_SHARED_COMPANY_PERMISSIONS: Final[frozenset[str]] = frozenset(
    {
        "settings:read",
        "products:read",
        "products:write",
        "customers:read",
        "customers:write",
        "sales:read",
        "sales:write",
        "dashboard:view",
        "reports:read",
        "reports:export",
    }
)

ROLE_PERMISSIONS: Final[dict[CompanyRole, frozenset[str]]] = {
    "admin": _SHARED_COMPANY_PERMISSIONS | _ADMIN_ONLY_PERMISSIONS,
    "user": _SHARED_COMPANY_PERMISSIONS,
}

PERMISSION_LABELS: Final[dict[str, str]] = {
    "company:admin": "executar ações administrativas da empresa",
    "settings:read": "visualizar as configurações da empresa",
    "settings:write": "alterar as configurações da empresa",
    "company_users:manage": "gerenciar usuários da empresa",
    "audit:read": "visualizar a auditoria da empresa",
    "products:read": "visualizar produtos",
    "products:write": "gerenciar produtos",
    "customers:read": "visualizar clientes",
    "customers:write": "gerenciar clientes",
    "sales:read": "visualizar vendas",
    "sales:write": "registrar vendas",
    "dashboard:view": "visualizar o dashboard",
    "reports:read": "visualizar relatórios",
    "reports:export": "exportar relatórios",
}


def normalize_company_role(role: str | None) -> CompanyRole:
    return "admin" if (role or "").strip().lower() == "admin" else "user"


def effective_company_role_from_values(role: str | None, *, is_company_owner: bool) -> CompanyRole:
    if is_company_owner:
        return "admin"
    return normalize_company_role(role)


def effective_company_role(user: User) -> CompanyRole:
    return effective_company_role_from_values(user.role, is_company_owner=user.is_company_owner)


def permissions_for_role(role: CompanyRole) -> frozenset[str]:
    return ROLE_PERMISSIONS[role]


def permission_label(permission: str) -> str:
    return PERMISSION_LABELS.get(permission, permission)


def user_has_permission(user: User, permission: str) -> bool:
    if permission not in PERMISSION_LABELS:
        raise ValueError(f"Permissão desconhecida: {permission}")
    return permission in permissions_for_role(effective_company_role(user))
