"""
配置文件 - SmartMoneyTracker
包含 API 密钥、股票池、信号权重和分析参数
"""

import os
from typing import Dict, List

# =============================================================================
# API 配置
# =============================================================================

# 数据源优先级配置 (A股)
# 可选: 'akshare', 'tushare'
A_STOCK_DATA_SOURCE = os.getenv('A_STOCK_DATA_SOURCE', 'akshare')

# Tushare Token (A股数据)
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')

# AkShare 配置
AKSHARE_ENABLED = True

# yfinance 配置 (美股/港股数据)
YFINANCE_ENABLED = True

# =============================================================================
# 股票池配置
# =============================================================================

# 默认股票池
STOCK_POOL: List[str] = [
    # A股示例
    '600519.SH',  # 贵州茅台
    '000858.SZ',  # 五粮液
    '000333.SZ',  # 美的集团

    # 美股示例
    # 'AAPL',       # Apple
    # 'MSFT',       # Microsoft
    # 'TSLA',       # Tesla

    # 港股示例
    # '0700.HK',   # 腾讯控股
    # '9988.HK',   # 阿里巴巴
]

# =============================================================================
# 信号权重配置 (Bidirectional: -10 to +10)
# =============================================================================
# 正数权重: 机构进场/吸筹信号 (Accumulation/Inflow)
# 负数权重: 机构离场/派发信号 (Distribution/Outflow)

SIGNAL_WEIGHTS: Dict[str, int] = {
    # ========== 进场信号 (正数权重) ==========

    # 价量关系 - 吸筹信号 (Accumulation Patterns)
    'ACCUMULATION_BREAKOUT': 2,            # 放量突破横盘区
    'WYCKOFF_SPRING': 2,                   # 威科夫弹簧/震仓

    # 技术指标 - 看涨信号 (Bullish Signals)
    'OBV_BULLISH_DIVERGENCE': 2,           # OBV看涨背离 (价格新低，OBV更高)
    'MFI_OVERSOLD': 1,                     # MFI超卖 (< 20)
    'MFI_BULLISH_DIVERGENCE': 2,           # MFI看涨背离

    # 结构性信号 - 吸筹证据 (Structural Accumulation)
    'NEW_INSTITUTION': 3,                  # 新机构进入十大股东 (最高权重)
    'INSTITUTIONAL_BUY_IN': 3,             # 机构增持
    'SHAREHOLDER_COUNT_DECREASE': 1,       # 股东户数减少 (筹码集中)

    # 微观结构 - 买方压力 (Microstructure Buy Pressure)
    'BID_WALL_SUPPORT': 1,                 # 买单墙支撑

    # 相对强弱 - 跑赢市场 (Relative Strength)
    'RSP_STRONG': 1,                       # 相对强度强势 (跑赢大盘/行业)

    # ========== 离场信号 (负数权重) ==========

    # 价量关系 - 派发信号 (Distribution Patterns)
    'HIGH_VOLUME_STAGNATION': -2,          # 高位放量滞涨
    'HIGH_VOLUME_DECLINE': -2,             # 放量下跌
    'BREAK_SUPPORT_HEAVY_VOLUME': -3,      # 放量跌破支撑 (最强离场信号)
    'LOW_VOLUME_RISE': -1,                 # 高位缩量上涨

    # 技术指标 - 看跌信号 (Bearish Signals)
    'OBV_BEARISH_DIVERGENCE': -2,          # OBV看跌背离 (价格新高，OBV更低)
    'MFI_OVERBOUGHT': -1,                  # MFI超买 (> 80)
    'MFI_BEARISH_DIVERGENCE': -2,          # MFI看跌背离
    'RSI_BEARISH_DIVERGENCE': -1,          # RSI看跌背离
    'MACD_BEARISH_DIVERGENCE': -2,         # MACD看跌背离

    # 结构性信号 - 派发证据 (Structural Distribution)
    'INSTITUTIONAL_SELL_OFF': -3,          # 机构大幅减持 (最高权重)
    'SHAREHOLDER_COUNT_INCREASE': -1,      # 股东户数增加 (筹码分散)
    'INSIDER_SELLING': -3,                 # 董监高减持

    # 微观结构 - 卖方压力 (Microstructure Sell Pressure)
    'ASK_WALL_PRESSURE': -1,               # 卖盘压单

    # 相对强弱 - 跑输市场 (Relative Weakness)
    'RSP_WEAK': -1,                        # 相对强度疲弱 (跑输大盘/行业)
    'SECTOR_UNDERPERFORMANCE': -1,         # 跑输行业板块

    # 基本面催化剂 (Fundamental Catalysts)
    'POSITIVE_NEWS': 3,                    # 正面新闻/催化剂
    'NEGATIVE_NEWS': -3,                   # 负面新闻
    'EARNINGS_BEAT': 4,                    # 业绩超预期
    'EARNINGS_WARNING': -4,                # 业绩预警
    'POLICY_TAILWIND': 3,                  # 有利政策
    'POLICY_HEADWIND': -3,                 # 不利政策
}

