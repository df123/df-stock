#!/bin/bash

# 功能：清理端口、启动后端和前端服务

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 安全清理端口函数 - 只杀死我们的服务进程，避免杀死VSCode相关进程
cleanup_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -z "$pids" ]; then
        echo "  Port $port is free"
        return 0
    fi
    
    echo "  Checking processes on port $port..."
    
    for pid in $pids; do
        # 获取进程的命令行
        local cmd=$(ps -p $pid -o command= 2>/dev/null)
        
        # 检查是否是VSCode相关进程
        if echo "$cmd" | grep -qiE "(ssh|code|vscode|vscode-server|remote)"; then
            echo "    Skipping VSCode process (PID: $pid): $cmd"
            continue
        fi
        
        # 检查是否是我们的服务进程（uvicorn、npm、node）
        if echo "$cmd" | grep -qiE "(uvicorn|npm|node.*vite)"; then
            echo "    Killing service process (PID: $pid): $cmd"
            kill $pid 2>/dev/null
            sleep 0.5
            # 如果进程还在，强制杀死
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
        else
            echo "    Skipping unknown process (PID: $pid): $cmd"
        fi
    done
    
    sleep 1
}

# 清理端口
echo "Cleaning up ports..."
cleanup_port 8000
cleanup_port 8080

# 确保logs目录存在
mkdir -p logs

# 保存PID的文件
PID_FILE="$PROJECT_ROOT/logs/service_pids.txt"

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

# 保存PID到文件
echo "$API_PID" > "$PID_FILE"
echo "$WEB_PID" >> "$PID_FILE"

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
echo "  ./scripts/stop.sh"
echo "  or: kill $API_PID $WEB_PID"
echo ""
echo "PIDs saved to: $PID_FILE"
