from __future__ import annotations

from datetime import datetime
import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from app.core.db import Base
from app.core.security import hash_password
from app.dependencies.authorization import require_company_permission
from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.product import Product
from app.models.user import User
from app.routes.auth import get_current_user_profile
from app.routes.company_settings import update_company_settings_route
from app.routes.products import get_product
from app.schemas.company_settings import CompanySettingsUpdate
from app.schemas.product import ProductCreate


class InternalSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.seed: dict[str, int] = self._seed_data()

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def _seed_data(self) -> dict[str, int]:
        with self.SessionLocal() as db:
            alpha = Company(
                name="Alpha",
                status="active",
                plan="premium",
                billing_cycle="monthly",
                payment_status="paid",
            )
            beta = Company(
                name="Beta",
                status="active",
                plan="premium",
                billing_cycle="monthly",
                payment_status="paid",
            )
            db.add_all([alpha, beta])
            db.flush()

            db.add_all(
                [
                    CompanySettings(company_id=alpha.id, theme="light", primary_color="#111111", features=["vendas"]),
                    CompanySettings(company_id=beta.id, theme="light", primary_color="#222222", features=["vendas"]),
                ]
            )

            alpha_admin = User(
                company_id=alpha.id,
                email="alpha-admin@example.com",
                full_name="Alpha Admin",
                hashed_password=hash_password("senha-segura-123"),
                role="admin",
                is_company_owner=True,
                is_active=True,
            )
            alpha_user = User(
                company_id=alpha.id,
                email="alpha-user@example.com",
                full_name="Alpha User",
                hashed_password=hash_password("senha-segura-123"),
                role="user",
                is_company_owner=False,
                is_active=True,
            )
            beta_admin = User(
                company_id=beta.id,
                email="beta-admin@example.com",
                full_name="Beta Admin",
                hashed_password=hash_password("senha-segura-123"),
                role="admin",
                is_company_owner=True,
                is_active=True,
            )
            db.add_all([alpha_admin, alpha_user, beta_admin])
            db.flush()

            beta_product = Product(
                company_id=beta.id,
                name="Produto Beta",
                sku="BETA-001",
                description="Item privado",
                quantity=5,
                validity=datetime(2099, 1, 1),
                min_quantity=1,
                price=10,
            )
            db.add(beta_product)
            db.commit()

            return {
                "alpha_admin_id": alpha_admin.id,
                "alpha_user_id": alpha_user.id,
                "beta_admin_id": beta_admin.id,
                "beta_product_id": beta_product.id,
            }

    def _get_user(self, user_id: int) -> User:
        with self.SessionLocal() as db:
            user = db.get(User, user_id)
            assert user is not None, f"Usuário de teste {user_id} não encontrado"
            return user

    def _request(self, path: str) -> Request:
        return Request(
            {
                "type": "http",
                "method": "PUT",
                "path": path,
                "headers": [],
                "client": ("127.0.0.1", 12345),
            }
        )

    def test_company_owner_is_exposed_as_admin_role(self) -> None:
        with self.SessionLocal() as db:
            payload = get_current_user_profile(
                current_user=self._get_user(self.seed["alpha_admin_id"]),
                db=db,
            )

        self.assertEqual(payload.role, "admin")
        self.assertTrue(payload.is_company_owner)

    def test_collaborator_cannot_update_company_settings(self) -> None:
        collaborator = self._get_user(self.seed["alpha_user_id"])
        dependency = require_company_permission("settings:write")

        with self.assertRaises(HTTPException) as context:
            dependency(current_user=collaborator)

        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("alterar as configurações da empresa", context.exception.detail)

    def test_collaborator_cannot_manage_company_users(self) -> None:
        collaborator = self._get_user(self.seed["alpha_user_id"])
        dependency = require_company_permission("company_users:manage")

        with self.assertRaises(HTTPException) as context:
            dependency(current_user=collaborator)

        self.assertEqual(context.exception.status_code, 403)

    def test_product_idor_is_blocked_across_companies(self) -> None:
        with self.SessionLocal() as db:
            with self.assertRaises(HTTPException) as context:
                get_product(
                    product_id=self.seed["beta_product_id"],
                    db=db,
                    current_user=self._get_user(self.seed["alpha_admin_id"]),
                )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Produto não encontrado")

    def test_product_payload_rejects_unexpected_company_id(self) -> None:
        with self.assertRaises(ValidationError) as context:
            ProductCreate.model_validate(
                {
                    "name": "Produto Seguro",
                    "sku": "ALPHA-001",
                    "quantity": 2,
                    "validity": datetime(2099, 1, 1),
                    "min_quantity": 1,
                    "price": 19.9,
                    "description": "Validação rígida",
                    "company_id": 999,
                }
            )

        self.assertIn("company_id", str(context.exception))

    def test_company_settings_logo_url_requires_safe_scheme(self) -> None:
        with self.assertRaises(ValidationError) as context:
            CompanySettingsUpdate(logo_url="javascript:alert(1)")

        self.assertIn("URL segura", str(context.exception))

    def test_admin_can_update_company_settings(self) -> None:
        with self.SessionLocal() as db:
            current_user = require_company_permission("settings:write")(
                current_user=self._get_user(self.seed["alpha_admin_id"])
            )
            updated = update_company_settings_route(
                payload=CompanySettingsUpdate(theme="dark", primary_color="#123456"),
                request=self._request("/api/settings/company"),
                db=db,
                current_user=current_user,
            )
            updated_theme = updated.theme
            updated_primary_color = updated.primary_color

        self.assertEqual(updated_theme, "dark")
        self.assertEqual(updated_primary_color, "#123456")


if __name__ == "__main__":
    unittest.main()
