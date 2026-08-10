"""Tests for the point-in-time AkQuant backtesting layer."""

import json
import unittest

import numpy as np
import pandas as pd

import config
from backtesting import SignalBacktestConfig, SignalBacktester
from data_fetcher.manager import DataFetcher


def make_prices(size: int = 100) -> pd.DataFrame:
    sequence = np.arange(size, dtype=float)
    close = 100.0 + sequence * 0.2
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=size, freq="B"),
        "open": close - 0.1,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": 1_000_000.0 + sequence,
    })


class TestSignalBacktester(unittest.TestCase):
    def setUp(self):
        self.fetcher = DataFetcher(config)
        self.settings = SignalBacktestConfig(
            warmup_period=60,
            commission_bps=0,
            slippage_bps=0,
        )

    @staticmethod
    def trend_evaluator(history: pd.DataFrame):
        rating = "BUY" if history["close"].iloc[-1] >= history["close"].iloc[0] else "SELL"
        return {"score": 2 if rating == "BUY" else -2, "rating": rating,
                "triggered_signals": {"TREND": {}}}

    def test_orders_fill_on_next_bar_open(self):
        prices = make_prices()
        run = SignalBacktester(
            config, self.fetcher, evaluator=self.trend_evaluator
        ).run("TEST", data=prices, settings=self.settings)

        self.assertGreaterEqual(len(run.orders), 1)
        first_order = run.orders.iloc[0]
        self.assertEqual(first_order["side"], "buy")
        self.assertAlmostEqual(first_order["avg_price"], prices.iloc[60]["open"])
        self.assertEqual(run.summary["fill_policy"], "next_open")
        self.assertTrue(run.summary["lookahead_safe"])

    def test_future_changes_do_not_change_prior_signals(self):
        prices = make_prices(110)
        changed = prices.copy()
        changed.loc[90:, ["open", "high", "low", "close"]] *= 5
        backtester = SignalBacktester(
            config, self.fetcher, evaluator=self.trend_evaluator
        )

        first = backtester.run("TEST", data=prices, settings=self.settings)
        second = backtester.run("TEST", data=changed, settings=self.settings)
        cutoff = pd.Timestamp(prices.loc[89, "date"], tz="UTC")
        first_signals = first.signals[pd.to_datetime(first.signals["date"]) <= cutoff]
        second_signals = second.signals[pd.to_datetime(second.signals["date"]) <= cutoff]

        self.assertEqual(first_signals["score"].tolist(), second_signals["score"].tolist())
        self.assertEqual(first_signals["rating"].tolist(), second_signals["rating"].tolist())

    def test_rejects_insufficient_data(self):
        backtester = SignalBacktester(
            config, self.fetcher, evaluator=self.trend_evaluator
        )
        with self.assertRaisesRegex(ValueError, "At least 62"):
            backtester.run("TEST", data=make_prices(61), settings=self.settings)

    def test_result_is_json_serializable(self):
        run = SignalBacktester(
            config, self.fetcher, evaluator=self.trend_evaluator
        ).run("TEST", data=make_prices(), settings=self.settings)
        payload = run.to_dict()

        self.assertEqual(payload["ticker"], "TEST")
        self.assertIn("summary", payload)
        self.assertGreater(len(payload["signals"]), 0)
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
