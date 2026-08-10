"""Configurable notification channels for scheduled scans."""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, Protocol

logger = logging.getLogger(__name__)


class Notifier(Protocol):
    def send(self, payload: Dict[str, Any]) -> None: ...


class ConsoleNotifier:
    def send(self, payload: Dict[str, Any]) -> None:
        logger.warning(
            "ALERT %s %s score=%+.1f signals=%s",
            payload["ticker"],
            payload["rating"],
            payload["score"],
            payload["signal_count"],
        )


class JsonlNotifier:
    def __init__(self, path: str) -> None:
        self.path = Path(path).expanduser().resolve()
        self._lock = threading.Lock()

    def send(self, payload: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


class WebhookNotifier:
    def __init__(self, url: str, timeout: float = 10.0) -> None:
        self.url = url
        self.timeout = timeout

    def send(self, payload: Dict[str, Any]) -> None:
        import requests

        response = requests.post(self.url, json=payload, timeout=self.timeout)
        response.raise_for_status()


class NotificationRouter:
    def __init__(self, notifiers: Iterable[Notifier]) -> None:
        self.notifiers = list(notifiers)

    @classmethod
    def from_config(cls, app_config: Any) -> "NotificationRouter":
        notifiers: list[Notifier] = [ConsoleNotifier()]
        log_path = str(getattr(app_config, "ALERT_LOG_PATH", "")).strip()
        if log_path:
            notifiers.append(JsonlNotifier(log_path))
        webhook = str(getattr(app_config, "ALERT_WEBHOOK_URL", "")).strip()
        if webhook:
            notifiers.append(
                WebhookNotifier(
                    webhook,
                    float(getattr(app_config, "DATA_REQUEST_TIMEOUT", 15)),
                )
            )
        return cls(notifiers)

    def send(self, payload: Dict[str, Any]) -> None:
        for notifier in self.notifiers:
            try:
                notifier.send(payload)
            except Exception as error:
                logger.error(
                    "Alert channel %s failed: %s",
                    type(notifier).__name__,
                    error,
                    exc_info=True,
                )
