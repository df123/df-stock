#!/bin/bash

# ETF量化分析系统 - 一键启动脚本
# 功能：检查端口占用、关闭旧进程、启动后端和前端服务
# 注意: 此脚本使用 --reload 模式启动后端，适合开发环境
# 生产环境应移除 --reload 标志

# 定义清理函数
cleanup() {
    echo ""
    echo "正在停止已启动的服务..."
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "✓ 后端API服务已停止"
    fi
    if [ -n "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null
        echo "✓ 前端Web服务已停止"
    fi
    exit 0
}

# 捕获中断信号，确保清理
trap cleanup SIGINT SIGTERM

echo "========================================="
echo "  ETF量化分析系统 - 一键启动"
echo "========================================="
echo ""

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "项目根目录: $PROJECT_ROOT"
echo ""

# 检查端口占用并关闭进程的函数
check_and_kill_port() {
    local port=$1
    local service_name=$2
    
    echo "检查 $service_name 端口 $port..."
    
    # 使用 lsof 检查端口占用
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo "⚠️  端口 $port 已被占用 (PID: $pid)"
        echo "正在尝试优雅关闭 $service_name 进程..."
        
        # 先尝试优雅终止 (SIGTERM)
        if kill $pid 2>/dev/null; then
            echo "已发送终止信号，等待进程退出..."
            sleep 2
            
            # 检查进程是否仍在运行
            pid=$(lsof -ti:$port 2>/dev/null)
            if [ -n "$pid" ]; then
                echo "进程未响应，正在强制终止..."
                # 强制终止 (SIGKILL)
                if kill -9 $pid 2>/dev/null; then
                    sleep 1
                    # 再次检查
                    pid=$(lsof -ti:$port 2>/dev/null)
                    if [ -n "$pid" ]; then
                        echo "✗ 关闭 $service_name 进程失败"
                        return 1
                    else
                        echo "✓ $service_name 进程已强制关闭"
                    fi
                else
                    echo "✗ 无法终止进程 (权限不足或其他错误)"
                    return 1
                fi
            else
                echo "✓ $service_name 进程已优雅关闭"
            fi
        else
            echo "✗ 无法终止进程 (权限不足或其他错误)"
            return 1
        fi
    else
        echo "✓ 端口 $port 未被占用"
    fi
    echo ""
    return 0
}

# 检查环境
echo "检查运行环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm"
    exit 1
fi

if ! command -v lsof &> /dev/null; then
    echo "错误: 未找到lsof命令"
    exit 1
fi

echo "✓ 环境检查通过"
echo ""

# 确保logs目录存在
mkdir -p logs

# 检查并关闭API服务（端口8000）
check_and_kill_port 8000 "后端API"
if [ $? -ne 0 ]; then
    echo "无法关闭后端API服务，请手动处理"
    exit 1
fi

# 检查并关闭Web服务（端口8080）
check_and_kill_port 8080 "前端Web"
if [ $? -ne 0 ]; then
    echo "无法关闭前端Web服务，请手动处理"
    exit 1
fi

# 启动后端API服务
echo "========================================="
echo "  启动后端API服务"
echo "========================================="
echo ""
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "日志文件: logs/api.log"
echo ""

PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH nohup python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!

echo "✓ 后端API服务已启动 (PID: $API_PID)"
echo ""

# 等待后端服务启动
echo "等待后端服务启动..."
sleep 3

# 检查后端服务是否启动成功
if ! lsof -ti:8000 > /dev/null 2>&1; then
    echo "✗ 后端API服务启动失败，请查看日志: logs/api.log"
    exit 1
fi

echo "✓ 后端API服务启动成功"
echo ""

# 启动前端Web服务
echo "========================================="
echo "  启动前端Web服务"
echo "========================================="
echo ""
echo "前端地址: http://localhost:8080"
echo "日志文件: logs/web.log"
echo ""

cd web
nohup npm run dev > ../logs/web.log 2>&1 &
WEB_PID=$!
cd ..

echo "✓ 前端Web服务已启动 (PID: $WEB_PID)"
echo ""

# 等待前端服务启动
echo "等待前端服务启动..."
sleep 3

# 检查前端服务是否启动成功
if ! lsof -ti:8080 > /dev/null 2>&1; then
    echo "✗ 前端Web服务启动失败，请查看日志: logs/web.log"
    exit 1
fi

echo "✓ 前端Web服务启动成功"
echo ""

# 显示启动信息
echo "========================================="
echo "  服务启动完成"
echo "========================================="
echo ""
echo "后端API服务:"
echo "  地址: http://localhost:8000"
echo "  文档: http://localhost:8000/docs"
echo "  PID: $API_PID"
echo "  日志: logs/api.log"
echo ""
echo "前端Web服务:"
echo "  地址: http://localhost:8080"
echo "  PID: $WEB_PID"
echo "  日志: logs/web.log"
echo ""
echo "查看实时日志:"
echo "  后端: tail -f logs/api.log"
echo "  前端: tail -f logs/web.log"
echo ""
echo "停止服务:"
echo "  kill $API_PID $WEB_PID"
echo ""
echo "========================================="
