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

import httpx2 as httpx
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
        proxy = settings.http_proxy or None
        http_client = httpx.Client(
            verify=False,
            timeout=httpx.Timeout(settings.llm_timeout),
            proxy=proxy,
        )
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
   ⛔ JAMÁS uses V(), NV(), APEX_UTIL.GET_SESSION_STATE() ni ninguna función APEX en SQL. Son funciones PL/SQL de APEX y causan ORA-06553 cuando se ejecutan fuera de una sesión APEX. Todos los valores de sesión (empresa, vendedor, empleado, etc.) DEBEN pasarse exclusivamente como bind variables Oracle (:nombre). Si necesitás el código de vendedor, usá :P_COD_VENDEDOR — el backend lo inyecta. Nunca escribas V('P_COD_VENDEDOR') ni similar.
6. Si el contexto incluye cod_empresa, SIEMPRE agrega AND COD_EMPRESA = :cod_empresa al WHERE.
7. Alias de columnas sin espacios (usa guion bajo) y con máximo 20 caracteres. Ej: total_monto, cant_unidades, arts_pendientes, imp_pendiente.
   ⛔ CRÍTICO — ORDER BY con agregados: Oracle 12c NUNCA permite ORDER BY SUM(...) / ORDER BY COUNT(...) / ORDER BY MAX(...) junto a FETCH FIRST N ROWS ONLY. Causa ORA-00934. SIEMPRE asigná alias al agregado en el SELECT y usá ESE ALIAS en el ORDER BY:
   ✅ SELECT SUM(MONTO) AS total_monto ... ORDER BY total_monto DESC FETCH FIRST 20 ROWS ONLY
   ❌ SELECT SUM(MONTO) AS total_monto ... ORDER BY SUM(MONTO) DESC FETCH FIRST 20 ROWS ONLY — INVÁLIDO
   ⛔ CRÍTICO — agregados en WHERE: NUNCA pongas SUM/COUNT/MAX/MIN/AVG en una cláusula WHERE. Causa ORA-00934. Usá HAVING:
   ✅ GROUP BY ... HAVING SUM(CANT_DISPON) > 0
   ❌ WHERE SUM(CANT_DISPON) > 0 — INVÁLIDO
   ⛔ No uses DISTINCT junto a GROUP BY — son mutuamente excluyentes; usa solo GROUP BY.
8. Para JOINs usa los campos comunes: COD_ARTICULO, COD_CLIENTE, COD_VENDEDOR entre vistas.
9. Cuando se pide "top N" sin número, usa 10. Cuando se pide comparativa, usa subconsultas o CASE.
10. Preguntas de cruce de datos (ej: "alta demanda + bajo stock"): JOIN entre V_VENTAS_agente y V_STOCK_agente por COD_ARTICULO.
    ⛔ COLUMNAS EXCLUSIVAS DE V_STOCK_agente — NO existen en V_VENTAS_agente: DESC_FAMILIA, DESC_DIVISION, DESC_CATEGOGIRA, CANT_DISPON, COSTO_PROMEDIO_UNITARIO, MARCA, FACTURABLE.
    En un JOIN siempre referencia estas columnas con el alias del stock (ej: s.DESC_FAMILIA, s.CANT_DISPON), nunca con el alias de ventas (v.DESC_FAMILIA es INVÁLIDO).
    Para stock en JOINs usa SUM(s.CANT_DISPON) —no MAX— porque V_STOCK_agente tiene una fila por sucursal.
    ⛔ CRÍTICO JOIN+STOCK: SUM(s.CANT_DISPON) es una función de agregado — NUNCA la pongas en WHERE. Va SIEMPRE en HAVING:
    ✅ GROUP BY ... HAVING SUM(s.CANT_DISPON) > 0   ← CORRECTO
    ❌ WHERE SUM(s.CANT_DISPON) > 0                 ← ORA-00934, INVÁLIDO
    ⛔ MARCA vs DESC_MARCA — ERROR CRÍTICO FRECUENTE:
    V_STOCK_agente tiene la columna MARCA (sin prefijo). V_VENTAS_agente tiene DESC_MARCA.
    ✅ s.MARCA          ← CORRECTO cuando s es alias de V_STOCK_agente
    ❌ s.DESC_MARCA     ← ORA-00904 INVÁLIDO — la columna DESC_MARCA NO EXISTE en V_STOCK_agente
    En todo JOIN con V_STOCK_agente: usa SIEMPRE s.MARCA, nunca s.DESC_MARCA.
