#!/bin/bash
# ETF量化分析系统 - 安装脚本

echo "=========================================="
echo "ETF量化分析系统 - 安装脚本"
echo "=========================================="

# 检查Python版本
echo ""
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前Python版本: $python_version"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n): " create_venv
if [ "$create_venv" = "y" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "虚拟环境创建成功"
    
    echo ""
    echo "激活虚拟环境..."
    source venv/bin/activate
    echo "虚拟环境已激活"
fi

# 安装依赖
echo ""
echo "安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 检查安装结果
echo ""
echo "=========================================="
echo "检查安装结果..."
echo "=========================================="

packages=("akshare" "pandas" "pandas_ta" "backtrader" "matplotlib" "numpy")

for pkg in "${packages[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        version=$(python3 -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "unknown")
        echo "✓ $pkg ($version)"
    else
        echo "✗ $pkg 未安装"
    fi
done

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "快速开始:"
echo "  1. 运行测试: python3 test_system.py"
echo "  2. 查看示例: python3 examples.py"
echo "  3. 查看帮助: python3 main.py --help"
echo ""
echo "如使用了虚拟环境，请先激活:"
echo "  source venv/bin/activate"
echo ""
