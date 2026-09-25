from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.company_settings import CompanySettings
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.sale import Sale
    from app.models.sale_item import SaleItem
    from app.models.user import User


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(20), default="basic", nullable=False, index=True)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False, index=True)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    mercado_pago_reference: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    paid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list[User]] = relationship("User", back_populates="company", cascade="all, delete-orphan")
    products: Mapped[list[Product]] = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    customers: Mapped[list[Customer]] = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    sales: Mapped[list[Sale]] = relationship("Sale", back_populates="company", cascade="all, delete-orphan")
    sale_items: Mapped[list[SaleItem]] = relationship("SaleItem", back_populates="company", cascade="all, delete-orphan")
    settings: Mapped[CompanySettings | None] = relationship(
        "CompanySettings", back_populates="company", uselist=False, cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list[AuditLog]] = relationship("AuditLog", back_populates="company", cascade="all, delete-orphan")

