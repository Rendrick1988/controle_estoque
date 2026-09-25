from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib import error, request
from uuid import uuid4

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.plans import (
    BillingCycle,
    PaymentStatus,
    PlanCode,
    PLAN_OFFERS,
    default_features_for_plan,
    normalize_billing_cycle,
    normalize_plan,
    plan_offer,
)
from app.core.security import decode_billing_access_token
from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.user import User
from app.schemas.billing import BillingCheckoutRequest
from app.services.audit_service import log_action, serialize_instance


def public_plan_catalog() -> dict[str, object]:
    public_plan_offers = [
        PLAN_OFFERS["free"],
        PLAN_OFFERS["basic"],
        PLAN_OFFERS["professional"],
        PLAN_OFFERS["premium"],
    ]
    return {
        "payment_provider": "mercado_pago",
        "annual_discount_copy": "",
        "offers": public_plan_offers,
    }


def _mercado_pago_access_token() -> str:
    access_token = (settings.MERCADO_PAGO_ACCESS_TOKEN or "").strip()
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mercado Pago ainda não foi configurado. Defina MERCADO_PAGO_ACCESS_TOKEN para liberar o checkout.",
        )
    return access_token


def _mercado_pago_request_json(
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    error_detail: str,
) -> dict[str, Any]:
    access_token = _mercado_pago_access_token()
    request_body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {access_token}"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
        headers["X-Idempotency-Key"] = str(uuid4())

    api_base = settings.MERCADO_PAGO_API_BASE_URL.rstrip("/")
    http_request = request.Request(url=f"{api_base}{path}", data=request_body, method=method, headers=headers)
    try:
        with request.urlopen(http_request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw_response_body = exc.read().decode("utf-8", errors="ignore")
        detail = error_detail
        if raw_response_body:
            try:
                parsed = json.loads(raw_response_body)
                detail = parsed.get("message") or parsed.get("error") or detail
            except json.JSONDecodeError:
                detail = raw_response_body or detail
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_detail,
        ) from exc


def _price_for_cycle(plan: PlanCode, billing_cycle: BillingCycle) -> float:
    offer = plan_offer(plan)
    if billing_cycle == "annual":
        return float(offer["annual_price"])
    return float(offer["monthly_price"])


def _checkout_title(plan: PlanCode, billing_cycle: BillingCycle) -> str:
    offer = plan_offer(plan)
    cycle_label = "Anual" if billing_cycle == "annual" else "Mensal"
    return f"{offer['name']} - {cycle_label}"


def _back_urls(plan: PlanCode, billing_cycle: BillingCycle) -> dict[str, str]:
    base_url = settings.APP_BASE_URL.rstrip("/")
    suffix = f"plan={plan}&billing_cycle={billing_cycle}"
    return {
        "success": f"{base_url}/?checkout=success&{suffix}",
        "failure": f"{base_url}/?checkout=failure&{suffix}",
        "pending": f"{base_url}/?checkout=pending&{suffix}",
    }


def _notification_url() -> str:
    configured = (settings.MERCADO_PAGO_NOTIFICATION_URL or "").strip()
    if configured:
        return configured
    return f"{settings.APP_BASE_URL.rstrip('/')}/api/billing/mercado-pago/webhook"


def _build_external_reference(company_id: int, plan: PlanCode, billing_cycle: BillingCycle) -> str:
    return f"controle-estoque:company:{company_id}:plan:{plan}:cycle:{billing_cycle}:{uuid4()}"


def _parse_external_reference(external_reference: str | None) -> int | None:
    parts = str(external_reference or "").split(":")
    for index, part in enumerate(parts):
        if part == "company" and index + 1 < len(parts):
            try:
                return int(parts[index + 1])
            except (TypeError, ValueError):
                return None
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    raw_datetime = str(value).strip()
    if not raw_datetime:
        return None
    if raw_datetime.endswith("Z"):
        raw_datetime = f"{raw_datetime[:-1]}+00:00"
    try:
        return datetime.fromisoformat(raw_datetime)
    except ValueError:
        return None


