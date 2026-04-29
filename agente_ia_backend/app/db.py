from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import oracledb

from .settings import settings

_BIND_RE = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")


def _filter_binds(sql: str, binds: dict) -> dict:
    """Devuelve solo los bind variables que aparecen realmente en el SQL.
    Evita ORA-01036 cuando el LLM incluye parámetros extra en el dict."""
    used = {m.upper() for m in _BIND_RE.findall(sql)}
    return {k: v for k, v in binds.items() if k.upper() in used}

# Thick mode para compatibilidad con hashes de contraseña antiguos (10g/11g verifier).
oracledb.init_oracle_client(lib_dir=r"C:\app\client\product\12.2.0\client_1")


def _make_dsn() -> str:
    return oracledb.makedsn(
        host=settings.oracle_host,
        port=settings.oracle_port,
        service_name=settings.oracle_service,
    )


_pool: oracledb.ConnectionPool | None = None


def get_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool

    # oracledb defaults to "thin" mode unless init_oracle_client is used.
    _pool = oracledb.create_pool(
        user=settings.oracle_user,
        password=settings.oracle_password,
        dsn=_make_dsn(),
        min=1,
        max=4,
        increment=1,
        getmode=oracledb.POOL_GETMODE_WAIT,
        timeout=60,
        wait_timeout=15,
        retry_count=1,
        retry_delay=1,
    )
    return _pool


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[dict[str, Any]]


def query(sql: str, binds: dict[str, Any] | None = None, *, max_rows: int) -> QueryResult:
    import logging
    _log = logging.getLogger("agente_ia_backend")
    pool = get_pool()
    binds = _filter_binds(sql, binds or {})
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.arraysize = min(max_rows, 200)
            try:
                cur.execute(sql, binds)
            except oracledb.DatabaseError:
                _log.error("DB.query FAILED\nSQL: %s\nbinds: %s", sql, binds)
                raise
            cols = [d[0].lower() for d in (cur.description or [])]
            fetched = cur.fetchmany(numRows=max_rows)
            out_rows: list[dict[str, Any]] = []
            for r in fetched:
                out_rows.append({cols[i]: r[i] for i in range(len(cols))})
            return QueryResult(columns=cols, rows=out_rows)


def query_scalar(sql: str, binds: dict[str, Any] | None = None) -> Any:
    pool = get_pool()
    binds = _filter_binds(sql, binds or {})
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, binds)
            row = cur.fetchone()
            return row[0] if row else None

