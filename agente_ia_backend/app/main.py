from __future__ import annotations

import logging

import os

import anthropic
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import oracledb

from .agent import handle_chat, handle_greet
from .schemas import ChatRequest, ChatResponse, GreetRequest
from .security import require_api_key
from .settings import settings


logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
log = logging.getLogger("agente_ia_backend")


app = FastAPI(title="Agente IA Comercial", version="0.1.0", root_path=os.getenv("ROOT_PATH", ""))

# Si el backend se consume desde APEX en otro host, CORS puede ser útil.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/greet", response_model=ChatResponse)
def greet(payload: GreetRequest, _: None = Depends(require_api_key)) -> ChatResponse:
    try:
        res = handle_greet(payload.usuario, payload.contexto)
        return ChatResponse(respuesta=res.respuesta, sql_generado=res.sql_generado, datos=res.datos)
    except Exception:
        log.exception("Error in /greet")
        return ChatResponse(
            respuesta="Hola 👋\n\nSoy tu asistente comercial. ¿En qué te puedo ayudar hoy?",
            sql_generado=None,
            datos={"intencion": "GREET_FALLBACK"},
        )


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, _: None = Depends(require_api_key)) -> ChatResponse:
    try:
        res = handle_chat(payload.mensaje, payload.usuario, payload.contexto, payload.historial)
        return ChatResponse(respuesta=res.respuesta, sql_generado=res.sql_generado, datos=res.datos)
    except oracledb.DatabaseError as e:
        err_str = str(e)
        log.exception("Oracle DatabaseError")
        # ORA-009xx / ORA-004xx = error de SQL generado por el LLM → mensaje accionable
        if any(code in err_str for code in ("ORA-009", "ORA-004", "ORA-001", "ORA-006")):
            msg = (
                "📊 Resumen:\n"
                "El modelo generó una consulta SQL con un error de sintaxis o columna inválida.\n\n"
                "📈 Hallazgos clave:\n"
                f"- Error Oracle: {err_str.splitlines()[0]}\n\n"
                "⚠️ Alertas:\n"
                "La consulta no pudo ejecutarse.\n\n"
                "💡 Recomendaciones:\n"
                "- Intentá reformular la pregunta con más detalle.\n"
                "- Ejemplo: en vez de 'stock crítico' probá 'artículos con cantidad disponible menor a 5'."
            )
        else:
            msg = (
                "📊 Resumen:\n"
                "No pude conectarme a Oracle para ejecutar la consulta.\n\n"
                "📈 Hallazgos clave:\n"
                "- La conexión a Oracle falló (credenciales o red).\n\n"
                "⚠️ Alertas:\n"
                "Revisar `.env` (ORACLE_USER / ORACLE_PASSWORD) y permisos sobre las vistas.\n\n"
                "💡 Recomendaciones:\n"
                "- Verificar que el usuario tenga SELECT sobre las vistas INV.V_*_APEX."
            )
        return ChatResponse(
            respuesta=msg,
            sql_generado=None,
            datos={"error": "oracle_database_error"},
        )
    except ValueError as e:
        log.warning("Bind variable faltante: %s", e)
        return ChatResponse(
            respuesta=(
                "📊 Resumen:\n"
                "El modelo generó una consulta con parámetros incompletos.\n\n"
                "📈 Hallazgos clave:\n"
                f"- {e}\n\n"
                "⚠️ Alertas:\n"
                "No se pudo ejecutar la consulta de forma segura.\n\n"
                "💡 Recomendaciones:\n"
                "- Intentá reformular la pregunta.\n"
                "- Ejemplo: 'qué compra habitualmente ZEIN SRL' o 'stock disponible para ZEIN SRL'."
            ),
            sql_generado=None,
            datos={"error": "unbound_params"},
        )
    except anthropic.RateLimitError:
        log.warning("Anthropic rate limit alcanzado")
        return ChatResponse(
            respuesta=(
                "📊 Resumen:\n"
                "El servicio de IA está temporalmente saturado.\n\n"
                "📈 Hallazgos clave:\n"
                "- Se alcanzó el límite de requests a la API de Claude.\n\n"
                "⚠️ Alertas:\n"
                "Esperá unos segundos e intentá de nuevo.\n\n"
                "💡 Recomendaciones:\n"
                "- Volvé a enviar la misma pregunta en unos instantes."
            ),
            sql_generado=None,
            datos={"error": "rate_limit"},
        )
    except (anthropic.APITimeoutError, anthropic.APIConnectionError) as e:
        log.exception("Anthropic conexión/timeout: %s", e)
        return ChatResponse(
            respuesta=(
                "📊 Resumen:\n"
                "No se pudo conectar al servicio de IA en este momento.\n\n"
                "📈 Hallazgos clave:\n"
                "- Error de conexión con la API de Claude.\n\n"
                "⚠️ Alertas:\n"
                "Puede ser un problema temporal de red.\n\n"
                "💡 Recomendaciones:\n"
                "- Intentá de nuevo en unos segundos."
            ),
            sql_generado=None,
            datos={"error": "api_connection_error"},
        )
    except Exception as e:
        log.exception("Unhandled error in /chat")
        raise HTTPException(status_code=500, detail="Error interno del agente IA") from e

