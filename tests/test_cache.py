"""Tests for persistent market-data caching."""

import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from data_fetcher.cache import DataFrameTTLCache
from data_fetcher.manager import DataFetcher


class TestDataFrameTTLCache(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.cache = DataFrameTTLCache(self.temporary.name)
        self.frame = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-07']),
            'open': [100.0],
            'high': [101.0],
            'low': [99.0],
            'close': [100.5],
            'volume': [1000.0],
            'amount': [100500.0],
        })

    def tearDown(self):
        self.temporary.cleanup()

    def test_round_trip_preserves_frame(self):
        self.cache.set('daily', ('TEST', '20260801', '20260810'), self.frame)
        restored = self.cache.get(
            'daily', ('TEST', '20260801', '20260810'), ttl_seconds=3600
        )
        pd.testing.assert_frame_equal(restored, self.frame)

    def test_expired_entry_is_removed(self):
        key = ('TEST', '20260801', '20260810')
        self.cache.set('daily', key, self.frame)
        time.sleep(0.001)
        restored = self.cache.get('daily', key, ttl_seconds=0)
        self.assertIsNone(restored)
        self.assertEqual(list(Path(self.temporary.name).rglob('*.json.gz')), [])

    def test_corrupt_entry_fails_closed(self):
        key = ('TEST', '20260801', '20260810')
        path = self.cache._path('daily', key)
        path.parent.mkdir(parents=True)
        path.write_text('not gzip', encoding='utf-8')
        self.assertIsNone(self.cache.get('daily', key, ttl_seconds=3600))
        self.assertFalse(path.exists())


class TestDataFetcherPersistentCache(unittest.TestCase):
    def test_second_fetcher_uses_disk_without_provider_call(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = SimpleNamespace(
                A_STOCK_DATA_SOURCE='akshare',
                AKSHARE_HISTORY_SOURCE='tencent',
                DATA_REQUEST_TIMEOUT=15,
                CACHE_ENABLED=True,
                PERSISTENT_CACHE_ENABLED=True,
                CACHE_DIR=directory,
                CACHE_EXPIRY_DAYS=1,
                TUSHARE_TOKEN='',
                QUANT_ENGINE='native',
                AKSHARE_ENABLED=False,
            )
            first = DataFetcher(settings)
            expected = pd.DataFrame({
                'date': pd.to_datetime(['2026-08-07']),
                'open': [100.0], 'high': [101.0], 'low': [99.0],
                'close': [100.5], 'volume': [1000.0], 'amount': [100500.0],
            })
            with patch.object(first, '_get_us_stock_daily', return_value=expected):
                first.get_daily_data('TEST', '20260801', '20260810')

            second = DataFetcher(settings)
            with patch.object(second, '_get_us_stock_daily') as provider:
                restored = second.get_daily_data('TEST', '20260801', '20260810')

            provider.assert_not_called()
            pd.testing.assert_frame_equal(restored, expected)


if __name__ == '__main__':
    unittest.main()
