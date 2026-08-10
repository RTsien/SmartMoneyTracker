"""SQLite-backed point-in-time disclosure snapshots."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


class DisclosureStore:
    """Persist records by publication time so historical queries cannot see the future."""

    def __init__(self, path: str, source_timezone: str = "Asia/Shanghai") -> None:
        self.path = Path(path).expanduser().resolve()
        self.source_timezone = ZoneInfo(source_timezone)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def _initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS disclosure_snapshots (
                    ticker TEXT NOT NULL,
                    dataset TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    record_key TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (
                        ticker, dataset, period_end, published_at, record_key
                    )
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_disclosure_as_of
                ON disclosure_snapshots (ticker, dataset, published_at)
            """)

    def ingest_frame(
        self,
        ticker: str,
        dataset: str,
        frame: pd.DataFrame,
        period_column: str,
        publication_column: Optional[str] = None,
        record_key_columns: Sequence[str] = (),
        observed_at: Optional[Any] = None,
    ) -> int:
        if frame.empty:
            return 0
        if period_column not in frame.columns:
            raise ValueError(f"Missing period column: {period_column}")
        if publication_column and publication_column not in frame.columns:
            raise ValueError(f"Missing publication column: {publication_column}")

        observed = self._utc_iso(observed_at or datetime.now(timezone.utc))
        rows = []
        for row_number, (_, row) in enumerate(frame.iterrows()):
            period_value = row.get(period_column)
            if pd.isna(period_value):
                continue
            period = pd.Timestamp(period_value).date().isoformat()
            published_value = row.get(publication_column) if publication_column else observed
            published = self._utc_iso(published_value if pd.notna(published_value) else observed)
            key_values = [self._json_value(row.get(column)) for column in record_key_columns]
            record_key = json.dumps(key_values or ["record"], ensure_ascii=False)
            payload = {
                str(column): self._json_value(value)
                for column, value in row.items()
            }
            payload[period_column] = period
            rows.append((
                ticker.upper(), dataset, period, published, observed,
                record_key, json.dumps(payload, ensure_ascii=False),
            ))

        with self._connect() as connection:
            connection.executemany("""
                INSERT INTO disclosure_snapshots (
                    ticker, dataset, period_end, published_at,
                    observed_at, record_key, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (
                    ticker, dataset, period_end, published_at, record_key
                ) DO UPDATE SET
                    observed_at = excluded.observed_at,
                    payload = excluded.payload
            """, rows)
        return len(rows)

    def as_of(self, ticker: str, dataset: str, decision_time: Any) -> pd.DataFrame:
        cutoff = self._utc_iso(decision_time)
        with self._connect() as connection:
            stored = connection.execute("""
                SELECT period_end, published_at, record_key, payload
                FROM disclosure_snapshots
                WHERE ticker = ? AND dataset = ? AND published_at <= ?
                ORDER BY published_at ASC, observed_at ASC
            """, (ticker.upper(), dataset, cutoff)).fetchall()
        latest_publication = {}
        for period, published, record_key, payload in stored:
            latest_publication[period] = published
        latest = []
        for period, published, record_key, payload in stored:
            if published != latest_publication[period]:
                continue
            record = json.loads(payload)
            record["published_at"] = published
            latest.append(record)
        return pd.DataFrame(latest)

    def count(self, ticker: Optional[str] = None, dataset: Optional[str] = None) -> int:
        conditions = []
        params = []
        if ticker:
            conditions.append("ticker = ?")
            params.append(ticker.upper())
        if dataset:
            conditions.append("dataset = ?")
            params.append(dataset)
        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        with self._connect() as connection:
            return int(connection.execute(
                f"SELECT COUNT(*) FROM disclosure_snapshots{where}", params
            ).fetchone()[0])

    def _utc_iso(self, value: Any) -> str:
        timestamp = pd.Timestamp(value)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize(self.source_timezone)
        return timestamp.tz_convert("UTC").isoformat()

    @staticmethod
    def _json_value(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (pd.Timestamp, datetime)):
            return value.isoformat()
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, float) and np.isnan(value):
            return None
        if isinstance(value, (bool, int, float, str)):
            return value
        return str(value)
