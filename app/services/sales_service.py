from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, Request, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.user import User
from app.schemas.sale import SaleCreate
from app.services.audit_service import log_action, serialize_instance
from app.services.plan_limits_service import enforce_sale_cap


def _product_stock_snapshot(product: Product) -> dict:
    data = {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "quantity": product.quantity,
    }
    if product.sold_by_weight:
        data["weight_stock_kg"] = float(product.weight_stock_kg or 0)
    return data


def _deduct_stock(product: Product, *, quantity: int | None, weight_kg: float | None) -> None:
    if weight_kg is not None:
        if not product.sold_by_weight:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{product.name} não é vendido por peso",
            )
        current = Decimal(str(product.weight_stock_kg or 0))
        needed = Decimal(str(weight_kg))
        product.weight_stock_kg = float(current - needed)
        return

    if quantity is None:
        raise HTTPException(status_code=400, detail="Quantidade inválida")
    if product.sold_by_weight:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{product.name} deve ser vendido por peso (kg)",
        )
    product.quantity -= quantity


def _available_stock(product: Product) -> tuple[str, Decimal]:
    if product.sold_by_weight:
        return "kg", Decimal(str(product.weight_stock_kg or 0))
    return "un", Decimal(str(product.quantity))


def _requested_amount(
    requested_by_product: dict[int, tuple[Decimal, Decimal]],
    product_id: int,
    *,
    quantity: int | None,
    weight_kg: float | None,
) -> None:
    unit_qty, unit_weight = requested_by_product.get(product_id, (Decimal(0), Decimal(0)))
    if weight_kg is not None:
        requested_by_product[product_id] = (unit_qty, unit_weight + Decimal(str(weight_kg)))
    elif quantity is not None:
        requested_by_product[product_id] = (unit_qty + Decimal(quantity), unit_weight)


def create_sale(db: Session, current_user: User, payload: SaleCreate, *, request: Request | None = None) -> Sale:
    company_id = current_user.company_id
    enforce_sale_cap(db, company_id)
    try:
        customer = None
        if payload.customer_id is not None:
            customer = db.scalar(
                select(Customer).where(
                    and_(Customer.id == payload.customer_id, Customer.company_id == company_id)
                )
            )
            if not customer:
                raise HTTPException(status_code=404, detail="Cliente não encontrado")

        requested_by_product: dict[int, tuple[Decimal, Decimal]] = {}
        for sale_item_payload in payload.items:
            _requested_amount(
                requested_by_product,
                sale_item_payload.product_id,
                quantity=sale_item_payload.quantity,
                weight_kg=sale_item_payload.weight_kg,
            )

        product_ids = list(requested_by_product.keys())
        products = list(
            db.scalars(
                select(Product)
                .where(and_(Product.company_id == company_id, Product.id.in_(product_ids)))
                .with_for_update()
            ).all()
        )
        products_by_id = {product.id: product for product in products}

        missing_product_ids = [product_id for product_id in product_ids if product_id not in products_by_id]
        if missing_product_ids:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Produtos não encontrados para esta empresa: "
                    f"{', '.join(map(str, missing_product_ids))}"
                ),
            )

        stock_errors: list[str] = []
        for product_id, (req_units, req_kg) in requested_by_product.items():
            product = products_by_id[product_id]
            unit_label, available = _available_stock(product)
            if product.sold_by_weight:
                if req_kg > available:
                    stock_errors.append(
                        f"{product.name} (SKU {product.sku}) possui {available:.3f} kg e precisa de {req_kg:.3f} kg"
                    )
            elif req_units > available:
                stock_errors.append(
                    f"{product.name} (SKU {product.sku}) possui {int(available)} un e precisa de {int(req_units)} un"
                )
        if stock_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente: {'; '.join(stock_errors)}",
            )

        sale = Sale(customer_id=customer.id if customer else None, company_id=company_id, total_value=0)
        db.add(sale)
        db.flush()

        total_value = 0.0
        for sale_item_payload in payload.items:
            product = products_by_id[sale_item_payload.product_id]
            before_product = _product_stock_snapshot(product)
            unit_price = float(product.price)

            if sale_item_payload.weight_kg is not None:
                weight = float(sale_item_payload.weight_kg)
                line_total = unit_price * weight
                _deduct_stock(product, quantity=None, weight_kg=weight)
                db.add(
                    SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=None,
                        weight_kg=weight,
                        price=unit_price,
                        company_id=company_id,
                    )
                )
                stock_note = f"(-{weight:.3f} kg)"
            else:
                qty = int(sale_item_payload.quantity or 0)
                line_total = unit_price * qty
                _deduct_stock(product, quantity=qty, weight_kg=None)
                db.add(
                    SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=qty,
                        weight_kg=None,
                        price=unit_price,
                        company_id=company_id,
                    )
                )
                stock_note = f"(-{qty} un)"

            total_value += line_total
            log_action(
                db,
                action="UPDATE",
                entity="stock",
                entity_id=product.id,
                user_id=current_user.id,
                company_id=company_id,
                request=request,
                before_data=before_product,
                after_data=_product_stock_snapshot(product),
                description=f"Baixa de estoque após venda: {product.name} {stock_note}",
                auto_commit=False,
            )

        sale.total_value = round(total_value, 2)
        log_action(
            db,
            action="CREATE",
            entity="sale",
            entity_id=sale.id,
            user_id=current_user.id,
            company_id=company_id,
            request=request,
            after_data={
                "sale": serialize_instance(sale),
                "customer": {"id": customer.id, "name": customer.name} if customer else None,
                "items": [sale_item_payload.model_dump() for sale_item_payload in payload.items],
            },
            description=(
                f"Venda criada para {customer.name} no valor de R$ {sale.total_value:.2f}"
                if customer
                else f"Venda criada sem cliente cadastrado no valor de R$ {sale.total_value:.2f}"
            ),
            auto_commit=False,
        )
        db.commit()

        return get_sale(db, sale.id, company_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao processar venda")


def list_sales(db: Session, company_id: int, *, limit: int = 100) -> list[Sale]:
    query = (
        select(Sale)
        .where(Sale.company_id == company_id)
        .options(joinedload(Sale.customer), joinedload(Sale.items).joinedload(SaleItem.product))
        .order_by(Sale.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(query).unique().all())


def get_sale(db: Session, sale_id: int, company_id: int) -> Sale:
    query = (
        select(Sale)
        .where(and_(Sale.id == sale_id, Sale.company_id == company_id))
        .options(joinedload(Sale.customer), joinedload(Sale.items).joinedload(SaleItem.product))
    )
    sale = db.scalars(query).unique().first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return sale
