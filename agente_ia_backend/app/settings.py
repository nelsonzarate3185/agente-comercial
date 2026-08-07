from __future__ import annotations

from pydantic import BaseModel
import os
from pathlib import Path

from dotenv import load_dotenv


# Carga .env desde la raíz del proyecto (agente_ia_backend/.env) si existe.
_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env", override=False)


class Settings(BaseModel):
    oracle_host: str = os.getenv("ORACLE_HOST", "192.168.15.88")
    oracle_port: int = int(os.getenv("ORACLE_PORT", "1521"))
    oracle_service: str = os.getenv("ORACLE_SERVICE", "ngodes")
    oracle_user: str = os.getenv("ORACLE_USER", "")
    oracle_password: str = os.getenv("ORACLE_PASSWORD", "")
    # Thick mode: ruta a Oracle Instant Client. Vacío = thin mode.
    oracle_client_dir: str = os.getenv(
        "ORACLE_CLIENT_DIR",
        r"C:\app\client\product\12.2.0\client_1",
    )

    api_key: str | None = os.getenv("API_KEY") or None
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    db_call_timeout_ms: int = int(os.getenv("DB_CALL_TIMEOUT_MS", "8000"))
    max_rows: int = int(os.getenv("MAX_ROWS", "50"))

    # LLM
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
    llm_timeout: float = float(os.getenv("LLM_TIMEOUT", "60"))
    http_proxy: str = os.getenv("HTTP_PROXY", "")


settings = Settings()

# Tratar placeholders como "no configurado"
if settings.api_key and settings.api_key.strip().upper() in {"CHANGE_ME", "CHANGEME"}:
    settings.api_key = None

