from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    mensaje: str = Field(min_length=1, max_length=4000)
    usuario: str = Field(min_length=1, max_length=255)
    contexto: dict[str, Any] | None = None
    historial: list[dict[str, str]] | None = None


class GreetRequest(BaseModel):
    usuario: str = Field(min_length=1, max_length=255)
    contexto: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    respuesta: str
    sql_generado: str | None = None
    datos: dict[str, Any] | None = None

