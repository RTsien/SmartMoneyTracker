"""
数据获取管理器
统一管理不同数据源的API调用
支持 A股 (Tushare/AkShare)、美股 (yfinance)、港股 (yfinance/Tushare)
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
        self.tushare_token = config.TUSHARE_TOKEN
        self.ts_api = None
        self.akshare_available = False

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

        try:
            if market == 'A_STOCK':
                return self._get_a_stock_daily(ticker, start_date, end_date)
            elif market == 'HK_STOCK':
                return self._get_hk_stock_daily(ticker, start_date, end_date)
            else:  # US_STOCK
                return self._get_us_stock_daily(ticker, start_date, end_date)
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

    def _get_a_stock_daily_akshare(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用 AkShare 获取A股日线数据"""
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
                adjust=""
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

    def _get_us_stock_daily(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取美股日线数据"""
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
        """获取港股日线数据 (使用 yfinance)"""
        return self._get_us_stock_daily(ticker, start_date, end_date)

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
