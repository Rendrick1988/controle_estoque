from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"
BILLING_ACCESS_SCOPE = "billing_checkout"
PASSWORD_RESET_SCOPE = "password_reset"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def _encode_token(
    subject: str,
    *,
    expires_minutes: int,
    extra_claims: dict[str, object] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode: dict[str, object] = {"sub": subject, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    return _encode_token(
        subject,
        expires_minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_billing_access_token(*, user_id: int, company_id: int, expires_minutes: int = 12 * 60) -> str:
    return _encode_token(
        str(user_id),
        expires_minutes=expires_minutes,
        extra_claims={"scope": BILLING_ACCESS_SCOPE, "company_id": company_id},
    )


def create_password_reset_token(user_id: int, expires_minutes: int | None = None) -> str:
    return _encode_token(
        str(user_id),
        expires_minutes=expires_minutes or settings.PASSWORD_RESET_EXPIRE_MINUTES,
        extra_claims={"scope": PASSWORD_RESET_SCOPE},
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Token inválido") from e


def decode_billing_access_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("scope") != BILLING_ACCESS_SCOPE:
        raise ValueError("Token inválido")
    return payload


def decode_password_reset_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("scope") != PASSWORD_RESET_SCOPE:
        raise ValueError("Token inválido")
    return payload

