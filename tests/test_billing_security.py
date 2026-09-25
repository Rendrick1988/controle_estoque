from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from app.core.db import Base
from app.models.company import Company
from app.routes.auth import register_company
from app.schemas.billing import BillingCheckoutRequest
from app.schemas.user import RegisterRequest
from app.services.billing_service import create_mercado_pago_checkout, confirm_mercado_pago_payment


class BillingSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def _request(self, path: str) -> Request:
        return Request(
            {
                "type": "http",
                "method": "POST",
                "path": path,
                "headers": [],
                "client": ("127.0.0.1", 12345),
            }
        )

    def _register_company(self, *, company_name: str, email: str, plan: str = "basic") -> dict:
        with self.SessionLocal() as db:
            response = register_company(
                RegisterRequest(
                    company={"name": company_name},
                    plan=plan,
                    billing_cycle="monthly",
                    admin={
                        "email": email,
                        "full_name": "Responsável",
                        "password": "senha-segura-123",
                    },
                ),
                request=self._request("/api/auth/register"),
                db=db,
            )
            return response.model_dump()

    def _get_company(self, *, company_name: str) -> Company:
        with self.SessionLocal() as db:
            company = db.scalar(select(Company).where(Company.name == company_name))
            self.assertIsNotNone(company)
            return company

    def test_paid_registration_returns_billing_access_token(self) -> None:
        registration = self._register_company(company_name="Empresa Token", email="token@example.com")

        self.assertEqual(registration["company"]["status"], "pending")
        self.assertTrue(registration["billing_access_token"])

    def test_checkout_accepts_valid_billing_token(self) -> None:
        registration = self._register_company(company_name="Empresa Checkout", email="checkout@example.com")

        with self.SessionLocal() as db, patch(
            "app.services.billing_service._mercado_pago_request_json",
            return_value={
                "init_point": "https://mp.test/checkout",
                "sandbox_init_point": "https://sandbox.mp.test/checkout",
            },
        ):
            payload = create_mercado_pago_checkout(
                db,
                BillingCheckoutRequest(
                    billing_access_token=registration["billing_access_token"],
                    plan="professional",
                    billing_cycle="annual",
                    company_name="Empresa Checkout",
                    email="checkout@example.com",
                ),
                request_obj=self._request("/api/billing/mercado-pago/checkout"),
            )

        self.assertEqual(payload["checkout_url"], "https://mp.test/checkout")
        self.assertEqual(payload["plan"], "professional")
        self.assertEqual(payload["billing_cycle"], "annual")

        company = self._get_company(company_name="Empresa Checkout")
        self.assertEqual(company.plan, "professional")
        self.assertEqual(company.billing_cycle, "annual")
        self.assertEqual(company.status, "pending")
        self.assertTrue(company.mercado_pago_reference)

    def test_checkout_token_cannot_be_redirected_to_another_company(self) -> None:
        alpha = self._register_company(company_name="Empresa Alpha", email="alpha@example.com")
        self._register_company(company_name="Empresa Beta", email="beta@example.com")

        with self.SessionLocal() as db:
            with self.assertRaises(HTTPException) as context:
                create_mercado_pago_checkout(
                    db,
                    BillingCheckoutRequest(
                        billing_access_token=alpha["billing_access_token"],
                        plan="premium",
                        billing_cycle="monthly",
                        company_name="Empresa Beta",
                        email="beta@example.com",
                    ),
                    request_obj=self._request("/api/billing/mercado-pago/checkout"),
                )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "O nome da empresa não confere com o cadastro salvo.")

        alpha_company = self._get_company(company_name="Empresa Alpha")
        beta_company = self._get_company(company_name="Empresa Beta")
        self.assertIsNone(alpha_company.mercado_pago_reference)
        self.assertIsNone(beta_company.mercado_pago_reference)
        self.assertEqual(beta_company.plan, "basic")

    def test_confirm_requires_payment_id(self) -> None:
        self._register_company(company_name="Empresa Confirm", email="confirm@example.com")

        with self.SessionLocal() as db, self.assertRaises(HTTPException) as context:
            confirm_mercado_pago_payment(db, request_obj=self._request("/api/billing/mercado-pago/confirm"))

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            "Informe um payment_id válido retornado pelo Mercado Pago.",
        )

    def test_confirm_rejects_payment_from_another_company(self) -> None:
        alpha = self._register_company(company_name="Empresa Confirm Alpha", email="confirm-alpha@example.com")
        beta = self._register_company(company_name="Empresa Confirm Beta", email="confirm-beta@example.com")

        with self.SessionLocal() as db, patch(
            "app.services.billing_service._fetch_mercado_pago_payment",
            return_value={
                "id": "mp-payment-123",
                "status": "approved",
                "metadata": {
                    "company_id": beta["company"]["id"],
                    "plan": "basic",
                    "billing_cycle": "monthly",
                },
            },
        ), self.assertRaises(HTTPException) as context:
            confirm_mercado_pago_payment(
                db,
                payment_id="mp-payment-123",
                billing_access_token=alpha["billing_access_token"],
                request_obj=self._request("/api/billing/mercado-pago/confirm"),
            )

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Confirmação não autorizada para este pagamento.")


if __name__ == "__main__":
    unittest.main()
