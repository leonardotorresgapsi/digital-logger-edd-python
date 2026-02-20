import json
import os
from datetime import datetime, timezone
from typing import Any

from .base import BaseDriver

TABLE_NAME = "LGS_EDD_SDK_HIS"
DDL = """
CREATE TABLE IF NOT EXISTS LGS_EDD_SDK_HIS (
    id SERIAL PRIMARY KEY,
    traceId VARCHAR(255) NOT NULL,
    timeLocal TIMESTAMP NOT NULL,
    timeUTC TIMESTAMP NOT NULL,
    service VARCHAR(255) NOT NULL,
    level VARCHAR(50) NOT NULL,
    "user" VARCHAR(255),
    action VARCHAR(255),
    context VARCHAR(255),
    request JSONB,
    response JSONB,
    durationMs FLOAT,
    tags TEXT,
    messageInfo TEXT,
    messageRaw TEXT,
    flagSummary INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_lgs_edd_sdk_his_trace_id ON LGS_EDD_SDK_HIS(traceId);
CREATE INDEX IF NOT EXISTS idx_lgs_edd_sdk_his_time_utc ON LGS_EDD_SDK_HIS(timeUTC);
"""


class PostgresDriver(BaseDriver):
    def __init__(self, db_url: str = "") -> None:
        self.db_url = db_url or os.getenv("DB_URL", "")
        if not self.db_url:
            raise ValueError("DB_URL no esta configurado")
        self.conn = None
        self.migrated = False

    def _ensure_connection(self) -> None:
        if self.conn is not None:
            return
        try:
            import psycopg
        except ImportError as exc:
            raise ImportError(
                "psycopg is required for PostgresDriver. Install with `pip install psycopg`."
            ) from exc
        self.conn = psycopg.connect(self.db_url)
        print("[digital-edd-logger] Conectado a PostgreSQL")

    def _ensure_table(self) -> None:
        if self.migrated:
            return
        self._ensure_connection()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(DDL)
        self.conn.commit()
        self.migrated = True
        print(f"[digital-edd-logger] Tabla {TABLE_NAME} verificada/creada")

    def send(self, record: dict[str, Any]) -> str:
        self._ensure_table()
        assert self.conn is not None
        sql_query = """
        INSERT INTO LGS_EDD_SDK_HIS
            (traceId, timeLocal, timeUTC, service, level, "user", action, context,
             request, response, durationMs, tags, messageInfo, messageRaw, flagSummary)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        now_local = datetime.now()
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        request_json = (
            json.dumps(record.get("request")) if record.get("request") is not None else None
        )
        response_json = (
            json.dumps(record.get("response")) if record.get("response") is not None else None
        )
        tags = record.get("tags")
        tags_str = ",".join(tags) if isinstance(tags, list) and tags else None

        with self.conn.cursor() as cur:
            cur.execute(
                sql_query,
                (
                    record.get("traceId"),
                    now_local,
                    now_utc,
                    record.get("service"),
                    record.get("level"),
                    record.get("user"),
                    record.get("action"),
                    record.get("context"),
                    request_json,
                    response_json,
                    record.get("durationMs"),
                    tags_str,
                    record.get("messageInfo"),
                    record.get("messageRaw"),
                    0,
                ),
            )
            row = cur.fetchone()
        self.conn.commit()
        if not row:
            raise RuntimeError("No id returned while inserting log record")
        return str(row[0])

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None
