# SmartMoneyTracker

> 追踪"聪明钱"的足迹：基于多维度分析的机构资金撤离信号识别系统

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 项目简介

SmartMoneyTracker 是一个模块化的 Python 应用程序，用于自动化扫描和分析 **A股、美股、港股** 市场的股票，识别大资金（机构投资者）可能正在撤离的信号。

在复杂的证券市场中，"大资金"由共同基金、养老基金、对冲基金、QFII 以及高净值投资者组成。它们的投资策略、时间视野和执行方式各不相同，在市场中留下了各异的信号。识别这些撤离信号对于：

- ✅ **风险管理**：避免"接飞刀"
- ✅ **战术定位**：与机构情绪保持一致
- ✅ **趋势预判**：预判潜在的趋势反转

至关重要。

## 🎯 核心特点

### 多维度分析框架

系统**不依赖任何单一指标**，而是整合多个独立分析领域的信号：

1. **价量关系分析**
   - 高位放量滞涨
   - 放量跌破关键支撑位
   - 高位缩量上涨

2. **技术指标信号**
   - OBV（能量潮）看跌背离
   - MFI（资金流量指标）看跌背离
   - 动量指标背离

3. **市场微观结构**
   - Level-2 盘口分析
   - 订单失衡率（SOIR）
   - 算法交易足迹识别

4. **股东结构变化**
   - 机构持股变动追踪
   - 股东户数变化分析
   - 董监高减持监控

5. **相对强弱分析**
   - 个股与板块比较
   - 个股与大盘背离识别
   - RSP（相对强弱比）分析

6. **基本面催化剂**
   - 负面新闻监控
   - 业绩预警追踪
   - 政策变化影响

### 智能风险评分

- 基于权重的多信号聚合
- 综合风险评分（0-10）
- 风险等级分类（LOW / MEDIUM / HIGH）
- 人类可读的分析报告

## 🏗️ 系统架构

```
SmartMoneyTracker/
│
├── main.py                      # 主程序入口
├── config.py                    # 配置文件
├── requirements.txt             # 依赖库
│
├── data_fetcher/                # 数据获取层
│   ├── __init__.py
│   └── manager.py               # 统一数据API管理器
│
├── analysis/                    # 信号分析层（核心逻辑）
│   ├── __init__.py
│   ├── pv_signals.py           # 价量关系信号
│   ├── indicator_signals.py    # 技术指标信号
│   ├── structural_signals.py   # 结构性信号
│   └── relative_strength.py    # 相对强弱信号
│
├── aggregator/                  # 风险聚合层
│   ├── __init__.py
│   └── scorer.py               # 信号计分与风险评级
│
└── reporting/                   # 报告生成层
    ├── __init__.py
    └── generator.py            # 生成文本/HTML报告
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

```
===== Institutional Exit Scan Report =====
Ticker: 600519.SH
Date: 2025-10-13
Risk Score: 7/10 (HIGH)

Triggered Signals:
[+] HIGH_VOLUME_STAGNATION (Score: 1) on 2025-09-15
    股价在大幅上涨后出现成交量激增但价格停滞

[+] MFI_BEARISH_DIVERGENCE (Score: 2)
    股价创新高但资金流量指标未能同步

[+] INSTITUTIONAL_SELL_OFF (Score: 3)
    China Merchants Fund 减持 5%

[+] RELATIVE_STRENGTH_WEAK (Score: 1)
    跑输 CSI 白酒指数

Recommendation:
机构派发概率较高，建议谨慎。大资金可能正在利用散户热情卖出筹码。
```

## 📊 支持的市场

| 市场 | 数据源 | 核心特色 |
|------|--------|----------|
| **A股** | Tushare, AkShare | 北向资金监控、十大股东分析、董监高减持追踪 |
| **美股** | yfinance, SEC EDGAR | 13F 报告分析、内部人交易监控 |
| **港股** | 港交所数据 | 披露易（DI）数据、南向资金追踪 |

## 📈 数据来源

- **日线行情**: Tushare, yfinance
- **Level-2 数据**: 东方财富 Choice, 万得
- **机构持仓**:
  - A股: Tushare (top10_holders, stk_holdernumber)
  - 美股: SEC EDGAR 13F 报告
  - 港股: 披露易（DI）
- **资金流向**:
  - 北向资金: Tushare (hk_hold)
  - 南向资金: Eastmoney API
- **公告新闻**: 巨潮资讯网、交易所官网

## 🔧 配置说明

在 `config.py` 中配置：

```python
# API 密钥
TUSHARE_TOKEN = "your_token_here"
AKSHARE_ENABLED = True

# 股票池
STOCK_POOL = [
    '600519.SH',  # 贵州茅台
    'AAPL',       # Apple
    '00700.HK'    # 腾讯控股
]

# 信号权重
SIGNAL_WEIGHTS = {
    'HIGH_VOLUME_STAGNATION': 1,
    'OBV_DIVERGENCE': 2,
    'INSTITUTIONAL_SELL_OFF': 3,
    'BREAK_SUPPORT_HEAVY_VOLUME': 3,
    # ...
}

# 分析参数
LOOKBACK_PERIOD = 60  # 回看天数
VOL_MULTIPLIER = 2.0   # 放量倍数
```

## 📚 理论基础

本项目基于《撤离信号：识别股票大资金退出的多维度分析框架》研究报告。详细分析框架请参考：

- [完整理论文档](PREREQUISITES.md)
- [技术规格说明](SPEC.md)

### 核心理论要点

1. **资金流向的谬误**: 传统"主力资金流向"指标存在根本性逻辑缺陷，实际衡量的是交易"攻击性"而非真实资金流向。

2. **多信号收敛**: 高置信度的判断需要来自不同分析维度的信号相互验证。

3. **领先与滞后**: 市场数据信号（价量、指标）通常领先于公开披露（财报、公告）。

4. **市场差异化**: A股、美股、港股在投资者结构、交易规则、披露机制上存在差异，需要差异化分析策略。

## 🛣️ 开发路线图

### Phase 1: 核心功能 ✅
- [x] 项目架构设计
- [x] 理论框架文档
- [x] 技术规格说明

### Phase 2: 数据层 (进行中)
- [ ] 实现数据获取管理器
- [ ] 集成 Tushare API
- [ ] 集成 AkShare API
- [ ] 集成 yfinance

### Phase 3: 分析层
- [ ] 价量关系信号分析
- [ ] 技术指标信号分析
- [ ] 结构性信号分析
- [ ] 相对强弱分析

### Phase 4: 聚合与报告
- [ ] 风险评分系统
- [ ] 报告生成器
- [ ] 可视化图表

### Phase 5: 优化与扩展
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
