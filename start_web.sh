#!/bin/bash

# Web服务一键启动脚本

echo "========================================="
echo "  ETF量化分析系统 - Web服务启动"
echo "========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm"
    exit 1
fi

echo "环境检查通过"
echo ""

# 安装Python依赖
echo "正在安装Python依赖..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Python依赖安装成功"
else
    echo "✗ Python依赖安装失败"
    exit 1
fi
echo ""

# 安装前端依赖
echo "正在安装前端依赖..."
cd web
npm install --silent
if [ $? -eq 0 ]; then
    echo "✓ 前端依赖安装成功"
else
    echo "✗ 前端依赖安装失败"
    exit 1
fi
cd ..
echo ""

echo "========================================="
echo "  启动说明"
echo "========================================="
echo ""
echo "请分别在两个终端中运行以下命令："
echo ""
echo "终端1 - 启动后端服务："
echo "  cd /home/df/df-stock"
echo "  ./start_api.sh"
echo ""
echo "终端2 - 启动前端服务："
echo "  cd /home/df/df-stock/web"
echo "  npm run dev"
echo ""
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:8080"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "========================================="
