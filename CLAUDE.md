# Kairos — Agente Comercial IA (App APEX 122)

## Qué es este proyecto

Oracle APEX 22.1, aplicación 122 "Kairos". Agente comercial con IA: el vendedor hace preguntas en lenguaje natural, el backend genera SQL sobre Oracle 12c, ejecuta y analiza los resultados con Claude. Puede abrir pedidos directamente desde el chat.

## Archivos del proyecto

```
apex/
  f122_page_233.sql   — Página de chat del agente (interfaz)
  f122_page_34.sql    — Formulario de pedido (destino del botón "Crear pedido")

agente_ia_backend/app/
  agent.py            — Orquestador: chat, greet, inyección del botón pedido
  llm_service.py      — Prompts y llamadas a Claude (generate_sql + analyze_results)
  db.py               — Pool Oracle, query(), query_scalar(), _filter_binds()
  schema_catalog.py   — Catálogo de vistas disponibles para el LLM
  main.py             — FastAPI: /health, /greet, /chat
  settings.py         — Config (.env)
  sql_safety.py       — Valida que el SQL sea solo SELECT
```

## Reglas absolutas — nunca violar

- **NO tocar Page 0** (página 0 de APEX).
- **NO usar** `window.location.reload()`, `apex.page.reload()`, ni `location.reload()`.
- **NO usar** `clearcache` ni `reset` al navegar de página 233 → 34.
- **Siempre incluir** `cod_empleado`, `cod_vendedor`, `ver_otros_vendedores` en cada request al backend.
- El botón "Crear pedido" lo inyecta **siempre el backend** (`agent.py`). El LLM **nunca** debe generarlo — causa JSON inválido en Oracle.
- Static ID del report de detalle en página 34: `detalle` → refrescar con `$('#detalle').trigger('apexrefresh')`.

## Flujo chat → pedido

```
Página 233 (chat)
  ↓ usuario hace clic en "Crear pedido"
  ↓ js_abrir_pedido(codC, itemsJson)
      • deduplica items por cod sumando qty
      • llama SET_PEDIDO_CHAT (ON_DEMAND pág 233)
      • guarda cod_cliente en sessionStorage
  ↓ navega a página 34

Página 34 (pedido)
  CARGA_VALORES DA (DOM ready):
    seq 25 — lee sessionStorage → apex.item('P34_COD_CLIENTE').setValue(codC)
             → dispara DA datos_cliente (~600 ms)
    seq 35 — setTimeout(2000) → llama CARGAR_PEDIDO_CHAT (ON_DEMAND pág 34)
             → lee colección PEDIDO_CHAT
             → calcula precio via PRECIO_web_empresa_APEX()
             → calcula IVA via st_articulos + st_iva
             → llama vtpedido_34.vtpedido_add_det() por cada artículo
             → $('#detalle').trigger('apexrefresh')
```

## Colección APEX usada

`PEDIDO_CHAT` (session-scoped):
- `c001` = cod_cliente
- `c002` = items JSON `[{"cod":"ART1","desc":"...","qty":2}, ...]`

## Oracle 12c — restricciones SQL críticas

| ❌ No usar | ✅ Usar en cambio |
|-----------|-----------------|
| `LIMIT N` | `FETCH FIRST N ROWS ONLY` |
| `STRING_AGG(...)` | `LISTAGG(col,', ') WITHIN GROUP (ORDER BY col)` |
| `LISTAGG(DISTINCT ...)` | subquery `SELECT DISTINCT` + `LISTAGG` |
| `SUM(x) > 0` en WHERE | `HAVING SUM(x) > 0` |
| `ORDER BY SUM(x)` | alias en SELECT + `ORDER BY alias` |
| `DISTINCT` + `GROUP BY` juntos | solo `GROUP BY` |
| `COD_ART_CORTO` como id de artículo | `COD_ARTICULO` siempre |
| Hardcodear `COD_EMPRESA` en SQL | bind variable `:cod_empresa` |
| `SUM(s.CANT_DISPON) > 0` en WHERE (JOIN stock) | `HAVING SUM(s.CANT_DISPON) > 0` |

