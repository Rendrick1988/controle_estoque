from __future__ import annotations
import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.authorization import require_company_permission
from app.dependencies.plan_access import require_plan_capability
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.services.audit_service import log_action, serialize_instance
from app.services.plan_limits_service import enforce_customer_cap

router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
    dependencies=[Depends(require_plan_capability("clientes"))],
)
def normalize_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf)


def validate_cpf(cpf: str) -> bool:
    cpf = normalize_cpf(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    return True

@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("customers:write")),
):
    if payload.cpf:
        normalized_cpf = normalize_cpf(payload.cpf)

        if not validate_cpf(normalized_cpf):
            raise HTTPException(
                status_code=400,
                detail="CPF inválido",
            )
        
        existing_customer = db.scalar(
            select(Customer).where(
                and_(
                    Customer.cpf == normalized_cpf,
                    Customer.company_id == current_user.company_id,
                )
            )
        )

        if existing_customer:
            raise HTTPException(
                status_code=400,
                detail="CPF já cadastrado",
            )

        payload.cpf = normalized_cpf


    enforce_customer_cap(db, current_user.company_id)
    customer = Customer(company_id=current_user.company_id, **payload.model_dump())
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já cadastrado para esta empresa")
    db.refresh(customer)
    log_action(
        db,
        action="CREATE",
        entity="customer",
        entity_id=customer.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        after_data=serialize_instance(customer),
        description=f"Cliente criado: {customer.name}",
    )
    return customer


@router.get("", response_model=list[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("customers:read")),
):
    query = select(Customer).where(Customer.company_id == current_user.company_id).order_by(Customer.created_at.desc())
    return list(db.scalars(query).all())


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("customers:read")),
):
    query = select(Customer).where(
        and_(Customer.id == customer_id, Customer.company_id == current_user.company_id)
    )
    customer = db.scalar(query)

    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("customers:write")),
):
    query = select(Customer).where(
        and_(Customer.id == customer_id, Customer.company_id == current_user.company_id)
    )
    customer = db.scalar(query)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    before_data = serialize_instance(customer)
    updated_fields = payload.model_dump(exclude_unset=True)

    if "cpf" in updated_fields:
        cpf_raw = updated_fields["cpf"]
        if not cpf_raw:
            updated_fields["cpf"] = None
        else:
            normalized_cpf = normalize_cpf(str(cpf_raw))

            if not validate_cpf(normalized_cpf):
                raise HTTPException(
                    status_code=400,
                    detail="CPF inválido",
                )

            existing_customer = db.scalar(
                select(Customer).where(
                    and_(
                        Customer.cpf == normalized_cpf,
                        Customer.id != customer.id,
                        Customer.company_id == current_user.company_id,
                    )
                )
            )

            if existing_customer:
                raise HTTPException(
                    status_code=400,
                    detail="CPF já cadastrado",
                )

            updated_fields["cpf"] = normalized_cpf

    for field_name, field_value in updated_fields.items():
        setattr(customer, field_name, field_value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já cadastrado para esta empresa")
    db.refresh(customer)
    log_action(
        db,
        action="UPDATE",
        entity="customer",
        entity_id=customer.id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        after_data=serialize_instance(customer),
        description=f"Cliente atualizado: {customer.name}",
    )
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_permission("customers:write")),
):
    query = select(Customer).where(
        and_(Customer.id == customer_id, Customer.company_id == current_user.company_id)
    )
    customer = db.scalar(query)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    before_data = serialize_instance(customer)
    customer_name = customer.name
    linked_sales_count = int(
        db.scalar(
            select(func.count(Sale.id)).where(
                and_(Sale.customer_id == customer.id, Sale.company_id == current_user.company_id)
            )
        )
        or 0
    )
    if linked_sales_count:
        db.execute(
            update(Sale)
            .where(and_(Sale.customer_id == customer.id, Sale.company_id == current_user.company_id))
            .values(customer_id=None)
        )
        db.flush()
    db.delete(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível excluir o cliente")
    log_action(
        db,
        action="DELETE",
        entity="customer",
        entity_id=customer_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        request=request,
        before_data=before_data,
        after_data={"detached_sales_count": linked_sales_count},
        description=(
            f"Cliente removido: {customer_name}"
            if linked_sales_count == 0
            else f"Cliente removido: {customer_name} (vendas desvinculadas: {linked_sales_count})"
        ),
    )
    return None
