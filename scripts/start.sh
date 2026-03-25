#!/bin/bash

# 功能：清理端口、启动后端和前端服务

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 清理端口
echo "Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 1

# 确保logs目录存在
mkdir -p logs

# 启动后端API服务
echo "Starting ETF Analysis System..."
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:8080"
echo "  - API Docs: http://localhost:8000/docs"
echo ""

PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH nohup python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!

cd web
nohup npm run dev > ../logs/web.log 2>&1 &
WEB_PID=$!
cd ..

sleep 2

# 显示启动信息
echo "Services started:"
echo "  Backend PID: $API_PID (logs/api.log)"
echo "  Frontend PID: $WEB_PID (logs/web.log)"
echo ""
echo "View logs:"
echo "  tail -f logs/api.log"
echo "  tail -f logs/web.log"
echo ""
echo "Stop services:"
echo "  kill $API_PID $WEB_PID"
