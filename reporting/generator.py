"""
报告生成模块 (Bidirectional Reporting)
将分析结果格式化为人类可读的报告，支持双向评分展示

报告特点:
- 分离展示吸筹信号 (Inflow Signals) 和派发信号 (Outflow Signals)
- 评分范围: -10 to +10
- 评级: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
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
        score_result: Dict[str, Any],
        recommendation: str
    ) -> str:
        """
        生成文本格式报告 (双向评分)

        Args:
            ticker: 股票代码
            score_result: 评分结果 (支持双向评分)
            recommendation: 投资建议

        Returns:
            格式化的报告文本
        """
        report_lines = []

        # 报告头部
        report_lines.append("=" * 70)
        report_lines.append("      Smart Money Tracker - 机构资金动向分析报告")
        report_lines.append("=" * 70)
        report_lines.append("")

        # 基本信息
        report_lines.append(f"股票代码: {ticker}")
        report_lines.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # 综合评分 (双向)
        score = score_result.get('score', 0)
        score_range = score_result.get('score_range', '(-10 to +10)')
        rating = score_result.get('rating', 'NEUTRAL')
        signal_count = score_result.get('signal_count', 0)
        inflow_count = score_result.get('inflow_count', 0)
        outflow_count = score_result.get('outflow_count', 0)

        rating_indicator = self._get_rating_indicator(rating)

        report_lines.append(f"综合评分: {score:+.1f}/10 {score_range}")
        report_lines.append(f"综合评级: {rating} {rating_indicator}")
        report_lines.append(f"触发信号数: {signal_count} (进场: {inflow_count}, 离场: {outflow_count})")
        report_lines.append("")

        # 吸筹信号 (正分)
        inflow_signals = score_result.get('inflow_signals', {})
        if inflow_signals:
            report_lines.append("=" * 70)
            report_lines.append("  进场信号 (吸筹/Accumulation) 🟢")
            report_lines.append("=" * 70)
            report_lines.append("")

            for signal_name, signal_info in inflow_signals.items():
                weight = signal_info['weight']
                data = signal_info['data']

                # 信号名称和权重
                report_lines.append(f"[+{weight}] {self._translate_signal_name(signal_name)}")

                # 信号描述
                if 'description' in data:
                    report_lines.append(f"      {data['description']}")

                # 信号日期
                if 'signal_date' in data and data['signal_date']:
                    date_str = self._format_date(data['signal_date'])
                    report_lines.append(f"      信号日期: {date_str}")

                # 详细信息
                if 'details' in data and data['details']:
                    for key, value in data['details'].items():
                        if key not in ['reductions', 'broken_supports']:
                            report_lines.append(f"        • {key}: {value}")

                report_lines.append("")

        # 派发信号 (负分)
        outflow_signals = score_result.get('outflow_signals', {})
        if outflow_signals:
            report_lines.append("=" * 70)
            report_lines.append("  离场信号 (派发/Distribution) 🔴")
            report_lines.append("=" * 70)
            report_lines.append("")

            for signal_name, signal_info in outflow_signals.items():
                weight = signal_info['weight']
                data = signal_info['data']

                # 信号名称和权重
                report_lines.append(f"[{weight}] {self._translate_signal_name(signal_name)}")

                # 信号描述
                if 'description' in data:
                    report_lines.append(f"      {data['description']}")

                # 信号日期
                if 'signal_date' in data and data['signal_date']:
                    date_str = self._format_date(data['signal_date'])
                    report_lines.append(f"      信号日期: {date_str}")

                # 详细信息
                if 'details' in data and data['details']:
                    for key, value in data['details'].items():
                        if key not in ['reductions', 'broken_supports']:
                            report_lines.append(f"        • {key}: {value}")

                report_lines.append("")

        # 无信号情况
        if signal_count == 0:
            report_lines.append("未检测到明显的机构进出场信号。")
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
    def _get_rating_indicator(rating: str) -> str:
        """获取评级对应的指示符"""
        indicators = {
            'STRONG_BUY': '🚀🚀',
            'BUY': '🚀',
            'NEUTRAL': '⚪',
            'SELL': '⚠️',
            'STRONG_SELL': '🛑🛑'
        }
        return indicators.get(rating, '')

    @staticmethod
    def _format_date(date_value) -> str:
        """格式化日期"""
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y-%m-%d')
        return str(date_value)

    @staticmethod
    def _translate_signal_name(signal_name: str) -> str:
        """将信号代码翻译为中文名称 (双向)"""
        translations = {
            # 进场/吸筹信号
            'ACCUMULATION_BREAKOUT': '放量突破横盘区',
            'WYCKOFF_SPRING': '威科夫弹簧/震仓',
            'OBV_BULLISH_DIVERGENCE': 'OBV 看涨背离',
            'MFI_BULLISH_DIVERGENCE': 'MFI 看涨背离',
            'MFI_OVERSOLD': 'MFI 超卖',
            'NEW_INSTITUTION': '新机构进入十大股东',
            'INSTITUTIONAL_BUY_IN': '机构增持',
            'SHAREHOLDER_COUNT_DECREASE': '股东户数减少',
            'BID_WALL_SUPPORT': '买单墙支撑',
            'RSP_STRONG': '相对强度强势',
            'POSITIVE_NEWS': '正面新闻/催化剂',
            'EARNINGS_BEAT': '业绩超预期',
            'POLICY_TAILWIND': '有利政策',

            # 离场/派发信号
            'HIGH_VOLUME_STAGNATION': '高位放量滞涨',
            'HIGH_VOLUME_DECLINE': '放量下跌',
            'BREAK_SUPPORT_HEAVY_VOLUME': '放量跌破支撑位',
            'LOW_VOLUME_RISE': '高位缩量上涨',
            'OBV_BEARISH_DIVERGENCE': 'OBV 看跌背离',
            'MFI_BEARISH_DIVERGENCE': 'MFI 看跌背离',
            'MFI_OVERBOUGHT': 'MFI 超买',
            'RSI_BEARISH_DIVERGENCE': 'RSI 看跌背离',
            'MACD_BEARISH_DIVERGENCE': 'MACD 看跌背离',
            'INSTITUTIONAL_SELL_OFF': '机构大幅减持',
            'SHAREHOLDER_COUNT_INCREASE': '股东户数显著增加',
            'INSIDER_SELLING': '董监高减持',
            'ASK_WALL_PRESSURE': '卖盘压单',
            'RSP_WEAK': '相对强度疲弱',
            'SECTOR_UNDERPERFORMANCE': '跑输行业板块',
            'NEGATIVE_NEWS': '负面新闻',
            'EARNINGS_WARNING': '业绩预警',
            'POLICY_HEADWIND': '不利政策',
        }
        return translations.get(signal_name, signal_name)

    def generate_json_report(
        self,
        ticker: str,
        score_result: Dict[str, Any],
        recommendation: str
    ) -> Dict[str, Any]:
        """
        生成 JSON 格式报告 (双向评分)

        Args:
            ticker: 股票代码
            score_result: 评分结果
            recommendation: 投资建议

        Returns:
            JSON 格式的报告
        """
        return {
            'ticker': ticker,
            'analysis_time': datetime.now().isoformat(),
            'score': score_result.get('score', 0),
            'score_range': score_result.get('score_range', '(-10 to +10)'),
            'rating': score_result.get('rating', 'NEUTRAL'),
            'signal_count': score_result.get('signal_count', 0),
            'inflow_count': score_result.get('inflow_count', 0),
            'outflow_count': score_result.get('outflow_count', 0),
            'inflow_signals': score_result.get('inflow_signals', {}),
            'outflow_signals': score_result.get('outflow_signals', {}),
            'triggered_signals': score_result.get('triggered_signals', {}),
            'recommendation': recommendation
        }


def generate_report(
    ticker: str,
    score_result: Dict[str, Any],
    recommendation: str,
    config,
    format: str = 'text'
) -> Any:
    """
    便捷函数：生成报告 (双向评分)

    Args:
        ticker: 股票代码
        score_result: 评分结果
        recommendation: 投资建议
        config: 配置模块
        format: 报告格式 ('text' 或 'json')

    Returns:
        报告内容
    """
    generator = ReportGenerator(config)

    if format == 'json':
        return generator.generate_json_report(ticker, score_result, recommendation)
    else:
        return generator.generate_report(ticker, score_result, recommendation)
