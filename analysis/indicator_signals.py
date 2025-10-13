"""
技术指标信号分析模块
识别 OBV、MFI、RSI、MACD 等指标的看跌背离
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class IndicatorSignals:
    """技术指标信号分析器"""

    def __init__(self, config):
        """
        初始化技术指标分析器

        Args:
            config: 配置模块
        """
        self.config = config
        self.params = config.INDICATOR_PARAMS

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        执行技术指标分析

        Args:
            df: 包含价格和技术指标的 DataFrame

        Returns:
            包含所有信号的字典
        """
        if df.empty:
            logger.warning("数据为空，无法进行技术指标分析")
            return {}

        signals = {}

        # 1. OBV 看跌背离
        obv_signal = self.detect_obv_bearish_divergence(df)
        if obv_signal['detected']:
            signals['OBV_DIVERGENCE'] = obv_signal

        # 2. MFI 看跌背离
        mfi_signal = self.detect_mfi_bearish_divergence(df)
        if mfi_signal['detected']:
            signals['MFI_DIVERGENCE'] = mfi_signal

        # 3. RSI 看跌背离
        rsi_signal = self.detect_rsi_bearish_divergence(df)
        if rsi_signal['detected']:
            signals['RSI_DIVERGENCE'] = rsi_signal

        # 4. MACD 看跌背离
        macd_signal = self.detect_macd_bearish_divergence(df)
        if macd_signal['detected']:
            signals['MACD_DIVERGENCE'] = macd_signal

        return signals

    def detect_obv_bearish_divergence(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测 OBV 看跌背离

        逻辑:
        价格创新高 (Higher High)，但 OBV 未能创新高 (Lower High)

        Args:
            df: 包含 close 和 obv 的 DataFrame

        Returns:
            信号字典
        """
        lookback = self.params['obv_lookback']

        if 'obv' not in df.columns or len(df) < lookback:
            return {'detected': False}

        # 寻找价格和 OBV 的局部高点
        price_peaks = self._find_peaks(df['close'].tail(lookback))
        obv_peaks = self._find_peaks(df['obv'].tail(lookback))

        # 检查背离
        divergence = self._check_bearish_divergence(
            df.tail(lookback),
            'close',
            'obv',
            price_peaks,
            obv_peaks
        )

        if divergence:
            return {
                'detected': True,
                'signal_date': df['date'].iloc[-1] if 'date' in df.columns else None,
                'description': f"OBV看跌背离: 价格创新高但OBV未能同步",
                'severity': 'high',
                'details': divergence
            }

        return {'detected': False}

    def detect_mfi_bearish_divergence(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测 MFI 看跌背离

        Args:
            df: 包含 close 和 mfi 的 DataFrame

        Returns:
            信号字典
        """
        lookback = self.params['mfi_lookback']

        if 'mfi' not in df.columns or len(df) < lookback:
            return {'detected': False}

        # 寻找局部高点
        price_peaks = self._find_peaks(df['close'].tail(lookback))
        mfi_peaks = self._find_peaks(df['mfi'].tail(lookback))

        # 检查背离
        divergence = self._check_bearish_divergence(
            df.tail(lookback),
            'close',
            'mfi',
            price_peaks,
            mfi_peaks
        )

        if divergence:
            return {
                'detected': True,
                'signal_date': df['date'].iloc[-1] if 'date' in df.columns else None,
                'description': f"MFI看跌背离: 价格创新高但资金流量指标未能同步",
                'severity': 'high',
                'details': divergence
            }

        return {'detected': False}

    def detect_rsi_bearish_divergence(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测 RSI 看跌背离

        Args:
            df: 包含 close 和 rsi 的 DataFrame

        Returns:
            信号字典
        """
        lookback = 60

        if 'rsi' not in df.columns or len(df) < lookback:
            return {'detected': False}

        # 寻找局部高点
        price_peaks = self._find_peaks(df['close'].tail(lookback))
        rsi_peaks = self._find_peaks(df['rsi'].tail(lookback))

        # 检查背离
        divergence = self._check_bearish_divergence(
            df.tail(lookback),
            'close',
            'rsi',
            price_peaks,
            rsi_peaks
        )

        if divergence:
            # RSI 背离的权重较低，因为 RSI 本身是震荡指标
            return {
                'detected': True,
                'signal_date': df['date'].iloc[-1] if 'date' in df.columns else None,
                'description': f"RSI看跌背离: 价格创新高但RSI动能减弱",
                'severity': 'medium',
                'details': divergence
            }

        return {'detected': False}

    def detect_macd_bearish_divergence(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测 MACD 看跌背离

        Args:
            df: 包含 close 和 macd 的 DataFrame

        Returns:
            信号字典
        """
        lookback = 60

        if 'macd' not in df.columns or len(df) < lookback:
            return {'detected': False}

        # 寻找局部高点
        price_peaks = self._find_peaks(df['close'].tail(lookback))
        macd_peaks = self._find_peaks(df['macd'].tail(lookback))

        # 检查背离
        divergence = self._check_bearish_divergence(
            df.tail(lookback),
            'close',
            'macd',
            price_peaks,
            macd_peaks
        )

        if divergence:
            return {
                'detected': True,
                'signal_date': df['date'].iloc[-1] if 'date' in df.columns else None,
                'description': f"MACD看跌背离: 价格创新高但MACD趋势动能衰减",
                'severity': 'high',
                'details': divergence
            }

        return {'detected': False}

    @staticmethod
    def _find_peaks(series: pd.Series, order: int = 5) -> List[int]:
        """
        寻找时间序列的局部峰值

        Args:
            series: 时间序列数据
            order: 峰值检测窗口大小

        Returns:
            峰值索引列表
        """
        peaks = []
        series_values = series.values

        for i in range(order, len(series_values) - order):
            # 检查是否为局部最大值
            window = series_values[i - order:i + order + 1]
            if series_values[i] == max(window):
                peaks.append(i)

        return peaks

    @staticmethod
    def _check_bearish_divergence(
        df: pd.DataFrame,
        price_col: str,
        indicator_col: str,
        price_peaks: List[int],
        indicator_peaks: List[int]
    ) -> Dict[str, Any]:
        """
        检查价格和指标之间是否存在看跌背离

        Args:
            df: 数据
            price_col: 价格列名
            indicator_col: 指标列名
            price_peaks: 价格峰值索引
            indicator_peaks: 指标峰值索引

        Returns:
            背离详情字典，如果不存在背离则返回 None
        """
        if len(price_peaks) < 2 or len(indicator_peaks) < 2:
            return None

        # 重置索引以便使用整数索引
        df_reset = df.reset_index(drop=True)

        # 获取最近两个价格峰值
        price_peak1_idx = price_peaks[-2]
        price_peak2_idx = price_peaks[-1]

        price1 = df_reset[price_col].iloc[price_peak1_idx]
        price2 = df_reset[price_col].iloc[price_peak2_idx]

        # 价格是否创新高 (Higher High)
        if price2 <= price1:
            return None

        # 寻找对应的指标峰值
        # 允许一定的时间偏差
        tolerance = 10

        indicator_peak1 = None
        indicator_peak2 = None

        for ind_peak in indicator_peaks:
            if abs(ind_peak - price_peak1_idx) <= tolerance:
                indicator_peak1 = df_reset[indicator_col].iloc[ind_peak]
            if abs(ind_peak - price_peak2_idx) <= tolerance:
                indicator_peak2 = df_reset[indicator_col].iloc[ind_peak]

        if indicator_peak1 is None or indicator_peak2 is None:
            return None

        # 检查指标是否未能创新高 (Lower High)
        if indicator_peak2 >= indicator_peak1:
            return None

        # 确认背离
        return {
            'price_peak1': float(price1),
            'price_peak2': float(price2),
            'price_change': f"{(price2 / price1 - 1):.2%}",
            'indicator_peak1': float(indicator_peak1),
            'indicator_peak2': float(indicator_peak2),
            'indicator_change': f"{(indicator_peak2 / indicator_peak1 - 1):.2%}",
            'divergence_strength': abs(indicator_peak2 / indicator_peak1 - 1)
        }


def analyze_indicators(df: pd.DataFrame, config) -> Dict[str, Any]:
    """
    便捷函数：执行技术指标分析

    Args:
        df: 价格和指标数据
        config: 配置模块

    Returns:
        信号字典
    """
    analyzer = IndicatorSignals(config)
    return analyzer.analyze(df)
