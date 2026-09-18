"""
Catálogo estático de vistas disponibles para el agente IA.
Estructura real del esquema INV en Oracle 12c.
"""
from __future__ import annotations

VIEWS: dict[str, dict] = {
    "INV.V_VENTAS_agente": {
        "alias": "ventas",
        "description": (
            "Líneas de ventas y facturación. Cada fila es un artículo vendido en un comprobante. "
            "Usar para: análisis de ventas por período, top productos, top clientes, "
            "ranking vendedores, tendencias, comparativas de monto/cantidad."
        ),
        "columns": {
            "FEC_FACTURA":         "DATE     – Fecha de emisión de la factura (usar para filtros por período)",
            "FEC_PEDIDO":          "DATE     – Fecha del pedido",
            "COD_CLIENTE":         "VARCHAR2 – Código del cliente",
            "NOMBRE":              "VARCHAR2 – Nombre o razón social del cliente",
            "COD_ARTICULO":        "VARCHAR2 – Código completo del artículo",
            "COD_ART_CORTO":       "VARCHAR2 – Código corto del artículo",
            "DESC_ARTICULO":       "VARCHAR2 – Descripción del artículo",
            "CANTIDAD":            "NUMBER   – Cantidad de unidades vendidas",
            "MONTO":               "NUMBER   – Monto total de la línea en moneda local",
            "COD_VENDEDOR":        "VARCHAR2 – Código del vendedor responsable",
            "NOMBRE_VENDEDOR":     "VARCHAR2 – Nombre completo del vendedor",
            "COD_EMPRESA":         "VARCHAR2 – Código de empresa (SIEMPRE filtrar por esto si existe en contexto)",
            "COD_DIVISION":        "VARCHAR2 – División comercial (solo código; DESC_DIVISION NO existe en esta vista, está en V_STOCK_agente)",
            "COD_FAMILIA":         "VARCHAR2 – Familia de producto (solo código; DESC_FAMILIA NO existe en esta vista, está en V_STOCK_agente)",
            "COD_CATEGORIA":       "VARCHAR2 – Categoría de producto (solo código)",
            "COD_MARCA":           "VARCHAR2 – Código de marca",
            "DESC_MARCA":          "VARCHAR2 – Nombre de la marca",
            "TIP_COMPROBANTE":     "VARCHAR2 – Tipo de comprobante. Ventas reales: 'FCR','FCO'. Notas crédito: 'NCR'. SIEMPRE filtrar solo por ventas: TIP_COMPROBANTE IN ('FCR','FCO'). Nunca usar 'FT'.",
            "ESTADO":              "VARCHAR2 – Estado del comprobante",
        },
        "date_filter_col": "FEC_FACTURA",
    },
    "INV.V_STOCK_agente": {
        "alias": "stock",
        "description": (
            "Stock disponible por artículo y sucursal. "
            "Usar para: artículos con stock crítico o bajo, inventario por sucursal, "
            "costo promedio, valor del inventario, análisis de disponibilidad."
        ),
        "columns": {
            "COD_SUCURSAL":            "VARCHAR2 – Código de la sucursal",
            "DESC_SUCURSAL":           "VARCHAR2 – Nombre de la sucursal",
            "COD_ARTICULO":            "VARCHAR2 – Código del artículo",
            "DESC_ARTICULO":           "VARCHAR2 – Descripción del artículo",
            "CANT_DISPON":             "NUMBER   – Cantidad disponible en stock (columna clave)",
            "COSTO_PROMEDIO_UNITARIO": "NUMBER   – Costo promedio por unidad",
            "MARCA":                   "VARCHAR2 – Marca del artículo (columna se llama MARCA, NO DESC_MARCA — ese nombre solo existe en V_VENTAS_agente)",
            "COD_ART_CORTO":           "VARCHAR2 – Código corto del artículo (preferir sobre COD_ARTICULO; puede estar vacío)",
            "DESC_CATEGOGIRA":         "VARCHAR2 – Categoría del artículo",
            "DESC_FAMILIA":            "VARCHAR2 – Familia de producto",
            "DESC_DIVISION":           "VARCHAR2 – División",
            "COD_EMPRESA":             "VARCHAR2 – Código de empresa",
            "COD_RUBRO":               "VARCHAR2 – Rubro del artículo. SIEMPRE filtrar COD_RUBRO='PR' para productos comercializables",
            "FACTURABLE":              "VARCHAR2 – S=Facturable, N=No facturable",
        },
        "date_filter_col": None,
    },
    "INV.V_PROMOCIONES_APEX": {
        "alias": "promociones",
        "description": (
            "Promociones comerciales vigentes por artículo. "
            "Usar para: listar promos activas, descuentos disponibles, artículos con regalo/bonificación, "
            "promos mix (varios artículos), promos por cliente específico."
        ),
        "columns": {
            "COD_ARTICULO":           "VARCHAR2 – Código del artículo que activa la promo",
            "CANTIDAD_MINIMA_COMPRA": "NUMBER   – Cantidad mínima de compra para activar la promo",
            "DESCUENTO_PRODUCTO":     "NUMBER   – % de descuento sobre el producto principal",
            "COD_ARTICULO_PROMO":     "VARCHAR2 – Código del artículo regalo o bonificado",
            "CANTIDAD_REGALO":        "NUMBER   – Cantidad de unidades del artículo regalo",
            "DESCUENTO_PROMO":        "NUMBER   – % de descuento sobre el artículo bonificado",
            "ART_CORTO_REGALO":       "VARCHAR2 – Código corto del artículo regalo",
            "NRO_PROMO":              "VARCHAR2 – Número identificador de la promoción",
            "COD_EMPRESA_PROMO":      "VARCHAR2 – Código de empresa (SIEMPRE filtrar si está en contexto)",
            "NOMBRE_PROMO":           "VARCHAR2 – Nombre descriptivo de la promoción",
            "COD_ARTICULO_PRINCIPAL": "VARCHAR2 – Código completo del artículo principal",
            "FECHA_INICIO":           "DATE     – Fecha inicio de vigencia (no FEC_ALTA)",
            "FECHA_FIN":              "DATE     – Fecha fin de vigencia (no FEC_CIERRE)",
            "COD_LISTA_PRECIO":       "VARCHAR2 – Lista de precio a la que aplica",
            "COD_CLIENTE":            "VARCHAR2 – Cliente específico (NULL = aplica a todos)",
            "PROMO_MIX":              "VARCHAR2 – S=Promo mix (múltiples artículos), N=Normal",
        },
        "date_filter_col": "FECHA_INICIO",
    },
    "INV.V_CLIENTE_agente": {
        "alias": "clientes",
        "description": (
            "Maestro de clientes con indicadores comerciales y financieros. "
            "Usar para: clientes inactivos, deudas vencidas, crédito disponible, "
            "ranking por ventas anuales/mensuales, segmentación por tipo o vendedor."
        ),
        "columns": {
            "COD_CLIENTE":        "VARCHAR2 – Código único del cliente",
            "NOMBRE":             "VARCHAR2 – Nombre o razón social",
            "FEC_ULTIMA_COMPRA":  "DATE     – Fecha de la última compra (clave para detectar inactividad)",
            "DEUDA_VENCIDA":      "NUMBER   – Monto de deuda vencida",
            "DEUDA_TOTAL":        "NUMBER   – Deuda total del cliente",
            "CREDITO_DISPONIBLE": "NUMBER   – Crédito disponible para nuevas compras",
            "LINEA_DE_CREDITO":   "NUMBER   – Límite máximo de crédito asignado",
            "VENTA_ANIO":         "NUMBER   – Ventas acumuladas del año en curso",
            "VENTA_MES":          "NUMBER   – Ventas del mes actual",
            "COD_VENDEDOR":       "VARCHAR2 – Código del vendedor asignado",
            "NOMBRE_VENDEDOR":    "VARCHAR2 – Nombre del vendedor asignado",
            "COD_TIP_CLIENTE":    "VARCHAR2 – Código de tipo de cliente",
            "TIPO_CLIENTE":       "VARCHAR2 – Descripción del tipo de cliente",
            "ESTADO":             "VARCHAR2 – Estado del cliente. Valores exactos: 'ACTIVO', 'INACTIVO', 'BLOQUEADO', 'CREDITO BLOQUEADO'. Nunca usar 'A' ni 'B'.",
            "SCORING":            "VARCHAR2 – Scoring crediticio del cliente",
            "DESCRIPCION_CIUDAD": "VARCHAR2 – Ciudad del cliente",
        },
        "date_filter_col": "FEC_ULTIMA_COMPRA",
    },
    "INV.V_METAS_VENDEDORES": {
        "alias": "metas",
        "description": (
            "Metas de ventas asignadas por vendedor y período. "
            "Usar para: comparar ventas reales vs meta, calcular % de cumplimiento, "
            "detectar vendedores lejos de su objetivo, analizar brecha faltante."
        ),
        "columns": {
            "COD_EMPRESA":  "VARCHAR2 – Código de empresa (SIEMPRE filtrar si está en contexto)",
            "COD_VENDEDOR": "VARCHAR2 – Código del vendedor",
            "FECHA_INICIO": "DATE     – Inicio del período de la meta",
            "FECHA_FIN":    "DATE     – Fin del período de la meta",
            "MONTO_META":   "NUMBER   – Monto objetivo de ventas para el período",
        },
        "date_filter_col": "FECHA_INICIO",
    },
    "INV.V_PEDIDOS_PRODUCTOS": {
        "alias": "pedidos",
        "description": (
            "Líneas de pedidos de clientes con estado de facturación y autorización. "
            "Usar para: pedidos pendientes o parcialmente facturados, pedidos sin autorizar, "
            "importe pendiente de cobro, seguimiento de clientes con pedidos abiertos, "
            "productos con alta demanda en cartera de pedidos."
        ),
        "columns": {
            "COD_EMPRESA":          "VARCHAR2 – Código de empresa",
            "COD_CLIENTE":          "VARCHAR2 – Código del cliente",
            "SIGLAS":               "VARCHAR2 – Moneda del pedido",
            "IMPORTE":              "NUMBER   – Importe original del pedido",
            "IMPORTE_PENDIENTE":    "NUMBER   – Importe pendiente de facturación (clave para análisis de cartera)",
            "NRO_COMPROBANTE":      "VARCHAR2 – Número del pedido (usar para agrupar líneas del mismo pedido)",
            "TIPO":                 "VARCHAR2 – Tipo de entrega del pedido",
            "ORIGEN_ENTREGA":       "VARCHAR2 – Lugar de entrega",
            "COMENTARIO":           "VARCHAR2 – Comentario del pedido",
            "NOMBRE_SUCURSAL":      "VARCHAR2 – Sucursal del cliente",
            "DEPARTAMENTO":         "VARCHAR2 – Departamento de la sucursal",
            "CIUDAD":               "VARCHAR2 – Ciudad de la sucursal",
            "VOLUMEN":              "NUMBER   – Volumen del pedido",
            "FECHA_PEDIDO":         "DATE     – Fecha de creación del pedido",
            "ESTADO":               "VARCHAR2 – Estado: 'ANULADO','CERRADO','FACTURADO','PARCIALMENTE_FACTURADO','PENDIENTE'",
            "COD_ARTICULO":         "VARCHAR2 – Código del artículo",
            "CANTIDAD":             "NUMBER   – Cantidad pedida",
            "CANTIDAD_FACTURADA":   "NUMBER   – Cantidad ya facturada",
            "AUTORIZACION":         "VARCHAR2 – Estado de autorización del pedido (NULL = sin bloqueo)",
            "COD_VENDEDOR":         "VARCHAR2 – Código del vendedor responsable",
        },
        "date_filter_col": "FECHA_PEDIDO",
    },
    "INV.V_ORDENES_TRABAJO_CLIENTES": {
        "alias": "ordenes_trabajo",
        "description": (
            "Órdenes de trabajo (OT) / reparaciones de artículos de clientes. "
            "Usar para: OTs pendientes de reparación, OTs en garantía, tiempo sin reparar, "
            "OTs ingresadas en un período. NO tiene COD_VENDEDOR — filtrar vendedor vía "
            "subquery de clientes sobre V_VENTAS_agente."
        ),
        "columns": {
            "OT":               "VARCHAR2 – Número de la orden de trabajo",
            "ESTADO_OT":        "VARCHAR2 – Estado actual de la OT",
            "FECHA_INGRESO":    "DATE     – Fecha en que ingresó la OT (columna de filtro por período)",
            "FECHA_REPARACION": "DATE     – Fecha de reparación/cierre. NULL = pendiente de reparar",
            "NUMERO_GARANTIA":  "VARCHAR2 – Número de garantía (si aplica)",
            "COD_ARTICULO":     "VARCHAR2 – Código del artículo en reparación",
            "DESC_ARTICULO":    "VARCHAR2 – Descripción del artículo",
            "COD_EMPRESA":      "VARCHAR2 – Código de empresa (SIEMPRE filtrar si está en contexto)",
            "EN_GARANTIA":      "VARCHAR2 – 'S' = en garantía, 'N' = fuera de garantía",
            "COD_CLIENTE":      "VARCHAR2 – Código del cliente dueño del artículo",
            "NOM_CLIENTE":      "VARCHAR2 – Nombre del cliente",
            "COD_ORIGEN":       "VARCHAR2 – Origen de la OT",
        },
        "date_filter_col": "FECHA_INGRESO",
    },
}


def build_schema_text() -> str:
    """Genera el bloque de texto del esquema para el system prompt del LLM."""
    parts = []
    for view_name, info in VIEWS.items():
        cols = "\n".join(f"    {col}: {desc}" for col, desc in info["columns"].items())
        parts.append(
            f"Vista: {view_name}\n"
            f"Uso: {info['description']}\n"
            f"Columnas:\n{cols}"
        )
    return "\n\n---\n\n".join(parts)
