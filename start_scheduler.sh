#!/bin/bash

# API定时任务启动脚本
# 作者: AI Assistant
# 功能: 启动API定时调用服务

echo "🚀 API定时任务启动脚本"
echo "=========================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目录: $SCRIPT_DIR"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python 3"
    exit 1
fi

echo "✅ Python环境检查通过"

# 检查依赖是否安装
echo "🔍 检查依赖..."
if ! python3 -c "import schedule" &> /dev/null; then
    echo "⚠️  未找到schedule库，正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请手动执行: pip3 install -r requirements.txt"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖检查通过"
fi

# 检查必要文件
if [ ! -f "scheduler.py" ]; then
    echo "❌ 错误: 未找到scheduler.py文件"
    exit 1
fi

if [ ! -f "api_caller.py" ]; then
    echo "❌ 错误: 未找到api_caller.py文件"
    exit 1
fi

echo "✅ 文件检查通过"

# 创建日志目录
mkdir -p logs

echo ""
echo "🎯 准备启动定时任务调度器..."
echo "📅 任务计划: 每天 10:00 执行API调用"
echo "🔑 API密钥: app-4djToLaTnYL1NYdlHv75knvx"
echo ""
echo "💡 提示:"
echo "  • 按 Ctrl+C 可以停止服务"
echo "  • 日志文件: scheduler.log 和 api_calls.log"
echo "  • 如需后台运行，请使用: nohup ./start_scheduler.sh &"
echo ""

# 启动调度器
echo "🚀 启动调度器..."
python3 scheduler.py