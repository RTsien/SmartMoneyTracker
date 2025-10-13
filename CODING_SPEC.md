# SmartMoneyTracker 项目规格说明

## 1. 项目概述

### 1.1. 目标
本项目旨在创建一个模块化的Python应用程序，用于自动化扫描和分析A股、美股、港股市场的股票，识别“大资金”（即机构投资者）从**进场（吸筹）到离场（派发）**的全周期信号。

### 1.2. 核心原则
系统不依赖任何单一指标。它将整合来自价量分析、技术指标、市场微观结构、股东披露文件和宏观资金流等多个维度的数据，计算出一个综合性的“机构动向评分”（范围从-10到+10），并生成分析报告，以全面评估大资金的真实意图。

### 1.3. 技术栈

- **语言**: Python 3.9+
- **核心库**: Pandas, NumPy, Requests, Matplotlib/Plotly
- **数据接口**: Tushare, AkShare, yfinance (或其他美股/港股API)
- **并发处理** (可选): concurrent.futures 或 asyncio 以加速多股票扫描

## 2. 系统架构

项目将采用模块化设计,分为数据层、分析层、聚合层和报告层。

```
smart-money-tracker/
│
├── main.py                 # 主程序入口，协调扫描流程
├── config.py               # 配置文件 (API密钥, 股票池, 信号权重, 阈值等)
├── requirements.txt        # 项目依赖库
│
├── data_fetcher/           # 数据获取模块
│   ├── __init__.py
│   └── manager.py          # 统一的数据API管理器
│
├── analysis/               # 信号分析模块 (核心逻辑)
│   ├── __init__.py
│   ├── price_volume_signals.py   # 价量关系信号 (吸筹与派发)
│   ├── indicator_signals.py      # 技术指标信号 (背离等)
│   ├── disclosure_signals.py     # 公开披露信号 (股东, 公告等)
│   ├── microstructure_signals.py # 微观结构信号 (Level-2)
│   └── relative_strength.py      # 相对强弱信号
│
├── aggregator/             # 信号聚合模块
│   ├── __init__.py
│   └── scorer.py           # 信号计分与综合评级
│
└── reporting/              # 报告生成模块
    ├── __init__.py
    └── generator.py        # 生成文本或HTML报告
```

---

## 3. 数据需求与来源 (Data Requirements & Sources)

`data_fetcher/manager.py` 模块将负责从不同来源获取数据。

| 数据类别 | 所需字段 | 推荐数据源/接口 | 对应分析章节 |
| :--- | :--- | :--- | :--- |
| **日线行情** | 开/高/低/收/成交量/成交额 | Tushare (`daily`), yfinance | 第一、二、五节 |
| **Level-2 行情** | 十档盘口, 逐笔成交/委托 [1, 2, 3, 4, 5] | 商业数据提供商 (如万得, 东方财富Choice) | 第四节 |
| **股东户数** | 股东户数, 报告期 | Tushare (`stk_holdernumber`) [6] | 第三节 |
| **十大股东** | 股东名称, 持股数, 变动 | Tushare (`top10_holders`), AkShare | 第三节 |
| **董监高持股** | 变动人, 变动股数, 日期 | Tushare (`stk_hold_change`) | 第三节 |
| **北向/南向资金** | 持股明细, 每日流动 | Tushare (`hk_hold`), Eastmoney API | 第六节 |
| **美股机构持仓** | 13F报告数据 | SEC EDGAR, 第三方API | 第六节 |
| **港股股东披露** | 披露易(DI)数据 | 港交所网站 (需爬虫), 商业数据提供商 | 第六节 |
| **公司公告/新闻** | 标题, 内容, 日期 | 巨潮资讯网 (A股), 各交易所官网, 新闻API | 第三节 |

---

## 4. 核心模块规格 (Core Modules Specification)

### 4.1. `analysis/price_volume_signals.py` (价量关系信号)

  * **进场信号 (Accumulation):**
    * `detect_accumulation_breakout(df, vol_multiplier)`: 检测成交量显著放大（大于`vol_multiplier`倍均量）的向上突破。
    * `detect_wyckoff_spring(df)`: 识别威科夫吸筹模式中的“弹簧”或“震仓”形态。
    * **返回:** `(True, 'SIGNAL_NAME', date)` 或 `(False, None, None)`。

  * **离场信号 (Distribution):**
    * `detect_high_volume_stagnation(df, vol_multiplier)`: 检测高位放量但价格停滞。
    * `detect_high_volume_decline(df, vol_multiplier)`: 检测放量下跌。
    * `detect_break_support(df, vol_multiplier)`: 检测放量跌破关键支撑位。
    * **返回:** `(True, 'SIGNAL_NAME', date)` 或 `(False, None, None)`。