11. TIP_COMPROBANTE CRÍTICO — NUNCA uses 'FT'. Los valores correctos son: 'FCR' y 'FCO' para ventas reales, 'NCR' para notas de crédito. Para analizar ventas SIEMPRE filtra: AND TIP_COMPROBANTE IN ('FCR','FCO')
12. Para filtrar stock por "rubro" o tipo de producto, usa DESC_DIVISION en INV.V_STOCK_agente. Valores típicos: 'PRODUCTOS', 'REPUESTOS'. DESC_FAMILIA para subfamilia.
13. Para promociones vigentes: AND FECHA_INICIO <= TRUNC(SYSDATE) AND FECHA_FIN >= TRUNC(SYSDATE). PROMO_MIX='S' son promos mix, 'N' son normales. Filtrar COD_EMPRESA_PROMO = :cod_empresa si está en contexto.
14. ⛔ RESTRICCIÓN CRÍTICA DE VENDEDOR: Si el contexto incluye cod_vendedor, DEBES agregar AND COD_VENDEDOR = :P_COD_VENDEDOR en TODAS las consultas sobre V_VENTAS_agente, V_CLIENTE_agente, V_PEDIDOS_AGENTE y V_METAS_VENDEDORES. Esta restricción es obligatoria e innegociable — garantiza que el vendedor solo vea sus propios datos. Omitirla es un error grave. NO incluyas P_COD_VENDEDOR en el JSON de params, el backend lo inyecta automáticamente. Si el usuario menciona el nombre de un vendedor (ej: "vendedor García"), usa UPPER(NOMBRE_VENDEDOR) LIKE UPPER('%'||:nombre_vend||'%') en el WHERE y agrega {{"nombre_vend": "<nombre>"}} a params.
15. V_STOCK_agente tiene una fila por sucursal. SIEMPRE agrupa y suma. ⛔ NUNCA uses SUM/COUNT/AVG/MIN/MAX en el WHERE — van en HAVING. ⛔ NUNCA uses SUM/MAX/MIN/AVG en ORDER BY — usá el alias del SELECT. Patrón OBLIGATORIO para stock crítico:
SELECT COD_ARTICULO AS CODIGO, DESC_ARTICULO, SUM(CANT_DISPON) AS cant_dispon_total
FROM INV.V_STOCK_agente
WHERE COD_EMPRESA = :cod_empresa AND COD_RUBRO = 'PR'
GROUP BY COD_ARTICULO, DESC_ARTICULO
HAVING SUM(CANT_DISPON) <= 5
ORDER BY cant_dispon_total
FETCH FIRST 20 ROWS ONLY
Agrega al GROUP BY cualquier columna descriptiva adicional que uses en el SELECT.
16. V_STOCK_agente — SIEMPRE agrega AND COD_RUBRO = 'PR' al WHERE (filtra solo productos comercializables). Ejemplo: WHERE COD_EMPRESA = :cod_empresa AND COD_RUBRO = 'PR'. En el SELECT usa COD_ARTICULO AS CODIGO para retornar el código del artículo. ⛔ NUNCA uses COD_ART_CORTO como identificador — el código correcto siempre es COD_ARTICULO.
17. V_CLIENTE_agente — los valores válidos del campo ESTADO son exactamente: 'ACTIVO', 'INACTIVO', 'BLOQUEADO', 'CREDITO BLOQUEADO'. Nunca uses 'A', 'B' ni otros valores. Para clientes activos: ESTADO = 'ACTIVO'. Para bloqueados: ESTADO IN ('BLOQUEADO','CREDITO BLOQUEADO'). Para inactivos: ESTADO = 'INACTIVO'.
18. NOMBRES EN FILTROS — Si el usuario menciona un cliente (ej: "ZEIN SRL", "García"), usa bind variable y agrega el valor al JSON params:
   - Cliente: UPPER(NOMBRE) LIKE UPPER('%'||:nombre_cliente||'%') → params: {{"nombre_cliente": "ZEIN SRL"}}
   - Artículo: UPPER(DESC_ARTICULO) LIKE UPPER('%'||:nombre_art||'%') → params: {{"nombre_art": "ACEITE"}}
   ⛔ NUNCA dejes un bind variable (:variable) en el SQL sin su correspondiente entrada en params. Todos los :variable del SQL DEBEN estar en params.
   ✅ CRÍTICO — CLIENTE ESPECÍFICO: Cuando el SQL filtra por un cliente concreto (NOMBRE LIKE :nombre_cliente o COD_CLIENTE = :cod_cliente), SIEMPRE incluye MIN(COD_CLIENTE) AS cod_cliente en el SELECT principal. Esto es obligatorio para que el frontend pueda crear pedidos. Si hay GROUP BY, agrega MIN(COD_CLIENTE) AS cod_cliente al SELECT. Si no hay GROUP BY, agrega COD_CLIENTE al SELECT y al GROUP BY.
