from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings
from app.core.db import engine
from app.routes.audit import router as audit_router
from app.routes.auth import router as auth_router
from app.routes.billing import router as billing_router
from app.routes.company_settings import router as company_settings_router
from app.routes.company_users import router as company_users_router
from app.routes.customers import router as customers_router
from app.routes.dashboard import router as dashboard_router
from app.routes.products import router as products_router
from app.routes.reports import router as reports_router
from app.routes.sales import router as sales_router


app = FastAPI(title="SaaS Controle de Estoque", version="1.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(sales_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(company_settings_router)
app.include_router(company_users_router)
app.include_router(audit_router)


@app.get("/healthz", include_in_schema=False)
def healthcheck():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded", "database": "unreachable"})

    return {"status": "ok", "database": "reachable"}


# Frontend estático
web_dir = Path(__file__).resolve().parent.parent / "web"


app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="web")

