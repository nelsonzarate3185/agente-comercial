from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from .db import query_scalar
from .settings import settings

log = logging.getLogger("agente_ia_backend")


def validate_user_db(nombre_usuario: str, clave_secreta: str) -> bool:
    """Valida credenciales contra INV.USUARIOS_JWT. Devuelve True si el usuario
    existe, la clave coincide y ACTIVO = 'S'."""
    sql = """
        SELECT COUNT(*)
          FROM inv.usuarios_jwt
         WHERE UPPER(nombre_usuario) = UPPER(:nombre_usuario)
           AND clave_secreta        = :clave_secreta
           AND ACTIVO               = 'S'
    """
    try:
        count = query_scalar(sql, {
            "nombre_usuario": nombre_usuario,
            "clave_secreta": clave_secreta,
        })
        return int(count or 0) > 0
    except Exception:
        log.exception("Error validando usuario JWT en DB")
        return False


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[str]:
    """Verifica el token y devuelve el subject (username) o None si es inválido."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        log.debug("JWT expirado")
        return None
    except jwt.InvalidTokenError as e:
        log.debug("JWT inválido: %s", e)
        return None
