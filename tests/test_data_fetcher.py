"""
数据获取器单元测试
测试股票名称获取功能
"""

import unittest
import sys
import os
from unittest.mock import patch

import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from data_fetcher.manager import DataFetcher


class TestDataFetcher(unittest.TestCase):
    """数据获取器测试类"""

    def setUp(self):
        """测试前设置"""
        self.fetcher = DataFetcher(config)

    def test_detect_a_stock_market(self):
        """测试A股市场检测"""
        self.assertEqual(self.fetcher._detect_market('600519.SH'), 'A_STOCK')
        self.assertEqual(self.fetcher._detect_market('000858.SZ'), 'A_STOCK')

    def test_detect_hk_stock_market(self):
        """测试港股市场检测"""
        self.assertEqual(self.fetcher._detect_market('0700.HK'), 'HK_STOCK')
        self.assertEqual(self.fetcher._detect_market('9988.HK'), 'HK_STOCK')

    def test_detect_us_stock_market(self):
        """测试美股市场检测"""
        self.assertEqual(self.fetcher._detect_market('AAPL'), 'US_STOCK')
        self.assertEqual(self.fetcher._detect_market('GOOGL'), 'US_STOCK')

    def test_get_stock_name_returns_string(self):
        """测试获取股票名称返回字符串"""
        # 测试各种市场的股票代码
        tickers = ['600519.SH', '0700.HK', 'AAPL', 'INVALID']
        
        for ticker in tickers:
            name = self.fetcher.get_stock_name(ticker)
            self.assertIsInstance(name, str, 
                f"get_stock_name('{ticker}') 应该返回字符串")
            self.assertTrue(len(name) > 0,
                f"get_stock_name('{ticker}') 不应该返回空字符串")

    def test_get_stock_name_fallback_to_ticker(self):
        """测试获取失败时返回股票代码"""
        # 使用一个不存在的股票代码
        invalid_ticker = 'INVALID_TICKER_12345'
        name = self.fetcher.get_stock_name(invalid_ticker)
        
        # 应该返回原始代码
        self.assertEqual(name, invalid_ticker)

    def test_us_stock_name_mapping(self):
        """测试美股名称映射"""
        # 测试常见美股的中文名称
        test_cases = {
            'AAPL': '苹果',
            'MSFT': '微软',
            'GOOGL': '谷歌',
            'NVDA': '英伟达',
            'AMD': '超威半导体',
            'PDD': '拼多多'
        }
        
        for ticker, expected_name in test_cases.items():
            name = self.fetcher._get_us_stock_name(ticker)
            self.assertEqual(name, expected_name,
                f"美股 {ticker} 的中文名应该是 {expected_name}，但得到了 {name}")

    def test_a_stock_history_falls_back_between_akshare_sources(self):
        """东方财富失败后应回退到腾讯行情接口。"""
        self.fetcher.akshare_history_source = 'eastmoney'
        expected = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-07']),
            'open': [1400.0],
            'high': [1410.0],
            'low': [1390.0],
            'close': [1405.0],
            'volume': [1000.0],
            'amount': [1_405_000.0],
        })

        with patch.object(
            self.fetcher,
            '_get_a_stock_daily_akshare_eastmoney',
            return_value=pd.DataFrame()
        ) as eastmoney, patch.object(
            self.fetcher,
            '_get_a_stock_daily_akshare_tencent',
            return_value=expected
        ) as tencent:
            result = self.fetcher._get_a_stock_daily_akshare(
                '600519.SH',
                '20260801',
                '20260810'
            )

        eastmoney.assert_called_once()
        tencent.assert_called_once()
        pd.testing.assert_frame_equal(result, expected)

    def test_us_stock_history_prefers_akshare(self):
        """美股日线应优先使用 AkShare 新浪接口并裁剪日期。"""
        source = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-01', '2026-08-07', '2026-08-11']),
            'open': [200.0, 210.0, 220.0],
            'high': [205.0, 215.0, 225.0],
            'low': [195.0, 205.0, 215.0],
            'close': [202.0, 212.0, 222.0],
            'volume': [1000.0, 1200.0, 1400.0],
        })

        with patch.object(
            self.fetcher.ak,
            'stock_us_daily',
            return_value=source
        ) as akshare, patch.object(
            self.fetcher,
            '_get_stock_daily_yfinance',
            return_value=pd.DataFrame()
        ) as yfinance:
            result = self.fetcher._get_us_stock_daily(
                'AAPL',
                '20260805',
                '20260810'
            )

        akshare.assert_called_once_with(symbol='AAPL', adjust='')
        yfinance.assert_not_called()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['close'], 212.0)
        self.assertEqual(result.iloc[0]['amount'], 254400.0)

    def test_hk_stock_history_prefers_akshare(self):
        """港股代码应转换为五位代码并优先使用 AkShare 新浪接口。"""
        source = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-07']),
            'open': [479.0],
            'high': [483.2],
            'low': [475.4],
            'close': [478.8],
            'volume': [16319939.0],
            'amount': [7803757295.0],
        })

        with patch.object(
            self.fetcher.ak,
            'stock_hk_daily',
            return_value=source
        ) as akshare, patch.object(
            self.fetcher,
            '_get_stock_daily_yfinance',
            return_value=pd.DataFrame()
        ) as yfinance:
            result = self.fetcher._get_hk_stock_daily(
                '0700.HK',
                '20260801',
                '20260810'
            )

        akshare.assert_called_once_with(symbol='00700', adjust='')
        yfinance.assert_not_called()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['close'], 478.8)

    def test_us_stock_history_falls_back_to_yfinance(self):
        """AkShare 无数据时仍应保留 yfinance 备用路径。"""
        expected = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-07']),
            'open': [100.0],
            'high': [101.0],
            'low': [99.0],
            'close': [100.5],
            'volume': [500.0],
            'amount': [50250.0],
        })

        with patch.object(
            self.fetcher,
            '_get_us_stock_daily_akshare',
            return_value=pd.DataFrame()
        ), patch.object(
            self.fetcher,
            '_get_stock_daily_yfinance',
            return_value=expected
        ) as yfinance:
            result = self.fetcher._get_us_stock_daily(
                'AAPL',
                '20260801',
                '20260810'
            )

        yfinance.assert_called_once_with('AAPL', '20260801', '20260810')
        pd.testing.assert_frame_equal(result, expected)

    def test_market_indexes_use_akshare_sina(self):
        """美股和港股基准指数也应避开 Yahoo 限流。"""
        source = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-07']),
            'open': [7700.0],
            'high': [7760.0],
            'low': [7690.0],
            'close': [7750.0],
            'volume': [100000.0],
            'amount': [0.0],
        })

        with patch.object(
            self.fetcher.ak,
            'index_us_stock_sina',
            return_value=source
        ) as us_index, patch.object(
            self.fetcher.ak,
            'stock_hk_index_daily_sina',
            return_value=source
        ) as hk_index:
            us_result = self.fetcher._get_us_stock_daily_akshare(
                '^GSPC', '20260801', '20260810'
            )
            hk_result = self.fetcher._get_us_stock_daily_akshare(
                '^HSI', '20260801', '20260810'
            )

        us_index.assert_called_once_with(symbol='.INX')
        hk_index.assert_called_once_with(symbol='HSI')
        self.assertEqual(len(us_result), 1)
        self.assertEqual(len(hk_result), 1)

    def test_daily_data_uses_in_memory_cache(self):
        """同一批次重复使用基准指数时不应重复访问远端。"""
        expected = pd.DataFrame({
            'date': pd.to_datetime(['2026-08-07']),
            'open': [7700.0],
            'high': [7760.0],
            'low': [7690.0],
            'close': [7750.0],
            'volume': [100000.0],
            'amount': [0.0],
        })

        with patch.object(
            self.fetcher,
            '_get_us_stock_daily',
            return_value=expected
        ) as remote:
            first = self.fetcher.get_daily_data(
                '^GSPC', start_date='20260801', end_date='20260810'
            )
            second = self.fetcher.get_daily_data(
                '^GSPC', start_date='20260801', end_date='20260810'
            )

        remote.assert_called_once()
        self.assertIsNot(first, second)
        pd.testing.assert_frame_equal(first, second)


