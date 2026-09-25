from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # CREATE/UPDATE/DELETE/LOGIN
    entity: Mapped[str] = mapped_column(String(50), nullable=False)  # product/user/etc
    entity_id: Mapped[int | None] = mapped_column(Integer)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    before_data: Mapped[dict | list | None] = mapped_column(JSON)
    after_data: Mapped[dict | list | None] = mapped_column(JSON)

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
    company = relationship("Company", back_populates="audit_logs")

