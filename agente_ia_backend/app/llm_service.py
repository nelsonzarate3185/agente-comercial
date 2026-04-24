"""
Servicio LLM — generación de SQL y análisis de resultados usando Claude (Anthropic).
Dos responsabilidades separadas:
  1. generate_sql  → interpreta la pregunta, devuelve SQL + params
  2. analyze_results → interpreta los datos y devuelve insight de negocio
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx
import anthropic

from .settings import settings
from .schema_catalog import build_schema_text

log = logging.getLogger("agente_ia_backend")

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY no configurada en .env. "
                "Obtené una clave en https://console.anthropic.com/"
            )
        # Proxy corporativo con certificado autofirmado: deshabilitamos verificación SSL.
        http_client = httpx.Client(verify=False)
        _client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            http_client=http_client,
        )
    return _client


_SCHEMA_TEXT = build_schema_text()

_SQL_SYSTEM = f"""Eres un experto en Oracle SQL 12c para una empresa distribuidora comercial.
Tu única función es transformar preguntas de negocio en consultas SQL correctas y seguras.

VISTAS DISPONIBLES (usa siempre el prefijo del esquema INV.):
{_SCHEMA_TEXT}

REGLAS OBLIGATORIAS — NUNCA las violes:
1. Genera ÚNICAMENTE sentencias SELECT. Jamás INSERT, UPDATE, DELETE, DROP, MERGE, EXECUTE ni DDL.
2. Sintaxis Oracle 12c: FETCH FIRST N ROWS ONLY (no LIMIT), NVL(), TRUNC(), ADD_MONTHS(), TO_CHAR()
3. Limita siempre resultados: máximo 50 filas. Usa FETCH FIRST 20 ROWS ONLY (o el N apropiado).
4. Filtros de fecha estándar Oracle:
   - Mes actual:     FEC >= TRUNC(SYSDATE,'MM') AND FEC < ADD_MONTHS(TRUNC(SYSDATE,'MM'),1)
   - Hoy:            FEC >= TRUNC(SYSDATE)
   - Últimos N días: FEC >= TRUNC(SYSDATE) - :dias
   - Año actual:     FEC >= TRUNC(SYSDATE,'YYYY')
5. Bind variables Oracle con :nombre. Ejemplos: :cod_empresa, :dias, :min_stock, :top_n
6. Si el contexto incluye cod_empresa, SIEMPRE agrega AND COD_EMPRESA = :cod_empresa al WHERE.
7. Alias de columnas sin espacios (usa guion bajo). Ej: total_monto, cant_unidades.
8. Para JOINs usa los campos comunes: COD_ARTICULO, COD_CLIENTE, COD_VENDEDOR entre vistas.
9. Cuando se pide "top N" sin número, usa 10. Cuando se pide comparativa, usa subconsultas o CASE.
10. Preguntas de cruce de datos (ej: "alta demanda + bajo stock"): JOIN entre V_VENTAS_APEX y V_STOCK_APEX por COD_ARTICULO.
11. TIP_COMPROBANTE CRÍTICO — NUNCA uses 'FT'. Los valores correctos son: 'FCR' y 'FCO' para ventas reales, 'NCR' para notas de crédito. Para analizar ventas SIEMPRE filtra: AND TIP_COMPROBANTE IN ('FCR','FCO')
12. Para filtrar stock por "rubro" o tipo de producto, usa DESC_DIVISION en INV.V_STOCK_APEX. Valores típicos: 'PRODUCTOS', 'REPUESTOS'. DESC_FAMILIA para subfamilia.
13. Para promociones vigentes: AND FECHA_INICIO <= TRUNC(SYSDATE) AND FECHA_FIN >= TRUNC(SYSDATE). PROMO_MIX='S' son promos mix, 'N' son normales. Filtrar COD_EMPRESA_PROMO = :cod_empresa si está en contexto.
14. Si el contexto incluye cod_vendedor, SIEMPRE agrega AND COD_VENDEDOR = :cod_vendedor en consultas sobre V_VENTAS_APEX y V_CLIENTE_APEX.

RESPONDE ÚNICAMENTE con JSON válido, sin markdown, sin texto adicional antes o después:
{{
  "sql": "SELECT ...",
  "params": {{"param1": valor1, "param2": valor2}},
  "table_description": "Una oración describiendo qué representa cada fila del resultado"
}}

Si la pregunta es imposible de responder con las vistas disponibles:
{{"sql": null, "params": {{}}, "table_description": "Motivo: [explicación]"}}
"""

_ANALYSIS_SYSTEM = """Eres un analista de inteligencia comercial senior de una empresa distribuidora.
Recibirás: la pregunta del usuario, el SQL ejecutado y los resultados.
Tu tarea: generar un análisis de negocio claro, específico y accionable.

