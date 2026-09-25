from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.customer import Customer
    from app.models.sale_item import SaleItem


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    total_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)

    customer: Mapped[Customer | None] = relationship("Customer", back_populates="sales")
    company: Mapped[Company] = relationship("Company", back_populates="sales")
    items: Mapped[list[SaleItem]] = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
