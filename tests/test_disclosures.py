"""Tests for point-in-time disclosure storage and structural backtesting."""

import tempfile
import unittest

import pandas as pd

import config
from backtesting import SignalBacktestConfig, SignalBacktester
from data_fetcher.manager import DataFetcher
from disclosures import DisclosureStore, PointInTimeStructuralAnalyzer
from tests.test_backtesting import make_prices


class TestDisclosureStore(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.store = DisclosureStore(f"{self.temporary.name}/disclosures.sqlite3")
        self.holdings = pd.DataFrame({
            'end_date': pd.to_datetime(['2024-12-31', '2025-03-31', '2025-03-31']),
            'ann_date': pd.to_datetime(['2025-02-01', '2025-05-01', '2025-05-01']),
            'holder_name': ['Fund A', 'Fund A', 'Fund B'],
            'hold_ratio': [0.10, 0.20, 0.08],
            'hold_amount': [100, 200, 80],
        })
        self.shareholders = pd.DataFrame({
            'end_date': pd.to_datetime(['2024-12-31', '2025-03-31']),
            'ann_date': pd.to_datetime(['2025-02-01', '2025-05-01']),
            'holder_num': [1000, 800],
        })
        self.store.ingest_frame(
            'TEST', 'institutional_holdings', self.holdings,
            'end_date', 'ann_date', ('holder_name',),
        )
        self.store.ingest_frame(
            'TEST', 'shareholder_count', self.shareholders,
            'end_date', 'ann_date', (),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_as_of_query_excludes_future_publications(self):
        before = self.store.as_of(
            'TEST', 'institutional_holdings', '2025-04-30 23:59:59+08:00'
        )
        after = self.store.as_of(
            'TEST', 'institutional_holdings', '2025-05-01 23:59:59+08:00'
        )

        self.assertEqual(len(before), 1)
        self.assertEqual(set(before['holder_name']), {'Fund A'})
        self.assertEqual(len(after), 3)
        self.assertEqual(self.store.count('TEST', 'institutional_holdings'), 3)

    def test_structural_analysis_uses_only_available_periods(self):
        analyzer = PointInTimeStructuralAnalyzer(config, self.store)
        before = analyzer.analyze('TEST', '2025-04-30 23:59:59+08:00')
        after = analyzer.analyze('TEST', '2025-05-01 23:59:59+08:00')

        self.assertEqual(before, {})
        self.assertIn('NEW_INSTITUTION', after)
        self.assertIn('INSTITUTIONAL_BUY_IN', after)
        self.assertIn('SHAREHOLDER_COUNT_DECREASE', after)

    def test_later_correction_replaces_the_whole_period_snapshot(self):
        correction = pd.DataFrame({
            'end_date': pd.to_datetime(['2025-03-31']),
            'ann_date': pd.to_datetime(['2025-05-10']),
            'holder_name': ['Fund A'],
            'hold_ratio': [0.18],
            'hold_amount': [180],
        })
        self.store.ingest_frame(
            'TEST', 'institutional_holdings', correction,
            'end_date', 'ann_date', ('holder_name',),
        )

        before_correction = self.store.as_of(
            'TEST', 'institutional_holdings', '2025-05-09 23:59:59+08:00'
        )
        after_correction = self.store.as_of(
            'TEST', 'institutional_holdings', '2025-05-10 23:59:59+08:00'
        )

        current_before = before_correction[
            before_correction['end_date'] == '2025-03-31'
        ]
        current_after = after_correction[
            after_correction['end_date'] == '2025-03-31'
        ]
        self.assertEqual(set(current_before['holder_name']), {'Fund A', 'Fund B'})
        self.assertEqual(set(current_after['holder_name']), {'Fund A'})

    def test_backtest_never_emits_structural_signal_before_publication(self):
        backtester = SignalBacktester(
            config,
            DataFetcher(config),
            disclosure_store=self.store,
        )
        settings = SignalBacktestConfig(
            warmup_period=60,
            rebalance_every=1,
            commission_bps=0,
            slippage_bps=0,
            include_structural=True,
        )
        run = backtester.run('TEST', data=make_prices(150), settings=settings)
        structural = run.signals[
            run.signals['signals'].map(lambda names: 'NEW_INSTITUTION' in names)
        ]

        self.assertFalse(structural.empty)
        first_signal = pd.Timestamp(structural.iloc[0]['date'])
        publication = pd.Timestamp('2025-05-01', tz='Asia/Shanghai').tz_convert('UTC')
        self.assertGreaterEqual(first_signal, publication)

    def test_structural_backtest_requires_point_in_time_store(self):
        backtester = SignalBacktester(config, DataFetcher(config))
        settings = SignalBacktestConfig(
            warmup_period=60,
            include_structural=True,
        )
        with self.assertRaisesRegex(ValueError, 'DisclosureStore'):
            backtester.run('TEST', data=make_prices(100), settings=settings)


if __name__ == '__main__':
    unittest.main()