FORMATO OBLIGATORIO — usa exactamente estos emojis y secciones, en este orden:

📊 Resumen:
[2-3 oraciones con el hallazgo principal. Incluye cifras concretas de los datos.]

📈 Hallazgos clave:
- [hallazgo 1 con número o valor real del resultado]
- [hallazgo 2 con número o valor real del resultado]
- [hallazgo 3 si aplica, omitir si no hay datos suficientes]

⚠️ Alertas:
[alerta concreta de riesgo basada en los datos, o "(sin alertas críticas)" si todo está bien]

💡 Recomendaciones:
- [acción comercial concreta 1 — quién debe hacer qué]
- [acción comercial concreta 2 — quién debe hacer qué]

REGLAS DE ANÁLISIS:
- Usa los números exactos del resultado, nunca los inventes ni redondees sin decirlo
- Nombra entidades concretas: "el cliente GARCIA S.A. no compra hace 45 días" (no "hay clientes inactivos")
- Si el resultado está vacío, explica qué significa y qué ajuste probar
- Detecta anomalías: valores extremos, caídas, crecimiento inusual
- Para stock: si CANT_DISPON = 0, es quiebre; si <= 5, es crítico
- Para clientes: > 60 días sin compra es inactividad; deuda vencida > crédito disponible es bloqueo inminente
- Para ventas: compara con el contexto (top productos, caídas, concentración de clientes)
- Sé directo y específico. Máximo 300 palabras en total.

TABLA HTML — Si el resultado tiene 3 o más filas, incluye en "📈 Hallazgos clave:" una tabla HTML compacta (máximo 10 filas, 5 columnas más relevantes) con este formato exacto:
<table style="width:100%;border-collapse:collapse;font-size:12px;margin:6px 0"><tr style="background:#0572c6;color:#fff"><th style="padding:4px 6px;text-align:left">COLUMNA</th></tr><tr style="border-bottom:1px solid #eee"><td style="padding:4px 6px">VALOR</td></tr></table>
Usa los nombres de columna reales del resultado. Fuera de la tabla sigue usando texto plano.
"""


def generate_sql(
    question: str,
    context: dict[str, Any],
    history: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Genera SQL a partir de la pregunta usando el LLM.
    Retorna: {"sql": str|None, "params": dict, "table_description": str}
    """
    client = _get_client()

    messages: list[dict] = []

    # Historial de conversación — últimas 6 entradas (3 pares user/assistant)
    if history:
        for h in history[-6:]:
            role = h.get("role", "")
            content = h.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": str(content)[:2000]})

    # Construir mensaje del usuario con contexto
    ctx_parts: list[str] = []
    if context.get("cod_empresa"):
        ctx_parts.append(f"cod_empresa='{context['cod_empresa']}'")
    if context.get("cod_vendedor"):
        ctx_parts.append(f"cod_vendedor='{context['cod_vendedor']}'")
    if context.get("periodo"):
        ctx_parts.append(f"periodo='{context['periodo']}'")

    user_content = f"Pregunta: {question}"
    if ctx_parts:
        user_content += "\nContexto disponible: " + ", ".join(ctx_parts)

    messages.append({"role": "user", "content": user_content})

    log.info("LLM→SQL | pregunta: %.100s", question)

    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=1024,
        system=_SQL_SYSTEM,
        messages=messages,
    )

    raw = response.content[0].text.strip()

    # Limpiar markdown si el LLM lo agrega (no debería, pero por las dudas)
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json\n"):
            raw = raw[5:]
        elif raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        log.error("LLM devolvió JSON inválido: %.300s", raw)
        raise ValueError(f"El modelo devolvió una respuesta no estructurada: {raw[:150]}")

    return result


def analyze_results(
    question: str,
    sql: str,
    table_description: str,
    rows: list[dict],
    columns: list[str],
) -> str:
    """
    Analiza los resultados de la consulta y devuelve un insight de negocio formateado.
    """
    client = _get_client()

    if not rows:
        data_text = "(La consulta no retornó ninguna fila — resultado vacío)"
    else:
        header = " | ".join(columns)
        separator = "-" * min(len(header), 120)
        data_lines = [header, separator]
        for row in rows[:25]:
            data_lines.append(" | ".join(str(row.get(c, "")) for c in columns))
        if len(rows) > 25:
            data_lines.append(f"... ({len(rows)} filas en total, mostrando las primeras 25)")
        data_text = "\n".join(data_lines)

    content = (
        f"Pregunta del usuario: {question}\n\n"
        f"SQL ejecutado:\n{sql}\n\n"
        f"Descripción del resultado: {table_description}\n\n"
        f"Datos obtenidos:\n{data_text}"
    )

    log.info("LLM→análisis | filas=%d cols=%s", len(rows), columns[:5])

    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=1500,
        system=_ANALYSIS_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )

    return response.content[0].text.strip()
