from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.billing import (
    BillingCheckoutConfirmOut,
    BillingCheckoutOut,
    BillingCheckoutRequest,
    PublicPlanCatalogOut,
)
from app.services.billing_service import (
    confirm_mercado_pago_payment,
    create_mercado_pago_checkout,
    handle_mercado_pago_webhook,
    public_plan_catalog,
)

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans", response_model=PublicPlanCatalogOut)
def list_public_plans():
    return public_plan_catalog()


@router.post("/mercado-pago/checkout", response_model=BillingCheckoutOut)
def create_mercado_pago_checkout_route(
    checkout_request: BillingCheckoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return create_mercado_pago_checkout(db, checkout_request, request_obj=request)


@router.get("/mercado-pago/confirm", response_model=BillingCheckoutConfirmOut)
def confirm_checkout(
    request: Request,
    payment_id: str | None = Query(default=None),
    collection_id: str | None = Query(default=None),
    billing_access_token: str | None = Header(default=None, alias="X-Billing-Access-Token"),
    db: Session = Depends(get_db),
):
    return confirm_mercado_pago_payment(
        db,
        payment_id=payment_id or collection_id,
        billing_access_token=billing_access_token,
        request_obj=request,
    )


@router.post("/mercado-pago/webhook")
async def handle_mercado_pago_webhook_route(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    webhook_payload: dict | None = None
    if raw_body:
        try:
            webhook_payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            webhook_payload = None
    return handle_mercado_pago_webhook(
        db,
        payload=webhook_payload,
        query_params=dict(request.query_params),
        request_obj=request,
    )
