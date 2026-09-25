from __future__ import annotations

import os
import subprocess
import sys

import uvicorn


def env_flag(name: str) -> bool | None:
    value = os.getenv(name)
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return None

def should_run_migrations() -> bool:
    explicit = env_flag("RUN_MIGRATIONS")
    if explicit is not None:
        return explicit
    return True

def main() -> None:
    host = os.getenv("UVICORN_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("UVICORN_PORT", "8000")))

    if should_run_migrations():
        print("Aplicando migrations com alembic upgrade head...", flush=True)
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    else:
        print("RUN_MIGRATIONS=0 detectado; iniciando sem migrations.", flush=True)

    print(f"Iniciando Uvicorn em http://{host}:{port}", flush=True)
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )

if __name__ == "__main__":
    main()
