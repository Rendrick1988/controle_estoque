from __future__ import annotations

from typing import Literal

PlanCode = Literal["free", "basic", "professional", "premium"]
BillingCycle = Literal["monthly", "annual"]
PaymentStatus = Literal["pending", "paid", "past_due", "canceled"]

SUPPORTED_PLANS: tuple[PlanCode, ...] = ("free", "basic", "professional", "premium")
SUPPORTED_BILLING_CYCLES: tuple[BillingCycle, ...] = ("monthly", "annual")
SUPPORTED_PAYMENT_STATUSES: tuple[PaymentStatus, ...] = ("pending", "paid", "past_due", "canceled")
PLAN_ALIASES: dict[str, PlanCode] = {
    "gratis": "free",
    "gratuito": "free",
}
BILLING_CYCLE_ALIASES: dict[str, BillingCycle] = {}
PAYMENT_STATUS_ALIASES: dict[str, PaymentStatus] = {
    "unpaid": "pending",
    "overdue": "past_due",
}
ALL_PLAN_CAPABILITIES = {
    "vendas",
    "clientes",
    "relatorio",
    "dashboard_avancado",
    "multi_users",
    "audit",
    "exports",
}
DEFAULT_PLAN_FEATURES = ["vendas", "relatorio", "dashboard_avancado"]

PLAN_CAPABILITIES: dict[PlanCode, set[str]] = {
    "free": ALL_PLAN_CAPABILITIES.copy(),
    "basic": ALL_PLAN_CAPABILITIES.copy(),
    "professional": ALL_PLAN_CAPABILITIES.copy(),
    "premium": ALL_PLAN_CAPABILITIES.copy(),
}

PLAN_FEATURES: dict[PlanCode, list[str]] = {
    "free": DEFAULT_PLAN_FEATURES.copy(),
    "basic": DEFAULT_PLAN_FEATURES.copy(),
    "professional": DEFAULT_PLAN_FEATURES.copy(),
    "premium": DEFAULT_PLAN_FEATURES.copy(),
}

PLAN_CAPS: dict[PlanCode, dict[str, int | None]] = {
    "free": {
        "products": 15,
        "customers": 15,
        "users": 1,
        "sales": 30,
        "report_history": 30,
        "audit_logs": 30,
        "sales_list": 30,
        "report_days": 7,
        "report_months": 3,
        "top_products": 3,
        "dashboard_days": 7,
        "dashboard_months": 3,
        "dashboard_top": 3,
        "dashboard_recent_sales": 3,
    },
    "basic": {
        "products": 80,
        "customers": 80,
        "users": 2,
        "sales": 500,
        "report_history": 90,
        "audit_logs": 120,
        "sales_list": 80,
        "report_days": 30,
        "report_months": 12,
        "top_products": 8,
        "dashboard_days": 14,
        "dashboard_months": 12,
        "dashboard_top": 5,
        "dashboard_recent_sales": 5,
    },
    "professional": {
        "products": 400,
        "customers": 400,
        "users": 5,
        "sales": 5000,
        "report_history": 300,
        "audit_logs": 400,
        "sales_list": 300,
        "report_days": 90,
        "report_months": 24,
        "top_products": 15,
        "dashboard_days": 14,
        "dashboard_months": 12,
        "dashboard_top": 8,
        "dashboard_recent_sales": 8,
    },
    "premium": {
        "products": None,
        "customers": None,
        "users": 15,
        "sales": None,
        "report_history": 1000,
        "audit_logs": 1000,
        "sales_list": 500,
        "report_days": 365,
        "report_months": 36,
        "top_products": 50,
        "dashboard_days": 14,
        "dashboard_months": 12,
        "dashboard_top": 8,
        "dashboard_recent_sales": 8,
    },
}

