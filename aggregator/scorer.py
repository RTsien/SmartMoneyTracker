"""
风险聚合模块
根据多个信号计算综合风险评分
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskAggregator:
    """风险评分聚合器"""

    def __init__(self, config):
        """
        初始化风险聚合器

        Args:
            config: 配置模块
        """
        self.config = config
        self.signal_weights = config.SIGNAL_WEIGHTS
        self.risk_thresholds = config.RISK_THRESHOLDS

    def calculate_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算综合风险评分

        Args:
            signals: 所有触发的信号字典

        Returns:
            包含风险评分和等级的字典
        """
        if not signals:
            return {
                'risk_score': 0,
                'max_score': 10,
                'risk_level': 'LOW',
                'triggered_signals': {},
                'signal_count': 0
            }

        total_score = 0
        triggered_signals = {}

        # 累加各信号的分数
        for signal_name, signal_data in signals.items():
            if signal_name in self.signal_weights:
                weight = self.signal_weights[signal_name]
                total_score += weight

                triggered_signals[signal_name] = {
                    'weight': weight,
                    'data': signal_data
                }

                logger.info(f"触发信号: {signal_name} (权重: {weight})")

        # 确定风险等级
        risk_level = self._determine_risk_level(total_score)

        return {
            'risk_score': total_score,
            'max_score': 10,
            'risk_level': risk_level,
            'triggered_signals': triggered_signals,
            'signal_count': len(triggered_signals)
        }

    def _determine_risk_level(self, score: int) -> str:
        """
        根据评分确定风险等级

        Args:
            score: 风险评分

        Returns:
            风险等级: 'LOW', 'MEDIUM', 'HIGH'
        """
        for level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= score <= max_score:
                return level

        # 如果超过最高阈值，返回 HIGH
        return 'HIGH'

    def get_recommendation(self, risk_level: str) -> str:
        """
        根据风险等级给出建议

        Args:
            risk_level: 风险等级

        Returns:
            投资建议文本
        """
        recommendations = {
            'LOW': '当前未检测到明显的机构撤离信号。建议继续观察。',
            'MEDIUM': '检测到部分撤离信号。建议提高警惕，密切关注后续价量变化和持仓动向。',
            'HIGH': '检测到多个高置信度撤离信号。大资金可能正在派发筹码。建议谨慎，考虑降低仓位或离场观望。'
        }

        return recommendations.get(risk_level, '无法评估')


def aggregate_risk(signals: Dict[str, Any], config) -> Dict[str, Any]:
    """
    便捷函数：聚合风险评分

    Args:
        signals: 信号字典
        config: 配置模块

    Returns:
        风险评分结果
    """
    aggregator = RiskAggregator(config)
    return aggregator.calculate_score(signals)
