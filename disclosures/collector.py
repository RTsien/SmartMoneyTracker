"""Normalize provider responses into point-in-time disclosure snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from .store import DisclosureStore


class DisclosureSnapshotCollector:
    def __init__(self, data_fetcher: Any, store: DisclosureStore) -> None:
        self.data_fetcher = data_fetcher
        self.store = store

    def collect(self, ticker: str, observed_at: Optional[Any] = None) -> Dict[str, int]:
        observed = observed_at or datetime.now(timezone.utc)
        holdings = self._normalize_holdings(
            self.data_fetcher.get_institutional_holdings(ticker)
        )
        shareholder_count = self._normalize_shareholder_count(
            self.data_fetcher.get_shareholder_count(ticker)
        )
        return {
            "institutional_holdings": self._ingest(
                ticker, "institutional_holdings", holdings,
                "end_date", "ann_date", ("holder_name",), observed,
            ),
            "shareholder_count": self._ingest(
                ticker, "shareholder_count", shareholder_count,
                "end_date", "ann_date", (), observed,
            ),
        }

    def _ingest(
        self,
        ticker: str,
        dataset: str,
        frame: pd.DataFrame,
        period_column: str,
        publication_column: str,
        keys: Iterable[str],
        observed_at: Any,
    ) -> int:
        if frame.empty:
            return 0
        publication = publication_column if publication_column in frame else None
        return self.store.ingest_frame(
            ticker=ticker,
            dataset=dataset,
            frame=frame,
            period_column=period_column,
            publication_column=publication,
            record_key_columns=tuple(keys),
            observed_at=observed_at,
        )

    @staticmethod
    def _rename_first(frame: pd.DataFrame, target: str, candidates: Iterable[str]) -> None:
        if target in frame.columns:
            return
        for candidate in candidates:
            if candidate in frame.columns:
                frame.rename(columns={candidate: target}, inplace=True)
                return

    @classmethod
    def _normalize_holdings(cls, source: pd.DataFrame) -> pd.DataFrame:
        if source is None or source.empty:
            return pd.DataFrame()
        frame = source.copy()
        cls._rename_first(frame, "end_date", ("report_date", "截止日期", "报告期"))
        cls._rename_first(frame, "ann_date", ("公告日期", "发布日期"))
        cls._rename_first(frame, "holder_name", ("Holder", "股东名称", "机构名称"))
        cls._rename_first(frame, "hold_amount", ("shares", "Shares", "持股数量"))
        cls._rename_first(frame, "hold_ratio", ("pct_held", "% Out", "持股比例"))
        required = {"end_date", "holder_name"}
        return frame if required.issubset(frame.columns) else pd.DataFrame()

    @classmethod
    def _normalize_shareholder_count(cls, source: pd.DataFrame) -> pd.DataFrame:
        if source is None or source.empty:
            return pd.DataFrame()
        frame = source.copy()
        cls._rename_first(
            frame, "end_date",
            ("股东户数统计截止日", "截止日期", "报告期"),
        )
        cls._rename_first(frame, "ann_date", ("公告日期", "发布日期"))
        cls._rename_first(
            frame, "holder_num",
            ("股东户数-本次", "本次股东户数", "股东户数"),
        )
        required = {"end_date", "holder_num"}
        return frame if required.issubset(frame.columns) else pd.DataFrame()
