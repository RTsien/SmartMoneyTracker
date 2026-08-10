# SmartMoneyTracker

[English](README.md) | **简体中文**

> 追踪"聪明钱"的足迹：基于多维度分析的机构资金进出场全周期识别系统

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 项目简介

SmartMoneyTracker 是一个模块化的 Python 应用程序，用于自动化扫描和分析 **A股、美股、港股** 市场的股票，识别大资金（机构投资者）从**进场（吸筹）到离场（派发）**的全周期信号。

在复杂的证券市场中，"大资金"由共同基金、养老基金、对冲基金、QFII 以及高净值投资者组成。它们的投资策略、时间视野和执行方式各不相同，在市场中留下了各异的信号。识别这些全周期信号对于：

- ✅ **风险管理**：避免在机构派发时"接飞刀"
- ✅ **机会捕捉**：识别机构吸筹建仓的早期信号
- ✅ **战术定位**：与机构情绪保持一致
- ✅ **趋势预判**：预判潜在的趋势启动与反转

至关重要。

## 🎯 核心特点

### 多维度分析框架

系统**不依赖任何单一指标**，而是整合多个独立分析领域的双向信号：

1. **价量关系分析**
   - **吸筹信号**：底部放量横盘、放量突破阻力位、威科夫吸筹模式（弹簧/LPS）
   - **派发信号**：高位放量滞涨、放量跌破关键支撑位、高位缩量上涨

2. **技术指标信号**
   - **吸筹信号**：OBV/MFI 看涨背离、MFI 超卖区（<20）
   - **派发信号**：OBV/MFI 看跌背离、MFI 超买区（>80）

3. **市场微观结构** ⚠️ *需要商业Level-2数据接口*
   - **吸筹信号**：关键支撑位持续买单墙
   - **派发信号**：关键阻力位持续卖盘压单
   - Level-2 盘口分析、订单失衡率（SOIR）、算法交易足迹识别
   - **说明**：此模块已实现接口规范，但需要商业数据源（万得/东方财富Choice等，费用数千至数万元/年）。当前使用免费数据源（AkShare/Tushare/yfinance）时，其他20+种信号已足够强大

4. **股东结构变化**
   - **吸筹信号**：新进机构股东、股东户数减少
   - **派发信号**：机构减持、股东户数增加
   - 董监高持股变动监控

5. **相对强弱分析**
   - **吸筹信号**：RSP 持续跑赢大盘/行业指数
   - **派发信号**：RSP 持续跑输大盘/行业指数
   - 个股与板块比较、个股与大盘背离识别

6. **基本面催化剂**
   - **吸筹催化剂**：新产品发布、行业格局改善、业绩超预期、有利政策
   - **派发催化剂**：财务造假、高管丑闻、业绩预警、不利监管

### 智能双向评分

- 基于权重的多信号聚合
- 综合动向评分（**-10 到 +10**）
  - **+6 到 +10**：STRONG_BUY（强烈买入）- 强烈吸筹信号
  - **+2 到 +5**：BUY（买入）- 温和吸筹信号
  - **-1 到 +1**：NEUTRAL（中性）- 无明确方向
  - **-5 到 -2**：SELL（卖出）- 温和派发信号
  - **-10 到 -6**：STRONG_SELL（强烈卖出）- 强烈派发信号
- 人类可读的分析报告

### AkQuant 指标引擎

