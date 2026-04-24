from __future__ import annotations

import re


_DANGEROUS = re.compile(
    r"\b("
    r"delete|update|insert|merge|drop|alter|truncate|create|replace|grant|revoke|"
    r"commit|rollback|execute|dbms_|utl_|begin|declare|call"
    r")\b",
    re.IGNORECASE,
)

_SELECT_ONLY = re.compile(r"^\s*select\b", re.IGNORECASE)


def validate_select_only(sql: str) -> None:
    if not _SELECT_ONLY.search(sql or ""):
        raise ValueError("Solo se permiten consultas SELECT.")
    if _DANGEROUS.search(sql):
        raise ValueError("SQL bloqueado por seguridad (palabra reservada peligrosa).")