### 4.2. `analysis/indicator_signals.py` (技术指标信号)

  * `detect_obv_divergence(df, lookback_period)`:
      * **逻辑:** 在`lookback_period`内，同时检测OBV的看涨背离（价格新低，OBV更高）和看跌背离（价格新高，OBV更低）。
      * **返回:** `('BULLISH_DIVERGENCE', date)` 或 `('BEARISH_DIVERGENCE', date)` 或 `(None, None)`。

  * `detect_mfi_signals(df, lookback_period)`:
      * **逻辑:** 检测MFI的看涨背离、看跌背离，以及是否进入超卖区(<20)或超买区(>80)。
      * **返回:** 信号名称列表，如 ``。

### 4.3. `analysis/disclosure_signals.py` (公开披露信号)

  * `analyze_shareholder_structure(ticker, market)`:
      * **逻辑:**
          * **A股:** 对比连续季度的前十大流通股东，识别头部机构的新进/增持（进场信号）或减持/退出（离场信号）。同时分析股东户数变化，减少为进场信号，增加为离场信号。
          * **美股:** 解析连续季度的13F报告，识别知名机构的建仓/增持或减持/清仓。
          * **港股:** 监控披露易(DI)数据，发现大股东持股比例跨越整数百分比的增持或减持申报。
      * **返回:** 信号名称列表，如 ``。

### 4.4. `analysis/microstructure_signals.py` (微观结构信号)
  * `analyze_order_book(level2_data)`:
      * **逻辑:** 识别是否存在持续、真实的“买单墙”（进场信号）或“卖盘压单”（离场信号）。
      * **返回:** `'BID_WALL_SUPPORT'` 或 `'ASK_WALL_PRESSURE'` 或 `None`。

### 4.5. `analysis/relative_strength.py` (相对强弱信号)

  * `analyze_rsp(stock_df, benchmark_df)`:
      * **逻辑:** 计算个股与基准（行业ETF或大盘指数）的相对强弱比率（RSP）。持续上行的RSP为进场信号，持续下行为离场信号 [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]。
      * **返回:** `'STRONG'` (进场), `'WEAK'` (离场), 或 `'NEUTRAL'`。

---

## 5. 信号聚合与报告 (Aggregation & Reporting)

### 5.1. `aggregator/scorer.py`

  * `class SignalAggregator`:
      * **`__init__(self, config)`:** 加载`config.py`中定义的信号权重。
      * **`calculate_score(signals)`:**
          * **逻辑:** 接收一个包含所有已触发信号的字典。根据预设的权重表（进场信号为正，离场信号为负）累加分数。
          * **权重表示例 (在`config.py`中定义):**
            ```python
            SIGNAL_WEIGHTS = {
                # Inflow Signals (Positive Score)
                'ACCUMULATION_BREAKOUT': 2,
                'OBV_BULLISH_DIVERGENCE': 2,
                'NEW_INSTITUTION': 3,
                'SHAREHOLDER_COUNT_DECREASE': 1,
                'RSP_STRONG': 1,

                # Outflow Signals (Negative Score)
                'HIGH_VOLUME_STAGNATION': -2,
                'OBV_BEARISH_DIVERGENCE': -2,
                'INSTITUTIONAL_SELL_OFF': -3,
                'BREAK_SUPPORT_HEAVY_VOLUME': -3,
                'RSP_WEAK': -1
            }
            ```
          * **返回:** 一个综合动向分数 (e.g., -10 到 +10) 和评级 (`'STRONG_SELL'`, `'SELL'`,`'NEUTRAL'`, `'BUY'`, `'STRONG_BUY'`)。
          * **评分-评级映射:**
            - `+6 到 +10`: `'STRONG_BUY'` (强烈吸筹)
            - `+2 到 +5`: `'BUY'` (温和吸筹)
            - `-1 到 +1`: `'NEUTRAL'` (中性)
            - `-5 到 -2`: `'SELL'` (温和派发)
            - `-10 到 -6`: `'STRONG_SELL'` (强烈派发)

### 5.2. `reporting/generator.py`

  * `generate_report(ticker, score, rating, triggered_signals)`:
      * **逻辑:** 将分析结果格式化为人类可读的报告。
      * **输出示例:**
        ```
        ===== Smart Money Tracker Report =====
        Ticker: 600519.SH
        Date: 2025-10-13
        Overall Score: +7/10 (STRONG_BUY)

        --- Inflow Signals Triggered ---
        [+] ACCUMULATION_BREAKOUT (Score: +2) on 2025-10-12
        [+] OBV_BULLISH_DIVERGENCE (Score: +2)
        [+] NEW_INSTITUTION (Score: +3) - China Merchants Fund entered top 10 holders.
        [+] RSP_STRONG (Score: +1) - Outperforming CSI Liquor Index.

        --- Outflow Signals Triggered ---
        (None)

        Recommendation: High probability of institutional accumulation. Trend is bullish.
        ```

---

## 6. 依赖项 (`requirements.txt`)

```
pandas>=1.5.0
numpy>=1.23.0
requests>=2.28.0
tushare>=1.2.80
akshare>=1.9.0
yfinance>=0.2.0
matplotlib>=3.6.0
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