def _resolve_company_owner_from_billing_access_token(
    db: Session,
    billing_access_token: str,
    *,
    allow_active: bool = False,
) -> tuple[Company, User]:
    raw_billing_access_token = (billing_access_token or "").strip()
    if not raw_billing_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Checkout não autorizado. Refaça o cadastro antes de pagar.",
        )

    try:
        token_payload = decode_billing_access_token(raw_billing_access_token)
        user_id = int(token_payload.get("sub"))
        token_company_id = int(token_payload.get("company_id"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Checkout não autorizado. Refaça o cadastro antes de pagar.",
        ) from exc

    owner = db.get(User, user_id)
    if not owner or not owner.is_active or not owner.is_company_owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Checkout não autorizado. Refaça o cadastro antes de pagar.",
        )
    if owner.company_id != token_company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Checkout não autorizado. Refaça o cadastro antes de pagar.",
        )

    company = db.get(Company, owner.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
    if company.status == "active" and not allow_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta empresa já está ativa. Faça login para gerenciar a assinatura.",
        )
    return company, owner


def _resolve_company_for_checkout(db: Session, checkout_request: BillingCheckoutRequest) -> tuple[Company, User]:
    company, owner = _resolve_company_owner_from_billing_access_token(
        db,
        checkout_request.billing_access_token,
    )

    informed_name = (checkout_request.company_name or "").strip()
    if informed_name and company.name.strip() != informed_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome da empresa não confere com o cadastro salvo.",
        )

    informed_email = (checkout_request.email or "").strip().lower()
    if owner and informed_email and owner.email.strip().lower() != informed_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O responsável informado não confere com o cadastro da empresa.",
        )
    return company, owner


def _sync_settings_for_plan(db: Session, company: Company, old_plan: str) -> None:
    company_settings = db.scalar(select(CompanySettings).where(CompanySettings.company_id == company.id))
    if company_settings and normalize_plan(old_plan) == normalize_plan(company.plan):
        return
    if company_settings:
        company_settings.features = default_features_for_plan(company.plan)
    else:
        db.add(
            CompanySettings(
                company_id=company.id,
                theme="light",
                primary_color="#7c5cff",
                features=default_features_for_plan(company.plan),
            )
        )


def create_mercado_pago_checkout(
    db: Session, checkout_request: BillingCheckoutRequest, *, request_obj: Request | None = None
) -> dict[str, object]:
    if checkout_request.plan == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plano Free é liberado no cadastro e não precisa de checkout.",
        )

    company, owner = _resolve_company_for_checkout(db, checkout_request)
    before_data = serialize_instance(company)
    external_reference = _build_external_reference(company.id, checkout_request.plan, checkout_request.billing_cycle)

    preference: dict[str, Any] = {
        "items": [
            {
                "id": f"{checkout_request.plan}-{checkout_request.billing_cycle}",
                "title": _checkout_title(checkout_request.plan, checkout_request.billing_cycle),
                "description": company.name,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": _price_for_cycle(checkout_request.plan, checkout_request.billing_cycle),
            }
        ],
        "back_urls": _back_urls(checkout_request.plan, checkout_request.billing_cycle),
        "auto_return": "approved",
        "external_reference": external_reference,
        "metadata": {
            "company_id": company.id,
            "plan": checkout_request.plan,
            "billing_cycle": checkout_request.billing_cycle,
        },
        "notification_url": _notification_url(),
    }
    payer_email = (checkout_request.email or owner.email or "").strip().lower()
    if payer_email:
        preference["payer"] = {"email": payer_email}

    checkout_preference_response = _mercado_pago_request_json(
        "/checkout/preferences",
        method="POST",
        payload=preference,
        error_detail="Não foi possível conectar ao Mercado Pago para criar o checkout.",
    )
    checkout_url = checkout_preference_response.get("init_point")
    if not checkout_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Mercado Pago não retornou a URL de checkout.",
        )

    old_plan = company.plan
    company.plan = normalize_plan(checkout_request.plan)
    company.billing_cycle = normalize_billing_cycle(checkout_request.billing_cycle)
    if company.status != "active":
        company.status = "pending"
        company.payment_status = "pending"
        company.paid_until = None
    company.mercado_pago_reference = external_reference[:120]
    _sync_settings_for_plan(db, company, old_plan)
    db.commit()
    db.refresh(company)

    log_action(
        db,
        action="CHECKOUT_CREATED",
        entity="company",
        entity_id=company.id,
        user_id=None,
        company_id=company.id,
        request=request_obj,
        before_data=before_data,
        after_data=serialize_instance(company),
        description=f"Checkout Mercado Pago iniciado automaticamente para {company.name}",
    )

    return {
        "provider": "mercado_pago",
        "checkout_url": checkout_url,
        "sandbox_checkout_url": checkout_preference_response.get("sandbox_init_point"),
        "plan": checkout_request.plan,
        "billing_cycle": checkout_request.billing_cycle,
    }


