"""Tests for bounded, provider-aware batch scanning."""

import threading
import time
import unittest
from unittest.mock import patch

from main import SmartMoneyScanner


class TestBatchConcurrency(unittest.TestCase):
    def setUp(self):
        self.scanner = SmartMoneyScanner()
        self.scanner.batch_rate_limits = {
            'A_STOCK': 0.0,
            'US_STOCK': 0.0,
            'HK_STOCK': 0.0,
        }

    def test_batch_is_bounded_and_preserves_input_order(self):
        active = 0
        peak = 0
        lock = threading.Lock()

        def fake_scan(ticker, _period, _structure):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            time.sleep(0.02)
            with lock:
                active -= 1
            return {'ticker': ticker, 'success': True}

        tickers = ['600519.SH', 'AAPL', '0700.HK', 'MSFT']
        with patch.object(self.scanner, 'scan_stock', side_effect=fake_scan):
            results = self.scanner.scan_batch(tickers, max_workers=2)

        self.assertEqual(list(results), tickers)
        self.assertEqual(peak, 2)

    def test_duplicate_tickers_are_scanned_once(self):
        with patch.object(
            self.scanner,
            'scan_stock',
            return_value={'ticker': 'AAPL', 'success': True},
        ) as scan:
            results = self.scanner.scan_batch(['aapl', 'AAPL'], max_workers=2)

        self.assertEqual(list(results), ['AAPL'])
        scan.assert_called_once()

    def test_rate_limit_is_scoped_by_market(self):
        self.scanner.batch_rate_limits['US_STOCK'] = 0.03
        started = []

        def fake_scan(ticker, _period, _structure):
            started.append((ticker, time.monotonic()))
            return {'ticker': ticker, 'success': True}

        with patch.object(self.scanner, 'scan_stock', side_effect=fake_scan):
            self.scanner.scan_batch(['AAPL', 'MSFT'], max_workers=2)

        started.sort(key=lambda item: item[1])
        self.assertGreaterEqual(started[1][1] - started[0][1], 0.025)


if __name__ == '__main__':
    unittest.main()