# =============================================================================
# 分析参数配置
# =============================================================================

# 价量分析参数
PV_PARAMS = {
    'lookback_period': 60,          # 回看周期（天）
    'vol_multiplier': 2.0,          # 放量倍数
    'price_change_threshold': 0.02, # 价格变动阈值（2%）
    'decline_threshold': 0.03,      # 下跌阈值（3%）
    'support_ma_periods': [20, 60, 120],  # 均线支撑周期
}

# 技术指标参数
INDICATOR_PARAMS = {
    'obv_lookback': 60,             # OBV回看周期
    'mfi_period': 14,               # MFI计算周期
    'mfi_lookback': 60,             # MFI回看周期
    'rsi_period': 14,               # RSI计算周期
    'macd_fast': 12,                # MACD快线周期
    'macd_slow': 26,                # MACD慢线周期
    'macd_signal': 9,               # MACD信号线周期
}

# 结构性分析参数
STRUCTURAL_PARAMS = {
    'shareholder_increase_threshold': 0.15,  # 股东户数增加阈值（15%）
    'institutional_reduction_threshold': 0.05,  # 机构减持阈值（5%）
    'insider_selling_threshold': 0.02,       # 内部人减持阈值（2%）
}

# 相对强弱参数
RELATIVE_STRENGTH_PARAMS = {
    'rsp_ma_period': 20,            # RSP移动平均周期
    'lookback_period': 60,          # 回看周期
}

# =============================================================================
# 评分配置 (Bidirectional Scoring: -10 to +10)
# =============================================================================

# 评分到评级的映射
SCORE_TO_RATING = {
    'STRONG_BUY': (6, 10),       # +6 到 +10: 强烈买入 (强力吸筹)
    'BUY': (2, 5),               # +2 到 +5: 买入 (温和吸筹)
    'NEUTRAL': (-1, 1),          # -1 到 +1: 中性
    'SELL': (-5, -2),            # -5 到 -2: 卖出 (温和派发)
    'STRONG_SELL': (-10, -6),    # -10 到 -6: 强烈卖出 (强力派发)
}

# =============================================================================
# 市场配置
# =============================================================================

# 市场基准指数
MARKET_BENCHMARKS = {
    'SH': '000001.SH',    # 上证指数
    'SZ': '399001.SZ',    # 深证成指
    'US': '^GSPC',        # S&P 500
    'HK': '^HSI',         # 恒生指数
}

# =============================================================================
# 数据缓存配置
# =============================================================================

CACHE_ENABLED = True
CACHE_DIR = './cache'
CACHE_EXPIRY_DAYS = 1  # 缓存过期天数

# =============================================================================
# 日志配置
# =============================================================================

LOG_LEVEL = 'INFO'
LOG_FILE = 'smartmoney_tracker.log'

# =============================================================================
# 报告配置
# =============================================================================

REPORT_OUTPUT_DIR = './reports'
REPORT_FORMAT = 'text'  # 可选: 'text', 'html', 'json'
