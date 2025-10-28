#!/bin/bash
# 运行所有测试的快捷脚本

cd "$(dirname "$0")"
python3 tests/run_tests.py "$@"
