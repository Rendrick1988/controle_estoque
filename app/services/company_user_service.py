from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_company_user_or_404(db: Session, company_id: int, user_id: int) -> User:
    user = db.scalar(select(User).where(and_(User.id == user_id, User.company_id == company_id)))
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def list_company_users(db: Session, company_id: int) -> list[User]:
    user_query = (
        select(User)
        .where(User.company_id == company_id)
        .order_by(User.is_company_owner.desc(), User.is_active.desc(), User.created_at.asc())
    )
    return list(db.scalars(user_query).all())


def count_active_company_owners(db: Session, company_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(User.id)).where(
                and_(User.company_id == company_id, User.is_company_owner.is_(True), User.is_active.is_(True))
            )
        )
        or 0
    )


def user_profile(user: User) -> str:
    return "owner" if user.is_company_owner else "collaborator"


def serialize_company_user(user: User, *, current_user_id: int | None = None) -> dict:
    return {
        "id": user.id,
        "company_id": user.company_id,
        "email": user.email,
        "full_name": user.full_name,
        "profile": user_profile(user),
        "is_company_owner": user.is_company_owner,
        "is_active": user.is_active,
        "is_current_user": user.id == current_user_id,
        "created_at": user.created_at,
    }
