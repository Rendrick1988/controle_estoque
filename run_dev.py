from __future__ import annotations

import os
import platform

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

def should_enable_reload() -> bool:
    explicit = env_flag("UVICORN_RELOAD")
    if explicit is not None:
        return explicit
    return platform.system() != "Windows"

def main() -> None:
    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("UVICORN_PORT", "8000")))
    reload_enabled = should_enable_reload()

    if platform.system() == "Windows" and not reload_enabled:
        print(
            "Reload desativado automaticamente no Windows para evitar "
            "PermissionError: [WinError 5] com uvicorn --reload.",
            flush=True,
        )

    uvicorn.run("app.main:app", host=host, port=port, reload=reload_enabled)

if __name__ == "__main__":
    main()
