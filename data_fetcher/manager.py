"""
数据获取管理器
统一管理不同数据源的API调用
支持 A股、港股和美股的 AkShare 行情，并以 Tushare/yfinance 作为备用
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """统一的数据获取管理器"""

    def __init__(self, config):
        """
        初始化数据获取器

        Args:
            config: 配置模块
        """
        self.config = config
        self.data_source = getattr(config, 'A_STOCK_DATA_SOURCE', 'akshare')
        self.akshare_history_source = getattr(
            config,
            'AKSHARE_HISTORY_SOURCE',
            'tencent'
        ).strip().lower()
        if self.akshare_history_source not in {'tencent', 'eastmoney'}:
            logger.warning(
                "未知的 AKSHARE_HISTORY_SOURCE=%s，回退到 tencent",
                self.akshare_history_source
            )
            self.akshare_history_source = 'tencent'

        self.request_timeout = getattr(config, 'DATA_REQUEST_TIMEOUT', 15)
        self.cache_enabled = getattr(config, 'CACHE_ENABLED', True)
        self._daily_data_cache: Dict[Tuple[str, str, str], pd.DataFrame] = {}
        self.tushare_token = config.TUSHARE_TOKEN
        self.ts_api = None
        self.akshare_available = False
        self.indicator_engine = None
        self.quant_engine_name = getattr(config, 'QUANT_ENGINE', 'akquant').strip().lower()
        self.indicator_backend = getattr(
            config,
            'AKQUANT_TALIB_BACKEND',
            'rust'
        ).strip().lower()

        if self.quant_engine_name == 'akquant':
            try:
                from quant_engine import AkQuantIndicatorEngine

                self.indicator_engine = AkQuantIndicatorEngine(
                    backend=self.indicator_backend
                )
                logger.info(
                    "AkQuant 技术指标引擎初始化成功 (backend=%s)",
                    self.indicator_backend
                )
            except Exception as e:
                logger.warning("AkQuant 初始化失败，回退到原生指标实现: %s", e)
                self.quant_engine_name = 'native'
                self.indicator_backend = 'native'
        elif self.quant_engine_name == 'native':
            self.indicator_backend = 'native'
        else:
            logger.warning(
                "未知的 QUANT_ENGINE=%s，回退到原生指标实现",
                self.quant_engine_name
            )
            self.quant_engine_name = 'native'
            self.indicator_backend = 'native'

        # 初始化 AkShare
        if config.AKSHARE_ENABLED:
            try:
                import akshare as ak
                self.ak = ak
                self.akshare_available = True
                logger.info("AkShare 初始化成功")
            except Exception as e:
                logger.warning(f"AkShare 初始化失败: {e}")

        # 初始化 Tushare
        if self.tushare_token:
            try:
                import tushare as ts
                ts.set_token(self.tushare_token)
                self.ts_api = ts.pro_api()
                logger.info("Tushare 初始化成功")
            except Exception as e:
                logger.warning(f"Tushare 初始化失败: {e}")

    def _detect_market(self, ticker: str) -> str:
        """
        检测股票所属市场

        Args:
            ticker: 股票代码

        Returns:
            市场代码: 'A_STOCK', 'US_STOCK', 'HK_STOCK'
        """
        if ticker.endswith('.SH') or ticker.endswith('.SZ'):
            return 'A_STOCK'
        elif ticker.endswith('.HK'):
            return 'HK_STOCK'
        else:
            # 默认认为是美股
            return 'US_STOCK'

    def get_stock_name(self, ticker: str) -> str:
        """
        获取股票中文名称

        Args:
            ticker: 股票代码

        Returns:
            股票中文名称，如果获取失败返回股票代码本身
        """
        market = self._detect_market(ticker)
        
        try:
            if market == 'A_STOCK':
                # A股：使用 AkShare 或 Tushare
                return self._get_a_stock_name(ticker)
            elif market == 'HK_STOCK':
                # 港股：使用 yfinance 或 AkShare
                return self._get_hk_stock_name(ticker)
            else:
                # 美股：使用 yfinance
                return self._get_us_stock_name(ticker)
        except Exception as e:
            logger.warning(f"获取 {ticker} 名称失败: {e}")
            return ticker

    def _get_a_stock_name(self, ticker: str) -> str:
        """获取A股名称"""
        try:
            if self.akshare_available:
                # 转换代码格式：600519.SH -> 600519
                code = ticker.split('.')[0]
                # 获取股票信息
                stock_info = self.ak.stock_individual_info_em(symbol=code)
                if not stock_info.empty:
                    name = stock_info[stock_info['item'] == '股票简称']['value'].values
                    if len(name) > 0:
                        return name[0]
        except Exception as e:
            logger.debug(f"AkShare 获取A股名称失败: {e}")
        
        # 备用：使用 Tushare
        if self.ts_api:
            try:
                # 转换代码格式：600519.SH -> 600519.SH
                df = self.ts_api.stock_basic(ts_code=ticker, fields='ts_code,name')
                if not df.empty:
                    return df.iloc[0]['name']
            except Exception as e:
                logger.debug(f"Tushare 获取A股名称失败: {e}")
        
        return ticker

    def _get_hk_stock_name(self, ticker: str) -> str:
        """获取港股名称"""
        hk_name_map = {
            '0700.HK': '腾讯控股',
            '9988.HK': '阿里巴巴',
            '9618.HK': '京东集团',
            '3690.HK': '美团',
            '2097.HK': '蜜雪集团',
            '1810.HK': '小米集团',
        }
        if ticker in hk_name_map:
            return hk_name_map[ticker]

        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 尝试获取中文名称
            if 'longName' in info and info['longName']:
                name = info['longName']
                # 如果名称中包含中文，直接返回
                if any('\u4e00' <= c <= '\u9fff' for c in name):
                    return name
                # 否则尝试从 shortName 获取
                if 'shortName' in info and info['shortName']:
                    return info['shortName']
                return name
        except Exception as e:
            logger.debug(f"yfinance 获取港股名称失败: {e}")
        
        # 备用：使用 AkShare
        if self.akshare_available:
            try:
                code = ticker.replace('.HK', '')
                # 去掉前导零
                code = code.lstrip('0')
                df = self.ak.stock_hk_spot_em()
                stock_data = df[df['代码'] == code]
                if not stock_data.empty:
                    return stock_data.iloc[0]['名称']
            except Exception as e:
                logger.debug(f"AkShare 获取港股名称失败: {e}")
        
        return ticker

    def _get_us_stock_name(self, ticker: str) -> str:
        """获取美股名称"""
        # 常用映射不依赖网络，避免 yfinance 限流导致名称回退为代码。
        us_name_map = {
            'AAPL': '苹果',
            'MSFT': '微软',
            'GOOGL': '谷歌',
            'GOOG': '谷歌',
            'AMZN': '亚马逊',
            'TSLA': '特斯拉',
            'META': 'Meta',
            'NVDA': '英伟达',
            'AMD': '超威半导体',
            'NFLX': '奈飞',
            'PDD': '拼多多',
            'BABA': '阿里巴巴',
            'JD': '京东',
            'BIDU': '百度',
            'NIO': '蔚来',
            'XPEV': '小鹏汽车',
            'LI': '理想汽车'
        }

        if ticker in us_name_map:
            return us_name_map[ticker]

        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info

            # 否则返回英文名称
            if 'longName' in info and info['longName']:
                return info['longName']
            elif 'shortName' in info and info['shortName']:
                return info['shortName']
        except Exception as e:
            logger.debug(f"yfinance 获取美股名称失败: {e}")
        
        return ticker

    def get_daily_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: int = 250
    ) -> pd.DataFrame:
        """
        获取日线行情数据

        Args:
            ticker: 股票代码
            start_date: 开始日期 (格式: 'YYYYMMDD' 或 'YYYY-MM-DD')
            end_date: 结束日期 (格式: 'YYYYMMDD' 或 'YYYY-MM-DD')
            period: 如果未指定日期，回看的交易日天数

        Returns:
            DataFrame: 包含 open, high, low, close, volume 等字段
        """
        market = self._detect_market(ticker)

        # 如果未指定日期，使用默认周期
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=period * 2)).strftime('%Y%m%d')

        logger.info(f"获取 {ticker} 日线数据: {start_date} 至 {end_date}")

        cache_key = (ticker, start_date, end_date)
        if self.cache_enabled and cache_key in self._daily_data_cache:
            logger.info("使用内存缓存获取 %s 日线数据", ticker)
            return self._daily_data_cache[cache_key].copy(deep=True)

        try:
            if market == 'A_STOCK':
                df = self._get_a_stock_daily(ticker, start_date, end_date)
            elif market == 'HK_STOCK':
                df = self._get_hk_stock_daily(ticker, start_date, end_date)
            else:  # US_STOCK
                df = self._get_us_stock_daily(ticker, start_date, end_date)

            if self.cache_enabled and not df.empty:
                self._daily_data_cache[cache_key] = df.copy(deep=True)
            return df
        except Exception as e:
            logger.error(f"获取 {ticker} 数据失败: {e}")
            return pd.DataFrame()

    def _get_a_stock_daily(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取A股日线数据"""
        # 优先使用配置的数据源
        if self.data_source == 'akshare' and self.akshare_available:
            df = self._get_a_stock_daily_akshare(ticker, start_date, end_date)
            if not df.empty:
                return df
            # 如果 akshare 失败，尝试 tushare
            logger.warning("AkShare 获取数据失败，尝试使用 Tushare")
        
        # 使用 Tushare
        return self._get_a_stock_daily_tushare(ticker, start_date, end_date)

    def _get_a_stock_daily_akshare(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """按配置的优先级通过 AkShare 获取 A 股日线数据。"""
        providers = {
            'tencent': self._get_a_stock_daily_akshare_tencent,
            'eastmoney': self._get_a_stock_daily_akshare_eastmoney,
        }
        secondary = (
            'eastmoney'
            if self.akshare_history_source == 'tencent'
            else 'tencent'
        )

        for provider_name in (self.akshare_history_source, secondary):
            df = providers[provider_name](ticker, start_date, end_date)
            if not df.empty:
                logger.info(
                    "通过 AkShare %s 获取到 %s 日线数据",
                    provider_name,
                    ticker
                )
                return df
            logger.warning(
                "AkShare %s 未获取到 %s 数据，尝试下一个来源",
                provider_name,
                ticker
            )

        return pd.DataFrame()

    def _get_a_stock_daily_akshare_tencent(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """使用 AkShare 的腾讯行情接口获取 A 股日线数据。"""
        if not self.akshare_available:
            logger.error("AkShare 未初始化")
            return pd.DataFrame()

        try:
            market_prefix = 'sh' if ticker.endswith('.SH') else 'sz'
            symbol = f"{market_prefix}{ticker.split('.')[0]}"
            df = self.ak.stock_zh_a_hist_tx(
                symbol=symbol,
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="",
                timeout=self.request_timeout
            )

            if df.empty:
                return df

            df = df.rename(columns={'turnover': 'turnover_rate'})
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        except Exception as e:
            logger.error("AkShare 腾讯接口获取数据失败: %s", e)
            return pd.DataFrame()

    def _get_a_stock_daily_akshare_eastmoney(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """使用 AkShare 的东方财富接口获取 A 股日线数据。"""
        if not self.akshare_available:
            logger.error("AkShare 未初始化")
            return pd.DataFrame()

        try:
            # 格式化日期为 YYYY-MM-DD
            if len(start_date) == 8:
                start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            if len(end_date) == 8:
                end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

            # AkShare 使用不带后缀的股票代码
            symbol = ticker.split('.')[0]
            
            # 获取历史行情数据
            df = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="",
                timeout=self.request_timeout
            )

            if df.empty:
                return df

            # 标准化列名 (AkShare 返回中文列名)
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            })

            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            # 确保数值类型
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]

        except Exception as e:
            logger.error(f"AkShare 获取数据失败: {e}")
            return pd.DataFrame()

    def _get_a_stock_daily_tushare(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用 Tushare 获取A股日线数据"""
        if not self.ts_api:
            logger.error("Tushare API 未初始化")
            return pd.DataFrame()

        # 格式化日期
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')

        df = self.ts_api.daily(
            ts_code=ticker,
            start_date=start_date,
            end_date=end_date
        )

        if df.empty:
            return df

        # 标准化列名
        df = df.rename(columns={
            'trade_date': 'date',
            'vol': 'volume',
            'amount': 'amount'
        })

        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # 确保数值类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]

    def _normalize_akshare_history(
        self,
        df: pd.DataFrame,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """统一 AkShare 港股/美股日线字段并裁剪日期范围。"""
        if df.empty:
            return df

        df = df.copy().rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount',
        })
        required = {'date', 'open', 'high', 'low', 'close', 'volume'}
        if not required.issubset(df.columns):
            logger.warning("AkShare 行情字段不完整: %s", sorted(df.columns))
            return pd.DataFrame()

        df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
        for col in ('open', 'high', 'low', 'close', 'volume'):
            df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        else:
            df['amount'] = df['close'] * df['volume']

        date_format = '%Y%m%d' if len(start_date.replace('-', '')) == 8 else None
        start = pd.to_datetime(start_date.replace('-', ''), format=date_format)
        end = pd.to_datetime(end_date.replace('-', ''), format=date_format)
        df = df[(df['date'] >= start) & (df['date'] <= end)]
        df = df.dropna(subset=['date', 'open', 'high', 'low', 'close', 'volume'])
        df = df.sort_values('date').reset_index(drop=True)
        return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]

    def _get_us_stock_daily_akshare(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """通过 AkShare 新浪接口获取美股日线数据。"""
        if not self.akshare_available:
            return pd.DataFrame()

        try:
            us_indexes = {
                '^GSPC': '.INX',
                '^IXIC': '.IXIC',
                '^DJI': '.DJI',
            }
            if ticker == '^HSI':
                df = self.ak.stock_hk_index_daily_sina(symbol='HSI')
            elif ticker in us_indexes:
                df = self.ak.index_us_stock_sina(symbol=us_indexes[ticker])
            else:
                df = self.ak.stock_us_daily(symbol=ticker, adjust='')
            return self._normalize_akshare_history(df, start_date, end_date)
        except Exception as e:
            logger.warning("AkShare 新浪接口获取美股 %s 失败: %s", ticker, e)
            return pd.DataFrame()

    def _get_hk_stock_daily_akshare(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """通过 AkShare 新浪接口获取港股日线数据。"""
        if not self.akshare_available:
            return pd.DataFrame()

        try:
            symbol = ticker.removesuffix('.HK').zfill(5)
            df = self.ak.stock_hk_daily(symbol=symbol, adjust='')
            return self._normalize_akshare_history(df, start_date, end_date)
        except Exception as e:
            logger.warning("AkShare 新浪接口获取港股 %s 失败: %s", ticker, e)
            return pd.DataFrame()

    def _get_us_stock_daily(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取美股日线数据，优先 AkShare 新浪，失败后回退 yfinance。"""
        df = self._get_us_stock_daily_akshare(ticker, start_date, end_date)
        if not df.empty:
            logger.info("通过 AkShare 新浪获取到 %s 日线数据", ticker)
            return df

        logger.warning("AkShare 未获取到 %s 数据，尝试使用 yfinance", ticker)
        return self._get_stock_daily_yfinance(ticker, start_date, end_date)

    def _get_stock_daily_yfinance(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """通过 yfinance 获取美股或港股日线数据。"""
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance 未安装，请运行: pip install yfinance")
            return pd.DataFrame()

        # 格式化日期为 YYYY-MM-DD
        if len(start_date) == 8:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        if len(end_date) == 8:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return df

        # 标准化列名
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # 计算成交额 (美股为美元)
        df['amount'] = df['close'] * df['volume']

        return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]

    def _get_hk_stock_daily(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取港股日线数据，优先 AkShare 新浪，失败后回退 yfinance。"""
        df = self._get_hk_stock_daily_akshare(ticker, start_date, end_date)
        if not df.empty:
            logger.info("通过 AkShare 新浪获取到 %s 日线数据", ticker)
            return df

        logger.warning("AkShare 未获取到 %s 数据，尝试使用 yfinance", ticker)
        return self._get_stock_daily_yfinance(ticker, start_date, end_date)

    def get_institutional_holdings(
        self,
        ticker: str,
        report_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取机构持股数据

        Args:
            ticker: 股票代码
            report_date: 报告期 (格式: 'YYYYMMDD')

        Returns:
            DataFrame: 机构持股明细
        """
        market = self._detect_market(ticker)

        try:
            if market == 'A_STOCK':
                return self._get_a_stock_holders(ticker, report_date)
            elif market == 'US_STOCK':
                return self._get_us_stock_holders(ticker)
            else:  # HK_STOCK
                return self._get_hk_stock_holders(ticker)
        except Exception as e:
            logger.error(f"获取 {ticker} 机构持股数据失败: {e}")
            return pd.DataFrame()

    def _get_a_stock_holders(self, ticker: str, report_date: Optional[str]) -> pd.DataFrame:
        """获取A股前十大流通股东"""
        # 优先使用配置的数据源
        if self.data_source == 'akshare' and self.akshare_available:
            df = self._get_a_stock_holders_akshare(ticker, report_date)
            if not df.empty:
                return df
            logger.warning("AkShare 获取机构持股数据失败，尝试使用 Tushare")
        
        # 使用 Tushare
        return self._get_a_stock_holders_tushare(ticker, report_date)

    def _get_a_stock_holders_akshare(self, ticker: str, report_date: Optional[str]) -> pd.DataFrame:
        """使用 AkShare 获取A股前十大流通股东"""
        if not self.akshare_available:
            logger.error("AkShare 未初始化")
            return pd.DataFrame()

        try:
            # AkShare 使用不带后缀的股票代码
            symbol = ticker.split('.')[0]
            
            # 获取十大流通股东数据
            df = self.ak.stock_gdfx_free_top_10_em(symbol=symbol)

            if df.empty:
                return df

            # 标准化列名以匹配 Tushare 格式
            # AkShare 返回的列名可能不同，需要根据实际情况调整
            return df

        except Exception as e:
            logger.error(f"AkShare 获取机构持股数据失败: {e}")
            return pd.DataFrame()

    def _get_a_stock_holders_tushare(self, ticker: str, report_date: Optional[str]) -> pd.DataFrame:
        """使用 Tushare 获取A股前十大流通股东"""
        if not self.ts_api:
            logger.error("Tushare API 未初始化")
            return pd.DataFrame()

        if not report_date:
            # 使用最新报告期
            report_date = datetime.now().strftime('%Y%m%d')

        df = self.ts_api.top10_floatholders(
            ts_code=ticker,
            end_date=report_date
        )

        return df

    def _get_us_stock_holders(self, ticker: str) -> pd.DataFrame:
        """
        获取美股机构持股数据
        
        数据源选项：
        1. yfinance - 提供主要机构持股者信息
        2. SEC EDGAR API - 13F 报告（需要额外实现）
        
        Args:
            ticker: 股票代码
            
        Returns:
            DataFrame: 机构持股数据
        """
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance 未安装")
            return pd.DataFrame()
        
        try:
            stock = yf.Ticker(ticker)
            # 获取主要持股者信息
            holders = stock.institutional_holders
            
            if holders is None or holders.empty:
                logger.warning(f"{ticker} 无机构持股数据")
                return pd.DataFrame()
            
            # 标准化列名以便后续分析
            holders = holders.rename(columns={
                'Holder': 'holder_name',
                'Shares': 'shares',
                'Date Reported': 'report_date',
                'Value': 'value',
                '% Out': 'pct_held'
            })
            
            return holders
            
        except Exception as e:
            logger.error(f"获取美股 {ticker} 机构持股数据失败: {e}")
            return pd.DataFrame()
    
    def _get_hk_stock_holders(self, ticker: str) -> pd.DataFrame:
        """
        获取港股机构持股数据
        
        数据源选项：
        1. AkShare - 提供港股通持股数据（优先）
        2. yfinance - 提供机构持股者信息（备选）
        3. 披露易 API（需要额外实现）
        
        Args:
            ticker: 股票代码（如 0700.HK）
            
        Returns:
            DataFrame: 机构持股数据
        """
        # 方案1：尝试使用 AkShare 获取港股通数据
        if self.akshare_available:
            try:
                # 提取股票代码（去掉 .HK 后缀）
                symbol = ticker.split('.')[0]
                
                # 获取港股通持股数据（南向资金）
                df = self.ak.stock_hk_ggt_components_em()
                
                if not df.empty:
                    # 筛选特定股票
                    df = df[df['代码'] == symbol]
                    
                    if not df.empty:
                        logger.info(f"通过 AkShare 获取到 {ticker} 港股通持股数据")
                        return df
                
                logger.debug(f"{ticker} 不在港股通标的中，尝试使用 yfinance")
                
            except Exception as e:
                logger.debug(f"AkShare 获取港股数据失败: {e}，尝试使用 yfinance")
        
        # 方案2：使用 yfinance 作为备选
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            holders = stock.institutional_holders
            
            if holders is None or holders.empty:
                logger.warning(f"{ticker} 无机构持股数据")
                return pd.DataFrame()
            
            # 标准化列名
            holders = holders.rename(columns={
                'Holder': 'holder_name',
                'Shares': 'shares',
                'Date Reported': 'report_date',
                'Value': 'value',
                '% Out': 'pct_held'
            })
            
            logger.info(f"通过 yfinance 获取到 {ticker} 机构持股数据")
            return holders
            
        except Exception as e:
            logger.error(f"获取港股 {ticker} 机构持股数据失败: {e}")
            return pd.DataFrame()

    def get_shareholder_count(self, ticker: str) -> pd.DataFrame:
        """
        获取股东户数数据

        Args:
            ticker: 股票代码

        Returns:
            DataFrame: 股东户数历史数据
        """
        market = self._detect_market(ticker)

        if market != 'A_STOCK':
            logger.warning(f"{ticker} 不是A股，暂不支持股东户数查询")
            return pd.DataFrame()

        # 优先使用配置的数据源
        if self.data_source == 'akshare' and self.akshare_available:
            df = self._get_shareholder_count_akshare(ticker)
            if not df.empty:
                return df
            logger.warning("AkShare 获取股东户数失败，尝试使用 Tushare")
        
        # 使用 Tushare
        return self._get_shareholder_count_tushare(ticker)

    def _get_shareholder_count_akshare(self, ticker: str) -> pd.DataFrame:
        """使用 AkShare 获取股东户数"""
        if not self.akshare_available:
            logger.error("AkShare 未初始化")
            return pd.DataFrame()

        try:
            # AkShare 使用不带后缀的股票代码
            symbol = ticker.split('.')[0]
            
            # 获取股东户数数据
            df = self.ak.stock_zh_a_gdhs(symbol=symbol)

            if df.empty:
                return df

            # 标准化列名以匹配 Tushare 格式
            # 需要根据 AkShare 实际返回的列名进行调整
            return df

        except Exception as e:
            logger.error(f"AkShare 获取股东户数失败: {e}")
            return pd.DataFrame()

    def _get_shareholder_count_tushare(self, ticker: str) -> pd.DataFrame:
        """使用 Tushare 获取股东户数"""
        if not self.ts_api:
            logger.error("Tushare API 未初始化")
            return pd.DataFrame()

        try:
            df = self.ts_api.stk_holdernumber(ts_code=ticker)
            return df
        except Exception as e:
            logger.error(f"获取 {ticker} 股东户数失败: {e}")
            return pd.DataFrame()

    def get_northbound_holdings(self, ticker: str) -> pd.DataFrame:
        """
        获取北向资金持股数据 (A股)

        Args:
            ticker: 股票代码

        Returns:
            DataFrame: 北向资金持股明细
        """
        market = self._detect_market(ticker)

        if market != 'A_STOCK':
            logger.warning(f"{ticker} 不是A股，无北向资金数据")
            return pd.DataFrame()

        # 优先使用配置的数据源
        if self.data_source == 'akshare' and self.akshare_available:
            df = self._get_northbound_holdings_akshare(ticker)
            if not df.empty:
                return df
            logger.warning("AkShare 获取北向资金数据失败，尝试使用 Tushare")
        
        # 使用 Tushare
        return self._get_northbound_holdings_tushare(ticker)

    def _get_northbound_holdings_akshare(self, ticker: str) -> pd.DataFrame:
        """使用 AkShare 获取北向资金持股数据"""
        if not self.akshare_available:
            logger.error("AkShare 未初始化")
            return pd.DataFrame()

        try:
            # AkShare 使用不带后缀的股票代码
            symbol = ticker.split('.')[0]
            
            # 获取北向资金持股数据
            df = self.ak.stock_em_hsgt_stock_statistics(symbol=symbol)

            if df.empty:
                return df

            return df

        except Exception as e:
            logger.error(f"AkShare 获取北向资金数据失败: {e}")
            return pd.DataFrame()

    def _get_northbound_holdings_tushare(self, ticker: str) -> pd.DataFrame:
        """使用 Tushare 获取北向资金持股数据"""
        if not self.ts_api:
            logger.error("Tushare API 未初始化")
            return pd.DataFrame()

        try:
            df = self.ts_api.hk_hold(ts_code=ticker)
            return df
        except Exception as e:
            logger.error(f"获取 {ticker} 北向资金数据失败: {e}")
            return pd.DataFrame()

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算常用技术指标

        Args:
            df: 包含 OHLCV 数据的 DataFrame

        Returns:
            DataFrame: 添加了技术指标的 DataFrame
        """
        if df.empty:
            return df

        df = df.copy()

        if self.indicator_engine is not None:
            try:
                return self.indicator_engine.enrich(df)
            except Exception as e:
                logger.warning(
                    "AkQuant 指标计算失败，回退到原生实现: %s",
                    e
                )

        # 计算移动平均线
        for period in [5, 10, 20, 60, 120, 250]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()

        # 计算 OBV (能量潮)
        df['obv'] = self._calculate_obv(df)

        # 计算 RSI
        df['rsi'] = self._calculate_rsi(df['close'], period=14)

        # 计算 MACD
        macd_data = self._calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']

        # 计算 MFI (资金流量指标)
        df['mfi'] = self._calculate_mfi(df, period=14)

        return df

    @staticmethod
    def _calculate_obv(df: pd.DataFrame) -> pd.Series:
        """计算 OBV 指标"""
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df['volume'].iloc[0]

        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """计算 RSI 指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def _calculate_macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, pd.Series]:
        """计算 MACD 指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line

        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def _calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算 MFI (资金流量指标)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']

        # 区分正负资金流
        positive_flow = pd.Series(0.0, index=df.index)
        negative_flow = pd.Series(0.0, index=df.index)

        for i in range(1, len(df)):
            if typical_price.iloc[i] > typical_price.iloc[i - 1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            elif typical_price.iloc[i] < typical_price.iloc[i - 1]:
                negative_flow.iloc[i] = money_flow.iloc[i]

        # 计算资金流比率
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()

        mfi_ratio = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + mfi_ratio))

        return mfi
