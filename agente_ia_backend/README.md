## Agente IA Comercial (Python + FastAPI) para Oracle APEX

Backend REST que recibe preguntas comerciales y responde con insights basados en Oracle 12c.

### 1) Requisitos
- Python 3.10+
- Acceso de red a Oracle: `192.168.15.88:1521/ngodes`

### 2) Configuración
1. Copiar variables:
   - Copiá `.env.example` a `.env` y completá `ORACLE_USER` / `ORACLE_PASSWORD`.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

### 3) Ejecutar

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Healthcheck: `GET /health`

### 4) API

#### POST /chat
Request:
```json
{
  "mensaje": "¿Qué productos tienen poco stock?",
  "usuario": "NZARATE",
  "contexto": {
    "cod_empresa": "1",
    "dias_inactivo": 60,
    "min_stock": 5
  }
}
```

Response:
```json
{
  "respuesta": "📊 Resumen:\n...\n\n📈 Hallazgos clave:\n- ...\n- ...\n\n⚠️ Alertas:\n...\n\n💡 Recomendaciones:\n- ...\n- ...",
  "sql_generado": "select ...",
  "datos": {
    "intencion": "LOW_STOCK",
    "filas": [
      {"producto":"X","stock_total":3}
    ]
  }
}
```

### 5) Seguridad
- Solo ejecuta SQL **SELECT** (bloquea `UPDATE/DELETE/INSERT/MERGE/DROP/...`).
- Si configurás `API_KEY`, exige header `X-API-Key`.

### 6) Integración con APEX (Página 233)

Opciones:

- **REST Data Source (recomendado)**:
  - Crear REST Data Source apuntando a `POST` `http://<host>:8000/chat`.
  - Mapear el body JSON con `P233_...` o valores de JavaScript.

- **APEX_WEB_SERVICE**:
  - Crear proceso Ajax Callback/On Demand que llame al endpoint con `apex_web_service.make_rest_request`.

#### JS mínimo (región HTML/estática en APEX)
Ejemplo (ajustar `API_URL` y API Key si aplica):

```javascript
const API_URL = "http://<host>:8000/chat";
const API_KEY = ""; // opcional

async function enviarAlAgenteIA(mensaje) {
  const body = {
    mensaje,
    usuario: apex.env.APP_USER,
    contexto: {
      periodo: "mes",
      min_stock: 5,
      dias_inactivo: 60
    }
  };
  const res = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(API_KEY ? {"X-API-Key": API_KEY} : {})
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error("Error API");
  const data = await res.json();
  return data.respuesta;
}
```