def _mercado_pago_payment_state(provider_status: str | None) -> tuple[PaymentStatus, bool]:
    normalized = (provider_status or "").strip().lower()
    if normalized == "approved":
        return "paid", True
    if normalized in {"authorized", "pending", "in_process", "in_mediation"}:
        return "pending", False
    if normalized in {"expired"}:
        return "past_due", False
    if normalized in {"cancelled", "canceled", "rejected", "refunded", "charged_back"}:
        return "canceled", False
    return "pending", False


def _payment_company_id(payment_data: dict[str, Any]) -> int | None:
    metadata = payment_data.get("metadata")
    if isinstance(metadata, dict):
        raw_company_id = metadata.get("company_id")
        try:
            if raw_company_id is not None:
                return int(raw_company_id)
        except (TypeError, ValueError):
            pass
    return _parse_external_reference(payment_data.get("external_reference"))


def _payment_plan(payment_data: dict[str, Any], company: Company) -> PlanCode:
    metadata = payment_data.get("metadata")
    if isinstance(metadata, dict) and metadata.get("plan"):
        return normalize_plan(metadata.get("plan"))
    return normalize_plan(company.plan)


def _payment_billing_cycle(payment_data: dict[str, Any], company: Company) -> BillingCycle:
    metadata = payment_data.get("metadata")
    if isinstance(metadata, dict) and metadata.get("billing_cycle"):
        return normalize_billing_cycle(metadata.get("billing_cycle"))
    return normalize_billing_cycle(company.billing_cycle)


def _paid_until(payment_data: dict[str, Any], billing_cycle: BillingCycle) -> datetime:
    base = (
        _parse_datetime(payment_data.get("date_approved"))
        or _parse_datetime(payment_data.get("date_last_updated"))
        or _parse_datetime(payment_data.get("date_created"))
        or datetime.now(timezone.utc)
    )
    days = 365 if billing_cycle == "annual" else 30
    return base + timedelta(days=days)


def _payment_message(company: Company, provider_status: str | None) -> str:
    if company.status == "active":
        return "Pagamento confirmado e acesso liberado automaticamente."
    if company.payment_status == "pending":
        return "Pagamento recebido, mas ainda pendente de compensação no Mercado Pago."
    if company.payment_status == "past_due":
        return "Pagamento em atraso. Regularize a cobrança para liberar o acesso."
    if company.payment_status == "canceled":
        return "Pagamento não concluído. Refaça o checkout para liberar o acesso."
    return f"Status recebido do Mercado Pago: {provider_status or 'desconhecido'}."


def _payment_sync_response(company: Company, provider_status: str | None) -> dict[str, object]:
    return {
        "provider": "mercado_pago",
        "provider_status": provider_status,
        "company_id": company.id,
        "status": company.status,
        "payment_status": company.payment_status,
        "plan": normalize_plan(company.plan),
        "billing_cycle": normalize_billing_cycle(company.billing_cycle),
        "access_released": company.status == "active",
        "message": _payment_message(company, provider_status),
    }


