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


def _btn_html(text: str) -> str:
    style = (
        "display:inline-block;margin:2px 4px 2px 0;padding:4px 10px;"
        "border-radius:12px;border:1px solid #0572c6;color:#0572c6;"
        "background:#fff;cursor:pointer;font-size:11px"
    )
    return (
        f'<button onclick="if(window._aiSend)window._aiSend(this.innerText)" '
        f'style="{style}">{text}</button>'
    )


def _section_html(emoji: str, title: str, questions: list) -> str:
    btns = "".join(_btn_html(q) for q in questions)
    return f'<div style="margin:5px 0"><b>{emoji} {title}:</b><br>{btns}</div>'


def handle_greet(
    usuario: str,
    contexto: dict[str, Any] | None,
) -> AgentResult:
    ctx = contexto or {}
    if not ctx.get("cod_empresa"):
        ctx["cod_empresa"] = "1"

    cod_empresa = str(ctx["cod_empresa"])

    ver_otros = str(ctx.get("ver_otros_vendedores", "") or "").strip().upper()
    cod_vendedor: str | None = None
    if ver_otros not in ("Y", "1", "TRUE", "S", "YES"):
        raw_ven = ctx.get("cod_vendedor")
        if raw_ven:
            cod_vendedor = str(raw_ven).strip().upper()

    # 1. Resolver nombre del empleado
    nombre: str | None = None

    # Estrategia A: NOMBRE_APELLIDO desde V_EMPLEADOS usando P_COD_EMPLEADO (página 0)
    cod_empleado = str(ctx.get("cod_empleado") or "").strip()
    if cod_empleado:
        try:
            r = db.query(
                "SELECT NOMBRE FROM INV.V_EMPLEADOS"
                " WHERE COD_EMPLEADO = :cod_emp AND ROWNUM = 1",
                {"cod_emp": cod_empleado},
                max_rows=1,
            )
            if r.rows:
                val = r.rows[0].get("nombre")
                if val and str(val).strip():
                    nombre = str(val).strip().title()
            log.info("GREET | COD_EMPLEADO=%s → nombre=%s", cod_empleado, nombre)
        except Exception as e:
            log.warning("GREET | V_EMPLEADOS error: %s", e)

    # Estrategia B (fallback): NOMBRE_VENDEDOR desde V_VENTAS_APEX usando cod_vendedor
    if not nombre and cod_vendedor:
        try:
            r = db.query(
                "SELECT NOMBRE_VENDEDOR FROM INV.V_VENTAS_APEX"
                " WHERE COD_VENDEDOR = :cod_vendedor AND COD_EMPRESA = :cod_empresa AND ROWNUM = 1",
                {"cod_vendedor": cod_vendedor, "cod_empresa": cod_empresa},
                max_rows=1,
            )
            if r.rows:
                val = r.rows[0].get("nombre_vendedor")
                if val and str(val).strip():
                    nombre = str(val).strip().title()
            log.info("GREET | NOMBRE_VENDEDOR fallback → nombre=%s", nombre)
        except Exception as e:
            log.warning("GREET | V_VENTAS_APEX error: %s", e)

    first_name = (nombre.split()[0] if nombre else None) or usuario or "vendedor"

    # 2. Mini stats — all fail-safe
    ventas_hoy: float | None = None
    stock_critico: int | None = None
    clientes_inactivos: int | None = None

    try:
        sql_v = (
            "SELECT NVL(SUM(MONTO), 0) AS TOTAL FROM INV.V_VENTAS_APEX"
            " WHERE COD_EMPRESA = :cod_empresa"
            " AND TIP_COMPROBANTE IN ('FCR','FCO')"
            " AND FEC_FACTURA >= TRUNC(SYSDATE)"
        )
        pv: dict = {"cod_empresa": cod_empresa}
        if cod_vendedor:
            sql_v += " AND COD_VENDEDOR = :cod_vendedor"
            pv["cod_vendedor"] = cod_vendedor
        r = db.query(sql_v, pv, max_rows=1)
        if r.rows:
            ventas_hoy = float(r.rows[0].get("total") or 0)
    except Exception:
        pass

    try:
        r = db.query(
            "SELECT COUNT(*) AS CNT FROM ("
            "SELECT COD_ARTICULO FROM INV.V_STOCK_APEX"
            " WHERE COD_EMPRESA = :cod_empresa AND COD_RUBRO = 'PR'"
            " GROUP BY COD_ARTICULO HAVING SUM(CANT_DISPON) <= 5)",
            {"cod_empresa": cod_empresa},
            max_rows=1,
        )
        if r.rows:
            stock_critico = int(r.rows[0].get("cnt") or 0)
    except Exception:
        pass

    try:
        sql_c = (
            "SELECT COUNT(*) AS CNT FROM INV.V_CLIENTE_APEX"
            " WHERE ESTADO = 'ACTIVO'"
            " AND FEC_ULTIMA_COMPRA < TRUNC(SYSDATE) - 60"
            " AND COD_VENDEDOR IS NOT NULL"
        )
        pc: dict = {}
        if cod_vendedor:
            sql_c += " AND COD_VENDEDOR = :cod_vendedor"
            pc["cod_vendedor"] = cod_vendedor
        r = db.query(sql_c, pc, max_rows=1)
        if r.rows:
            clientes_inactivos = int(r.rows[0].get("cnt") or 0)
    except Exception:
        pass

    # 3. Build greeting (HTML con botones clickeables)
    stats: list[str] = []
    if ventas_hoy is not None:
        fmt = f"Gs. {int(ventas_hoy):,}".replace(",", ".")
        stats.append(f"📊 Hoy llevás {fmt} en ventas")
    if stock_critico:
        stats.append(f"⚠️ {stock_critico} artículos con stock crítico o en cero")
    if clientes_inactivos:
        stats.append(f"💡 {clientes_inactivos} clientes sin compras en más de 60 días")

    html: list[str] = []
    html.append(f"<b>Hola {first_name} 👋</b><br>")
    html.append(
        "Soy tu asistente comercial. Te ayudo con "
        "<b>ventas</b>, <b>clientes</b>, <b>stock</b> y <b>oportunidades</b>.<br>"
    )

    if stats:
        html.append("<br><b>📋 Tu situación ahora mismo:</b><br>")
        for s in stats:
            html.append(f"{s}<br>")

    html.append("<br><b>💬 ¿Qué querés consultar hoy?</b>")
    html.append(_section_html("🔥", "Ventas", [
        "¿Cómo voy hoy?",
        "¿Cuánto vendí este mes?",
        "¿Estoy mejor que el mes pasado?",
    ]))
    html.append(_section_html("📦", "Productos", [
        "¿Qué productos puedo vender más hoy?",
        "¿Cuáles son los más vendidos?",
        "¿Qué productos tienen bajo stock?",
    ]))
    html.append(_section_html("🧍", "Clientes", [
        "¿Qué clientes compran más?",
        "¿Qué clientes están inactivos?",
        "¿A quién debería visitar hoy?",
    ]))
    html.append(_section_html("🎯", "Oportunidades", [
        "¿Dónde tengo oportunidades de venta?",
        "¿Qué puedo vender rápido hoy?",
        "¿Qué productos tienen alta demanda y stock disponible?",
    ]))

    return AgentResult(
        respuesta="".join(html),
        sql_generado=None,
        datos={"intencion": "GREET", "usuario": usuario},
    )
