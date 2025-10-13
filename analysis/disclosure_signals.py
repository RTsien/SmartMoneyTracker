"""
结构性信号分析模块 (Bidirectional)
分析机构持股变化、股东户数变化等结构性信号

吸筹信号:
- 新机构进入十大股东 (NEW_INSTITUTION)
- 机构增持 (INSTITUTIONAL_BUY_IN)
- 股东户数减少 (SHAREHOLDER_COUNT_DECREASE)

派发信号:
- 机构大幅减持 (INSTITUTIONAL_SELL_OFF)
- 股东户数显著增加 (SHAREHOLDER_COUNT_INCREASE)
- 董监高减持 (INSIDER_SELLING)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
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
        执行结构性信号分析 (双向)

        Args:
            ticker: 股票代码

        Returns:
            信号字典
        """
        signals = {}

        # ========== 吸筹信号 (Accumulation Signals) ==========

        # 1. 分析机构持股变化 - 新进和增持
        holdings_result = self.analyze_institutional_holdings(ticker)

        if holdings_result.get('new_institutions'):
            signals['NEW_INSTITUTION'] = holdings_result['new_institutions']

        if holdings_result.get('buy_in'):
            signals['INSTITUTIONAL_BUY_IN'] = holdings_result['buy_in']

        # 2. 分析股东户数变化 - 减少
        shareholder_decrease = self.analyze_shareholder_count_decrease(ticker)
        if shareholder_decrease['detected']:
            signals['SHAREHOLDER_COUNT_DECREASE'] = shareholder_decrease

        # ========== 派发信号 (Distribution Signals) ==========

        # 3. 分析机构持股变化 - 减持
        if holdings_result.get('sell_off'):
            signals['INSTITUTIONAL_SELL_OFF'] = holdings_result['sell_off']

        # 4. 分析股东户数变化 - 增加
        shareholder_increase = self.analyze_shareholder_count_increase(ticker)
        if shareholder_increase['detected']:
            signals['SHAREHOLDER_COUNT_INCREASE'] = shareholder_increase

        return signals

    def analyze_institutional_holdings(
        self,
        ticker: str,
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析机构持股变化 (双向)

        Args:
            ticker: 股票代码
            market: 市场类型 (可选)

        Returns:
            包含 new_institutions, buy_in, sell_off 的字典
        """
        result = {
            'new_institutions': None,
            'buy_in': None,
            'sell_off': None
        }

        try:
            # 获取机构持股数据
            holdings_df = self.data_fetcher.get_institutional_holdings(ticker)

            if holdings_df.empty:
                return result

            # Tushare 数据结构: ts_code, ann_date, end_date, holder_name, hold_amount, hold_ratio
            if 'end_date' not in holdings_df.columns:
                return result

            holdings_df['end_date'] = pd.to_datetime(holdings_df['end_date'])
            periods = sorted(holdings_df['end_date'].unique(), reverse=True)

            if len(periods) < 2:
                return result

            # 比较最近两期
            current_period = periods[0]
            prev_period = periods[1]

            current_holdings = holdings_df[holdings_df['end_date'] == current_period]
            prev_holdings = holdings_df[holdings_df['end_date'] == prev_period]

            current_holders = set(current_holdings['holder_name'].tolist())
            prev_holders = set(prev_holdings['holder_name'].tolist())

            reduction_threshold = self.params['institutional_reduction_threshold']

            # ========== 吸筹信号分析 ==========

            # 1. 新进机构
            new_holders = current_holders - prev_holders
            if new_holders:
                new_institutions_list = []
                for holder in new_holders:
                    holder_data = current_holdings[current_holdings['holder_name'] == holder].iloc[0]
                    new_institutions_list.append({
                        'holder': holder,
                        'ratio': f"{holder_data.get('hold_ratio', 0):.2%}",
                        'amount': holder_data.get('hold_amount', 0)
                    })

                result['new_institutions'] = {
                    'detected': True,
                    'signal_date': current_period,
                    'description': f"检测到{len(new_institutions_list)}家新机构进入十大股东",
                    'severity': 'high',
                    'signal_type': 'accumulation',
                    'details': {
                        'new_institutions': new_institutions_list
                    }
                }

            # 2. 机构增持
            increases = []
            for _, curr_row in current_holdings.iterrows():
                holder_name = curr_row.get('holder_name', '')
                curr_ratio = curr_row.get('hold_ratio', 0)

                prev_match = prev_holdings[prev_holdings['holder_name'] == holder_name]

                if not prev_match.empty:
                    prev_ratio = prev_match.iloc[0].get('hold_ratio', 0)
                    increase = curr_ratio - prev_ratio

                    if increase > reduction_threshold:  # 使用相同阈值
                        increases.append({
                            'holder': holder_name,
                            'prev_ratio': f"{prev_ratio:.2%}",
                            'current_ratio': f"{curr_ratio:.2%}",
                            'increase': f"{increase:.2%}"
                        })

            if increases:
                result['buy_in'] = {
                    'detected': True,
                    'signal_date': current_period,
                    'description': f"检测到{len(increases)}家机构增持",
                    'severity': 'high',
                    'signal_type': 'accumulation',
                    'details': {
                        'increases': increases
                    }
                }

            # ========== 派发信号分析 ==========

            # 3. 机构减持
            reductions = []
            for _, curr_row in current_holdings.iterrows():
                holder_name = curr_row.get('holder_name', '')
                curr_ratio = curr_row.get('hold_ratio', 0)

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

            # 4. 机构退出
            exited_holders = prev_holders - current_holders
            if exited_holders:
                for holder in exited_holders:
                    holder_data = prev_holdings[prev_holdings['holder_name'] == holder].iloc[0]
                    reductions.append({
                        'holder': holder,
                        'prev_ratio': f"{holder_data.get('hold_ratio', 0):.2%}",
                        'current_ratio': '0.00%',
                        'reduction': '完全退出'
                    })

            if reductions:
                result['sell_off'] = {
                    'detected': True,
                    'signal_date': current_period,
                    'description': f"检测到{len(reductions)}家机构减持",
                    'severity': 'critical',
                    'signal_type': 'distribution',
                    'details': {
                        'reductions': reductions
                    }
                }

        except Exception as e:
            logger.error(f"分析机构持股失败: {e}")

        return result

    def analyze_shareholder_count_decrease(self, ticker: str) -> Dict[str, Any]:
        """
        分析股东户数减少 (吸筹信号)

        逻辑:
        股东户数减少 = 筹码从散户向机构集中

        Args:
            ticker: 股票代码

        Returns:
            信号字典
        """
        try:
            shareholder_df = self.data_fetcher.get_shareholder_count(ticker)

            if shareholder_df.empty:
                return {'detected': False, 'description': '无股东户数数据'}

            if 'end_date' in shareholder_df.columns and 'holder_num' in shareholder_df.columns:
                shareholder_df['end_date'] = pd.to_datetime(shareholder_df['end_date'])
                shareholder_df = shareholder_df.sort_values('end_date', ascending=False)

                if len(shareholder_df) < 2:
                    return {'detected': False, 'description': '数据期数不足'}

                current = shareholder_df.iloc[0]
                previous = shareholder_df.iloc[1]

                current_count = current['holder_num']
                prev_count = previous['holder_num']

                decrease_ratio = (prev_count - current_count) / prev_count

                threshold = self.params['shareholder_increase_threshold']

                if decrease_ratio > threshold:
                    return {
                        'detected': True,
                        'signal_date': current['end_date'],
                        'description': f"股东户数显著减少{decrease_ratio:.2%} ({prev_count:,} -> {current_count:,})",
                        'severity': 'medium',
                        'signal_type': 'accumulation',
                        'details': {
                            'previous_count': int(prev_count),
                            'current_count': int(current_count),
                            'decrease_ratio': f"{decrease_ratio:.2%}"
                        }
                    }

        except Exception as e:
            logger.error(f"分析股东户数减少失败: {e}")

        return {'detected': False}

    def analyze_shareholder_count_increase(self, ticker: str) -> Dict[str, Any]:
        """
        分析股东户数增加 (派发信号)

        逻辑:
        股东户数显著增加 = 筹码从机构向散户派发

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
                        'signal_type': 'distribution',
                        'details': {
                            'previous_count': int(prev_count),
                            'current_count': int(current_count),
                            'increase_ratio': f"{increase_ratio:.2%}"
                        }
                    }

        except Exception as e:
            logger.error(f"分析股东户数增加失败: {e}")

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
