# SmartMoneyTracker 快速开始指南

**版本**: v0.3.0 - Bidirectional Analysis System

## 🎯 系统概述

SmartMoneyTracker 是一个**双向机构资金动向分析系统**，追踪机构从**进场（吸筹）到离场（派发）**的完整周期。

### 评分系统
- **评分范围**: -10 到 +10
- **正分 (+)**: 机构进场/吸筹信号 (Accumulation)
- **负分 (-)**: 机构离场/派发信号 (Distribution)
- **评级**: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/SmartMoneyTracker.git
cd SmartMoneyTracker
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据源（可选）

SmartMoneyTracker 默认使用 **AkShare**（无需配置），如需使用 Tushare 作为备选：

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，添加 Tushare Token
TUSHARE_TOKEN=your_token_here
```

---

## 使用方法

### 方式1: 命令行使用

#### 扫描单个股票

```bash
python main.py 600519.SH
```

**输出示例**:
```
综合评分: +7.0/10 (-10 to +10)
综合评级: STRONG_BUY 🚀🚀
触发信号数: 5 (进场: 3, 离场: 2)
```

#### 扫描多个股票

```bash
python main.py 600519.SH 000858.SZ 000333.SZ
```

#### 扫描配置文件中的股票池

```bash
python main.py --pool
```

#### 启用结构性信号分析（需要更多API调用）

```bash
python main.py 600519.SH --structure
```

#### 自定义数据回看期

```bash
python main.py 600519.SH --period 365
```

---

### 方式2: Python API 使用

创建一个 Python 脚本：

```python
from main import SmartMoneyScanner

# 创建扫描器
scanner = SmartMoneyScanner()

# 扫描单个股票
result = scanner.scan_stock('600519.SH')

if result['success']:
    # 打印完整报告
    print(result['report'])

    # 访问具体数据（双向评分）
    print(f"\n综合评分: {result['score']:+.1f}/10")
    print(f"综合评级: {result['rating']}")
    print(f"进场信号数: {result['inflow_count']}")
    print(f"离场信号数: {result['outflow_count']}")

    # 查看进场信号详情
    for signal, info in result['inflow_signals'].items():
        print(f"  {signal}: 权重 +{info['weight']}")

    # 查看离场信号详情
    for signal, info in result['outflow_signals'].items():
        print(f"  {signal}: 权重 {info['weight']}")
else:
    print(f"扫描失败: {result.get('error')}")
```

---

### 方式3: 运行示例

```bash
python example.py
```

示例包含：
- 单股票扫描（双向分析）
- 批量扫描
- 自定义配置（双向权重）
- 美股分析
- 原始数据访问

---

## 配置说明

编辑 `config.py` 来自定义：

### 1. 股票池

```python
STOCK_POOL = [
    '600519.SH',  # 贵州茅台
    '000858.SZ',  # 五粮液
    '000333.SZ',  # 美的集团
    # 添加更多股票...
]
```

### 2. 双向信号权重

```python
SIGNAL_WEIGHTS = {
    # ========== 进场信号 (正数权重) ==========
    'ACCUMULATION_BREAKOUT': 2,            # 放量突破横盘区
    'WYCKOFF_SPRING': 2,                   # 威科夫弹簧
    'OBV_BULLISH_DIVERGENCE': 2,           # OBV看涨背离
    'NEW_INSTITUTION': 3,                  # 新机构进入（最高权重）
    'INSTITUTIONAL_BUY_IN': 3,             # 机构增持

    # ========== 离场信号 (负数权重) ==========
    'HIGH_VOLUME_STAGNATION': -2,          # 高位放量滞涨
    'HIGH_VOLUME_DECLINE': -2,             # 放量下跌
    'BREAK_SUPPORT_HEAVY_VOLUME': -3,      # 放量跌破支撑
    'INSTITUTIONAL_SELL_OFF': -3,          # 机构减持（最高权重）
    'INSIDER_SELLING': -3,                 # 董监高减持
    # ...更多信号
}
```

### 3. 分析参数

```python
PV_PARAMS = {
    'lookback_period': 60,          # 回看周期（天）
    'vol_multiplier': 2.0,          # 放量倍数
    'price_change_threshold': 0.02, # 价格变动阈值（2%）
    # ...
}
```

---

## 输出示例

```
══════════════════════════════════════════════════════════════════
      Smart Money Tracker - 机构资金动向分析报告
