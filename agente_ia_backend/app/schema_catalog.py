"""
Catálogo estático de vistas disponibles para el agente IA.
Estructura real del esquema INV en Oracle 12c.
"""
from __future__ import annotations

VIEWS: dict[str, dict] = {
    "INV.V_VENTAS_APEX": {
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
            "COD_DIVISION":        "VARCHAR2 – División comercial",
            "COD_FAMILIA":         "VARCHAR2 – Familia de producto",
            "COD_CATEGORIA":       "VARCHAR2 – Categoría de producto",
            "COD_MARCA":           "VARCHAR2 – Código de marca",
            "DESC_MARCA":          "VARCHAR2 – Nombre de la marca",
            "TIP_COMPROBANTE":     "VARCHAR2 – Tipo de comprobante. Ventas reales: 'FCR','FCO'. Notas crédito: 'NCR'. SIEMPRE filtrar solo por ventas: TIP_COMPROBANTE IN ('FCR','FCO'). Nunca usar 'FT'.",
            "ESTADO":              "VARCHAR2 – Estado del comprobante",
        },
        "date_filter_col": "FEC_FACTURA",
    },
    "INV.V_STOCK_APEX": {
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
            "MARCA":                   "VARCHAR2 – Marca del artículo",
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
    "INV.V_CLIENTE_APEX": {
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
            "FEC_ULTIMA_VISITA":  "DATE     – Fecha de última visita del vendedor",
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
