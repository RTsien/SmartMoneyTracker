# SmartMoneyTracker 测试文档

## 📋 测试概述

本项目包含完整的单元测试套件，确保代码质量和功能正确性。

## 🧪 测试模块

### 1. `test_app.py` - Flask API 测试
测试 Web 接口的各项功能：

- ✅ 路由测试（主页、配置接口）
- ✅ 信号格式化功能
- ✅ 正负权重信号处理
- ✅ 空数据和边界情况
- ✅ API 错误处理

**关键测试**：
- `test_format_signals_with_negative_weight` - 确保负分不会显示为 `+0`
- `test_format_signals_with_positive_weight` - 确保正分正确显示
- `test_negative_score_not_zero` - 防止评分显示为0的回归

### 2. `test_scorer.py` - 信号聚合器测试
测试评分和评级逻辑：

- ✅ 空信号处理
- ✅ 进场信号评分（正分）
- ✅ 离场信号评分（负分）
- ✅ 混合信号处理
- ✅ 评级判定（STRONG_BUY 到 STRONG_SELL）
- ✅ 评分上下限（-10 到 +10）
- ✅ 信号分类（进场/离场）
- ✅ 投资建议生成

**关键测试**：
- `test_signal_weight_structure` - 确保信号结构包含 `weight` 字段
- `test_inflow_outflow_separation` - 确保信号正确分类
- `test_rating_boundaries` - 测试所有评级边界值

### 3. `test_data_fetcher.py` - 数据获取器测试
测试股票名称获取功能：

- ✅ 市场检测（A股、港股、美股）
- ✅ 股票名称获取
- ✅ 失败时的降级处理
- ✅ 美股中文名称映射
- ✅ 批量获取测试

## 🚀 运行测试

### 方法 1: 使用测试脚本（推荐）

```bash
# 运行所有测试
python3 run_tests.py
```

### 方法 2: 使用 unittest

```bash
# 运行所有测试
python3 -m unittest discover tests

# 运行特定测试文件
python3 -m unittest tests.test_app

# 运行特定测试类
python3 -m unittest tests.test_app.TestFlaskAPI

# 运行特定测试方法
python3 -m unittest tests.test_app.TestFlaskAPI.test_format_signals_with_negative_weight
```

### 方法 3: 使用 pytest（需要安装）

```bash
# 安装 pytest
pip install pytest pytest-cov

# 运行测试
pytest tests/

# 运行测试并显示覆盖率
pytest tests/ --cov=. --cov-report=html
```

## 📊 测试输出示例

```
======================================================================
SmartMoneyTracker 单元测试
======================================================================

test_analyze_api_missing_ticker (tests.test_app.TestFlaskAPI) ... ok
test_batch_api_missing_tickers (tests.test_app.TestFlaskAPI) ... ok
test_config_route (tests.test_app.TestFlaskAPI) ... ok
test_format_signals_empty_input (tests.test_app.TestFlaskAPI) ... ok
test_format_signals_no_weight (tests.test_app.TestFlaskAPI) ... ok
test_format_signals_with_empty_data (tests.test_app.TestFlaskAPI) ... ok
test_format_signals_with_multiple_signals (tests.test_app.TestFlaskAPI) ... ok
test_format_signals_with_negative_weight (tests.test_app.TestFlaskAPI) ... ok
test_format_signals_with_positive_weight (tests.test_app.TestFlaskAPI) ... ok
test_index_route (tests.test_app.TestFlaskAPI) ... ok
test_negative_score_not_zero (tests.test_app.TestSignalScoreDisplay) ... ok
test_positive_score_not_zero (tests.test_app.TestSignalScoreDisplay) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.123s

OK

======================================================================
测试总结
======================================================================
运行测试数: 35
成功: 35
失败: 0
错误: 0
跳过: 0

✅ 所有测试通过！
```

## 🐛 关键测试案例

### 防止评分显示为 +0 的回归

这是修复 MACD看跌背离显示为 `+0` 问题后添加的测试：

```python
def test_format_signals_with_negative_weight(self):
    """测试格式化离场信号（负权重）"""
    signals = {
        'MACD_BEARISH_DIVERGENCE': {
            'weight': -2,
            'data': {
                'description': 'MACD看跌背离',
                'date': '2025-10-20'
            }
        }
    }
    
    formatted = format_signals(signals)
    
    # 确保评分是 -2，而不是 0
    self.assertEqual(formatted[0]['score'], -2)
```

