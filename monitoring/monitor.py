"""Market-aware end-of-day scheduling and duplicate-safe alerts."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from zoneinfo import ZoneInfo

from .notifiers import NotificationRouter

logger = logging.getLogger(__name__)


class MonitorState:
    """Persistent run/alert keys used to suppress duplicate work."""

    def __init__(self, path: str) -> None:
        self.path = Path(path).expanduser().resolve()
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {"runs": {}, "alerts": []}

    def was_run(self, market: str, date: str) -> bool:
        return self.data.get("runs", {}).get(market) == date

    def mark_run(self, market: str, date: str) -> None:
        self.data.setdefault("runs", {})[market] = date
        self.save()

    def was_alerted(self, key: str) -> bool:
        return key in self.data.get("alerts", [])

    def mark_alerted(self, key: str) -> None:
        alerts = self.data.setdefault("alerts", [])
        alerts.append(key)
        self.data["alerts"] = alerts[-2000:]
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}-",
            suffix=".tmp",
            dir=self.path.parent,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, ensure_ascii=False, indent=2)
            os.replace(temporary_name, self.path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)


class EndOfDayMonitor:
    """Run configured stock pools after each market closes."""

    def __init__(
        self,
        scanner: Any,
        app_config: Any,
        notifier: Optional[Any] = None,
        state: Optional[MonitorState] = None,
    ) -> None:
        self.scanner = scanner
        self.config = app_config
        self.timezone = ZoneInfo(getattr(app_config, "MONITOR_TIMEZONE", "Asia/Shanghai"))
        self.schedules = dict(getattr(app_config, "MONITOR_SCHEDULES", {}))
        self.alert_ratings = set(
            getattr(app_config, "ALERT_RATINGS", ("STRONG_BUY", "STRONG_SELL"))
        )
        self.notifier = notifier or NotificationRouter.from_config(app_config)
        self.state = state or MonitorState(
            getattr(app_config, "MONITOR_STATE_PATH", "./cache/monitor_state.json")
        )

    def due_markets(self, now: Optional[datetime] = None) -> list[str]:
        current = now or datetime.now(self.timezone)
        if current.weekday() >= 5:
            return []
        due = []
        date_key = current.date().isoformat()
        for market, schedule in self.schedules.items():
            hour, minute = (int(value) for value in schedule.split(":"))
            scheduled = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if current >= scheduled and not self.state.was_run(market, date_key):
                due.append(market)
        return due

    def run_market(self, market: str, now: Optional[datetime] = None) -> Dict[str, Any]:
        current = now or datetime.now(self.timezone)
        date_key = current.date().isoformat()
        tickers = self._market_tickers(market)
        if not tickers:
            logger.info("No configured tickers for %s", market)
            self.state.mark_run(market, date_key)
            return {}

        results = self.scanner.scan_batch(
            tickers,
            period=int(getattr(self.config, "MONITOR_PERIOD", 250)),
            analyze_structure=bool(
                getattr(self.config, "MONITOR_ANALYZE_STRUCTURE", False)
            ),
        )
        for ticker, result in results.items():
            if not result.get("success") or result.get("rating") not in self.alert_ratings:
                continue
            alert_key = f"{date_key}:{ticker}:{result['rating']}"
            if self.state.was_alerted(alert_key):
                continue
            payload = {
                "event": "smart_money_signal",
                "market": market,
                "date": date_key,
                "timestamp": current.isoformat(),
                "ticker": ticker,
                "score": float(result.get("score", 0.0)),
                "rating": result["rating"],
                "signal_count": int(result.get("signal_count", 0)),
                "inflow_count": int(result.get("inflow_count", 0)),
                "outflow_count": int(result.get("outflow_count", 0)),
            }
            self.notifier.send(payload)
            self.state.mark_alerted(alert_key)
        self.state.mark_run(market, date_key)
        return results

    def run_once(
        self,
        markets: Optional[Iterable[str]] = None,
        now: Optional[datetime] = None,
    ) -> Dict[str, Dict[str, Any]]:
        return {
            market: self.run_market(market, now=now)
            for market in (markets or self.schedules.keys())
        }

    def serve_forever(self) -> None:
        poll_seconds = max(5.0, float(getattr(self.config, "MONITOR_POLL_SECONDS", 60)))
        logger.info(
            "End-of-day monitor started (%s): %s",
            self.timezone,
            self.schedules,
        )
        while True:
            now = datetime.now(self.timezone)
            for market in self.due_markets(now):
                try:
                    self.run_market(market, now=now)
                except Exception as error:
                    logger.error("Scheduled scan for %s failed: %s", market, error, exc_info=True)
            time.sleep(poll_seconds)

    def _market_tickers(self, market: str) -> list[str]:
        return [
            ticker for ticker in getattr(self.config, "STOCK_POOL", [])
            if self.scanner.data_fetcher._detect_market(ticker) == market
        ]