Vistas disponibles (siempre prefijo `INV.`):
`V_VENTAS_APEX`, `V_STOCK_APEX`, `V_CLIENTE_APEX`, `V_PEDIDOS_PRODUCTOS`, `V_METAS_VENDEDORES`, `V_PROMOCIONES_APEX`

### Filtros obligatorios por vista

- `V_VENTAS_APEX` ventas reales: `TIP_COMPROBANTE IN ('FCR','FCO')`
- `V_VENTAS_APEX` notas de crédito: `TIP_COMPROBANTE = 'NCR'`
- `V_STOCK_APEX` stock comercializable: `COD_RUBRO = 'PR'`
- `V_CLIENTE_APEX` estados válidos: `'ACTIVO'`, `'INACTIVO'`, `'BLOQUEADO'`, `'CREDITO BLOQUEADO'`
- Sugerencias de artículos: `UPPER(NVL(DESC_DIVISION,'')) != 'PROMOS'`
- Módulo Clientes mayoristas: `TIPO_CLIENTE IN ('MAYORISTA A','MAYORISTA B','MAYORISTA C','CORPORATIVOS','GASTRONOMIA','SUPERMERCADO','MAYORISTA-GASTRONOMIA') AND ESTADO = 'ACTIVO'`

## Reglas VER_OTROS_VENDEDORES

- `'N'` → `AND COD_VENDEDOR = :P_COD_VENDEDOR` en toda consulta sobre ventas/clientes/pedidos/metas.
- `'S'` → puede ver todos los vendedores (rankings, comparativas).
- El backend fuerza el filtro aunque el LLM lo omita (`_inject_vendor_filter` en `agent.py`).
- `P_COD_VENDEDOR` **nunca** va en el JSON `params` del LLM — el backend lo inyecta solo.

## Botón "Crear pedido" — lógica backend (agent.py)

Se inyecta si: `cod_cliente` en contexto + resultado tiene columna `cod_articulo`/`codigo` + el LLM **no** generó el botón.

Items: máximo **14 líneas** (tras deduplicación).

Columnas de cantidad (prioridad):
1. `cant_cliente` → promedio histórico del cliente (últimos 3 meses)
2. `cant_vendedor` → 80% del promedio del vendedor (últimos 3 meses)
3. columna genérica (`qty_sugerida`, `cantidad`, etc.)
4. mínimo absoluto: 1

JSON del botón: `ensure_ascii=True`, caracteres de control filtrados. El LLM **nunca** genera este botón.

## Botones de sugerencias (greet + getSug)

```
🔥 Ventas:          ¿Cómo voy hoy? | ¿Cuánto vendí este mes? | ¿Estoy mejor que el mes pasado? | ¿Qué notas de crédito tuve este mes?
📦 Productos:       ¿Qué productos puedo vender más hoy? | ¿Cuáles son los más vendidos? | ¿Qué productos tienen bajo stock?
🧍 Clientes:        Ranking de compras de clientes | Clientes mayoristas activos sin compras este mes | Clientes mayoristas activos sin compras esta semana | ¿A quién debería visitar hoy?
🎯 Metas:           ¿Cómo voy contra mi meta este mes? | ¿Cuánto me falta para alcanzar mi meta? | ¿Qué porcentaje de mi meta ya cumplí?
📦 Pedidos:         ¿Qué pedidos tengo pendientes? | ¿Cuáles son mis pedidos más grandes sin cerrar? | ¿Qué pedidos necesitan autorización?
💡 Oportunidades:   ¿Dónde tengo oportunidades de venta? | ¿Qué puedo vender rápido hoy? | ¿Qué productos tienen alta demanda y stock disponible?
🔧 Reparaciones/OT: ¿Qué OTs tienen mis clientes? | ¿Hay OTs en garantía pendientes? | ¿Qué OTs ingresaron este mes? | ¿Cuánto tiempo llevan sin repararse?
```