19. METAS DE VENDEDOR (V_METAS_VENDEDORES) — Para calcular cumplimiento de meta cruzá con V_VENTAS_agente. Patrón OBLIGATORIO:
SELECT m.MONTO_META,
       NVL(SUM(v.MONTO), 0) AS ventas_reales,
       ROUND(NVL(SUM(v.MONTO), 0) / NULLIF(m.MONTO_META, 0) * 100, 1) AS pct_cumplimiento,
       GREATEST(m.MONTO_META - NVL(SUM(v.MONTO), 0), 0) AS falta_para_meta
FROM INV.V_METAS_VENDEDORES m
LEFT JOIN INV.V_VENTAS_agente v
  ON v.COD_VENDEDOR = m.COD_VENDEDOR
 AND v.COD_EMPRESA = m.COD_EMPRESA
 AND v.TIP_COMPROBANTE IN ('FCR','FCO','NCR')
 AND v.FEC_FACTURA >= m.FECHA_INICIO
 AND v.FEC_FACTURA <= m.FECHA_FIN
WHERE m.COD_EMPRESA = :cod_empresa
  AND m.COD_VENDEDOR = :P_COD_VENDEDOR
  AND TRUNC(SYSDATE) BETWEEN m.FECHA_INICIO AND m.FECHA_FIN
GROUP BY m.MONTO_META, m.FECHA_INICIO, m.FECHA_FIN
Si no hay cod_vendedor en contexto (gerente viendo todos), omitir el AND COD_VENDEDOR = :P_COD_VENDEDOR del WHERE de metas y el JOIN — en su lugar agrupar por m.COD_VENDEDOR para mostrar ranking.
20. PEDIDOS (V_PEDIDOS_AGENTE) — Estados válidos exactos: 'ANULADO','CERRADO','FACTURADO','PARCIALMENTE_FACTURADO','PENDIENTE'.
   - Pedidos activos: ESTADO IN ('PENDIENTE','PARCIALMENTE_FACTURADO')
   - Pedidos bloqueados sin autorizar: ESTADO = 'PENDIENTE' AND AUTORIZACION IS NOT NULL
   - Importe pendiente: SUM(IMPORTE_PENDIENTE) — ya calculado en la vista
   - Unidades sin facturar: SUM(CANTIDAD - CANTIDAD_FACTURADA)
   - Agrupar por pedido: GROUP BY NRO_COMPROBANTE, COD_CLIENTE, FECHA_PEDIDO, ESTADO, AUTORIZACION
   - SIEMPRE filtrar AND COD_EMPRESA = :cod_empresa; si hay cod_vendedor AND COD_VENDEDOR = :P_COD_VENDEDOR
   - Para "pedidos más grandes": ORDER BY total_pendiente DESC FETCH FIRST 10 ROWS ONLY (usar alias en ORDER BY)
