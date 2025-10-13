"""
结构性信号分析模块
分析机构持股变化、股东户数变化、董监高减持等
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class StructuralSignals:
    """结构性信号分析器"""

    def __init__(self, config, data_fetcher):
        """
        初始化结构性信号分析器

        Args:
            config: 配置模块
            data_fetcher: 数据获取器实例
        """
        self.config = config
        self.data_fetcher = data_fetcher
        self.params = config.STRUCTURAL_PARAMS

    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        执行结构性信号分析

        Args:
            ticker: 股票代码

        Returns:
            信号字典
        """
        signals = {}

        # 1. 分析机构持股变化
        holdings_signal = self.analyze_institutional_holdings(ticker)
        if holdings_signal['detected']:
            signals['INSTITUTIONAL_SELL_OFF'] = holdings_signal

        # 2. 分析股东户数变化
        shareholder_signal = self.analyze_shareholder_count(ticker)
        if shareholder_signal['detected']:
            signals['SHAREHOLDER_COUNT_INCREASE'] = shareholder_signal

        return signals

    def analyze_institutional_holdings(
        self,
        ticker: str,
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析机构持股变化

        Args:
            ticker: 股票代码
            market: 市场类型 (可选)

        Returns:
            信号字典
        """
        try:
            # 获取机构持股数据
            holdings_df = self.data_fetcher.get_institutional_holdings(ticker)

            if holdings_df.empty:
                return {
                    'detected': False,
                    'description': '无机构持股数据'
                }

            # 分析最近的持股变化
            # 简化版本：检查是否有重要机构减持
            reduction_threshold = self.params['institutional_reduction_threshold']

            # 这里需要根据实际数据结构进行调整
            # Tushare 的 top10_floatholders 数据结构:
            # ts_code, ann_date, end_date, holder_name, hold_amount, hold_ratio

            # 按报告期分组
            if 'end_date' in holdings_df.columns:
                latest_period = holdings_df['end_date'].max()
                holdings_df['end_date'] = pd.to_datetime(holdings_df['end_date'])
                periods = sorted(holdings_df['end_date'].unique(), reverse=True)

                if len(periods) < 2:
                    return {
                        'detected': False,
                        'description': '数据期数不足'
                    }

                # 比较最近两期
                current_period = periods[0]
                prev_period = periods[1]

                current_holdings = holdings_df[holdings_df['end_date'] == current_period]
                prev_holdings = holdings_df[holdings_df['end_date'] == prev_period]

                # 查找减持的机构
                reductions = []
                for _, curr_row in current_holdings.iterrows():
                    holder_name = curr_row.get('holder_name', '')
                    curr_ratio = curr_row.get('hold_ratio', 0)

                    # 在上期数据中查找同一持有人
                    prev_match = prev_holdings[prev_holdings['holder_name'] == holder_name]

                    if not prev_match.empty:
                        prev_ratio = prev_match.iloc[0].get('hold_ratio', 0)
                        reduction = prev_ratio - curr_ratio

                        if reduction > reduction_threshold:
                            reductions.append({
                                'holder': holder_name,
                                'prev_ratio': f"{prev_ratio:.2%}",
                                'current_ratio': f"{curr_ratio:.2%}",
                                'reduction': f"{reduction:.2%}"
                            })

                if reductions:
                    return {
                        'detected': True,
                        'signal_date': current_period,
                        'description': f"检测到{len(reductions)}家机构减持",
                        'severity': 'critical',
                        'details': {
                            'reductions': reductions
                        }
                    }

        except Exception as e:
            logger.error(f"分析机构持股失败: {e}")

        return {'detected': False}

    def analyze_shareholder_count(self, ticker: str) -> Dict[str, Any]:
        """
        分析股东户数变化

        逻辑:
        股东户数显著增加 + 机构持股比例下降 = 筹码从机构向散户派发

        Args:
            ticker: 股票代码

        Returns:
            信号字典
        """
        try:
            # 获取股东户数数据
            shareholder_df = self.data_fetcher.get_shareholder_count(ticker)

            if shareholder_df.empty:
                return {
                    'detected': False,
                    'description': '无股东户数数据'
                }

            # Tushare 数据结构: ts_code, ann_date, end_date, holder_num
            if 'end_date' in shareholder_df.columns and 'holder_num' in shareholder_df.columns:
                shareholder_df['end_date'] = pd.to_datetime(shareholder_df['end_date'])
                shareholder_df = shareholder_df.sort_values('end_date', ascending=False)

                if len(shareholder_df) < 2:
                    return {
                        'detected': False,
                        'description': '数据期数不足'
                    }

                # 比较最近两期
                current = shareholder_df.iloc[0]
                previous = shareholder_df.iloc[1]

                current_count = current['holder_num']
                prev_count = previous['holder_num']

                increase_ratio = (current_count - prev_count) / prev_count

                threshold = self.params['shareholder_increase_threshold']

                if increase_ratio > threshold:
                    return {
                        'detected': True,
                        'signal_date': current['end_date'],
                        'description': f"股东户数显著增加{increase_ratio:.2%} ({prev_count:,} -> {current_count:,})",
                        'severity': 'high',
                        'details': {
                            'previous_count': int(prev_count),
                            'current_count': int(current_count),
                            'increase_ratio': f"{increase_ratio:.2%}"
                        }
                    }

        except Exception as e:
            logger.error(f"分析股东户数失败: {e}")

        return {'detected': False}


def analyze_structural(ticker: str, config, data_fetcher) -> Dict[str, Any]:
    """
    便捷函数：执行结构性分析

    Args:
        ticker: 股票代码
        config: 配置模块
        data_fetcher: 数据获取器

    Returns:
        信号字典
    """
    analyzer = StructuralSignals(config, data_fetcher)
    return analyzer.analyze(ticker)
