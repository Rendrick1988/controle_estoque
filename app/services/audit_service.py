from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect as sa_inspect

from app.models.audit_log import AuditLog


def _jsonify(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {str(key): _jsonify(item_value) for key, item_value in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonify(item_value) for item_value in value]
    return value


def serialize_instance(instance: Any) -> dict[str, Any] | list[Any] | None:
    if instance is None:
        return None
    if isinstance(instance, (dict, list, tuple, set)):
        return _jsonify(instance)
    if hasattr(instance, "model_dump"):
        return _jsonify(instance.model_dump())

    mapper = sa_inspect(instance).mapper
    return {attr.key: _jsonify(getattr(instance, attr.key)) for attr in mapper.column_attrs}


def request_metadata(request: Request | None) -> tuple[str | None, str | None]:
    if not request:
        return None, None
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


def serialize_audit_log(audit_log: AuditLog) -> dict[str, Any]:
    return {
        "id": audit_log.id,
        "action": audit_log.action,
        "entity": audit_log.entity,
        "entity_id": audit_log.entity_id,
        "user_id": audit_log.user_id,
        "user_email": audit_log.user.email if audit_log.user else None,
        "company_id": audit_log.company_id,
        "company_name": audit_log.company.name if audit_log.company else None,
        "ip_address": audit_log.ip_address,
        "user_agent": audit_log.user_agent,
        "before_data": _jsonify(audit_log.before_data),
        "after_data": _jsonify(audit_log.after_data),
        "description": audit_log.description,
        "created_at": audit_log.created_at,
    }


def log_action(
    db: Session,
    *,
    action: str,
    entity: str,
    entity_id: int | None,
    user_id: int | None,
    company_id: int | None,
    description: str,
    request: Request | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    before_data: dict[str, Any] | list[Any] | None = None,
    after_data: dict[str, Any] | list[Any] | None = None,
    auto_commit: bool = True,
) -> AuditLog:
    request_ip, request_agent = request_metadata(request)
    audit_log = AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        user_id=user_id,
        company_id=company_id,
        ip_address=ip_address or request_ip,
        user_agent=user_agent or request_agent,
        before_data=_jsonify(before_data),
        after_data=_jsonify(after_data),
        description=description,
    )
    db.add(audit_log)
    if auto_commit:
        db.commit()
        db.refresh(audit_log)
    else:
        db.flush()
    return audit_log

