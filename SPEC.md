# SmartMoneyTracker 项目规格说明

## 1. 项目概述

### 1.1. 目标

本项目旨在创建一个模块化的Python应用程序，用于自动化扫描和分析A股、美股、港股市场的股票，识别大资金（机构投资者）可能正在撤离的信号。

### 1.2. 核心原则

系统不依赖任何单一指标。它将整合来自价量分析、技术指标、微观结构、股东结构和宏观资金流等多个维度的数据，计算出一个综合"撤离风险评分"，并生成分析报告。

### 1.3. 技术栈

- **语言**: Python 3.9+
- **核心库**: Pandas, NumPy, Requests, Matplotlib/Plotly
- **数据接口**: Tushare, AkShare, yfinance (或其他美股/港股API)
- **并发处理** (可选): concurrent.futures 或 asyncio 以加速多股票扫描

---

## 2. 系统架构

项目将采用模块化设计，分为数据层、分析层、聚合层和报告层。

```
institutional-exit-scanner/
│
├── main.py                 # 主程序入口，协调扫描流程
├── config.py               # 配置文件 (API密钥, 股票池, 阈值等)
├── requirements.txt        # 项目依赖库
│
├── data_fetcher/           # 数据获取模块
│   ├── __init__.py
│   └── manager.py          # 统一的数据API管理器
│
├── analysis/               # 信号分析模块 (核心逻辑)
│   ├── __init__.py
│   ├── pv_signals.py       # 价量关系信号
│   ├── indicator_signals.py # 技术指标信号
│   ├── structural_signals.py # 结构性信号 (股东, 公告等)
│   └── relative_strength.py # 相对强弱信号
│
├── aggregator/             # 风险聚合模块
│   ├── __init__.py
│   └── scorer.py           # 信号计分与风险评级
│
└── reporting/              # 报告生成模块
    ├── __init__.py
    └── generator.py        # 生成文本或HTML报告
```

---

## 3. 数据需求与来源

`data_fetcher/manager.py` 模块将负责从不同来源获取数据。

| 数据类别 | 所需字段 | 推荐数据源/接口 | 对应分析章节 |
|---------|---------|---------------|-------------|
| 日线行情 | 开/高/低/收/成交量/成交额 | Tushare (daily), yfinance | 第二、三、六节 |
| Level-2 行情 | 十档盘口, 逐笔成交/委托 | 商业数据提供商 (如万得, 东方财富Choice) | 第四节 |
| 股东户数 | 股东户数, 报告期 | Tushare (stk_holdernumber) | 第五节 |
| 十大股东 | 股东名称, 持股数, 变动 | Tushare (top10_holders), AkShare | 第五节 |
| 董监高持股 | 变动人, 变动股数, 日期 | Tushare (stk_hold_change) | 第五节 |
| 北向/南向资金 | 持股明细, 每日流动 | Tushare (hk_hold), Eastmoney API | 第七节 |
| 美股机构持仓 | 13F报告数据 | SEC EDGAR数据库, 第三方API (如FMP) | 第七节 |
| 港股股东披露 | 披露易(DI)数据 | 港交所网站 (需爬虫), 商业数据提供商 | 第七节 |
| 公司公告/新闻 | 标题, 内容, 日期 | 巨潮资讯网 (A股), 各交易所官网, 新闻API | 第五节 |

---

## 4. 核心模块规格

### 4.1. analysis/pv_signals.py (价量关系信号)

#### `detect_high_volume_stagnation(df, lookback_period, vol_multiplier, price_change_threshold)`

- **逻辑**: 检测在`lookback_period`定义的上涨趋势后，是否出现成交量显著放大（例如，大于`vol_multiplier`倍均量），但股价涨幅低于`price_change_threshold`的情况。
- **返回**: `True` 或 `False`，以及信号发生的日期。

#### `detect_high_volume_decline(df, vol_multiplier, decline_threshold)`

- **逻辑**: 检测股价单日跌幅超过`decline_threshold`，且成交量大于`vol_multiplier`倍均量。
- **返回**: `True` 或 `False`。

#### `detect_break_support(df, support_levels, vol_multiplier)`

- **逻辑**: 检测股价是否放量（大于`vol_multiplier`倍均量）跌破关键支撑位（如60日均线、前期低点）。
- **返回**: `True` 或 `False`，以及被跌破的支撑位。

---

### 4.2. analysis/indicator_signals.py (技术指标信号)

#### `detect_obv_bearish_divergence(df, lookback_period)`

