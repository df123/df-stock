#!/bin/bash

# 增量更新ETF数据的Shell脚本
# 用于方便地从命令行启动增量更新

set -e

cd "$(dirname "$0")"
cd ..

echo "========================================="
echo "增量更新ETF历史数据"
echo "========================================="

if [ -n "$1" ]; then
    echo "更新指定的ETF代码: $@"
    python scripts/incremental_update.py --codes "$@"
else
    echo "更新所有ETF..."
    python scripts/incremental_update.py
fi

echo ""
echo "更新完成！"
echo "========================================="
