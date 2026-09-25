from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.dependencies.auth import get_current_company_owner
from app.dependencies.plan_access import require_plan_capability
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogOut
from app.services.audit_service import serialize_audit_log
from app.services.plan_limits_service import effective_int_cap

router = APIRouter(
    prefix="/api/audit",
    tags=["audit"],
    dependencies=[Depends(require_plan_capability("audit"))],
)


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    action: str | None = Query(default=None),
    entity: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=150),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_owner),
):
    company_id = current_user.company_id
    capped_limit = effective_int_cap(db, company_id, limit, cap_key="audit_logs", absolute_max=1000)
    filters = [AuditLog.company_id == company_id]
    if action:
        filters.append(AuditLog.action == action)
    if entity:
        filters.append(AuditLog.entity == entity)
    if date_from:
        filters.append(AuditLog.created_at >= date_from)
    if date_to:
        filters.append(AuditLog.created_at <= date_to)
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(AuditLog.description.ilike(term), AuditLog.entity.ilike(term), AuditLog.action.ilike(term)))

    query = (
        select(AuditLog)
        .where(and_(*filters))
        .options(joinedload(AuditLog.user), joinedload(AuditLog.company))
        .order_by(AuditLog.created_at.desc())
        .limit(capped_limit)
    )
    return [serialize_audit_log(audit_log) for audit_log in db.scalars(query).all()]