def _fetch_mercado_pago_payment(payment_id: str) -> dict[str, Any]:
    return _mercado_pago_request_json(
        f"/v1/payments/{payment_id}",
        method="GET",
        error_detail="Não foi possível consultar o pagamento no Mercado Pago.",
    )


def sync_mercado_pago_payment(
    db: Session,
    payment_data: dict[str, Any],
    *,
    request_obj: Request | None = None,
    source: str = "confirm",
) -> dict[str, object]:
    company_id = _payment_company_id(payment_data)
    if company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O pagamento recebido não está vinculado a nenhuma empresa.",
        )

    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada para o pagamento.")

    before_data = serialize_instance(company)
    provider_status = str(payment_data.get("status") or "").strip().lower() or None
    payment_status, is_paid = _mercado_pago_payment_state(provider_status)
    old_plan = company.plan

    company.plan = _payment_plan(payment_data, company)
    company.billing_cycle = _payment_billing_cycle(payment_data, company)
    company.payment_status = payment_status
    company.mercado_pago_reference = str(payment_data.get("id") or payment_data.get("external_reference") or "")[:120] or None

    if is_paid:
        company.status = "active"
        company.paid_until = _paid_until(payment_data, company.billing_cycle)
    else:
        if company.status != "active":
            company.status = "pending"
            company.paid_until = None

    _sync_settings_for_plan(db, company, old_plan)
    db.commit()
    db.refresh(company)

    action = "PAYMENT_APPROVED" if is_paid else f"PAYMENT_{payment_status.upper()}"
    log_action(
        db,
        action=action,
        entity="company",
        entity_id=company.id,
        user_id=None,
        company_id=company.id,
        request=request_obj,
        before_data=before_data,
        after_data=serialize_instance(company),
        description=f"Pagamento conciliado automaticamente via Mercado Pago ({source}) para {company.name}",
    )
    return _payment_sync_response(company, provider_status)


def confirm_mercado_pago_payment(
    db: Session,
    *,
    payment_id: str | None = None,
    billing_access_token: str | None = None,
    request_obj: Request | None = None,
    source: str = "confirm",
) -> dict[str, object]:
    if not payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe um payment_id válido retornado pelo Mercado Pago.",
        )

    payment_data = _fetch_mercado_pago_payment(str(payment_id))
    company_id = _payment_company_id(payment_data)
    if company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O pagamento recebido não está vinculado a nenhuma empresa.",
        )

    company, _owner = _resolve_company_owner_from_billing_access_token(
        db,
        billing_access_token or "",
        allow_active=True,
    )
    if company.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Confirmação não autorizada para este pagamento.",
        )

    return sync_mercado_pago_payment(db, payment_data, request_obj=request_obj, source=source)


def handle_mercado_pago_webhook(
    db: Session,
    *,
    payload: dict[str, Any] | None,
    query_params: dict[str, Any],
    request_obj: Request | None = None,
) -> dict[str, object]:
    webhook_body = payload or {}
    event_type = str(
        webhook_body.get("type")
        or webhook_body.get("topic")
        or query_params.get("type")
        or query_params.get("topic")
        or ""
    )
    payment_id = (
        webhook_body.get("data", {}).get("id")
        if isinstance(webhook_body.get("data"), dict)
        else None
    ) or webhook_body.get("id") or query_params.get("data.id") or query_params.get("id")

    if event_type and "payment" not in event_type.lower() and not payment_id:
        return {"ok": True, "ignored": True}
    if not payment_id:
        return {"ok": True, "ignored": True}

    payment_sync_result = confirm_mercado_pago_payment(
        db,
        payment_id=str(payment_id),
        request_obj=request_obj,
        source="webhook",
    )
    return {"ok": True, "ignored": False, "result": payment_sync_result}
