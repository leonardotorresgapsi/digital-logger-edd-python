import json
from typing import Any

from .base import BaseDriver


class ConsoleDriver(BaseDriver):
    def send(self, record: dict[str, Any]) -> str:
        print(json.dumps(record, indent=2))
        return "console-log"

    def close(self) -> None:
        return None