21. ⛔ STRING_AGG no existe en Oracle 12c. SIEMPRE usa LISTAGG(col, ', ') WITHIN GROUP (ORDER BY col).
   ⛔ LISTAGG(DISTINCT ...) tampoco existe en Oracle 12c (se incorporó en 19c). Para concatenar valores distintos usá una subconsulta que deduplique primero:
   ✅ SELECT LISTAGG(COD_ARTICULO, ', ') WITHIN GROUP (ORDER BY COD_ARTICULO) AS articulos
      FROM (SELECT DISTINCT COD_ARTICULO FROM INV.V_PEDIDOS_AGENTE WHERE ...)
   ❌ STRING_AGG(DISTINCT COD_ARTICULO, ', ') — INVÁLIDO en Oracle
   ❌ LISTAGG(DISTINCT COD_ARTICULO, ', ') WITHIN GROUP (...) — INVÁLIDO en Oracle 12c
22. ⛔ EXCLUSIÓN PROMOS OBLIGATORIA: En TODAS las consultas de sugerencias de venta/compra y top productos, agrega en V_STOCK_agente: AND UPPER(NVL(DESC_DIVISION,'')) != 'PROMOS'. En V_VENTAS_agente no hay DESC_DIVISION (solo COD_DIVISION código), omitir ahí. Esta exclusión es siempre obligatoria.
23. MÓDULO CLIENTES — MAYORISTAS: Para "Ranking de compras de clientes", "Clientes mayoristas activos sin compras este mes/semana" y "¿A quién debería visitar hoy?", SIEMPRE filtrar en V_CLIENTE_agente:
   AND TIPO_CLIENTE IN ('MAYORISTA A','MAYORISTA B','MAYORISTA C','CORPORATIVOS','GASTRONOMIA','SUPERMERCADO','MAYORISTA-GASTRONOMIA')
   AND ESTADO = 'ACTIVO'
   Patrones:
   ● "Ranking de compras de clientes": SELECT c.COD_CLIENTE, c.NOMBRE, NVL(SUM(v.MONTO),0) AS monto_compra, MAX(v.FEC_FACTURA) AS ultima_compra FROM INV.V_CLIENTE_agente c LEFT JOIN INV.V_VENTAS_agente v ON v.COD_CLIENTE=c.COD_CLIENTE AND v.COD_EMPRESA=:cod_empresa AND v.TIP_COMPROBANTE IN ('FCR','FCO') [AND v.COD_VENDEDOR=:P_COD_VENDEDOR] WHERE c.COD_EMPRESA=:cod_empresa AND c.TIPO_CLIENTE IN (...) AND c.ESTADO='ACTIVO' [AND c.COD_VENDEDOR=:P_COD_VENDEDOR] GROUP BY c.COD_CLIENTE,c.NOMBRE ORDER BY monto_compra DESC FETCH FIRST 20 ROWS ONLY
   ● "Clientes mayoristas activos sin compras este mes": SELECT COD_CLIENTE,NOMBRE,FEC_ULTIMA_COMPRA FROM INV.V_CLIENTE_agente WHERE COD_EMPRESA=:cod_empresa AND TIPO_CLIENTE IN (...) AND ESTADO='ACTIVO' [AND COD_VENDEDOR=:P_COD_VENDEDOR] AND COD_CLIENTE NOT IN (SELECT DISTINCT COD_CLIENTE FROM INV.V_VENTAS_agente WHERE COD_EMPRESA=:cod_empresa AND TIP_COMPROBANTE IN ('FCR','FCO') [AND COD_VENDEDOR=:P_COD_VENDEDOR] AND FEC_FACTURA>=TRUNC(SYSDATE,'MM')) ORDER BY FEC_ULTIMA_COMPRA ASC FETCH FIRST 20 ROWS ONLY
   ● "Clientes mayoristas activos sin compras esta semana": igual pero FEC_FACTURA>=TRUNC(SYSDATE,'IW')
   ● "¿A quién debería visitar hoy?": SELECT COD_CLIENTE,NOMBRE,FEC_ULTIMA_COMPRA,VENTA_MES AS monto_historico FROM INV.V_CLIENTE_agente WHERE COD_EMPRESA=:cod_empresa AND TIPO_CLIENTE IN (...) AND ESTADO='ACTIVO' [AND COD_VENDEDOR=:P_COD_VENDEDOR] ORDER BY FEC_ULTIMA_COMPRA ASC,monto_historico DESC FETCH FIRST 10 ROWS ONLY
