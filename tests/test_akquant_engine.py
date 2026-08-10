"""Tests for the AKQuant technical-indicator adapter."""

import unittest

import numpy as np
import pandas as pd

from quant_engine import AkQuantIndicatorEngine


class TestAkQuantIndicatorEngine(unittest.TestCase):
    def setUp(self):
        size = 320
        sequence = np.arange(size, dtype=float)
        close = 100.0 + sequence * 0.08 + np.sin(sequence / 5.0)
        self.frame = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=size, freq='D'),
            'open': close - 0.2,
            'high': close + 1.0,
            'low': close - 1.0,
            'close': close,
            'volume': 1_000_000.0 + sequence * 1000.0,
            'amount': close * (1_000_000.0 + sequence * 1000.0),
        })
        self.engine = AkQuantIndicatorEngine(backend='rust')

    def test_enrich_adds_expected_indicators(self):
        result = self.engine.enrich(self.frame)

        expected_columns = {
            'ma5', 'ma10', 'ma20', 'ma60', 'ma120', 'ma250',
            'obv', 'rsi', 'macd', 'macd_signal', 'macd_hist', 'mfi'
        }
        self.assertTrue(expected_columns.issubset(result.columns))
        self.assertEqual(len(result), len(self.frame))
        self.assertTrue(np.isfinite(result['ma250'].iloc[-1]))
        self.assertTrue(np.isfinite(result['rsi'].iloc[-1]))
        self.assertTrue(np.isfinite(result['mfi'].iloc[-1]))

    def test_enrich_does_not_mutate_input(self):
        original_columns = list(self.frame.columns)
        self.engine.enrich(self.frame)
        self.assertEqual(list(self.frame.columns), original_columns)

    def test_missing_ohlcv_column_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'volume'):
            self.engine.enrich(self.frame.drop(columns=['volume']))

    def test_empty_frame_is_supported(self):
        result = self.engine.enrich(self.frame.iloc[0:0])
        self.assertTrue(result.empty)


if __name__ == '__main__':
    unittest.main()
