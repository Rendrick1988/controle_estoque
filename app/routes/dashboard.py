from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.authorization import require_company_permission
from app.dependencies.feature_flags import require_feature
from app.dependencies.plan_access import require_plan_capability
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryOut
from app.services.dashboard_service import build_dashboard_payload

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_plan_capability("dashboard_avancado")), Depends(require_feature("dashboard_avancado"))],
)


@router.get("/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("dashboard:view")),
):
    return build_dashboard_payload(db, current_user.company_id)