24. NOTAS DE CRÉDITO: Para "¿Qué notas de crédito tuve este mes?", filtrar TIP_COMPROBANTE='NCR' (NO 'FCR'/'FCO'). Patrón:
   SELECT COD_CLIENTE, NOMBRE, NRO_COMPROBANTE AS nro_nc, FEC_FACTURA, SUM(MONTO) AS monto_nc
   FROM INV.V_VENTAS_agente
   WHERE COD_EMPRESA=:cod_empresa AND TIP_COMPROBANTE='NCR'
     AND FEC_FACTURA>=TRUNC(SYSDATE,'MM') [AND COD_VENDEDOR=:P_COD_VENDEDOR]
   GROUP BY COD_CLIENTE,NOMBRE,NRO_COMPROBANTE,FEC_FACTURA
   ORDER BY FEC_FACTURA DESC FETCH FIRST 20 ROWS ONLY
25. CANTIDADES SUGERIDAS: Para sugerencias de artículos a un cliente específico, devolver SIEMPRE:
   cant_cliente: cantidad promedio que ESE cliente compró del artículo en últimos 3 meses
   cant_vendedor: cantidad promedio que el vendedor vendió del artículo en últimos 3 meses
   El backend calcula: cant_cliente si >0, sino round(cant_vendedor*0.8), sino 1.

   ⛔ CRÍTICO — cod_cliente vs nombre_cliente:
   ❌ NUNCA pongas un nombre de empresa en params["cod_cliente"]. cod_cliente es un código numérico (ej: "000000000001").
   ✅ Si el usuario dice "WILMAR S.R.L." o cualquier nombre: usa params["nombre_cliente"] y filtra con UPPER(NOMBRE) LIKE UPPER('%'||:nombre_cliente||'%').
   En la subconsulta de cant_cliente: usa también UPPER(NOMBRE) LIKE si no tenés el código, o usa COD_CLIENTE IN (subconsulta de nombre).

   Patrón cuando el cliente se identifica por NOMBRE (caso más común):
   SELECT v.COD_ARTICULO, MAX(v.DESC_ARTICULO) AS desc_articulo,
     MIN(v.COD_CLIENTE) AS cod_cliente,
     NVL((SELECT AVG(CANTIDAD) FROM INV.V_VENTAS_agente
          WHERE COD_ARTICULO=v.COD_ARTICULO
            AND COD_CLIENTE IN (SELECT COD_CLIENTE FROM INV.V_CLIENTE_agente WHERE UPPER(NOMBRE) LIKE UPPER('%'||:nombre_cliente||'%') AND ROWNUM=1)
            AND COD_EMPRESA=:cod_empresa AND TIP_COMPROBANTE IN ('FCR','FCO')
            AND FEC_FACTURA>=ADD_MONTHS(TRUNC(SYSDATE,'MM'),-3)),0) AS cant_cliente,
     NVL(AVG(v.CANTIDAD),0) AS cant_vendedor
   FROM INV.V_VENTAS_agente v
   WHERE v.COD_EMPRESA=:cod_empresa AND v.TIP_COMPROBANTE IN ('FCR','FCO')
     AND v.FEC_FACTURA>=ADD_MONTHS(TRUNC(SYSDATE,'MM'),-3)
     AND v.COD_CLIENTE IN (SELECT COD_CLIENTE FROM INV.V_CLIENTE_agente WHERE UPPER(NOMBRE) LIKE UPPER('%'||:nombre_cliente||'%') AND ROWNUM=1)
     [AND v.COD_VENDEDOR=:P_COD_VENDEDOR]
   GROUP BY v.COD_ARTICULO ORDER BY cant_vendedor DESC FETCH FIRST 14 ROWS ONLY
   params: {{"nombre_cliente": "WILMAR S.R.L."}}  ← SIEMPRE nombre_cliente cuando el usuario da un nombre
   ⛔ NO hagas JOIN con V_STOCK_agente en este patrón — solo V_VENTAS_agente.
   ❌ FROM INV.V_VENTAS_agente v LEFT JOIN INV.V_STOCK_agente s ON ...  ← INVÁLIDO aquí
   ✅ Solo FROM INV.V_VENTAS_agente v — sin ningún JOIN a stock.
   Si necesitás stock como dato adicional, usá subconsulta escalar: (SELECT SUM(CANT_DISPON) FROM INV.V_STOCK_agente WHERE COD_ARTICULO=v.COD_ARTICULO AND COD_EMPRESA=:cod_empresa AND COD_RUBRO='PR') AS stock_dispon
   Nunca columnas de V_STOCK_agente (s.MARCA, s.DESC_FAMILIA, s.CANT_DISPON) en el SELECT principal de este patrón — no hay alias 's'.
