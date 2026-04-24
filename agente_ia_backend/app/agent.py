"""
Orquestador del agente IA comercial.

Flujo:
  pregunta → LLM genera SQL → validación → Oracle ejecuta → LLM analiza → respuesta
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from . import db
from .settings import settings
from .sql_safety import validate_select_only
from .llm_service import generate_sql, analyze_results

log = logging.getLogger("agente_ia_backend")


@dataclass
class AgentResult:
    respuesta: str
    sql_generado: str | None
    datos: dict[str, Any] | None


def handle_chat(
    mensaje: str,
    usuario: str,
    contexto: dict[str, Any] | None,
    history: list[dict] | None = None,
) -> AgentResult:
    ctx = contexto or {}

    # cod_empresa: viene de P_COD_EMPRESA en APEX, si está vacío o ausente usa "1"
    if not ctx.get("cod_empresa"):
        ctx["cod_empresa"] = "1"

    # cod_vendedor: filtrar por vendedor del contexto salvo que ver_otros_vendedores esté activo
    ver_otros = str(ctx.get("ver_otros_vendedores", "") or "").strip().upper()
    if ver_otros in ("Y", "1", "TRUE", "S", "YES"):
        ctx.pop("cod_vendedor", None)
    elif ctx.get("cod_vendedor"):
        ctx["cod_vendedor"] = str(ctx["cod_vendedor"]).strip().upper()

    # ── 1. LLM interpreta la pregunta y genera SQL ──────────────────────────
    llm = generate_sql(mensaje, ctx, history)
    sql: str | None = llm.get("sql")
    params: dict = llm.get("params") or {}
    table_desc: str = llm.get("table_description") or ""

    # ── 2. Pregunta fuera del alcance de los datos ───────────────────────────
    if not sql:
        return AgentResult(
            respuesta=(
                "📊 Resumen:\n"
                f"{table_desc}\n\n"
                "📈 Hallazgos clave:\n"
                "- La pregunta está fuera del alcance de los datos disponibles.\n\n"
                "⚠️ Alertas:\n"
                "(sin alertas)\n\n"
                "💡 Recomendaciones:\n"
                "- Podés consultarme sobre ventas, stock, clientes o productos.\n"
                "- Ejemplo: 'top 10 productos del mes', 'clientes sin compra en 60 días', "
                "'artículos con stock crítico', '¿dónde estoy perdiendo ventas?'."
            ),
            sql_generado=None,
            datos={"intencion": "OUT_OF_SCOPE", "usuario": usuario},
        )

    # ── 3. Validar SQL — sólo SELECT, sin palabras peligrosas ───────────────
    validate_select_only(sql)

    # ── 4. Inyectar parámetros del contexto si el LLM los referenció ────────
    if ctx.get("cod_empresa") and ":cod_empresa" in sql and "cod_empresa" not in params:
        params["cod_empresa"] = str(ctx["cod_empresa"])
    if ctx.get("cod_vendedor") and ":cod_vendedor" in sql and "cod_vendedor" not in params:
        params["cod_vendedor"] = str(ctx["cod_vendedor"])

    # ── 5. Ejecutar contra Oracle ────────────────────────────────────────────
    max_rows = min(int(ctx.get("max_rows") or settings.max_rows), 50)
    res = db.query(sql, params, max_rows=max_rows)

    # ── 6. LLM analiza resultados y genera insight de negocio ───────────────
    respuesta = analyze_results(mensaje, sql, table_desc, res.rows, res.columns)

    return AgentResult(
        respuesta=respuesta,
        sql_generado=sql,
        datos={
            "intencion": "LLM_DRIVEN",
            "usuario": usuario,
            "columnas": res.columns,
            "filas": res.rows,
            "total_filas": len(res.rows),
        },
    )
