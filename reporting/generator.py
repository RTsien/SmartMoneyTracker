"""
报告生成模块
将分析结果格式化为人类可读的报告
"""

from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config):
        """
        初始化报告生成器

        Args:
            config: 配置模块
        """
        self.config = config

    def generate_report(
        self,
        ticker: str,
        risk_result: Dict[str, Any],
        recommendation: str
    ) -> str:
        """
        生成文本格式报告

        Args:
            ticker: 股票代码
            risk_result: 风险评估结果
            recommendation: 投资建议

        Returns:
            格式化的报告文本
        """
        report_lines = []

        # 报告头部
        report_lines.append("=" * 60)
        report_lines.append("    Smart Money Tracker - 机构资金撤离信号分析报告")
        report_lines.append("=" * 60)
        report_lines.append("")

        # 基本信息
        report_lines.append(f"股票代码: {ticker}")
        report_lines.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # 风险评分
        risk_score = risk_result['risk_score']
        max_score = risk_result['max_score']
        risk_level = risk_result['risk_level']
        signal_count = risk_result['signal_count']

        risk_level_color = self._get_risk_color(risk_level)

        report_lines.append(f"风险评分: {risk_score}/{max_score} [{risk_level}]")
        report_lines.append(f"触发信号数: {signal_count}")
        report_lines.append("")

        # 触发的信号详情
        if signal_count > 0:
            report_lines.append("-" * 60)
            report_lines.append("触发的信号:")
            report_lines.append("-" * 60)
            report_lines.append("")

            for signal_name, signal_info in risk_result['triggered_signals'].items():
                weight = signal_info['weight']
                data = signal_info['data']

                # 信号名称和权重
                report_lines.append(f"[+] {self._translate_signal_name(signal_name)} (权重: {weight})")

                # 信号描述
                if 'description' in data:
                    report_lines.append(f"    {data['description']}")

                # 信号日期
                if 'signal_date' in data and data['signal_date']:
                    date_str = str(data['signal_date'])
                    if hasattr(data['signal_date'], 'strftime'):
                        date_str = data['signal_date'].strftime('%Y-%m-%d')
                    report_lines.append(f"    信号日期: {date_str}")

                # 详细信息
                if 'details' in data and data['details']:
                    report_lines.append(f"    详细信息:")
                    for key, value in data['details'].items():
                        if key not in ['reductions', 'broken_supports']:
                            report_lines.append(f"      - {key}: {value}")

                report_lines.append("")

        else:
            report_lines.append("未检测到明显的机构撤离信号。")
            report_lines.append("")

        # 投资建议
        report_lines.append("-" * 60)
        report_lines.append("投资建议:")
        report_lines.append("-" * 60)
        report_lines.append("")
        report_lines.append(recommendation)
        report_lines.append("")

        # 免责声明
        report_lines.append("-" * 60)
        report_lines.append("免责声明:")
        report_lines.append("-" * 60)
        report_lines.append("本报告仅供学习研究使用，不构成任何投资建议。")
        report_lines.append("投资有风险，决策需谨慎。")
        report_lines.append("")

        return "\n".join(report_lines)

    @staticmethod
    def _get_risk_color(risk_level: str) -> str:
        """获取风险等级对应的颜色标识"""
        colors = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🔴'
        }
        return colors.get(risk_level, '')

    @staticmethod
    def _translate_signal_name(signal_name: str) -> str:
        """将信号代码翻译为中文名称"""
        translations = {
            'HIGH_VOLUME_STAGNATION': '高位放量滞涨',
            'HIGH_VOLUME_DECLINE': '放量下跌',
            'BREAK_SUPPORT_HEAVY_VOLUME': '放量跌破支撑位',
            'LOW_VOLUME_RISE': '高位缩量上涨',
            'OBV_DIVERGENCE': 'OBV 看跌背离',
            'MFI_DIVERGENCE': 'MFI 看跌背离',
            'RSI_DIVERGENCE': 'RSI 看跌背离',
            'MACD_DIVERGENCE': 'MACD 看跌背离',
            'INSTITUTIONAL_SELL_OFF': '机构减持',
            'SHAREHOLDER_COUNT_INCREASE': '股东户数显著增加',
            'INSIDER_SELLING': '董监高减持',
            'RELATIVE_STRENGTH_WEAK': '相对强度疲弱',
            'SECTOR_UNDERPERFORMANCE': '跑输行业板块',
            'NEGATIVE_NEWS': '负面新闻',
            'EARNINGS_WARNING': '业绩预警',
            'POLICY_HEADWIND': '不利政策',
        }
        return translations.get(signal_name, signal_name)

    def generate_json_report(
        self,
        ticker: str,
        risk_result: Dict[str, Any],
        recommendation: str
    ) -> Dict[str, Any]:
        """
        生成 JSON 格式报告

        Args:
            ticker: 股票代码
            risk_result: 风险评估结果
            recommendation: 投资建议

        Returns:
            JSON 格式的报告
        """
        return {
            'ticker': ticker,
            'analysis_time': datetime.now().isoformat(),
            'risk_score': risk_result['risk_score'],
            'max_score': risk_result['max_score'],
            'risk_level': risk_result['risk_level'],
            'signal_count': risk_result['signal_count'],
            'triggered_signals': risk_result['triggered_signals'],
            'recommendation': recommendation
        }


def generate_report(
    ticker: str,
    risk_result: Dict[str, Any],
    recommendation: str,
    config,
    format: str = 'text'
) -> Any:
    """
    便捷函数：生成报告

    Args:
        ticker: 股票代码
        risk_result: 风险评估结果
        recommendation: 投资建议
        config: 配置模块
        format: 报告格式 ('text' 或 'json')

    Returns:
        报告内容
    """
    generator = ReportGenerator(config)

    if format == 'json':
        return generator.generate_json_report(ticker, risk_result, recommendation)
    else:
        return generator.generate_report(ticker, risk_result, recommendation)