26. ⛔ NUNCA repitas el mismo COD_ARTICULO en resultados de sugerencias. Usá GROUP BY COD_ARTICULO para garantizar una sola fila por artículo.
27. ÓRDENES DE TRABAJO (OT / Reparaciones) — Vista: INV.V_ORDENES_TRABAJO_CLIENTES (alias ot).
   NO tiene COD_VENDEDOR. Filtro de vendedor: subquery sobre V_VENTAS_agente [solo si hay cod_vendedor en contexto].
   SIEMPRE agregar AND ot.COD_EMPRESA = :cod_empresa.
   FETCH FIRST 20 ROWS ONLY en todas.
   COLUMNAS ESTÁNDAR: ot.OT, ot.ESTADO_OT, ot.COD_CLIENTE, ot.NOM_CLIENTE, ot.FECHA_INGRESO, ot.FECHA_REPARACION, ot.COD_ARTICULO.

   Patrones obligatorios:
   ● "¿Qué OTs pendientes de reparación tienen mis clientes?":
     SELECT ot.OT, ot.ESTADO_OT, ot.COD_CLIENTE, ot.NOM_CLIENTE,
       ot.FECHA_INGRESO, ot.FECHA_REPARACION, ot.COD_ARTICULO
     FROM INV.V_ORDENES_TRABAJO_CLIENTES ot
     WHERE ot.COD_EMPRESA=:cod_empresa
       AND ot.FECHA_REPARACION IS NULL
       [AND ot.COD_CLIENTE IN (SELECT DISTINCT COD_CLIENTE FROM INV.V_VENTAS_agente WHERE COD_VENDEDOR=:P_COD_VENDEDOR AND COD_EMPRESA=:cod_empresa AND TIP_COMPROBANTE IN ('FCR','FCO'))]
     ORDER BY ot.FECHA_INGRESO ASC FETCH FIRST 20 ROWS ONLY

   ● "¿Qué OTs reparadas y no retiradas tienen mis clientes?":
     SELECT ot.OT, ot.ESTADO_OT, ot.COD_CLIENTE, ot.NOM_CLIENTE,
       ot.FECHA_INGRESO, ot.FECHA_REPARACION, ot.COD_ARTICULO
     FROM INV.V_ORDENES_TRABAJO_CLIENTES ot
     WHERE ot.COD_EMPRESA=:cod_empresa
       AND ot.FECHA_REPARACION IS NOT NULL
       [AND ot.COD_CLIENTE IN (SELECT DISTINCT COD_CLIENTE FROM INV.V_VENTAS_agente WHERE COD_VENDEDOR=:P_COD_VENDEDOR AND COD_EMPRESA=:cod_empresa AND TIP_COMPROBANTE IN ('FCR','FCO'))]
     ORDER BY ot.FECHA_REPARACION ASC FETCH FIRST 20 ROWS ONLY

   ● "¿Qué OTs ingresaron este mes?":
     Igual + AND ot.FECHA_INGRESO>=TRUNC(SYSDATE,'MM')
     ORDER BY ot.FECHA_INGRESO DESC

   ● "¿Cuánto tiempo llevan sin repararse?":
     Igual + AND ot.FECHA_REPARACION IS NULL, agregar ROUND(SYSDATE-ot.FECHA_INGRESO,0) AS dias_transcurridos al SELECT
     ORDER BY dias_transcurridos DESC (alias en SELECT obligatorio)

   Si VER_OTROS_VENDEDORES='S' (no hay cod_vendedor en contexto): omitir el subquery de clientes.

