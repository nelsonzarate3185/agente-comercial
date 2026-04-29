"""
Orquestador del agente IA comercial.

Flujo:
  pregunta → LLM genera SQL → validación → Oracle ejecuta → LLM analiza → respuesta
"""
from __future__ import annotations

import logging
import re
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


def _agrupar_items(items_raw: list[dict]) -> list[dict]:
    """Agrupa artículos con el mismo cod sumando cantidades (elimina duplicados)."""
    agrupado: dict = {}
    for item in items_raw:
        cod = item["cod"]
        if cod in agrupado:
            agrupado[cod]["qty"] += item["qty"]
        else:
            agrupado[cod] = dict(item)
    return [v for v in agrupado.values() if v["qty"] > 0]


def _calcular_cantidad_sugerida(cant_cliente, cant_vendedor) -> int:
    """Cantidad sugerida: historial cliente → 80% promedio vendedor → mínimo 1."""
    try:
        c = float(cant_cliente or 0)
        if c > 0:
            return max(1, round(c))
    except (TypeError, ValueError):
        pass
    try:
        v = float(cant_vendedor or 0)
        if v > 0:
            return max(1, round(v * 0.8))
    except (TypeError, ValueError):
        pass
    return 1


def _inject_vendor_filter(sql: str, cod_vendedor: str, params: dict) -> tuple[str, dict]:
    """Garantiza AND COD_VENDEDOR = :P_COD_VENDEDOR si el LLM lo omitió."""
    sql_upper = sql.upper()

    # Ya tiene el filtro — solo asegurar el parámetro
    if "P_COD_VENDEDOR" in sql_upper:
        if "P_COD_VENDEDOR" not in params:
            params["P_COD_VENDEDOR"] = cod_vendedor
        return sql, params

    # No aplica a este SQL (no usa vistas que requieren filtro de vendedor)
    _vendor_views = ("V_VENTAS_APEX", "V_CLIENTE_APEX", "V_PEDIDOS_PRODUCTOS", "V_METAS_VENDEDORES")
    if not any(v in sql_upper for v in _vendor_views):
        return sql, params

    # Buscar la primera cláusula de nivel superior (profundidad 0 de paréntesis)
    # para insertar el filtro justo antes
    depth = 0
    pos_insert = None
    kw = re.compile(r"GROUP\s+BY|ORDER\s+BY|FETCH\s+FIRST|HAVING", re.IGNORECASE)
    i = 0
    while i < len(sql):
        c = sql[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0:
            m = kw.match(sql, i)
            if m:
                pos_insert = i
                break
        i += 1

    if pos_insert is not None:
        sql = sql[:pos_insert].rstrip() + " AND COD_VENDEDOR = :P_COD_VENDEDOR " + sql[pos_insert:]
    else:
        sql = sql.rstrip().rstrip(";") + " AND COD_VENDEDOR = :P_COD_VENDEDOR"

    params["P_COD_VENDEDOR"] = cod_vendedor
    log.warning("VENDOR_FILTER | LLM omitió el filtro de vendedor — forzado por backend")
    return sql, params


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

    # ── 4. Inyectar parámetros del contexto ──────────────────────────────────
    if ctx.get("cod_empresa") and ":cod_empresa" in sql and "cod_empresa" not in params:
        params["cod_empresa"] = str(ctx["cod_empresa"])
    # Enforcement: fuerza el filtro de vendedor aunque el LLM lo haya omitido
    if ctx.get("cod_vendedor"):
        sql, params = _inject_vendor_filter(sql, str(ctx["cod_vendedor"]), params)

    # ── 5. Validar que todos los bind variables del SQL tengan parámetro ────
    _binds_in_sql = set(re.findall(r":([A-Za-z_][A-Za-z0-9_]*)", sql))
    _params_upper = {k.upper() for k in params}
    _missing = [b for b in _binds_in_sql if b.upper() not in _params_upper]
    if _missing:
        log.error("UNBOUND_PARAMS | falta en params: %s | SQL: %.300s", _missing, sql)
        raise ValueError(f"Bind variables sin valor: {_missing}")

    # ── 6. Ejecutar contra Oracle ────────────────────────────────────────────
    max_rows = min(int(ctx.get("max_rows") or settings.max_rows), 50)
    res = db.query(sql, params, max_rows=max_rows)

    # ── 6. LLM analiza resultados y genera insight de negocio ───────────────
    _analysis_ctx: dict = {}
    # cod_cliente: prioridad 1) params["cod_cliente"] verificado como código real,
    #              2) columna cod_cliente en filas, 3) lookup por nombre_cliente.
    # El LLM a veces pone el NOMBRE en params["cod_cliente"] — verificamos contra BD.
    if params.get("cod_cliente"):
        _raw_cod = str(params["cod_cliente"])
        try:
            _verified = db.query_scalar(
                "SELECT COD_CLIENTE FROM INV.V_CLIENTE_APEX"
                " WHERE COD_CLIENTE = :c AND ROWNUM = 1",
                {"c": _raw_cod},
            )
            if _verified:
                _analysis_ctx["cod_cliente"] = str(_verified)
            else:
                # No es un código válido: intentar como nombre
                _by_name = db.query_scalar(
                    "SELECT COD_CLIENTE FROM INV.V_CLIENTE_APEX"
                    " WHERE UPPER(NOMBRE) LIKE UPPER('%'||:n||'%') AND ROWNUM = 1",
                    {"n": _raw_cod},
                )
                if _by_name:
                    _analysis_ctx["cod_cliente"] = str(_by_name)
                    log.info("ANALYSIS_CTX | cod_cliente resuelto por nombre: %r → %s", _raw_cod, _by_name)
        except Exception:
            _analysis_ctx["cod_cliente"] = _raw_cod
    elif res.rows and res.rows[0].get("cod_cliente"):
        _analysis_ctx["cod_cliente"] = str(res.rows[0]["cod_cliente"])
    elif params.get("nombre_cliente"):
        try:
            r = db.query_scalar(
                "SELECT COD_CLIENTE FROM INV.V_CLIENTE_APEX"
                " WHERE UPPER(NOMBRE) LIKE UPPER('%'||:n||'%') AND ROWNUM = 1",
                {"n": str(params["nombre_cliente"])},
            )
            if r:
                _analysis_ctx["cod_cliente"] = str(r)
        except Exception:
            pass
    if ctx.get("cod_vendedor"):
        _analysis_ctx["cod_vendedor"] = str(ctx["cod_vendedor"])
    log.info("ANALYSIS_CTX | %s", _analysis_ctx)
    respuesta = analyze_results(mensaje, sql, table_desc, res.rows, res.columns, context=_analysis_ctx)
    log.info("ANALYSIS_BTN | boton=%s", "js_abrir_pedido" in respuesta)

    # ── Botón "Crear pedido" — inyectado por el backend, no delegado al LLM ──
    cod_cliente_ctx = _analysis_ctx.get("cod_cliente")
    _article_cols = {"cod_articulo", "codigo"}
    _has_articles = bool(res.rows and _article_cols.intersection(set(res.columns)))
    # No inyectar en consultas de OTs/reparaciones ni en otras vistas que no sean de ventas/stock
    _is_ot_query = "ORDENES_TRABAJO" in sql.upper()
    _ot_cols = {"estado_ot", "fecha_reparacion", "nom_cliente"}
    _is_ot_result = bool(_ot_cols.intersection(set(res.columns)))
    if cod_cliente_ctx and _has_articles and not _is_ot_query and not _is_ot_result and "js_abrir_pedido" not in respuesta:
        _code_col    = next((c for c in res.columns if c in ("cod_articulo", "codigo")), "cod_articulo")
        _desc_col    = next((c for c in res.columns if c in ("desc_articulo", "articulo", "descripcion")), None)
        _div_col     = next((c for c in res.columns if c in ("desc_division",)), None)
        _qty_col_cli = next((c for c in res.columns if c in ("cant_cliente", "qty_cliente")), None)
        _qty_col_ven = next((c for c in res.columns if c in ("cant_vendedor", "qty_vendedor")), None)
        _qty_col     = next(
            (c for c in res.columns if c in (
                "qty_sugerida", "cant_sugerida", "cantidad_sugerida",
                "qty_vendida_mes", "compras_mes", "cantidad", "qty",
            )),
            None,
        )
        items_raw = []
        for row in res.rows[:50]:
            cod = str(row.get(_code_col) or "")
            if not cod:
                continue
            if _div_col and str(row.get(_div_col) or "").upper().strip() == "PROMOS":
                continue
            _raw_desc = str(row.get(_desc_col) or "") if _desc_col else ""
            desc = "".join(c for c in _raw_desc if ord(c) >= 0x20)[:40]
            if _qty_col_cli is not None or _qty_col_ven is not None:
                qty = _calcular_cantidad_sugerida(row.get(_qty_col_cli), row.get(_qty_col_ven))
            else:
                qty = max(1, int(row.get(_qty_col) or 1)) if _qty_col else 1
            items_raw.append({"cod": cod, "desc": desc, "qty": qty})
        items = _agrupar_items(items_raw)[:14]
        if items:
            import json as _json
            items_json = _json.dumps(items, ensure_ascii=True)
            btn = (
                f'<div style="margin-top:12px">'
                f'<button data-cliente="{cod_cliente_ctx}" data-items=\'{items_json}\' '
                f'onclick="window.js_abrir_pedido(this.dataset.cliente,this.dataset.items)" '
                f'style="padding:7px 16px;background:#0572c6;color:#fff;border:0;border-radius:6px;'
                f'cursor:pointer;font-size:13px">📋 Crear pedido para cliente {cod_cliente_ctx}</button>'
                f'</div>'
            )
            respuesta += "\n" + btn
            log.info("ANALYSIS_BTN | boton inyectado para cod_cliente=%s items=%d", cod_cliente_ctx, len(items))

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

    # Estrategia A: NVL(NOMBRE_APELLIDO, NOMBRE) desde V_EMPLEADOS usando P_COD_EMPLEADO (página 0)
    cod_empleado = str(ctx.get("cod_empleado") or "").strip()
    log.info("GREET | usuario=%s cod_empleado=%r cod_vendedor=%r", usuario, cod_empleado, cod_vendedor)
    if cod_empleado:
        try:
            r = db.query(
                "SELECT NOMBRE_APELLIDO, NOMBRE FROM INV.V_EMPLEADOS"
                " WHERE COD_EMPLEADO = :cod_emp AND ROWNUM = 1",
                {"cod_emp": cod_empleado},
                max_rows=1,
            )
            if r.rows:
                # NVL en Python: NOMBRE_APELLIDO primero, luego NOMBRE como fallback
                val = (
                    r.rows[0].get("nombre_apellido")
                    or r.rows[0].get("nombre")
                )
                if val and str(val).strip():
                    nombre = str(val).strip().title()
            log.info("GREET | COD_EMPLEADO=%s → row=%s → nombre=%s", cod_empleado, r.rows, nombre)
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

    nombre_mostrar = nombre or usuario or "vendedor"

    # 2. Mini stats — all fail-safe
    ventas_hoy: float | None = None
    ventas_mes: float | None = None
    stock_critico: int | None = None
    clientes_inactivos: int | None = None
    meta_pct: float | None = None
    meta_monto: float | None = None
    ventas_meta: float | None = None
    pedidos_cnt: int | None = None
    pedidos_monto: float | None = None

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
        sql_vm = (
            "SELECT NVL(SUM(MONTO), 0) AS TOTAL FROM INV.V_VENTAS_APEX"
            " WHERE COD_EMPRESA = :cod_empresa"
            " AND TIP_COMPROBANTE IN ('FCR','FCO')"
            " AND FEC_FACTURA >= TRUNC(SYSDATE, 'MM')"
        )
        pvm: dict = {"cod_empresa": cod_empresa}
        if cod_vendedor:
            sql_vm += " AND COD_VENDEDOR = :cod_vendedor"
            pvm["cod_vendedor"] = cod_vendedor
        r = db.query(sql_vm, pvm, max_rows=1)
        if r.rows:
            ventas_mes = float(r.rows[0].get("total") or 0)
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

    # Meta del mes (solo si tenemos cod_vendedor)
    if cod_vendedor:
        try:
            r = db.query(
                "SELECT m.MONTO_META,"
                " NVL(SUM(v.MONTO), 0) AS ventas_reales"
                " FROM INV.V_METAS_VENDEDORES m"
                " LEFT JOIN INV.V_VENTAS_APEX v"
                "   ON v.COD_VENDEDOR = m.COD_VENDEDOR"
                "  AND v.COD_EMPRESA = m.COD_EMPRESA"
                "  AND v.TIP_COMPROBANTE IN ('FCR','FCO')"
                "  AND v.FEC_FACTURA >= m.FECHA_INICIO"
                "  AND v.FEC_FACTURA <= m.FECHA_FIN"
                " WHERE m.COD_EMPRESA = :cod_empresa"
                "   AND m.COD_VENDEDOR = :cod_vendedor"
                "   AND TRUNC(SYSDATE) BETWEEN m.FECHA_INICIO AND m.FECHA_FIN"
                " GROUP BY m.MONTO_META, m.FECHA_INICIO, m.FECHA_FIN"
                " FETCH FIRST 1 ROWS ONLY",
                {"cod_empresa": cod_empresa, "cod_vendedor": cod_vendedor},
                max_rows=1,
            )
            if r.rows:
                _meta = float(r.rows[0].get("monto_meta") or 0)
                _ventas = float(r.rows[0].get("ventas_reales") or 0)
                if _meta > 0:
                    meta_pct = (_ventas / _meta) * 100
                    meta_monto = _meta
                    ventas_meta = _ventas
        except Exception:
            pass

    # Pedidos pendientes
    try:
        sql_ped = (
            "SELECT COUNT(DISTINCT NRO_COMPROBANTE) AS cnt,"
            " NVL(SUM(IMPORTE_PENDIENTE), 0) AS total_pend"
            " FROM INV.V_PEDIDOS_PRODUCTOS"
            " WHERE COD_EMPRESA = :cod_empresa"
            " AND ESTADO IN ('PENDIENTE','PARCIALMENTE_FACTURADO')"
        )
        pp: dict = {"cod_empresa": cod_empresa}
        if cod_vendedor:
            sql_ped += " AND COD_VENDEDOR = :cod_vendedor"
            pp["cod_vendedor"] = cod_vendedor
        r = db.query(sql_ped, pp, max_rows=1)
        if r.rows:
            pedidos_cnt = int(r.rows[0].get("cnt") or 0)
            pedidos_monto = float(r.rows[0].get("total_pend") or 0)
    except Exception:
        pass

    # 3. Build greeting (HTML con botones clickeables)
    stats: list[str] = []
    if ventas_hoy is not None:
        fmt = f"Gs. {int(ventas_hoy):,}".replace(",", ".")
        stats.append(f"📊 Hoy llevás {fmt} en ventas")
    if ventas_mes is not None:
        fmt_mes = f"Gs. {int(ventas_mes):,}".replace(",", ".")
        stats.append(f"📅 Este mes: {fmt_mes} en ventas")
    if meta_pct is not None and ventas_meta is not None and meta_monto is not None:
        emoji_meta = "🟢" if meta_pct >= 80 else ("🟡" if meta_pct >= 50 else "🔴")
        fmt_v = f"Gs. {int(ventas_meta):,}".replace(",", ".")
        fmt_m = f"Gs. {int(meta_monto):,}".replace(",", ".")
        stats.append(f"{emoji_meta} Meta del mes: {meta_pct:.1f}% ({fmt_v} de {fmt_m})")
    if pedidos_cnt:
        fmt_ped = f"Gs. {int(pedidos_monto):,}".replace(",", ".") if pedidos_monto else "—"
        stats.append(f"📦 {pedidos_cnt} pedido{'s' if pedidos_cnt != 1 else ''} pendiente{'s' if pedidos_cnt != 1 else ''} ({fmt_ped})")
    if stock_critico:
        stats.append(f"⚠️ {stock_critico} artículos con stock crítico o en cero")
    if clientes_inactivos:
        stats.append(f"💡 {clientes_inactivos} clientes sin compras en más de 60 días")

    html: list[str] = []
    html.append(f"<b>Hola {nombre_mostrar} 👋</b><br>")
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
        "¿Qué notas de crédito tuve este mes?",
    ]))
    html.append(_section_html("📦", "Productos", [
        "¿Qué productos puedo vender más hoy?",
        "¿Cuáles son los más vendidos?",
        "¿Qué productos tienen bajo stock?",
    ]))
    html.append(_section_html("🧍", "Clientes", [
        "Ranking de compras de clientes",
        "Clientes mayoristas activos sin compras este mes",
        "Clientes mayoristas activos sin compras esta semana",
        "¿A quién debería visitar hoy?",
    ]))
    html.append(_section_html("🎯", "Metas", [
        "¿Cómo voy contra mi meta este mes?",
        "¿Cuánto me falta para alcanzar mi meta?",
        "¿Qué porcentaje de mi meta ya cumplí?",
    ]))
    html.append(_section_html("📦", "Pedidos", [
        "¿Qué pedidos tengo pendientes?",
        "¿Cuáles son mis pedidos más grandes sin cerrar?",
        "¿Qué pedidos necesitan autorización?",
    ]))
    html.append(_section_html("🔧", "Reparaciones / OT", [
        "¿Qué OTs pendientes de reparación tienen mis clientes?",
        "¿Qué OTs reparadas y no retiradas tienen mis clientes?",
        "¿Qué OTs ingresaron este mes?",
        "¿Cuánto tiempo llevan sin repararse?",
    ]))
    html.append(_section_html("💡", "Oportunidades", [
        "¿Dónde tengo oportunidades de venta?",
        "¿Qué puedo vender rápido hoy?",
        "¿Qué productos tienen alta demanda y stock disponible?",
    ]))

    return AgentResult(
        respuesta="".join(html),
        sql_generado=None,
        datos={"intencion": "GREET", "usuario": usuario},
    )
