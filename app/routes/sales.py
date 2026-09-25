from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.authorization import require_company_permission
from app.dependencies.feature_flags import require_feature
from app.models.sale import Sale
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleListItem, SaleOut
from app.services.plan_limits_service import effective_int_cap
from app.services.sales_service import create_sale, get_sale, list_sales

router = APIRouter(
    prefix="/api/sales",
    tags=["sales"],
    dependencies=[Depends(require_feature("vendas"))],
)


def serialize_sale(sale: Sale) -> SaleOut:
    return SaleOut(
        id=sale.id,
        customer_id=sale.customer_id,
        customer_name=sale.customer.name if sale.customer else "Sem cliente cadastrado",
        total_value=float(sale.total_value),
        created_at=sale.created_at,
        company_id=sale.company_id,
        items=[
            {
                "id": sale_item.id,
                "sale_id": sale_item.sale_id,
                "product_id": sale_item.product_id,
                "quantity": sale_item.quantity,
                "weight_kg": float(sale_item.weight_kg) if sale_item.weight_kg is not None else None,
                "price": float(sale_item.price),
                "product_name": sale_item.product.name if sale_item.product else None,
                "sale_unit": "weight" if sale_item.weight_kg is not None else "quantity",
            }
            for sale_item in sale.items
        ],
    )


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale_route(
    payload: SaleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("sales:write")),
):
    sale = create_sale(db, current_user, payload, request=request)
    return serialize_sale(sale)


@router.get("", response_model=list[SaleListItem])
def list_sales_route(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("sales:read")),
):
    company_id = current_user.company_id
    capped_limit = effective_int_cap(db, company_id, limit, cap_key="sales_list", absolute_max=500)
    sales = list_sales(db, company_id, limit=capped_limit)
    return [
        SaleListItem(
            id=sale.id,
            customer_id=sale.customer_id,
            customer_name=sale.customer.name if sale.customer else "Sem cliente cadastrado",
            total_value=float(sale.total_value),
            created_at=sale.created_at,
            items_count=len(sale.items),
        )
        for sale in sales
    ]


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale_route(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("sales:read")),
):
    sale = get_sale(db, sale_id, current_user.company_id)
    return serialize_sale(sale)
