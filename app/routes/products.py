from __future__ import annotations
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.authorization import require_company_permission
from app.models.product import Product
from app.models.sale_item import SaleItem
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate, StockChartItem
from app.services.audit_service import log_action, serialize_instance
from app.services.plan_limits_service import enforce_product_cap

router = APIRouter(prefix="/api/products", tags=["products"])


def _normalize_weight_fields(product: Product) -> None:
    if not product.sold_by_weight:
        product.weight_stock_kg = None
        product.min_weight_kg = None


def _validity_date(value: datetime) -> date:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).date()
    return value.date()


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:write")),
):
    if _validity_date(payload.validity) < date.today():
        raise HTTPException(
           status_code=400,
           detail="Não é possível cadastrar produto vencido",
        )
    enforce_product_cap(db, current_user.company_id)
    product = Product(company_id=current_user.company_id, **payload.model_dump())
    _normalize_weight_fields(product)
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="SKU já existe para esta empresa")
    db.refresh(product)
    log_action(
        db,
        action="CREATE",
        entity="product",
        entity_id=product.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        after_data=serialize_instance(product),
        description=f"Produto criado: {product.name} (SKU {product.sku})",
    )
    return product


@router.get("", response_model=list[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:read")),
):
    query = (
        select(Product)
        .where(Product.company_id == current_user.company_id)
        .order_by(Product.created_at.desc())
    )
    return list(db.scalars(query).all())


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:write")),
):
    query = select(Product).where(
        and_(Product.id == product_id, Product.company_id == current_user.company_id)
    )
    product = db.scalar(query)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    before_data = serialize_instance(product)

    updated_fields = payload.model_dump(exclude_unset=True)

    if "validity" in updated_fields and updated_fields["validity"] is not None:
        if _validity_date(updated_fields["validity"]) < date.today():
            raise HTTPException(
                status_code=400,
                detail="Não é possível definir uma validade vencida",
            )
    
    for field_name, field_value in updated_fields.items():
        setattr(product, field_name, field_value)
    _normalize_weight_fields(product)

    if product.sold_by_weight and (
        product.weight_stock_kg is None or product.min_weight_kg is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Produtos por peso exigem estoque e estoque mínimo em kg",
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="SKU já existe para esta empresa")
    db.refresh(product)
    log_action(
        db,
        action="UPDATE",
        entity="product",
        entity_id=product.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        after_data=serialize_instance(product),
        description=f"Produto atualizado: {product.name} (SKU {product.sku})",
    )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:write")),
):
    query = select(Product).where(
        and_(Product.id == product_id, Product.company_id == current_user.company_id)
    )
    product = db.scalar(query)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    before_data = serialize_instance(product)
    product_name = product.name
    product_sku = product.sku
    linked_sale_items_count = int(
        db.scalar(
            select(func.count(SaleItem.id)).where(
                and_(SaleItem.product_id == product.id, SaleItem.company_id == current_user.company_id)
            )
        )
        or 0
    )
    if linked_sale_items_count:
        log_action(
            db,
            action="DELETE_BLOCKED",
            entity="product",
            entity_id=product_id,
            user_id=current_user.id,
            company_id=current_user.company_id,
            request=request,
            before_data=before_data,
            after_data={"linked_sale_items_count": linked_sale_items_count},
            description=(
                f"Tentativa de exclusao bloqueada para produto {product_name} (SKU {product_sku}) "
                f"com {linked_sale_items_count} item(ns) de venda vinculados"
            ),
        )
        raise HTTPException(
            status_code=400,
            detail=(
                "Nao e possivel excluir este produto porque ele ja possui vendas registradas. "
                "Mantenha-o no catalogo para preservar o historico."
            ),
        )
    db.delete(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nao foi possivel excluir o produto")
    log_action(
        db,
        action="DELETE",
        entity="product",
        entity_id=product_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        description=f"Produto removido: {product_name} (SKU {product_sku})",
    )
    return None


@router.get("/low-stock", response_model=list[ProductOut])
def list_low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:read")),
):
    query = select(Product).where(
        and_(
            Product.company_id == current_user.company_id,
            (
                (Product.sold_by_weight.is_(False) & (Product.quantity <= Product.min_quantity))
                | (
                    Product.sold_by_weight.is_(True)
                    & (func.coalesce(Product.weight_stock_kg, 0) <= func.coalesce(Product.min_weight_kg, 0))
                )
            ),
        )
    )
    return list(db.scalars(query).all())


@router.get("/chart", response_model=list[StockChartItem])
def list_stock_chart_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:read")),
):
    query = select(Product.name, Product.quantity, Product.validity).where(Product.company_id == current_user.company_id)
    chart_rows = db.execute(query).all()
    return [StockChartItem(name=row[0], quantity=row[1], validity=row[2]) for row in chart_rows]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("products:read")),
):
    query = select(Product).where(
        and_(Product.id == product_id, Product.company_id == current_user.company_id)
    )
    product = db.scalar(query)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

