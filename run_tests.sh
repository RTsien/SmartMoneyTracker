#!/bin/bash
# 运行所有测试的快捷脚本

cd "$(dirname "$0")"

if [ -x "venv/bin/python" ]; then
    PYTHON_BIN="venv/bin/python"
else
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" tests/run_tests.py "$@"
