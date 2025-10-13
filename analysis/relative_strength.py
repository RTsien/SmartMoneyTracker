"""
相对强弱分析模块
分析个股相对于板块/大盘的表现
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RelativeStrengthAnalyzer:
    """相对强弱分析器"""

    def __init__(self, config):
        """
        初始化相对强弱分析器

        Args:
            config: 配置模块
        """
        self.config = config
        self.params = config.RELATIVE_STRENGTH_PARAMS

    def analyze(
        self,
        stock_df: pd.DataFrame,
        benchmark_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        分析个股相对强弱

        Args:
            stock_df: 个股价格数据
            benchmark_df: 基准指数价格数据

        Returns:
            信号字典
        """
        if stock_df.empty or benchmark_df.empty:
            logger.warning("数据为空，无法进行相对强弱分析")
            return {}

        signals = {}

        # 计算相对强弱比率 (RSP)
        rsp_signal = self.calculate_rsp(stock_df, benchmark_df)
        if rsp_signal['status'] == 'WEAK':
            signals['RELATIVE_STRENGTH_WEAK'] = rsp_signal

        return signals

    def calculate_rsp(
        self,
        stock_df: pd.DataFrame,
        benchmark_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        计算相对强弱比率 (Relative Strength Price)

        RSP = 个股价格 / 基准价格

        Args:
            stock_df: 个股数据
            benchmark_df: 基准数据

        Returns:
            分析结果
        """
        lookback = self.params['lookback_period']

        # 对齐日期
        merged = pd.merge(
            stock_df[['date', 'close']],
            benchmark_df[['date', 'close']],
            on='date',
            how='inner',
            suffixes=('_stock', '_bench')
        )

        if len(merged) < lookback:
            return {
                'detected': False,
                'status': 'NEUTRAL',
                'description': '数据不足'
            }

        # 计算 RSP
        merged['rsp'] = merged['close_stock'] / merged['close_bench']

        # 计算 RSP 的移动平均
        ma_period = self.params['rsp_ma_period']
        merged['rsp_ma'] = merged['rsp'].rolling(window=ma_period).mean()

        # 分析 RSP 趋势
        recent_rsp = merged['rsp'].tail(lookback)
        rsp_slope = np.polyfit(range(len(recent_rsp)), recent_rsp, 1)[0]

        # RSP 下降趋势表明相对疲弱
        is_weak = rsp_slope < 0

        # 检查 RSP 是否跌破移动平均线
        current_rsp = merged['rsp'].iloc[-1]
        current_rsp_ma = merged['rsp_ma'].iloc[-1]
        below_ma = current_rsp < current_rsp_ma

        # 计算相对表现
        stock_return = (merged['close_stock'].iloc[-1] / merged['close_stock'].iloc[-lookback] - 1)
        bench_return = (merged['close_bench'].iloc[-1] / merged['close_bench'].iloc[-lookback] - 1)
        relative_return = stock_return - bench_return

        detected = is_weak and below_ma and relative_return < -0.05  # 跑输5%以上

        status = 'WEAK' if detected else 'NEUTRAL'

        return {
            'detected': detected,
            'status': status,
            'signal_date': merged['date'].iloc[-1] if not merged.empty else None,
            'description': f"相对强度疲弱: 跑输基准{abs(relative_return):.2%}",
            'severity': 'medium' if detected else 'none',
            'details': {
                'stock_return': f"{stock_return:.2%}",
                'benchmark_return': f"{bench_return:.2%}",
                'relative_return': f"{relative_return:.2%}",
                'rsp_slope': rsp_slope,
                'current_rsp': current_rsp,
                'rsp_ma': current_rsp_ma
            }
        }


def analyze_relative_strength(
    stock_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    config
) -> Dict[str, Any]:
    """
    便捷函数：执行相对强弱分析

    Args:
        stock_df: 个股数据
        benchmark_df: 基准数据
        config: 配置模块

    Returns:
        信号字典
    """
    analyzer = RelativeStrengthAnalyzer(config)
    return analyzer.analyze(stock_df, benchmark_df)