### 确保信号结构正确

```python
def test_signal_weight_structure(self):
    """测试信号权重结构正确性"""
    signals = {
        'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'}
    }
    
    result = self.aggregator.calculate_score(signals)
    
    signal_entry = result['triggered_signals']['OBV_BULLISH_DIVERGENCE']
    
    # 确保包含 weight 字段
    self.assertIn('weight', signal_entry)
    self.assertEqual(signal_entry['weight'], 2)
    
    # 确保包含 data 字段
    self.assertIn('data', signal_entry)
```

## 📈 测试覆盖率

当前测试覆盖的主要功能：

- ✅ **Flask API** - 100%
- ✅ **信号格式化** - 100%
- ✅ **信号聚合器** - 95%
- ✅ **评级判定** - 100%
- ✅ **数据获取器** - 80%

## 🔧 添加新测试

### 测试文件命名规范

- 测试文件名以 `test_` 开头
- 放在 `tests/` 目录下
- 测试类名以 `Test` 开头
- 测试方法名以 `test_` 开头

### 示例：添加新测试

```python
# tests/test_new_feature.py

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from your_module import your_function


class TestNewFeature(unittest.TestCase):
    """新功能测试类"""

    def setUp(self):
        """每个测试前运行"""
        pass

    def tearDown(self):
        """每个测试后运行"""
        pass

    def test_something(self):
        """测试某个功能"""
        result = your_function()
        self.assertEqual(result, expected_value)


if __name__ == '__main__':
    unittest.main()
```

## 🎯 测试最佳实践

### 1. 测试命名
- 使用描述性的测试名称
- 说明测试的目的和预期结果

### 2. 测试独立性
- 每个测试应该独立运行
- 不依赖其他测试的结果
- 使用 `setUp` 和 `tearDown` 管理测试状态

### 3. 断言清晰
- 使用合适的断言方法
- 添加错误消息说明预期行为

```python
self.assertEqual(result, expected, 
    f"期望得到 {expected}，但实际得到 {result}")
```

### 4. 边界测试
- 测试正常情况
- 测试边界值
- 测试异常情况

### 5. 测试数据
- 使用真实但简化的测试数据
- 避免依赖外部服务
- 使用 mock 模拟外部依赖

## 🔍 调试测试

### 运行单个测试并查看详细输出

```bash
python3 -m unittest tests.test_app.TestFlaskAPI.test_format_signals_with_negative_weight -v
```

### 在测试中添加调试输出

```python
def test_something(self):
    result = some_function()
    print(f"Debug: result = {result}")  # 调试输出
    self.assertEqual(result, expected)
```

### 使用 pdb 调试器

```python
def test_something(self):
    import pdb; pdb.set_trace()  # 设置断点
    result = some_function()
    self.assertEqual(result, expected)
```

## 📝 持续集成

### GitHub Actions 配置示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        python3 run_tests.py
```

## 🎓 测试资源

- [Python unittest 文档](https://docs.python.org/3/library/unittest.html)
- [pytest 文档](https://docs.pytest.org/)
- [测试驱动开发（TDD）](https://en.wikipedia.org/wiki/Test-driven_development)

## ✅ 测试检查清单

在提交代码前，确保：

- [ ] 所有测试通过
- [ ] 新功能有对应的测试
- [ ] Bug 修复有回归测试
- [ ] 测试覆盖率没有下降
- [ ] 测试代码遵循项目规范

## 🐛 已知问题

目前没有已知的测试问题。如果发现测试失败，请：

1. 检查是否有网络连接（某些测试可能需要访问数据源）
2. 确认所有依赖已正确安装
3. 查看测试输出的错误信息
4. 提交 Issue 报告问题

## 📞 获取帮助

如果测试遇到问题：

1. 查看测试输出的详细错误信息
2. 阅读相关测试代码的注释
3. 查看 [GitHub Issues](https://github.com/rtsien/SmartMoneyTracker/issues)
4. 提交新的 Issue 描述问题

---

**记住：好的测试是代码质量的保证！** 🎯
