from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import oracledb

from .agent import handle_chat
from .schemas import ChatRequest, ChatResponse
from .security import require_api_key
from .settings import settings


logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
log = logging.getLogger("agente_ia_backend")


app = FastAPI(title="Agente IA Comercial", version="0.1.0")

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


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, _: None = Depends(require_api_key)) -> ChatResponse:
    try:
        res = handle_chat(payload.mensaje, payload.usuario, payload.contexto, payload.historial)
        return ChatResponse(respuesta=res.respuesta, sql_generado=res.sql_generado, datos=res.datos)
    except oracledb.DatabaseError as e:
        # Respuesta controlada (sin detalles técnicos) para que APEX pueda mostrar algo útil.
        msg = (
            "📊 Resumen:\n"
            "No pude conectarme a la base Oracle para ejecutar la consulta.\n\n"
            "📈 Hallazgos clave:\n"
            "- La conexión a Oracle falló (credenciales o acceso).\n"
            "- Sin conexión no puedo generar insights confiables.\n\n"
            "⚠️ Alertas:\n"
            "Revisar `agente_ia_backend/.env` (ORACLE_USER / ORACLE_PASSWORD) y permisos a las vistas.\n\n"
            "💡 Recomendaciones:\n"
            "- Actualizar `ORACLE_PASSWORD` real y reiniciar el backend.\n"
            "- Verificar que el usuario tenga SELECT sobre `inv.v_ventas_apex`, `inv.v_stock_apex`, `inv.v_cliente_apex`."
        )
        log.exception("Oracle DatabaseError")
        return ChatResponse(
            respuesta=msg,
            sql_generado=None,
            datos={"error": "oracle_database_error"},
        )
    except Exception as e:
        log.exception("Unhandled error in /chat")
        raise HTTPException(status_code=500, detail="Error interno del agente IA") from e

