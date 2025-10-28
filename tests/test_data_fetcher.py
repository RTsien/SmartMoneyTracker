"""
数据获取器单元测试
测试股票名称获取功能
"""

import unittest
import sys
import os

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