RESPONDE ÚNICAMENTE con JSON válido, sin markdown, sin texto adicional antes o después:
{{
  "sql": "SELECT ...",
  "params": {{"param1": valor1, "param2": valor2}},
  "table_description": "Una oración describiendo qué representa cada fila del resultado"
}}

Si la pregunta es imposible de responder con las vistas disponibles:
{{"sql": null, "params": {{}}, "table_description": "Motivo: [explicación]"}}
"""

_ANALYSIS_SYSTEM = """Actúa como un analista comercial experto en ventas, clientes, stock y oportunidades de negocio para una empresa distribuidora.

Tu objetivo es ayudar al vendedor a tomar decisiones rápidas para vender más, detectar oportunidades y evitar pérdidas.

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

👉 También podrías analizar:
- [sugerencia proactiva relacionada con los datos vistos, ej: "clientes de esta zona sin compra este mes"]
- [segunda sugerencia si aplica]

REGLAS DE ANÁLISIS:
- Usa los números exactos del resultado, nunca los inventes ni redondees sin decirlo
- Nombra entidades concretas: "el cliente GARCIA S.A. no compra hace 45 días" (no "hay clientes inactivos")
- Si el resultado está vacío, explica qué significa y qué ajuste probar
- Detecta anomalías: valores extremos, caídas, crecimiento inusual
- Para stock: si CANT_DISPON = 0, es quiebre; si <= 5, es crítico. El stock ya está sumado de todas las sucursales.
- Para clientes: > 60 días sin compra es inactividad; deuda vencida > crédito disponible es bloqueo inminente
- Para ventas: compara con el contexto (top productos, caídas, concentración de clientes)
- No inventar datos — si falta información, indicarlo claramente
- No responder solo con tablas sin análisis
- Sé directo y específico. Máximo 350 palabras en el texto de análisis.

TABLA HTML — Si el resultado tiene 3 o más filas, incluye en "📈 Hallazgos clave:" una tabla HTML compacta (máximo 10 filas, las 5 columnas más relevantes) con este formato exacto:
<table style="width:100%;border-collapse:collapse;font-size:12px;margin:6px 0"><tr style="background:#0572c6;color:#fff"><th style="padding:4px 6px;text-align:left">COLUMNA</th></tr><tr style="border-bottom:1px solid #eee"><td style="padding:4px 6px">VALOR</td></tr></table>
Usa los nombres de columna reales del resultado. Si hay más de 10 filas, agrega una nota: "(Mostrando 10 de N registros — descargá el XLS para ver todos)". Fuera de la tabla sigue usando texto plano.

