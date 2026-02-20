from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .drivers import BaseDriver, ConsoleDriver, PostgresDriver, PubSubDriver
from .models import LogLevel, RequestInfo, ResponseInfo, TraceLog
from .utils import get_mexico_time_as_utc, is_production, log_error, log_warning


@dataclass
class LogOptions:
    trace_id: str = ""
    level: str = ""
    action: str = ""
    context: str = ""
    method: str = ""
    path: str = ""
    request_headers: dict[str, str] = field(default_factory=dict)
    request_body: Any = None
    status_code: int = 0
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: Any = None
    message_info: str = ""
    message_raw: str = ""
    duration_ms: float = 0.0
    tags: list[str] = field(default_factory=list)
    service: str = ""


class EddLogger:
    def __init__(self, service: str = "") -> None:
        self.service = service or "digital-edd"
        self.driver: BaseDriver | None = None

    def _get_driver(self) -> BaseDriver:
        if self.driver is None:
            self.driver = self._create_driver()
        return self.driver

    def _create_driver(self) -> BaseDriver:
        if is_production():
            try:
                return PubSubDriver("", "")
            except Exception as err:  # pragma: no cover - runtime fallback path
                log_error(f"No se pudo inicializar PubSubDriver: {err}")
                log_warning("Usando ConsoleDriver como fallback")
                return ConsoleDriver()
        try:
            return PostgresDriver("")
        except Exception as err:  # pragma: no cover - runtime fallback path
            log_error(f"No se pudo inicializar PostgresDriver: {err}")
            log_warning("Usando ConsoleDriver como fallback")
            return ConsoleDriver()

    def set_driver(self, driver: BaseDriver) -> None:
        self.driver = driver

    def send_trace_log(self, trace: TraceLog) -> str:
        return self._get_driver().send(trace.to_dict())

    def log(self, opts: LogOptions | dict[str, Any] | None = None) -> str:
        if opts is None:
            opts = LogOptions()
        elif isinstance(opts, dict):
            opts = LogOptions(**opts)

        level = opts.level or LogLevel.INFO.value
        request = None
        if opts.method and opts.path:
            request = RequestInfo(
                method=opts.method,
                path=opts.path,
                headers=opts.request_headers,
                body=opts.request_body,
            )

        response = None
        if opts.status_code != 0:
            response = ResponseInfo(
                status_code=opts.status_code,
                headers=opts.response_headers,
                body=opts.response_body,
            )

        service = opts.service or self.service
        trace = TraceLog(
            trace_id=opts.trace_id,
            timestamp=get_mexico_time_as_utc(),
            service=service,
            level=level,
            action=opts.action,
            context=opts.context,
            request=request,
            response=response,
            message_info=opts.message_info,
            message_raw=opts.message_raw,
            duration_ms=opts.duration_ms,
            tags=opts.tags,
        )
        log_warning("SendTraceLog")
        return self.send_trace_log(trace)

    def close(self) -> None:
        if self.driver is not None:
            self.driver.close()


def NewLogger(service: str = "") -> EddLogger:
    return EddLogger(service=service)
