"""
SmartMoneyTracker 主程序 (Bidirectional Analysis)
协调数据获取、信号分析、双向评分和报告生成

评分系统: -10 to +10
- 正分: 机构进场/吸筹 (Accumulation)
- 负分: 机构离场/派发 (Distribution)
"""

import config
from data_fetcher.manager import DataFetcher
from analysis.price_volume_signals import analyze_price_volume
from analysis.indicator_signals import analyze_indicators
from analysis.disclosure_signals import analyze_structural
from analysis.relative_strength import analyze_relative_strength
from aggregator.scorer import SignalAggregator
from reporting.generator import ReportGenerator

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SmartMoneyScanner:
    """机构资金动向扫描器 (Bidirectional Analysis)"""

    def __init__(self):
        """初始化扫描器"""
        logger.info("初始化 SmartMoneyTracker (双向分析系统)...")

        self.data_fetcher = DataFetcher(config)
        self.signal_aggregator = SignalAggregator(config)
        self.report_generator = ReportGenerator(config)

        logger.info("✅ SmartMoneyTracker 初始化完成 (评分范围: -10 to +10)")

    def scan_stock(
        self,
        ticker: str,
        period: int = 250,
        analyze_structure: bool = True
    ) -> Dict[str, Any]:
        """
        扫描单个股票

        Args:
            ticker: 股票代码
            period: 数据回看天数
            analyze_structure: 是否分析结构性信号（需要额外API调用）

        Returns:
            分析结果字典
        """
        logger.info(f"=" * 60)
        logger.info(f"开始分析: {ticker}")
        logger.info(f"=" * 60)

        try:
            # 1. 获取日线数据
            logger.info("步骤 1/5: 获取日线数据...")
            df = self.data_fetcher.get_daily_data(ticker, period=period)

            if df.empty:
                logger.error(f"无法获取 {ticker} 的数据")
                return {
                    'ticker': ticker,
                    'success': False,
                    'error': '无法获取数据'
                }

            # 打印数据概览并保存数据信息
            first_row = df.iloc[0]
            last_row = df.iloc[-1]
            logger.info(f"  获取到 {len(df)} 条数据记录")
            logger.info(f"  {first_row['date'].strftime('%Y-%m-%d') if 'date' in df.columns else '日期未知'} 开盘={first_row['open']:.2f} 收盘={first_row['close']:.2f}")
            logger.info(f"  {last_row['date'].strftime('%Y-%m-%d') if 'date' in df.columns else '日期未知'} 开盘={last_row['open']:.2f} 收盘={last_row['close']:.2f}")
            
            # 保存数据信息用于报告
            first_date_str = first_row['date'].strftime('%Y%m%d') if 'date' in df.columns else '未知'
            last_date_str = last_row['date'].strftime('%Y%m%d') if 'date' in df.columns else '未知'
            data_info = {
                'record_count': len(df),
                'date_range': f"{first_date_str} 至 {last_date_str}",
                'first_date': first_row['date'].strftime('%Y-%m-%d') if 'date' in df.columns else '未知',
                'first_open': float(first_row['open']),
                'first_close': float(first_row['close']),
                'last_date': last_row['date'].strftime('%Y-%m-%d') if 'date' in df.columns else '未知',
                'last_open': float(last_row['open']),
                'last_close': float(last_row['close'])
            }

            # 2. 计算技术指标
            logger.info("步骤 2/5: 计算技术指标...")
            df = self.data_fetcher.calculate_technical_indicators(df)

            # 3. 分析价量关系信号
            logger.info("步骤 3/5: 分析价量关系...")
            pv_signals = analyze_price_volume(df, config)
            logger.info(f"  检测到 {len(pv_signals)} 个价量信号")

            # 4. 分析技术指标信号
            logger.info("步骤 4/5: 分析技术指标...")
            indicator_signals = analyze_indicators(df, config)
            logger.info(f"  检测到 {len(indicator_signals)} 个指标信号")

            # 5. 分析相对强弱（需要基准数据）
            logger.info("步骤 5/5: 分析相对强弱...")
            relative_signals = {}

            # 获取基准指数数据
            market_code = self._get_market_code(ticker)
            if market_code in config.MARKET_BENCHMARKS:
                benchmark_ticker = config.MARKET_BENCHMARKS[market_code]
                benchmark_df = self.data_fetcher.get_daily_data(benchmark_ticker, period=period)

                if not benchmark_df.empty:
                    relative_signals = analyze_relative_strength(df, benchmark_df, config)
                    logger.info(f"  检测到 {len(relative_signals)} 个相对强弱信号")

            # 6. 分析结构性信号（可选）
            structural_signals = {}
            if analyze_structure:
                logger.info("分析结构性信号...")
                structural_signals = analyze_structural(ticker, config, self.data_fetcher)
                logger.info(f"检测到 {len(structural_signals)} 个结构性信号")

            # 7. 聚合所有信号并计算双向评分
            logger.info("聚合信号并计算综合评分...")
            all_signals = {
                **pv_signals,
                **indicator_signals,
                **relative_signals,
                **structural_signals
            }

            score_result = self.signal_aggregator.calculate_score(all_signals)
            
            # 添加数据信息到结果中
            score_result['data_info'] = data_info

            # 8. 生成建议
            rating = score_result['rating']
            score = score_result['score']
            recommendation = self.signal_aggregator.get_recommendation(rating, score)

            # 9. 生成报告
            report = self.report_generator.generate_report(
                ticker,
                score_result,
                recommendation
            )

            # 打印结果
            rating_emoji = {'STRONG_BUY': '🚀🚀', 'BUY': '🚀', 'NEUTRAL': '⚪',
                           'SELL': '⚠️', 'STRONG_SELL': '🛑🛑'}.get(rating, '')

            logger.info(f"✅ 分析完成: {ticker}")
            logger.info(f"📊 综合评分: {score:+.1f}/10")
            logger.info(f"🎯 综合评级: {rating} {rating_emoji}")
            logger.info(f"📝 触发信号: {score_result['signal_count']} 个 (进场: {score_result.get('inflow_count', 0)}, 离场: {score_result.get('outflow_count', 0)})")

            return {
                'ticker': ticker,
                'success': True,
                'score': score,
                'rating': rating,
                'signal_count': score_result['signal_count'],
                'inflow_count': score_result.get('inflow_count', 0),
                'outflow_count': score_result.get('outflow_count', 0),
                'inflow_signals': score_result.get('inflow_signals', {}),
                'outflow_signals': score_result.get('outflow_signals', {}),
                'triggered_signals': score_result.get('triggered_signals', {}),
                'recommendation': recommendation,
                'report': report,
                'data': df
            }

        except Exception as e:
            logger.error(f"分析 {ticker} 时发生错误: {e}", exc_info=True)
            return {
                'ticker': ticker,
                'success': False,
                'error': str(e)
            }

    def scan_batch(
        self,
        tickers: List[str],
        period: int = 250,
        analyze_structure: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量扫描多只股票

        Args:
            tickers: 股票代码列表
            period: 数据回看天数
            analyze_structure: 是否分析结构性信号

        Returns:
            字典，键为股票代码，值为分析结果
        """
        logger.info(f"开始批量扫描 {len(tickers)} 只股票...")

        results = {}

        for i, ticker in enumerate(tickers, 1):
            logger.info(f"\n进度: {i}/{len(tickers)}")
            result = self.scan_stock(ticker, period, analyze_structure)
            results[ticker] = result

        logger.info(f"\n批量扫描完成！")
        return results

    @staticmethod
    def _get_market_code(ticker: str) -> str:
        """获取股票所属市场代码"""
        if ticker.endswith('.SH'):
            return 'SH'
        elif ticker.endswith('.SZ'):
            return 'SZ'
        elif ticker.endswith('.HK'):
            return 'HK'
        else:
            return 'US'


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='SmartMoneyTracker - 机构资金动向分析系统 (双向评分: -10 to +10)'
    )

    parser.add_argument(
        'tickers',
        nargs='*',
        help='股票代码列表，多个代码用空格分隔'
    )

    parser.add_argument(
        '--pool',
        action='store_true',
        help='扫描配置文件中的股票池'
    )

    parser.add_argument(
        '--period',
        type=int,
        default=250,
        help='数据回看天数 (默认: 250)'
    )

    parser.add_argument(
        '--structure',
        action='store_true',
        help='启用结构性信号分析（需要更多 API 调用）'
    )

    args = parser.parse_args()

    # 确定要扫描的股票
    tickers_to_scan = []

    if args.pool:
        tickers_to_scan = config.STOCK_POOL
        logger.info(f"使用配置文件中的股票池: {len(tickers_to_scan)} 只股票")
    elif args.tickers:
        tickers_to_scan = args.tickers
    else:
        # 默认使用股票池
        tickers_to_scan = config.STOCK_POOL
        logger.info("未指定股票，使用默认股票池")

    if not tickers_to_scan:
        logger.error("没有要扫描的股票！请在命令行指定或在 config.py 中配置")
        return

    # 创建扫描器
    scanner = SmartMoneyScanner()

    # 执行扫描
    if len(tickers_to_scan) == 1:
        # 单个股票
        result = scanner.scan_stock(
            tickers_to_scan[0],
            period=args.period,
            analyze_structure=args.structure
        )

        if result['success']:
            print("\n" + result['report'])
        else:
            print(f"\n扫描失败: {result.get('error', '未知错误')}")

    else:
        # 批量扫描
        results = scanner.scan_batch(
            tickers_to_scan,
            period=args.period,
            analyze_structure=args.structure
        )

        # 打印摘要
        print("\n" + "=" * 70)
        print("批量扫描结果摘要 (双向评分)")
        print("=" * 70)

        for ticker, result in results.items():
            if result['success']:
                score = result['score']
                rating = result['rating']
                signal_count = result['signal_count']
                inflow_count = result.get('inflow_count', 0)
                outflow_count = result.get('outflow_count', 0)

                rating_emoji = {
                    'STRONG_BUY': '🚀🚀',
                    'BUY': '🚀',
                    'NEUTRAL': '⚪',
                    'SELL': '⚠️',
                    'STRONG_SELL': '🛑🛑'
                }.get(rating, '')

                print(f"\n{ticker}:")
                print(f"  综合评分: {score:+.1f}/10")
                print(f"  综合评级: {rating} {rating_emoji}")
                print(f"  触发信号: {signal_count} 个 (进场: {inflow_count}, 离场: {outflow_count})")
            else:
                print(f"\n{ticker}: ❌ 失败 - {result.get('error', '未知错误')}")


if __name__ == '__main__':
    main()
