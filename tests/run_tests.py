#!/usr/bin/env python3
"""
测试运行脚本
运行所有单元测试并生成报告
"""

import unittest
import sys
import os
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests(verbosity=2):
    """
    运行所有测试
    
    Args:
        verbosity: 详细程度 (0=静默, 1=正常, 2=详细)
    
    Returns:
        测试结果对象
    """
    # 发现并加载所有测试
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def main():
    """主函数"""
    print("=" * 70)
    print("SmartMoneyTracker 单元测试")
    print("=" * 70)
    print()
    
    # 运行测试
    result = run_tests(verbosity=2)
    
    # 打印总结
    print()
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    # 如果有失败或错误，返回非零退出码
    if result.failures or result.errors:
        print()
        print("❌ 测试失败！")
        sys.exit(1)
    else:
        print()
        print("✅ 所有测试通过！")
        sys.exit(0)


if __name__ == '__main__':
    main()
