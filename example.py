"""
SmartMoneyTracker 使用示例 (双向分析系统)
演示如何使用 API 进行机构资金动向分析

评分系统: -10 to +10
- 正分: 机构进场/吸筹 (Accumulation)
- 负分: 机构离场/派发 (Distribution)
"""

from main import SmartMoneyScanner
import config

# 方式1: 使用 SmartMoneyScanner 类
def example_scan_single_stock():
    """示例：扫描单个股票"""
    print("=" * 60)
    print("示例 1: 扫描单个股票")
    print("=" * 60)

    # 创建扫描器
    scanner = SmartMoneyScanner()

    # 扫描贵州茅台
    ticker = '600519.SH'
    result = scanner.scan_stock(ticker, period=250, analyze_structure=False)

    if result['success']:
        # 打印报告
        print(result['report'])

        # 访问具体数据
        print("\n详细信息:")
        print(f"综合评分: {result['score']:+.1f}/10 (-10 to +10)")
        print(f"综合评级: {result['rating']}")
        print(f"触发信号数: {result['signal_count']} (进场: {result['inflow_count']}, 离场: {result['outflow_count']})")

        # 查看进场信号
        if result['inflow_count'] > 0:
            print("\n进场信号 (吸筹) 🟢:")
            for signal_name, signal_info in result['inflow_signals'].items():
                print(f"  - {signal_name}: 权重 +{signal_info['weight']}")

        # 查看离场信号
        if result['outflow_count'] > 0:
            print("\n离场信号 (派发) 🔴:")
            for signal_name, signal_info in result['outflow_signals'].items():
                print(f"  - {signal_name}: 权重 {signal_info['weight']}")
    else:
        print(f"扫描失败: {result.get('error')}")


def example_scan_batch():
    """示例：批量扫描多只股票"""
    print("\n" + "=" * 60)
    print("示例 2: 批量扫描股票")
    print("=" * 60)

    scanner = SmartMoneyScanner()

    # 定义股票列表
    tickers = [
        '600519.SH',  # 贵州茅台
        '000858.SZ',  # 五粮液
        '000333.SZ',  # 美的集团
    ]

    # 批量扫描
    results = scanner.scan_batch(tickers, period=250, analyze_structure=False)

    # 打印摘要
    print("\n扫描结果摘要:")
    print("-" * 60)

    for ticker, result in results.items():
        if result['success']:
            rating = result['rating']
            score = result['score']
            rating_emoji = {
                'STRONG_BUY': '🚀🚀',
                'BUY': '🚀',
                'NEUTRAL': '⚪',
                'SELL': '⚠️',
                'STRONG_SELL': '🛑🛑'
            }.get(rating, '')

            print(f"{ticker}:")
            print(f"  综合评分: {score:+.1f}/10")
            print(f"  综合评级: {rating} {rating_emoji}")
            print(f"  触发信号: {result['signal_count']} 个 (进场: {result['inflow_count']}, 离场: {result['outflow_count']})")
            print(f"  建议: {result['recommendation'][:60]}...")
            print()


def example_custom_config():
    """示例：使用自定义配置"""
    print("\n" + "=" * 60)
    print("示例 3: 自定义配置")
    print("=" * 60)

    # 临时修改配置
    original_weights = config.SIGNAL_WEIGHTS.copy()

    # 增加 OBV 看涨背离的权重
    config.SIGNAL_WEIGHTS['OBV_BULLISH_DIVERGENCE'] = 3
    config.SIGNAL_WEIGHTS['OBV_BEARISH_DIVERGENCE'] = -3

    print("自定义配置:")
    print(f"  OBV_BULLISH_DIVERGENCE 权重: +{config.SIGNAL_WEIGHTS['OBV_BULLISH_DIVERGENCE']}")
    print(f"  OBV_BEARISH_DIVERGENCE 权重: {config.SIGNAL_WEIGHTS['OBV_BEARISH_DIVERGENCE']}")

    scanner = SmartMoneyScanner()
    result = scanner.scan_stock('600519.SH')

    if result['success']:
        print(f"\n综合评分: {result['score']:+.1f}/10")
        print(f"综合评级: {result['rating']}")

    # 恢复原配置
    config.SIGNAL_WEIGHTS = original_weights


def example_analyze_us_stock():
    """示例：分析美股"""
    print("\n" + "=" * 60)
    print("示例 4: 分析美股")
    print("=" * 60)

    scanner = SmartMoneyScanner()

    # 分析 Apple
    ticker = 'AAPL'
    print(f"分析 {ticker}...")

    result = scanner.scan_stock(ticker, period=250, analyze_structure=False)

    if result['success']:
        print(f"\n综合评分: {result['score']:+.1f}/10")
        print(f"综合评级: {result['rating']}")
        print(f"触发信号数: {result['signal_count']} (进场: {result['inflow_count']}, 离场: {result['outflow_count']})")
    else:
        print(f"分析失败: {result.get('error')}")


def example_get_raw_data():
    """示例：获取原始数据进行自定义分析"""
    print("\n" + "=" * 60)
    print("示例 5: 获取原始数据")
    print("=" * 60)

    scanner = SmartMoneyScanner()

    ticker = '600519.SH'
    result = scanner.scan_stock(ticker)

    if result['success']:
        # 访问原始数据 DataFrame
        df = result['data']

        print(f"数据记录数: {len(df)}")
        print(f"数据列: {df.columns.tolist()}")
        print(f"\n最近5日数据:")
        print(df[['date', 'close', 'volume', 'obv', 'rsi']].tail())


if __name__ == '__main__':
    """运行所有示例"""

    # 示例 1: 扫描单个股票
    example_scan_single_stock()

    # 示例 2: 批量扫描
    # example_scan_batch()

    # 示例 3: 自定义配置
    # example_custom_config()

    # 示例 4: 分析美股
    # example_analyze_us_stock()

    # 示例 5: 获取原始数据
    # example_get_raw_data()

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)
