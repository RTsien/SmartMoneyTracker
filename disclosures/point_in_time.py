"""Structural-signal adapter that only exposes disclosures known as of a date."""

from __future__ import annotations

from typing import Any, Dict

from analysis.disclosure_signals import StructuralSignals

from .store import DisclosureStore


class _PointInTimeFetcher:
    def __init__(self, store: DisclosureStore, as_of: Any) -> None:
        self.store = store
        self.as_of = as_of

    def get_institutional_holdings(self, ticker: str):
        return self.store.as_of(ticker, "institutional_holdings", self.as_of)

    def get_shareholder_count(self, ticker: str):
        return self.store.as_of(ticker, "shareholder_count", self.as_of)


class PointInTimeStructuralAnalyzer:
    def __init__(self, app_config: Any, store: DisclosureStore) -> None:
        self.app_config = app_config
        self.store = store

    def analyze(self, ticker: str, as_of: Any) -> Dict[str, Any]:
        fetcher = _PointInTimeFetcher(self.store, as_of)
        return StructuralSignals(self.app_config, fetcher).analyze(ticker)
