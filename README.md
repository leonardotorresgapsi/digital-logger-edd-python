# Digital EDD Logger (Python)

SDK de logging para servicios Python con soporte para PostgreSQL (desarrollo) y Google Cloud PubSub (producción).

## Instalación

```bash
pip install eddlogger
```

Dependencias opcionales por driver:

```bash
pip install psycopg            # para PostgresDriver
pip install google-cloud-pubsub  # para PubSubDriver
```

## Uso Rápido

```python
from eddlogger import EddLogger, LogOptions

logger = EddLogger("my-service")

record_id = logger.log(
    LogOptions(
        trace_id="abc-123",
        action="ORDER_CREATED",
        context="OrderService",
        method="POST",
        path="/api/orders",
        request_body={"product": "ABC", "qty": 2},
        status_code=200,
        response_body={"order_id": "12345"},
        duration_ms=150.5,
    )
)

logger.close()
```

## Configuración

### Local/Dev (PostgreSQL)

```bash
DB_URL=postgresql://user:password@localhost:5432/mydb
ENV=local
```

### Producción/QA (PubSub)

```bash
ENV=prod  # o "production", "qa", "qas"
GOOGLE_CLOUD_PROJECT=my-project-id
```

## Comportamiento

| ENV | Driver | Destino |
|-----|--------|---------|
| `local` (o vacío) | PostgreSQL | Tabla `LGS_EDD_SDK_HIS` |
| `prod`, `production`, `qa`, `qas` | PubSub | Topic `digital-edd-sdk` |

Si falta configuración, usa `ConsoleDriver` como fallback.

## API

```python
from eddlogger import LogOptions

LogOptions(
    trace_id="",
    level="",  # DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT
    action="",
    context="",
    method="",
    path="",
    request_headers={},
    request_body=None,
    status_code=0,
    response_headers={},
    response_body=None,
    duration_ms=0.0,
    message_info="",
    message_raw="",
    tags=[],
    service="",
)
```

## Variables de Entorno

| Variable               | Descripción                    | Requerido                             |
|------------------------|--------------------------------|---------------------------------------|
| `DB_URL`               | URL de PostgreSQL              | Solo en local                         |
| `ENV`                  | `local` para forzar PostgreSQL | Opcional                              |
| `GOOGLE_CLOUD_PROJECT` | Project ID de GCP              | Solo en prod                          |
| `SDKTRACKING_PUBLISH`  | `false` para deshabilitar      | Opcional                              |
| `PUBSUB_TOPIC_NAME`    | Nombre del topic               | Opcional (default: `digital-edd-sdk`) |
