from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"


@dataclass
class RequestInfo:
    method: str
    path: str
    headers: dict[str, str] | None = None
    body: Any = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "method": self.method,
            "path": self.path,
            "headers": self.headers or {},
        }
        if self.body is not None:
            data["body"] = self.body
        return data


@dataclass
class ResponseInfo:
    status_code: int
    headers: dict[str, str] | None = None
    body: Any = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "statusCode": self.status_code,
            "headers": self.headers or {},
        }
        if self.body is not None:
            data["body"] = self.body
        return data


@dataclass
class TraceLog:
    trace_id: str = ""
    timestamp: str = ""
    service: str = ""
    level: LogLevel | str = LogLevel.INFO
    action: str = ""
    context: str = ""
    request: RequestInfo | None = None
    response: ResponseInfo | None = None
    message_info: str = ""
    message_raw: str = ""
    duration_ms: float = 0.0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        level = self.level.value if isinstance(self.level, LogLevel) else self.level
        data: dict[str, Any] = {
            "traceId": self.trace_id,
            "timestamp": self.timestamp,
            "service": self.service,
            "level": level,
            "action": self.action,
        }
        if self.context:
            data["context"] = self.context
        if self.request is not None:
            data["request"] = self.request.to_dict()
        if self.response is not None:
            data["response"] = self.response.to_dict()
        if self.message_info:
            data["messageInfo"] = self.message_info
        if self.message_raw:
            data["messageRaw"] = self.message_raw
        if self.duration_ms:
            data["durationMs"] = self.duration_ms
        if self.tags:
            data["tags"] = self.tags
        return data
