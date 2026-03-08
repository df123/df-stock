#!/bin/bash

# FastAPI后端启动脚本

cd "$(dirname "$0")"

echo "正在启动FastAPI后端服务..."
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "日志文件: logs/api.log"
echo ""

# 确保logs目录存在
mkdir -p logs

PYTHONPATH=/home/df/df-stock:$PYTHONPATH uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload | tee logs/api.log
