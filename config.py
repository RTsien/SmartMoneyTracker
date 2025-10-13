"""
配置文件 - SmartMoneyTracker
包含 API 密钥、股票池、信号权重和分析参数
"""

import os
from typing import Dict, List

# =============================================================================
# API 配置
# =============================================================================

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
    # '00700.HK',   # 腾讯控股
    # '09988.HK',   # 阿里巴巴
]

# =============================================================================
# 信号权重配置
# =============================================================================

SIGNAL_WEIGHTS: Dict[str, int] = {
    # 价量关系信号 (1-3分)
    'HIGH_VOLUME_STAGNATION': 2,           # 高位放量滞涨
    'HIGH_VOLUME_DECLINE': 2,              # 放量下跌
    'BREAK_SUPPORT_HEAVY_VOLUME': 3,       # 放量跌破支撑
    'LOW_VOLUME_RISE': 1,                  # 高位缩量上涨

    # 技术指标信号 (2-3分)
    'OBV_DIVERGENCE': 2,                   # OBV看跌背离
    'MFI_DIVERGENCE': 2,                   # MFI看跌背离
    'RSI_DIVERGENCE': 1,                   # RSI看跌背离
    'MACD_DIVERGENCE': 2,                  # MACD看跌背离

    # 结构性信号 (2-4分)
    'INSTITUTIONAL_SELL_OFF': 4,           # 机构大幅减持
    'SHAREHOLDER_COUNT_INCREASE': 3,       # 股东户数显著增加
    'INSIDER_SELLING': 3,                  # 董监高减持

    # 相对强弱信号 (1-2分)
    'RELATIVE_STRENGTH_WEAK': 2,           # 相对强度疲弱
    'SECTOR_UNDERPERFORMANCE': 1,          # 跑输行业板块

    # 基本面催化剂 (3-4分)
    'NEGATIVE_NEWS': 3,                    # 负面新闻
    'EARNINGS_WARNING': 4,                 # 业绩预警
    'POLICY_HEADWIND': 3,                  # 不利政策
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
# 风险评分配置
# =============================================================================

# 风险等级阈值
RISK_THRESHOLDS = {
    'LOW': (0, 3),        # 0-3分: 低风险
    'MEDIUM': (4, 6),     # 4-6分: 中等风险
    'HIGH': (7, 10),      # 7-10分: 高风险
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