- 使用 [AkQuant](https://github.com/akfamily/akquant) 作为量化计算基础库
- 默认通过 Rust 后端计算 SMA、OBV、RSI、MACD 和 MFI
- 可配置 `rust`、`python` 或 `auto` TA-Lib 兼容后端
- 行情获取层保持独立，因为 AkQuant 是策略与回测框架，不是行情数据源

## 🏗️ 系统架构

```
SmartMoneyTracker/
│
├── main.py                         # 主程序入口
├── config.py                       # 配置文件
├── requirements.txt                # 依赖库
│
├── data_fetcher/                   # 数据获取层
│   ├── __init__.py
│   └── manager.py                  # 统一数据API管理器
│
├── analysis/                       # 信号分析层（核心逻辑）
│   ├── __init__.py
│   ├── price_volume_signals.py    # 价量关系信号（吸筹与派发）
│   ├── indicator_signals.py       # 技术指标信号（背离等）
│   ├── disclosure_signals.py      # 公开披露信号（股东、公告等）
│   ├── microstructure_signals.py  # 微观结构信号（Level-2）
│   └── relative_strength.py       # 相对强弱信号
│
├── aggregator/                     # 信号聚合层
│   ├── __init__.py
│   └── scorer.py                  # 信号计分与综合评级
│
├── quant_engine/                  # 量化计算层
│   ├── __init__.py
│   └── akquant_adapter.py         # AkQuant 指标适配器
│
├── backtesting/                   # 时点安全回测层
│   ├── __init__.py
│   ├── engine.py                  # AkQuant 事件驱动信号回测器
│   └── validation.py              # 滚动样本外验证
│
├── disclosures/                   # 公告时点披露存储
├── monitoring/                    # 收盘后调度和告警
├── backtest.py                    # 回测与验证命令行
├── monitor.py                     # 定时监控命令行
├── snapshot_disclosures.py        # 时点快照采集
│
└── reporting/                      # 报告生成层
    ├── __init__.py
    └── generator.py               # 生成文本/HTML报告
```

## 🚀 快速开始

### Docker 部署（推荐）🐳

使用 Docker 一键部署，无需配置环境：

```bash
# 克隆项目
git clone https://github.com/RTsien/SmartMoneyTracker.git
cd SmartMoneyTracker

# 启动服务
docker-compose up -d

# 在浏览器中访问
# http://localhost:8001
```

详细说明请查看：[Docker 部署文档](DOCKER.md)

### 本地安装

#### 前置要求

- Python 3.10+
- pip 包管理器

#### 安装步骤

```bash
# 克隆项目
git clone https://github.com/RTsien/SmartMoneyTracker.git
cd SmartMoneyTracker

# 安装依赖
pip install -r requirements.txt

# 如需使用 Tushare，可在 config.py 中配置 Token（可选）
```

### 使用方式

#### 方式一：Web 界面 🌐

```bash
# 启动 Web 服务
python app.py

# 在浏览器中访问
# http://localhost:8001
```

**Web 界面特性**：
- 🎨 现代化的用户界面
- 📊 实时分析结果展示
- 📈 可视化评分和信号
- 🔄 支持单股和批量分析
- 📱 响应式设计，支持移动设备
- 📉 策略、基准、回撤和信号评分交互图表

#### 方式二：命令行

```python
from main import SmartMoneyScanner

# 初始化扫描器
scanner = SmartMoneyScanner()

# 扫描单个股票
result = scanner.scan_stock('600519.SH')  # A股：贵州茅台
if result['success']:
    print(result['report'])

# 批量扫描股票池
stocks = ['600519.SH', 'AAPL', '0700.HK']
results = scanner.scan_batch(stocks)

# 生成报告
for stock, result in results.items():
    if result['success']:
        print(f"\n{stock}:")
        print(f"Score: {result['score']:+.1f}/10")
        print(f"Rating: {result['rating']}")
```

#### 方式三：历史回测

对价量与技术指标策略运行历史回测：

```bash
python3 backtest.py 600519.SH --period 1000 --warmup 120
```

回测使用 AkQuant 事件驱动引擎。每个决策点只读取当时已经出现的 K 线，订单在
**下一根 K 线开盘价**成交。报告包含扣除交易成本后的收益、买入持有收益、超额
收益、年化收益和波动率、Sharpe、最大回撤、胜率及交易次数。手续费和滑点默认
启用，也可以调整或输出 JSON：

```bash
python3 backtest.py AAPL --commission-bps 10 --slippage-bps 5 --json
```

价量和技术指标信号默认纳入回测。结构性信号需要显式开启，并且只能读取时点
数据库中当时已经公开的披露记录，避免公告日期偏差和幸存者偏差。

运行滚动样本外验证。每折只用训练窗口选择信号频率，再在紧随其后的未见区间
评估：

```bash
python3 backtest.py 600519.SH --period 2000 --walk-forward \
  --train-bars 504 --test-bars 126 --step-bars 126 \
  --candidates 1,5,20
```

敏感性表会把所有候选频率放在相同的样本外窗口比较。

#### 收盘后监控与时点披露

```bash
# 按公告时间采集披露快照
python3 snapshot_disclosures.py 600519.SH

# 每个历史决策点只读取当时已公开的结构性数据
python3 backtest.py 600519.SH --include-structural

# 立即扫描所有市场一次，或持续运行调度器
python3 monitor.py --once
python3 monitor.py
```

调度器分别配置 A 股、港股和美股时间，自动抑制重复告警，写入本地 JSONL，
也可选配 Webhook。

### 输出示例

#### 示例 1：派发信号

```
===== Smart Money Tracker Report =====
Ticker: 600519.SH
Date: 2025-10-13
Overall Score: -7/10 (SELL)

--- Outflow Signals Triggered ---
[-] HIGH_VOLUME_STAGNATION (Score: -2) on 2025-09-15
    股价在大幅上涨后出现成交量激增但价格停滞

[-] MFI_BEARISH_DIVERGENCE (Score: -2)
    股价创新高但资金流量指标未能同步

[-] INSTITUTIONAL_SELL_OFF (Score: -3)
    China Merchants Fund 减持 5%

[-] RSP_WEAK (Score: -1)
    跑输 CSI 白酒指数

--- Inflow Signals Triggered ---
(None)

Recommendation:
机构派发概率较高，建议谨慎。大资金可能正在利用散户热情卖出筹码。
```

#### 示例 2：吸筹信号

```
===== Smart Money Tracker Report =====
Ticker: 000858.SZ
Date: 2025-10-13
Overall Score: +7/10 (BUY)

--- Inflow Signals Triggered ---
[+] ACCUMULATION_BREAKOUT (Score: +2) on 2025-10-10
    放量突破长期盘整区，成交量为近期均量的 2.5 倍

[+] OBV_BULLISH_DIVERGENCE (Score: +2)
    股价创新低但 OBV 拒绝下跌

[+] NEW_INSTITUTION (Score: +3)
    China Merchants Fund 新进入前十大股东

[+] SHAREHOLDER_COUNT_DECREASE (Score: +1)
    股东户数较上季度减少 15%

--- Outflow Signals Triggered ---
(None)

Recommendation:
机构吸筹概率高，趋势看涨。筹码正从散户向机构集中。
```

## 📊 支持的市场

| 市场 | 数据源 | 核心特色 |
|------|--------|----------|
| **A股** | **AkShare（默认腾讯行情，东方财富备用）**, Tushare | 北向资金监控、十大股东分析、股东户数分析 |
| **美股** | **AkShare（新浪）**，yfinance 备用 | 机构持股数据、日线行情数据 |
| **港股** | **AkShare（新浪）**，yfinance 备用 | 机构持股数据、港股通持股数据 |

## 📈 数据来源

- **日线行情**: 
  - A股: **AkShare 腾讯接口（默认）或东方财富接口**, Tushare 兜底
  - 美股/港股: **AkShare 新浪接口**，yfinance 兜底
- **Level-2 数据** ⚠️ **未实现（需商业接口）**: 东方财富 Choice、万得等商业数据提供商
  - 费用：数千至数万元/年
  - 用途：微观结构信号（买单墙、卖盘压单检测）
  - 说明：架构已预留接口，有数据源时可直接扩展
- **机构持仓**:
  - A股: **AkShare**, Tushare (top10_holders, stk_holdernumber)
  - 美股: **yfinance (已实现)** - 机构持股者数据
  - 港股: **yfinance + AkShare (已实现)** - 双数据源支持
- **资金流向**:
  - 北向资金: **AkShare**, Tushare (hk_hold)
  - 南向资金: Eastmoney API
- **公告新闻**: 巨潮资讯网、交易所官网

## 🔧 配置说明

在 `config.py` 中配置：

```python
# 数据源配置
A_STOCK_DATA_SOURCE = 'akshare'  # 可选: 'akshare' (默认), 'tushare'
AKSHARE_ENABLED = True
AKSHARE_HISTORY_SOURCE = 'tencent'  # 可选: 'tencent' (默认), 'eastmoney'
TUSHARE_TOKEN = "your_token_here"  # 仅在使用 Tushare 时需要

# 量化计算引擎
QUANT_ENGINE = 'akquant'             # 可选: 'akquant' (默认), 'native'
AKQUANT_TALIB_BACKEND = 'rust'       # 可选: 'rust', 'python', 'auto'

# 股票池
STOCK_POOL = [
    '600519.SH',  # 贵州茅台
    'AAPL',       # Apple
    '0700.HK'     # 腾讯控股
]

# 信号权重（双向评分）
SIGNAL_WEIGHTS = {
    # 吸筹信号（正分）
    'ACCUMULATION_BREAKOUT': 2,
    'OBV_BULLISH_DIVERGENCE': 2,
    'NEW_INSTITUTION': 3,
    'SHAREHOLDER_COUNT_DECREASE': 1,
    'RSP_STRONG': 1,

    # 派发信号（负分）
    'HIGH_VOLUME_STAGNATION': -2,
    'OBV_BEARISH_DIVERGENCE': -2,
    'INSTITUTIONAL_SELL_OFF': -3,
    'BREAK_SUPPORT_HEAVY_VOLUME': -3,
    'RSP_WEAK': -1,
    # ...
}

# 分析参数
LOOKBACK_PERIOD = 60  # 回看天数
VOL_MULTIPLIER = 2.0   # 放量倍数
```

### 切换数据源

通过环境变量切换 A股数据源：

```bash
# 使用 AkShare (默认，无需 Token)
python3 main.py 600519.SH

# 将历史行情从默认腾讯接口切换为东方财富接口
AKSHARE_HISTORY_SOURCE=eastmoney python3 main.py 600519.SH

# 使用 Tushare (需要配置 TUSHARE_TOKEN)
A_STOCK_DATA_SOURCE=tushare python3 main.py 600519.SH
```

## 📚 理论基础

本项目基于以下详细分析框架：

- [完整理论文档](PREREQUISITES.md) - 追踪"聪明钱"的完整指南（进场与离场全周期）
- [技术规格说明](CODING_SPEC.md) - 系统实现详细规格

### 核心理论要点

1. **硬币的两面**: 机构资本的进场（吸筹）与离场（派发）构成完整周期。真正的市场洞察力来源于理解从建仓到拉升、再到派发撤离的完整逻辑链条。

2. **资金流向的谬误**: 传统"主力资金流向"指标存在根本性逻辑缺陷，实际衡量的是交易"攻击性"而非真实资金流向。

3. **多信号收敛**: 高置信度的判断需要来自不同分析维度的信号相互验证。任何单一指标都可能产生误导。

4. **信号序列**: 机构动向遵循一定模式：
   - 市场信号（价量、背离）通常最先出现（领先指标）
   - 基本面催化剂随后显现（滞后确认）
   - 官方披露最后出现（确凿但延迟）

5. **市场差异化**: A股、美股、港股在投资者结构、交易规则、披露机制上存在差异，需要差异化分析策略。

## 🛣️ 开发路线图

### Phase 1: 核心功能 ✅
- [x] 项目架构设计
- [x] 理论框架文档
- [x] 技术规格说明

### Phase 2: 数据层 ✅ 已完成
- [x] 实现数据获取管理器
- [x] 集成 AkShare API（默认）
- [x] 集成 Tushare API（备选）
- [x] 集成 yfinance（美股/港股）
- [x] 实现智能数据源切换

### Phase 3: 分析层 ✅ 已完成
- [x] 价量关系信号分析
- [x] 技术指标信号分析
- [x] 结构性信号分析
- [x] 相对强弱分析
- [x] 港美股机构持股数据获取

### Phase 4: 聚合与报告 ✅ 已完成
- [x] 风险评分系统
- [x] 报告生成器
- [x] 回测净值、基准、回撤和信号图表

### Phase 5: 优化与扩展 ✅ 已完成
- [x] 日线行情进程内缓存
- [x] 跨进程持久化 TTL 缓存
- [x] 带数据源限流和并发上限的批量处理
- [x] 收盘后定时扫描、重复抑制和可配置告警
- [x] Web 界面 ✅
- [x] 单元测试 ✅
- [x] AkQuant 下一根开盘成交的时点安全回测 MVP
- [x] 滚动样本外验证和样本外参数敏感性报告
- [x] 支持结构性信号回测的公告时点披露存储

## 🧪 测试

运行所有测试：

```bash
# 使用快捷脚本
./run_tests.sh

# 或直接运行
python3 tests/run_tests.py

# 运行特定测试
python3 -m unittest tests.test_app
```

详细测试文档请查看：[tests/TESTING.md](tests/TESTING.md)

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 运行测试确保通过 (`./run_tests.sh`)
5. 推送到分支 (`git push origin feature/AmazingFeature`)
6. 开启 Pull Request

## ⚠️ 免责声明

**本项目仅供学习和研究目的，不构成任何投资建议。**

- 过往表现不代表未来结果
- 投资有风险，决策需谨慎
- 使用本工具进行投资决策的风险由用户自行承担
- 请在使用前充分理解各类信号的含义和局限性

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- 感谢 AkQuant、Tushare、AkShare 等开源项目
- 理论框架参考了大量学术研究和市场实践
- 感谢所有贡献者的支持

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/RTsien/SmartMoneyTracker)
- 问题反馈: [Issues](https://github.com/RTsien/SmartMoneyTracker/issues)
- 讨论交流: [Discussions](https://github.com/RTsien/SmartMoneyTracker/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star！

**记住：市场永远在讲故事，而聪明钱的足迹就隐藏在价量关系、技术指标、盘口数据和持股变化之中。**
