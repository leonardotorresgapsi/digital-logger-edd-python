from abc import ABC, abstractmethod
from typing import Any


class BaseDriver(ABC):
    @abstractmethod
    def send(self, record: dict[str, Any]) -> str:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