Estos botones están definidos **en dos lugares** (deben mantenerse sincronizados):
1. `agent.py` → `handle_greet()` → `_section_html()`
2. `f122_page_233.sql` → acción JS con `getSug()`

## db.py — comportamiento importante

`_filter_binds(sql, binds)` filtra el dict antes de ejecutar en Oracle. Evita `ORA-01036` cuando el LLM incluye params extra que hardcodeó en el SQL (ej: `cod_empresa='1'` en SQL + `cod_empresa` en params).

## Errores conocidos y sus causas

| Error | Causa | Fix aplicado |
|-------|-------|-------------|
| `ORA-00934: group function not allowed here` | `SUM(...)` en WHERE en lugar de HAVING | Regla 7 + Regla 10 en `_SQL_SYSTEM` |
| `ORA-01036: illegal variable name/number` | bind variable en params no referenciado en SQL | `_filter_binds()` en `db.py` |
| `ORA-20987: strict mode JSON parser` | LLM generaba botón con JSON inválido (claves sin comillas) | LLM ya no genera el botón — solo backend |
| Items no cargados en pedido | `datos_cliente` DA no terminaba antes de `vtpedido_add_det` | `setTimeout(2000)` en seq 35 pág 34 |

## Contexto APEX — items de página importantes

**Página 233:**
- `P233_COD_EMPRESA` → empresa activa
- `P233_COD_VENDEDOR_PAG0` → vendedor
- `P233_COD_EMPLEADO` → empleado
- `P233_VER_OTROS_VENDEDORES` → flag visibilidad

**Página 34:**
- `P34_COD_CLIENTE`, `P34_NOM_CLIENTE`, `P34_COD_VENDEDOR`
- `P34_SER_COMPROBANTE` (default `'P'`), `P34_NRO_COMPROBANTE`, `P34_ID_PEDIDO`
- `P34_COD_LISTA_PRECIO` → necesario para `PRECIO_web_empresa_APEX()`
- `P34_TIP_CLIENTE` → si `'E'` (exportación), IVA = 0

## Vista OTs — INV.V_ORDENES_TRABAJO_CLIENTES

No tiene COD_VENDEDOR. El filtro de vendedor se aplica vía subquery:
```sql
AND ot.COD_CLIENTE IN (
  SELECT DISTINCT COD_CLIENTE FROM INV.V_VENTAS_APEX
  WHERE COD_VENDEDOR = :P_COD_VENDEDOR AND COD_EMPRESA = :cod_empresa
  AND TIP_COMPROBANTE IN ('FCR','FCO')
)
```
- `FECHA_REPARACION IS NULL` → pendiente
- `EN_GARANTIA = 'S'` → en garantía
- `ROUND(SYSDATE - FECHA_INGRESO, 0)` → días transcurridos (alias en SELECT, ORDER BY alias)
- Si `VER_OTROS_VENDEDORES = 'S'`: omitir el subquery de clientes

## Proceso IVA en CARGAR_PEDIDO_CHAT

```sql
JOIN st_iva iv ON iv.cod_iva = a.cod_iva
  AND iv.fec_vigencia = (SELECT MAX(fec_vigencia) FROM st_iva
    WHERE cod_iva = a.cod_iva AND fec_vigencia <= SYSDATE)
```
- `l_piva >= 0.09 AND <= 0.11` → IVA 10% → `l_g10`
- `l_piva >= 0.04 AND <= 0.06` → IVA 5% → `l_g5`
- else → exenta → `l_exen`

## Backend — API

URL: `http://10.100.13.110:8010`
- `POST /chat` → `handle_chat(mensaje, usuario, contexto, historial)`
- `POST /greet` → `handle_greet(usuario, contexto)`
- `GET /health`

Contexto mínimo: `{cod_empresa, cod_vendedor, cod_empleado, ver_otros_vendedores, periodo}`
