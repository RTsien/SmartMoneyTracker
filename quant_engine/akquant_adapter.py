"""AKQuant adapter for technical indicator computation."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


class AkQuantIndicatorEngine:
    """Compute SmartMoneyTracker indicators with ``akquant.talib``."""

    REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}
    SUPPORTED_BACKENDS = {"auto", "python", "rust"}

    def __init__(self, backend: str = "rust") -> None:
        backend = backend.strip().lower()
        if backend not in self.SUPPORTED_BACKENDS:
            supported = ", ".join(sorted(self.SUPPORTED_BACKENDS))
            raise ValueError(f"AKQuant backend must be one of: {supported}")

        from akquant import talib

        self.backend = backend
        self.talib = talib

    @staticmethod
    def _series(values: Iterable[float], index: pd.Index) -> pd.Series:
        array = np.asarray(values, dtype=float)
        if array.shape != (len(index),):
            raise ValueError(
                "AKQuant indicator returned an unexpected shape: "
                f"expected {(len(index),)}, got {array.shape}"
            )
        return pd.Series(array, index=index, dtype=float)

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of an OHLCV frame enriched with technical indicators."""
        if df.empty:
            return df.copy()

        missing = self.REQUIRED_COLUMNS.difference(df.columns)
        if missing:
            columns = ", ".join(sorted(missing))
            raise ValueError(f"OHLCV data is missing required columns: {columns}")

        result = df.copy()
        close = result["close"].to_numpy(dtype=float, copy=False)
        high = result["high"].to_numpy(dtype=float, copy=False)
        low = result["low"].to_numpy(dtype=float, copy=False)
        volume = result["volume"].to_numpy(dtype=float, copy=False)

        for period in (5, 10, 20, 60, 120, 250):
            values = self.talib.SMA(
                close,
                timeperiod=period,
                backend=self.backend,
            )
            result[f"ma{period}"] = self._series(values, result.index)

        result["obv"] = self._series(
            self.talib.OBV(close, volume, backend=self.backend),
            result.index,
        )
        result["rsi"] = self._series(
            self.talib.RSI(close, timeperiod=14, backend=self.backend),
            result.index,
        )

        macd, signal, histogram = self.talib.MACD(
            close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9,
            backend=self.backend,
        )
        result["macd"] = self._series(macd, result.index)
        result["macd_signal"] = self._series(signal, result.index)
        result["macd_hist"] = self._series(histogram, result.index)

        result["mfi"] = self._series(
            self.talib.MFI(
                high,
                low,
                close,
                volume,
                timeperiod=14,
                backend=self.backend,
            ),
            result.index,
        )
        return result