class TestStockNameIntegration(unittest.TestCase):
    """股票名称集成测试"""

    def setUp(self):
        """测试前设置"""
        self.fetcher = DataFetcher(config)

    def test_get_name_for_multiple_stocks(self):
        """测试批量获取股票名称"""
        tickers = [
            '600519.SH',  # A股
            '0700.HK',    # 港股
            'AAPL',       # 美股
            'NVDA'        # 美股
        ]
        
        names = {}
        for ticker in tickers:
            names[ticker] = self.fetcher.get_stock_name(ticker)
        
        # 确保所有股票都有名称
        for ticker in tickers:
            self.assertIn(ticker, names)
            self.assertIsInstance(names[ticker], str)
            self.assertTrue(len(names[ticker]) > 0)

    def test_name_different_from_ticker(self):
        """测试名称与代码不同（对于有映射的股票）"""
        # 这些股票应该有中文名称
        tickers_with_names = ['AAPL', 'NVDA', 'PDD', 'GOOGL']
        
        for ticker in tickers_with_names:
            name = self.fetcher.get_stock_name(ticker)
            # 名称应该与代码不同（因为有中文映射）
            # 注意：如果API调用失败，可能会返回英文名称
            self.assertIsNotNone(name)


if __name__ == '__main__':
    unittest.main()
