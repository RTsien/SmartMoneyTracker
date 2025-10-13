# SmartMoneyTracker 快速开始指南

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

## 使用方法

### 方式1: 命令行使用

#### 扫描单个股票

```bash
python main.py 600519.SH
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

    # 或访问具体数据
    print(f"风险评分: {result['risk_score']}/10")
    print(f"风险等级: {result['risk_level']}")
else:
    print(f"扫描失败: {result.get('error')}")
```

### 方式3: 运行示例

```bash
python example.py
```

## 配置说明

编辑 `config.py` 来自定义：

### 1. 股票池

```python
STOCK_POOL = [
    '600519.SH',  # 贵州茅台
    '000858.SZ',  # 五粮液
    # 添加更多股票...
]
```

### 2. 信号权重

```python
SIGNAL_WEIGHTS = {
    'HIGH_VOLUME_STAGNATION': 2,
    'OBV_DIVERGENCE': 2,
    'INSTITUTIONAL_SELL_OFF': 4,
    # ...
}
```

### 3. 分析参数

```python
PV_PARAMS = {
    'lookback_period': 60,
    'vol_multiplier': 2.0,
    # ...
}
```

## 输出示例

```
============================================================
    Smart Money Tracker - 机构资金撤离信号分析报告
============================================================

股票代码: 600519.SH
分析时间: 2025-10-13 15:30:45

风险评分: 7/10 [HIGH]
触发信号数: 4

------------------------------------------------------------
触发的信号:
------------------------------------------------------------

[+] 高位放量滞涨 (权重: 2)
    股价在上涨趋势后出现放量滞涨 (涨幅仅1.2%，成交量为均量2.3倍)
    信号日期: 2025-10-12

[+] MFI 看跌背离 (权重: 2)
    MFI看跌背离: 价格创新高但资金流量指标未能同步

[+] 机构减持 (权重: 4)
    检测到2家机构减持

[+] 相对强度疲弱 (权重: 2)
    相对强度疲弱: 跑输基准6.5%

------------------------------------------------------------
投资建议:
------------------------------------------------------------

检测到多个高置信度撤离信号。大资金可能正在派发筹码。
建议谨慎，考虑降低仓位或离场观望。
```

## 常见问题

### Q1: 提示 "Tushare API 未初始化"

**A:** 请确保：
1. 已安装 tushare: `pip install tushare`
2. 已在 `.env` 文件中配置正确的 Token
3. Token 有效且未过期

### Q2: 数据获取失败

**A:** 可能原因：
1. 股票代码格式错误（A股需加 .SH 或 .SZ 后缀）
2. API 限流（Tushare 免费版有调用频率限制）
3. 网络连接问题

### Q3: 如何分析美股或港股？

**A:**
- 美股：直接使用股票代码，如 `AAPL`, `MSFT`
- 港股：使用代码加 .HK 后缀，如 `00700.HK`

美股和港股使用 yfinance 库，无需 Tushare Token。

### Q4: 如何提高分析准确度？

**A:**
1. 增加数据回看期：`--period 365`
2. 启用结构性分析：`--structure`
3. 调整信号权重以适应不同市场环境
4. 结合多个股票的分析结果

## 高级用法

### 自定义数据源

编辑 `data_fetcher/manager.py` 添加新的数据源接口。

### 添加新的信号类型

1. 在 `analysis/` 目录创建新模块
2. 实现信号检测逻辑
3. 在 `main.py` 中集成
4. 在 `config.py` 中配置权重

### 批量导出报告

```python
scanner = SmartMoneyScanner()
results = scanner.scan_batch(['600519.SH', '000858.SZ'])

for ticker, result in results.items():
    if result['success']:
        with open(f'reports/{ticker}_report.txt', 'w') as f:
            f.write(result['report'])
```

## 技术支持

- 查看完整文档: [README.md](README.md)
- 理论框架: [PREREQUISITES.md](PREREQUISITES.md)
- 技术规格: [SPEC.md](SPEC.md)
- 问题反馈: [GitHub Issues](https://github.com/yourusername/SmartMoneyTracker/issues)

## 下一步

- 📖 阅读[理论文档](PREREQUISITES.md)深入了解分析框架
- 🔧 调整 [config.py](config.py) 以适应你的需求
- 🧪 使用历史数据进行回测验证
- 📊 开发可视化界面（计划中）

---

祝你投资顺利！记住：本工具仅供研究学习，不构成投资建议。
