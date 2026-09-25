from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity: str
    entity_id: int | None
    user_id: int | None
    user_email: str | None = None
    company_id: int | None
    company_name: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    before_data: dict[str, Any] | list[Any] | None = None
    after_data: dict[str, Any] | list[Any] | None = None
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

