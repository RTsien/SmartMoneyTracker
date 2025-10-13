# SmartMoneyTracker

> 追踪"聪明钱"的足迹：基于多维度分析的机构资金进出场全周期识别系统

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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
└── reporting/                      # 报告生成层
    ├── __init__.py
    └── generator.py               # 生成文本/HTML报告
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- pip 包管理器

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/SmartMoneyTracker.git
cd SmartMoneyTracker

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cp config.example.py config.py
# 编辑 config.py 添加您的 API 密钥
```

### 使用示例

```python
from main import SmartMoneyScanner

# 初始化扫描器
scanner = SmartMoneyScanner()

# 扫描单个股票
result = scanner.scan_stock('600519.SH')  # A股：贵州茅台
print(result.report)

# 批量扫描股票池
stocks = ['600519.SH', 'AAPL', '00700.HK']
results = scanner.scan_batch(stocks)

# 生成报告
for stock, result in results.items():
    print(f"\n{stock}:")
    print(f"Risk Score: {result.risk_score}/10")
    print(f"Risk Level: {result.risk_level}")
```

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
| **A股** | **AkShare (默认)**, Tushare | 北向资金监控、十大股东分析、股东户数分析 |
| **美股** | yfinance | 机构持股数据、日线行情数据 |
| **港股** | yfinance, AkShare | 机构持股数据、港股通持股数据 |

## 📈 数据来源

- **日线行情**: 
  - A股: **AkShare (默认)**, Tushare
  - 美股/港股: yfinance
- **Level-2 数据** ⚠️ **未实现（需商业接口）**: 东方财富 Choice、万得等商业数据提供商
  - 费用：数千至数万元/年
  - 用途：微观结构信号（买单墙、卖盘压单检测）
  - 说明：架构已预留接口，有数据源时可直接扩展
- **机构持仓**:
  - A股: **AkShare (默认)**, Tushare (top10_holders, stk_holdernumber)
  - 美股: **yfinance (已实现)** - 机构持股者数据
  - 港股: **yfinance + AkShare (已实现)** - 双数据源支持
- **资金流向**:
  - 北向资金: **AkShare (默认)**, Tushare (hk_hold)
  - 南向资金: Eastmoney API
- **公告新闻**: 巨潮资讯网、交易所官网

> **重要更新**: 
> - ✅ 系统默认使用 **AkShare** 作为 A股数据源（**无需 Token，开箱即用**）
> - ✅ 智能降级机制：AkShare 失败时自动切换到 Tushare
> - ✅ 港美股机构持股数据已实现（通过 yfinance）
> - ✅ 可通过环境变量 `A_STOCK_DATA_SOURCE` 手动切换数据源

## 🔧 配置说明

在 `config.py` 中配置：

```python
# 数据源配置
A_STOCK_DATA_SOURCE = 'akshare'  # 可选: 'akshare' (默认), 'tushare'
AKSHARE_ENABLED = True
TUSHARE_TOKEN = "your_token_here"  # 仅在使用 Tushare 时需要

# 股票池
STOCK_POOL = [
    '600519.SH',  # 贵州茅台
    'AAPL',       # Apple
    '00700.HK'    # 腾讯控股
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
- [ ] 可视化图表

### Phase 5: 优化与扩展
- [ ] 数据缓存机制
- [ ] 并发处理优化
- [ ] 实时监控模式
- [ ] Web 界面
- [ ] 回测系统

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## ⚠️ 免责声明

**本项目仅供学习和研究目的，不构成任何投资建议。**

- 过往表现不代表未来结果
- 投资有风险，决策需谨慎
- 使用本工具进行投资决策的风险由用户自行承担
- 请在使用前充分理解各类信号的含义和局限性

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢 Tushare、AkShare 等开源数据接口项目
- 理论框架参考了大量学术研究和市场实践
- 感谢所有贡献者的支持

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/rtsien/SmartMoneyTracker)
- 问题反馈: [Issues](https://github.com/rtsien/SmartMoneyTracker/issues)
- 讨论交流: [Discussions](https://github.com/rtsien/SmartMoneyTracker/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star！

**记住：市场永远在讲故事，而聪明钱的足迹就隐藏在价量关系、技术指标、盘口数据和持股变化之中。**