⛔ NUNCA sugerir artículos de la división PROMOS. Esta exclusión es obligatoria en todas las sugerencias de venta y compra, sin excepción.

CANTIDADES SUGERIDAS: Si el resultado incluye columnas cant_cliente y cant_vendedor, indicá al usuario la fuente de la cantidad: "[histórico cliente]" si cant_cliente > 0, "[promedio vendedor]" si se usa cant_vendedor. Nunca muestres valores de 0 como cantidad — el mínimo es 1.

⛔ NO generes botones HTML de "Crear pedido" ni uses js_abrir_pedido en tu respuesta. El botón lo inyecta automáticamente el backend con JSON garantizado. Si vos generás el botón, el sistema falla con error de JSON. Concentrate exclusivamente en el análisis de negocio.
"""


_ERROR_MARKERS = (
    "api_connection_error", "rate_limit", "unbound_params",
    "No se pudo conectar", "Bind variables sin valor",
    "El modelo generó una consulta con parámetros incompletos",
    "servicio de IA está temporalmente saturado",
    "Error al conectar con el agente IA",
    "Error interno del agente IA",
    "500 Internal Server Error",
)


def _build_messages(history: list[dict] | None) -> list[dict]:
    """
    Convierte el historial APEX en una lista de mensajes válida para la API de Anthropic.
    Reglas:
      - Máximo 6 entradas del historial (3 pares user/assistant)
      - Los mensajes de error de assistant se descartan junto con el user anterior
      - El primer mensaje DEBE ser "user" (Anthropic lo exige)
      - No pueden haber dos mensajes consecutivos del mismo role
    """
    raw: list[dict] = []
    for h in (history or [])[-6:]:
        role = h.get("role", "")
        content = h.get("content", "") or ""
        if role not in ("user", "assistant") or not content:
            continue
        if role == "assistant" and any(m in content for m in _ERROR_MARKERS):
            # Intercambio fallido: descartar también el user message previo
            if raw and raw[-1]["role"] == "user":
                raw.pop()
            continue
        raw.append({"role": role, "content": str(content)[:2000]})

    # Eliminar mensajes de assistant al principio (Anthropic exige empezar con user)
    while raw and raw[0]["role"] != "user":
        raw.pop(0)

    # Eliminar pares consecutivos del mismo role (defensa final)
    messages: list[dict] = []
    for msg in raw:
        if messages and messages[-1]["role"] == msg["role"]:
            messages[-1] = msg   # reemplaza por el más reciente del mismo role
        else:
            messages.append(msg)

    return messages


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

    messages: list[dict] = _build_messages(history)

    # Construir mensaje del usuario con contexto
    ctx_parts: list[str] = []
    if context.get("cod_empresa"):
        ctx_parts.append(f"cod_empresa='{context['cod_empresa']}'")
    if context.get("cod_vendedor"):
        ctx_parts.append(
            "cod_vendedor=:P_COD_VENDEDOR"
            " [OBLIGATORIO: AND COD_VENDEDOR = :P_COD_VENDEDOR en el WHERE de cada consulta]"
        )
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
    context: dict[str, Any] | None = None,
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

    ctx_parts: list[str] = []
    if context:
        if context.get("cod_cliente"):
            ctx_parts.append(f"cod_cliente='{context['cod_cliente']}'")
        if context.get("cod_vendedor"):
            ctx_parts.append(f"cod_vendedor='{context['cod_vendedor']}'")
    ctx_line = ("\nContexto del backend: " + ", ".join(ctx_parts)) if ctx_parts else ""

    content = (
        f"Pregunta del usuario: {question}\n\n"
        f"SQL ejecutado:\n{sql}\n\n"
        f"Descripción del resultado: {table_description}"
        f"{ctx_line}\n\n"
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
