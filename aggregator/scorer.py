"""
信号聚合模块 (Bidirectional Scoring)
根据多个信号计算综合动向评分 (-10 to +10)

评分含义:
- 正分 (+): 机构进场/吸筹 (Accumulation)
- 负分 (-): 机构离场/派发 (Distribution)
- 0: 中性 (Neutral)

评级映射:
- +6 to +10: STRONG_BUY
- +2 to +5: BUY
- -1 to +1: NEUTRAL
- -5 to -2: SELL
- -10 to -6: STRONG_SELL
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class SignalAggregator:
    """信号评分聚合器 (支持双向评分)"""

    def __init__(self, config):
        """
        初始化信号聚合器

        Args:
            config: 配置模块
        """
        self.config = config
        self.signal_weights = config.SIGNAL_WEIGHTS
        self.score_to_rating = config.SCORE_TO_RATING

    def calculate_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算综合动向评分 (双向评分: -10 to +10)

        Args:
            signals: 所有触发的信号字典

        Returns:
            包含评分和评级的字典
        """
        if not signals:
            return {
                'score': 0,
                'score_range': '(-10 to +10)',
                'rating': 'NEUTRAL',
                'triggered_signals': {},
                'signal_count': 0,
                'inflow_signals': {},
                'outflow_signals': {},
                'inflow_count': 0,
                'outflow_count': 0
            }

        total_score = 0
        triggered_signals = {}
        inflow_signals = {}   # 吸筹信号 (正分)
        outflow_signals = {}  # 派发信号 (负分)

        # 累加各信号的分数
        for signal_name, signal_data in signals.items():
            if signal_name in self.signal_weights:
                weight = self.signal_weights[signal_name]
                total_score += weight

                signal_entry = {
                    'weight': weight,
                    'data': signal_data
                }

                triggered_signals[signal_name] = signal_entry

                # 根据权重符号分类
                if weight > 0:
                    inflow_signals[signal_name] = signal_entry
                    logger.info(f"触发吸筹信号: {signal_name} (权重: +{weight})")
                elif weight < 0:
                    outflow_signals[signal_name] = signal_entry
                    logger.info(f"触发派发信号: {signal_name} (权重: {weight})")

        # 限制评分范围在 -10 到 +10
        total_score = max(-10, min(10, total_score))

        # 确定评级
        rating = self._determine_rating(total_score)

        return {
            'score': total_score,
            'score_range': '(-10 to +10)',
            'rating': rating,
            'triggered_signals': triggered_signals,
            'signal_count': len(triggered_signals),
            'inflow_signals': inflow_signals,
            'outflow_signals': outflow_signals,
            'inflow_count': len(inflow_signals),
            'outflow_count': len(outflow_signals)
        }

    def _determine_rating(self, score: float) -> str:
        """
        根据评分确定评级

        Args:
            score: 综合评分 (-10 to +10)

        Returns:
            评级: 'STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL'
        """
        for rating, (min_score, max_score) in self.score_to_rating.items():
            if min_score <= score <= max_score:
                return rating

        # 默认返回中性
        return 'NEUTRAL'

    def get_recommendation(self, rating: str, score: float) -> str:
        """
        根据评级给出建议

        Args:
            rating: 评级
            score: 评分

        Returns:
            投资建议文本
        """
        recommendations = {
            'STRONG_BUY': f'检测到强烈的机构吸筹信号(评分{score:+.1f})。大资金可能正在积极建仓。建议关注并考虑买入时机。',
            'BUY': f'检测到温和的机构吸筹信号(评分{score:+.1f})。有资金流入迹象。建议继续观察价量变化。',
            'NEUTRAL': '当前未检测到明显的机构进出场信号。建议保持观察。',
            'SELL': f'检测到部分机构派发信号(评分{score:+.1f})。建议提高警惕，密切关注后续价量变化。',
            'STRONG_SELL': f'检测到强烈的机构派发信号(评分{score:+.1f})。大资金可能正在大量离场。建议谨慎，考虑降低仓位。'
        }

        return recommendations.get(rating, '无法评估')


def aggregate_signals(signals: Dict[str, Any], config) -> Dict[str, Any]:
    """
    便捷函数：聚合信号评分

    Args:
        signals: 信号字典
        config: 配置模块

    Returns:
        评分结果
    """
    aggregator = SignalAggregator(config)
    return aggregator.calculate_score(signals)
