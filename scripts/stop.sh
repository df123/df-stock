#!/bin/bash

# 功能：安全停止后端和前端服务

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

PID_FILE="$PROJECT_ROOT/logs/service_pids.txt"

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "PID file not found: $PID_FILE"
    echo "Services may not be running or were started manually."
    echo ""
    echo "Attempting to find and stop services by port..."
    
    # 尝试通过端口查找并停止服务
    for port in 8000 8080; do
        pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                cmd=$(ps -p $pid -o command= 2>/dev/null)
                if echo "$cmd" | grep -qiE "(uvicorn|npm|node.*vite)"; then
                    echo "Stopping service on port $port (PID: $pid)"
                    kill $pid 2>/dev/null
                fi
            done
        fi
    done
    
    echo "Done."
    exit 0
fi

# 读取PID并停止服务
echo "Stopping services..."
while read -r pid; do
    if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
        cmd=$(ps -p $pid -o command= 2>/dev/null)
        echo "  Stopping process (PID: $pid): $cmd"
        kill $pid 2>/dev/null
        sleep 0.5
        # 如果进程还在，强制杀死
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Force killing process (PID: $pid)"
            kill -9 $pid 2>/dev/null
        fi
    else
        echo "  Process (PID: $pid) not running"
    fi
done < "$PID_FILE"

# 删除PID文件
rm -f "$PID_FILE"

echo "All services stopped."
