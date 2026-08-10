"""Tests for chronological walk-forward validation."""

import json
import unittest

import pandas as pd

import config
from backtesting import (
    SignalBacktestConfig,
    SignalBacktester,
    WalkForwardConfig,
    WalkForwardValidator,
)
from data_fetcher.manager import DataFetcher
from tests.test_backtesting import make_prices


class TestWalkForwardValidator(unittest.TestCase):
    def setUp(self):
        def trend_evaluator(history: pd.DataFrame):
            rising = history["close"].iloc[-1] >= history["close"].iloc[0]
            return {
                "score": 2 if rising else -2,
                "rating": "BUY" if rising else "SELL",
                "triggered_signals": {"TREND": {}},
            }

        fetcher = DataFetcher(config)
        backtester = SignalBacktester(config, fetcher, evaluator=trend_evaluator)
        self.validator = WalkForwardValidator(backtester)
        self.settings = SignalBacktestConfig(
            warmup_period=60,
            commission_bps=0,
            slippage_bps=0,
        )
        self.validation = WalkForwardConfig(
            train_bars=80,
            test_bars=40,
            step_bars=40,
            rebalance_candidates=(1, 5),
            min_folds=2,
        )

    def test_chronological_folds_and_sensitivity(self):
        prices = make_prices(260)
        run = self.validator.run(
            "TEST",
            data=prices,
            settings=self.settings,
            validation=self.validation,
        )

        self.assertEqual(run.summary["fold_count"], 3)
        self.assertTrue(run.summary["lookahead_safe"])
        self.assertEqual(len(run.sensitivity), 2)
        self.assertEqual(set(run.sensitivity["rebalance_every"]), {1, 5})
        for _, fold in run.folds.iterrows():
            self.assertLess(fold["train_end"], fold["test_start"])
        self.assertEqual(run.folds.iloc[0]["test_start"], prices.iloc[140]["date"].date().isoformat())
        json.dumps(run.to_dict())

    def test_rejects_too_few_folds(self):
        with self.assertRaisesRegex(ValueError, "requires at least"):
            self.validator.run(
                "TEST",
                data=make_prices(180),
                settings=self.settings,
                validation=self.validation,
            )

    def test_rejects_overlapping_test_windows(self):
        with self.assertRaisesRegex(ValueError, "avoid overlap"):
            WalkForwardConfig(train_bars=80, test_bars=40, step_bars=20)


if __name__ == "__main__":
    unittest.main()
