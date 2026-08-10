"""Tests for scheduled market scans and duplicate-safe alerts."""

import tempfile
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock
from zoneinfo import ZoneInfo

from monitoring import EndOfDayMonitor, MonitorState


class TestEndOfDayMonitor(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.config = SimpleNamespace(
            MONITOR_TIMEZONE='Asia/Shanghai',
            MONITOR_SCHEDULES={'A_STOCK': '15:30', 'US_STOCK': '06:30'},
            ALERT_RATINGS=('STRONG_BUY', 'STRONG_SELL'),
            MONITOR_STATE_PATH=f'{self.temporary.name}/state.json',
            MONITOR_PERIOD=250,
            MONITOR_ANALYZE_STRUCTURE=False,
            STOCK_POOL=['600519.SH', 'AAPL'],
        )
        self.scanner = Mock()
        self.scanner.data_fetcher._detect_market.side_effect = (
            lambda ticker: 'A_STOCK' if ticker.endswith('.SH') else 'US_STOCK'
        )
        self.notifier = Mock()
        self.monitor = EndOfDayMonitor(
            self.scanner,
            self.config,
            notifier=self.notifier,
            state=MonitorState(self.config.MONITOR_STATE_PATH),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_due_markets_respects_schedule_and_run_state(self):
        now = datetime(2026, 8, 10, 16, 0, tzinfo=ZoneInfo('Asia/Shanghai'))
        self.assertEqual(self.monitor.due_markets(now), ['A_STOCK', 'US_STOCK'])
        self.monitor.state.mark_run('A_STOCK', '2026-08-10')
        self.assertEqual(self.monitor.due_markets(now), ['US_STOCK'])

    def test_weekends_are_skipped(self):
        saturday = datetime(2026, 8, 8, 18, 0, tzinfo=ZoneInfo('Asia/Shanghai'))
        self.assertEqual(self.monitor.due_markets(saturday), [])

    def test_only_configured_ratings_alert_and_duplicates_are_suppressed(self):
        self.scanner.scan_batch.return_value = {
            '600519.SH': {
                'success': True, 'rating': 'STRONG_BUY', 'score': 7,
                'signal_count': 3, 'inflow_count': 3, 'outflow_count': 0,
            },
            '000001.SH': {
                'success': True, 'rating': 'NEUTRAL', 'score': 0,
                'signal_count': 0,
            },
        }
        now = datetime(2026, 8, 10, 16, 0, tzinfo=ZoneInfo('Asia/Shanghai'))

        self.monitor.run_market('A_STOCK', now)
        self.monitor.run_market('A_STOCK', now)

        self.notifier.send.assert_called_once()
        payload = self.notifier.send.call_args.args[0]
        self.assertEqual(payload['ticker'], '600519.SH')
        self.assertEqual(payload['rating'], 'STRONG_BUY')
        self.assertTrue(self.monitor.state.was_run('A_STOCK', '2026-08-10'))


if __name__ == '__main__':
    unittest.main()