- **逻辑**: 在`lookback_period`内，寻找股价创出新高（HH），但OBV指标未能创出新高（形成LH）的看跌背离形态。
- **返回**: `True` 或 `False`。

#### `detect_mfi_bearish_divergence(df, lookback_period)`

- **逻辑**: 类似于OBV，检测股价与MFI指标的看跌背离。
- **返回**: `True` 或 `False`。

---

### 4.3. analysis/structural_signals.py (结构性信号)

#### `analyze_institutional_holdings(ticker, market)`

- **逻辑**:
  - **A股**: 对比连续两个季度的前十大流通股东，识别头部公募基金、QFII的显著减持。
  - **美股**: 解析两个季度的13F报告，识别知名机构的清仓或大幅减持。
  - **港股**: 监控披露易(DI)数据，发现大股东持股比例跨越整数百分比的减持申报。
- **返回**: 包含减持机构名称和变动比例的列表。

#### `analyze_shareholder_count(ticker)`

- **逻辑**: 获取最新的股东户数数据，与上一期对比。如果户数显著增加（例如 > 15%），同时机构持股比例下降，则信号成立。
- **返回**: `True` 或 `False`。

---

### 4.4. analysis/relative_strength.py (相对强弱信号)

#### `analyze_rsp(stock_df, benchmark_df)`

- **逻辑**: 计算个股价格与基准（如行业ETF或大盘指数）价格的比率（RSP），判断RSP曲线是否跌破关键趋势线或形成顶背离。
- **返回**: `'WEAK'` 或 `'NEUTRAL'`。

---

## 5. 风险聚合与报告

### 5.1. aggregator/scorer.py

#### `class RiskAggregator`

**`__init__(self, config)`**
- 加载`config.py`中定义的信号权重。

**`calculate_score(signals)`**
- **逻辑**: 接收一个包含所有已触发信号的字典。根据预设的权重表（如下例）累加分数。

**权重表示例** (在`config.py`中定义):

```python
SIGNAL_WEIGHTS = {
    'HIGH_VOLUME_STAGNATION': 1,
    'OBV_DIVERGENCE': 2,
    'INSTITUTIONAL_SELL_OFF': 3,
    'BREAK_SUPPORT_HEAVY_VOLUME': 3,
    # ... 其他信号
}
```

- **返回**: 一个综合风险分数 (e.g., 0-10) 和风险等级 (`'LOW'`, `'MEDIUM'`, `'HIGH'`)。

---

### 5.2. reporting/generator.py

#### `generate_report(ticker, risk_score, risk_level, triggered_signals)`

- **逻辑**: 将分析结果格式化为人类可读的报告。

**输出示例**:

```
===== Institutional Exit Scan Report =====
Ticker: 600519.SH
Date: 2025-10-13
Risk Score: 7/10 (HIGH)

Triggered Signals:
[+] HIGH_VOLUME_STAGNATION (Score: 1) on 2025-09-15
[+] MFI_BEARISH_DIVERGENCE (Score: 2)
[+] INSTITUTIONAL_SELL_OFF (Score: 3) - China Merchants Fund reduced position by 5%.
[+] RELATIVE_STRENGTH_WEAK (Score: 1) - Underperforming CSI Liquor Index.

Recommendation: High probability of institutional distribution. Caution is advised.
```

---

## 6. 依赖项 (requirements.txt)

```
pandas>=1.5.0
numpy>=1.23.0
requests>=2.28.0
tushare>=1.2.80
akshare>=1.9.0
yfinance>=0.2.0
matplotlib>=3.6.0
plotly>=5.11.0
```

---

## 7. 实施建议

### 7.1. 开发阶段

1. **Phase 1**: 实现数据获取层 (`data_fetcher/manager.py`)
2. **Phase 2**: 实现核心分析模块 (`analysis/`)
3. **Phase 3**: 实现风险聚合器 (`aggregator/scorer.py`)
4. **Phase 4**: 实现报告生成器 (`reporting/generator.py`)
5. **Phase 5**: 集成主程序 (`main.py`) 并进行端到端测试

### 7.2. 测试策略

- 使用历史数据回测各个信号的准确性
- 对已知的机构撤离案例进行验证
- 调整信号权重以优化风险评分的准确性

### 7.3. 扩展性考虑

- 支持自定义信号权重配置
- 支持批量扫描股票池
- 支持实时监控模式（定时扫描）
- 支持多种报告格式输出（文本、HTML、JSON）