PLAN_OFFERS: dict[PlanCode, dict[str, object]] = {
    "free": {
        "code": "free",
        "name": "Plano Free",
        "badge": "Gratuito",
        "monthly_price": 0,
        "annual_price": 0,
        "audience": ["quem esta comecando", "micro negocios", "teste inicial"],
        "includes": ["todos os modulos liberados", "ate 15 produtos e 15 clientes", "ate 30 vendas", "limites iniciais"],
        "why": "Ideal para usar o sistema completo sem custo e crescer no seu ritmo.",
    },
    "basic": {
        "code": "basic",
        "name": "Plano Básico",
        "badge": "Essencial",
        "monthly_price": 59,
        "annual_price": 590,
        "audience": ["pequenos negocios", "autonomos", "lojas em operacao"],
        "includes": ["todos os modulos liberados", "ate 80 produtos e 80 clientes", "ate 500 vendas", "ate 2 usuarios"],
        "why": "Um passo simples para operar o sistema completo com mais folga no dia a dia.",
    },
    "professional": {
        "code": "professional",
        "name": "Plano Profissional",
        "badge": "Mais vendido",
        "monthly_price": 129,
        "annual_price": 1290,
        "audience": ["empresas em crescimento", "times pequenos", "rotina comercial ativa"],
        "includes": ["todos os modulos liberados", "ate 400 produtos e 400 clientes", "ate 5 usuarios", "historico ampliado"],
        "why": "Perfeito para empresas que querem mais volume, mais visibilidade e mais organizacao.",
    },
    "premium": {
        "code": "premium",
        "name": "Plano Premium",
        "badge": "Alta performance",
        "monthly_price": 249,
        "annual_price": 2490,
        "audience": ["operacoes maiores", "equipes que exigem controle", "gestao orientada por dados"],
        "includes": ["todos os modulos liberados", "produtos e vendas sem teto", "ate 15 usuarios", "maior historico e auditoria"],
        "why": "Controle maximo para empresas que precisam de escala, seguranca e performance.",
    },
}


def normalize_plan(plan: str | None) -> PlanCode:
    raw = (plan or "basic").strip().lower()
    normalized = PLAN_ALIASES.get(raw, raw)
    if normalized in SUPPORTED_PLANS:
        return normalized
    return "basic"


def normalize_billing_cycle(billing_cycle: str | None) -> BillingCycle:
    raw = (billing_cycle or "monthly").strip().lower()
    normalized = BILLING_CYCLE_ALIASES.get(raw, raw)
    if normalized in SUPPORTED_BILLING_CYCLES:
        return normalized
    return "monthly"


def normalize_payment_status(payment_status: str | None) -> PaymentStatus:
    raw = (payment_status or "pending").strip().lower()
    normalized = PAYMENT_STATUS_ALIASES.get(raw, raw)
    if normalized in SUPPORTED_PAYMENT_STATUSES:
        return normalized
    return "pending"


def plan_filter_values(plan: str | None) -> tuple[str, ...]:
    normalized = normalize_plan(plan)
    return (normalized,)


def plan_capabilities(plan: str | None) -> list[str]:
    return sorted(PLAN_CAPABILITIES[normalize_plan(plan)])


def plan_supports(plan: str | None, capability: str) -> bool:
    return capability.strip().lower() in PLAN_CAPABILITIES[normalize_plan(plan)]


def default_features_for_plan(plan: str | None) -> list[str]:
    return PLAN_FEATURES[normalize_plan(plan)].copy()


def sanitize_features_for_plan(plan: str | None, features: list[str] | None) -> list[str]:
    allowed = set(default_features_for_plan(plan))
    selected = list(features or [])
    sanitized: list[str] = []
    seen: set[str] = set()
    for feature in selected:
        value = (feature or "").strip().lower()
        if not value or value not in allowed or value in seen:
            continue
        sanitized.append(value)
        seen.add(value)
    return sanitized


def plan_caps(plan: str | None) -> dict[str, int | None]:
    return PLAN_CAPS[normalize_plan(plan)].copy()


def plan_offer(plan: str | None) -> dict[str, object]:
    return PLAN_OFFERS[normalize_plan(plan)].copy()
