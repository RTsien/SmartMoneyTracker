"""
SmartMoneyTracker 使用示例
演示如何使用 API 进行股票分析
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
        print(f"风险评分: {result['risk_score']}/10")
        print(f"风险等级: {result['risk_level']}")
        print(f"触发信号数: {result['signal_count']}")

        # 查看触发的信号
        if result['signal_count'] > 0:
            print("\n触发的信号:")
            for signal_name, signal_info in result['triggered_signals'].items():
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
            risk_level = result['risk_level']
            risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(risk_level, '')

            print(f"{ticker}:")
            print(f"  风险评分: {result['risk_score']}/10 ({risk_level}) {risk_emoji}")
            print(f"  触发信号: {result['signal_count']} 个")
            print(f"  建议: {result['recommendation'][:50]}...")
            print()


def example_custom_config():
    """示例：使用自定义配置"""
    print("\n" + "=" * 60)
    print("示例 3: 自定义配置")
    print("=" * 60)

    # 临时修改配置
    original_weights = config.SIGNAL_WEIGHTS.copy()

    # 增加 OBV 背离的权重
    config.SIGNAL_WEIGHTS['OBV_DIVERGENCE'] = 3

    print("自定义配置:")
    print(f"  OBV_DIVERGENCE 权重: {config.SIGNAL_WEIGHTS['OBV_DIVERGENCE']}")

    scanner = SmartMoneyScanner()
    result = scanner.scan_stock('600519.SH')

    if result['success']:
        print(f"\n风险评分: {result['risk_score']}/10 ({result['risk_level']})")

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
        print(f"\n风险评分: {result['risk_score']}/10")
        print(f"风险等级: {result['risk_level']}")
        print(f"触发信号数: {result['signal_count']}")
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