══════════════════════════════════════════════════════════════════

股票代码: 600519.SH
分析时间: 2025-10-13 15:30:00

综合评分: +7.0/10 (-10 to +10)
综合评级: STRONG_BUY 🚀🚀
触发信号数: 5 (进场: 3, 离场: 2)

══════════════════════════════════════════════════════════════════
  进场信号 (吸筹/Accumulation) 🟢
══════════════════════════════════════════════════════════════════

[+2] 放量突破横盘区
      成交量为均量2.5倍，突破价位150.00
      信号日期: 2025-10-12
        • consolidation_range: 15.00%
        • volume_ratio: 2.50x

[+2] OBV看涨背离
      价格创新低但OBV形成更高低点，资金暗中流入
      信号日期: 2025-10-10
        • divergence_strength: 强

[+3] 新机构进入十大股东
      检测到2家新机构进入十大股东
      信号日期: 2025-09-30
        • new_institutions: [机构A, 机构B]

══════════════════════════════════════════════════════════════════
  离场信号 (派发/Distribution) 🔴
══════════════════════════════════════════════════════════════════

[-2] 高位放量滞涨
      股价在上涨趋势后出现放量滞涨 (涨幅仅1.5%)
      信号日期: 2025-10-13

--------------------------------------------------------------
投资建议:
--------------------------------------------------------------

检测到强烈的机构吸筹信号(评分+7.0)。大资金可能正在积极建仓。
建议关注并考虑买入时机。
```

---

## 📊 理解评级系统

| 评级 | 评分范围 | 含义 | 建议 |
|-----|---------|------|------|
| **STRONG_BUY** 🚀🚀 | +6 to +10 | 强烈的机构吸筹信号 | 考虑买入时机 |
| **BUY** 🚀 | +2 to +5 | 温和的机构吸筹信号 | 继续观察 |
| **NEUTRAL** ⚪ | -1 to +1 | 无明显进出场信号 | 保持观察 |
| **SELL** ⚠️ | -5 to -2 | 部分机构派发信号 | 提高警惕 |
| **STRONG_SELL** 🛑🛑 | -10 to -6 | 强烈的机构派发信号 | 考虑降低仓位 |

---

## 常见问题

### Q1: 如何理解评分系统？

**A:**
- **正分（+）**: 表示检测到机构吸筹信号，分数越高表示吸筹迹象越明显
- **负分（-）**: 表示检测到机构派发信号，分数越低表示派发迹象越明显
- **中性（0附近）**: 没有明显的机构进出场信号

### Q2: 数据源如何选择？

**A:**
- **默认**: AkShare（无需配置，开箱即用）
- **备选**: Tushare（需要注册并配置 Token）
- **美港股**: yfinance（自动使用）

通过环境变量切换：
```bash
export A_STOCK_DATA_SOURCE=tushare  # 使用 Tushare
export A_STOCK_DATA_SOURCE=akshare  # 使用 AkShare（默认）
```

### Q3: 提示 "Tushare API 未初始化"

**A:** 如果你选择使用 Tushare，请确保：
1. 已安装 tushare: `pip install tushare`
2. 已在 `.env` 文件中配置正确的 Token
3. Token 有效且未过期

建议：直接使用默认的 AkShare，无需配置。

### Q4: 数据获取失败

**A:** 可能原因：
1. 股票代码格式错误（A股需加 .SH 或 .SZ 后缀）
2. API 限流（Tushare 免费版有调用频率限制）
3. 网络连接问题

### Q5: 如何分析美股或港股？

**A:**
- **美股**: 直接使用股票代码，如 `AAPL`, `MSFT`
- **港股**: 使用代码加 .HK 后缀，如 `00700.HK`

美股和港股使用 yfinance 库，无需 Tushare Token。

### Q6: 如何提高分析准确度？

**A:**
1. 增加数据回看期：`--period 365`
2. 启用结构性分析：`--structure`
3. 调整信号权重以适应不同市场环境
4. 结合多个股票的分析结果
5. 关注进场和离场信号数量对比

### Q7: 评分为什么不是整数？

**A:** 评分是所有触发信号的权重之和，可能是小数。例如：
- 触发 ACCUMULATION_BREAKOUT (+2) + MFI_OVERSOLD (+1) = +3
- 同时触发 HIGH_VOLUME_STAGNATION (-2) = 最终评分 +1

---

## 高级用法

### 批量扫描并筛选

```python
scanner = SmartMoneyScanner()
results = scanner.scan_batch(['600519.SH', '000858.SZ', '000333.SZ'])

