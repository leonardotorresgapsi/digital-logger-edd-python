import json
import os
from typing import Any

from .base import BaseDriver


class PubSubDriver(BaseDriver):
    def __init__(self, project_id: str = "", topic_name: str = "") -> None:
        self.project_id = (
            project_id
            or os.getenv("GOOGLE_CLOUD_PROJECT")
            or os.getenv("GCP_PROJECT")
            or ""
        )
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT no esta configurado")
        self.topic_name = topic_name or os.getenv("PUBSUB_TOPIC_NAME") or "digital-edd-sdk"
        self.publish_enabled = os.getenv("SDKTRACKING_PUBLISH", "true").lower() != "false"
        self.client = None
        self.topic_path = None

    def _ensure_client(self) -> None:
        if self.client is not None:
            return
        try:
            from google.cloud import pubsub_v1
        except ImportError as exc:
            raise ImportError(
                "google-cloud-pubsub is required for PubSubDriver. "
                "Install with `pip install google-cloud-pubsub`."
            ) from exc
        self.client = pubsub_v1.PublisherClient()
        self.topic_path = self.client.topic_path(self.project_id, self.topic_name)
        print(f"[digital-edd-logger] PubSub conectado al topic: {self.topic_name}")

    def send(self, record: dict[str, Any]) -> str:
        if not self.publish_enabled:
            return "publish-disabled"
        self._ensure_client()
        assert self.client is not None
        assert self.topic_path is not None
        data = json.dumps(record).encode("utf-8")
        future = self.client.publish(self.topic_path, data=data)
        return future.result()

    def close(self) -> None:
        self.client = None
        self.topic_path = None
