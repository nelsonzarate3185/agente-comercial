from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from .settings import settings


def require_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None),
) -> None:
    """Acepta Bearer JWT (usuarios en inv.usuarios_jwt) o X-API-Key (backward compat APEX)."""

    # 1. Bearer JWT — prioridad
    if authorization and authorization.startswith("Bearer "):
        from .auth import verify_token
        token = authorization[7:].strip()
        if verify_token(token):
            return
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # 2. X-API-Key — compatibilidad con APEX y llamadas internas
    if settings.api_key:
        if x_api_key and x_api_key == settings.api_key:
            return
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 3. Sin configuración de seguridad activa: acceso libre