# 筛选强烈吸筹信号
strong_buy = [
    (ticker, r) for ticker, r in results.items()
    if r['success'] and r['rating'] == 'STRONG_BUY'
]

print(f"发现 {len(strong_buy)} 只强吸筹股票")
for ticker, result in strong_buy:
    print(f"{ticker}: 评分 {result['score']:+.1f}, 进场信号 {result['inflow_count']} 个")
```

### 自定义权重配置

```python
import config

# 临时调整权重（更注重技术指标）
config.SIGNAL_WEIGHTS['OBV_BULLISH_DIVERGENCE'] = 3
config.SIGNAL_WEIGHTS['MFI_BULLISH_DIVERGENCE'] = 3

scanner = SmartMoneyScanner()
result = scanner.scan_stock('600519.SH')
```

### 添加新的信号类型

1. 在 `analysis/` 目录创建新模块或扩展现有模块
2. 实现信号检测逻辑，返回信号字典
3. 在 `main.py` 中集成新信号
4. 在 `config.py` 中配置权重（正数=吸筹，负数=派发）

### 批量导出报告

```python
scanner = SmartMoneyScanner()
results = scanner.scan_batch(['600519.SH', '000858.SZ'])

# 导出所有报告
for ticker, result in results.items():
    if result['success']:
        with open(f'reports/{ticker}_report.txt', 'w', encoding='utf-8') as f:
            f.write(result['report'])
```

---

## 🎓 学习路径

1. **快速体验**: 运行 `python example.py` 查看示例输出
2. **理解理论**: 阅读 [PREREQUISITES.md](PREREQUISITES.md) 了解双向分析框架
3. **深入技术**: 查看 [CODING_SPEC.md](CODING_SPEC.md) 了解实现细节
4. **自定义配置**: 修改 [config.py](config.py) 调整权重和参数
5. **扩展功能**: 参考 [CLAUDE.md](CLAUDE.md) 进行二次开发

---

## 🔍 使用建议

### 投资决策建议

1. **STRONG_BUY (🚀🚀)**:
   - 多个吸筹信号收敛
   - 可关注并研究基本面
   - 考虑逐步建仓

2. **BUY (🚀)**:
   - 有吸筹迹象但不强烈
   - 继续观察后续信号
   - 可加入观察列表

3. **NEUTRAL (⚪)**:
   - 无明显机构动向
   - 保持观察
   - 等待明确信号

4. **SELL (⚠️)**:
   - 出现部分派发信号
   - 提高警惕
   - 考虑减仓

5. **STRONG_SELL (🛑🛑)**:
   - 多个派发信号收敛
   - 机构可能大量离场
   - 考虑降低仓位或离场

### 最佳实践

- ✅ 结合基本面分析
- ✅ 关注信号数量对比（inflow_count vs outflow_count）
- ✅ 多只股票横向比较
- ✅ 定期调整权重适应市场环境
- ❌ 不要仅凭单一信号决策
- ❌ 不要忽视基本面因素

---

## 技术支持

- 📖 完整文档: [README.md](README.md)
- 🎓 理论框架: [PREREQUISITES.md](PREREQUISITES.md)
- 🔧 技术规格: [CODING_SPEC.md](CODING_SPEC.md)
- 🐛 问题反馈: [GitHub Issues](https://github.com/yourusername/SmartMoneyTracker/issues)

---

## 下一步

- 📖 阅读[双向分析理论](PREREQUISITES.md)深入了解分析框架
- 🔧 调整 [config.py](config.py) 以适应你的需求
- 🧪 使用历史数据进行回测验证
- 📊 开发可视化界面（计划中）

---

**免责声明**: 本工具仅供研究学习，不构成投资建议。投资有风险，入市需谨慎。

**祝你投资顺利！** 🚀
