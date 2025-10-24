#!/bin/bash

# 电话号码查询爬虫服务 - 完整环境安装脚本
# 包含ddddocr-master和项目所有依赖的一键安装
# 作者: 融数科技
# 版本: v2.0.0

echo "🚀 电话号码查询爬虫服务 - 完整环境安装"
echo "=============================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 全局变量
PYTHON_CMD=""
PIP_CMD=""
PROJECT_ROOT=$(pwd)

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# 检查操作系统
check_os() {
    print_step "检查操作系统..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "检测到 macOS 系统"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "检测到 Linux 系统"
    else
        OS="unknown"
        print_warning "未知操作系统: $OSTYPE"
    fi
}

# 检查Python环境
check_python() {
    print_step "检查Python环境..."
    
    # 检查python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python3版本: $python_version"
    elif command -v python &> /dev/null; then
        python_version=$(python --version 2>&1 | awk '{print $2}')
        if [[ $python_version == 3.* ]]; then
            PYTHON_CMD="python"
            print_success "Python版本: $python_version"
        else
            print_error "需要Python 3.x版本，当前版本: $python_version"
            exit 1
        fi
    else
        print_error "未找到Python，请先安装Python 3.x"
        exit 1
    fi
    
    # 检查Python版本是否符合要求 (3.7-3.13)
    version_check=$($PYTHON_CMD -c "
import sys
version = sys.version_info
if version.major == 3 and 7 <= version.minor <= 13:
    print('OK')
else:
    print('FAIL')
")
    
    if [ "$version_check" != "OK" ]; then
        print_error "Python版本不符合要求，需要Python 3.7-3.13"
        exit 1
    fi
}

# 检查pip环境
check_pip() {
    print_step "检查pip环境..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    pip_version=$($PIP_CMD --version 2>&1)
    print_success "pip版本: $pip_version"
}

# 检查必要文件
check_files() {
    print_step "检查项目文件..."
    
    required_files=("get_captcha.py" "phone.py" "requirements.txt")
    required_dirs=("ddddocr-master")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "缺少必要目录: $dir"
            exit 1
        fi
    done
    
    print_success "项目文件检查完成"
}

# 创建虚拟环境（可选）
create_virtual_env() {
    print_step "检查是否需要创建虚拟环境..."
    
    read -p "是否创建Python虚拟环境？(推荐) [y/N]: " create_venv
    
    if [[ $create_venv =~ ^[Yy]$ ]]; then
        venv_name="phoneNumber_env"
        
        if [ ! -d "$venv_name" ]; then
            print_info "创建虚拟环境: $venv_name"
            $PYTHON_CMD -m venv $venv_name
        fi
        
        print_info "激活虚拟环境..."
        source $venv_name/bin/activate
        
        # 更新pip命令为虚拟环境中的pip
        PIP_CMD="pip"
        
        print_success "虚拟环境已激活"
        print_warning "注意: 下次使用时需要手动激活虚拟环境: source $venv_name/bin/activate"
    fi
}

# 解决依赖冲突
resolve_dependencies() {
    print_step "解决依赖包版本冲突..."
    
    # 创建临时requirements文件，解决版本冲突
    temp_req="temp_requirements.txt"
    
    cat > $temp_req << EOF
# 核心依赖 - 兼容版本
numpy>=1.21.0,<2.0.0
Pillow>=8.0.0
opencv-python>=4.5.0
requests>=2.25.0

# OCR相关依赖
onnxruntime>=1.10.0
onnx>=1.10.0

# Excel处理
pandas>=1.3.0
openpyxl>=3.0.0

# 网络请求增强
fake-useragent>=1.0.0

# 日志处理
loguru>=0.6.0

# 图像处理增强
pytesseract>=0.3.8

# API相关（可选）
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
pydantic>=2.0.0
EOF

    print_success "依赖冲突解决方案已准备"
}

# 安装项目依赖
install_project_dependencies() {
    print_step "安装项目基础依赖..."
    
    # 先安装解决冲突后的依赖
    resolve_dependencies
    
    print_info "安装兼容版本的依赖包..."
    $PIP_CMD install -r temp_requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "项目基础依赖安装完成"
    else
        print_error "项目基础依赖安装失败"
        exit 1
    fi
    
    # 清理临时文件
    rm -f temp_requirements.txt
}

# 安装ddddocr
install_ddddocr() {
    print_step "安装ddddocr OCR库..."
    
    cd ddddocr-master
    
    # 检查是否已经安装
    if $PYTHON_CMD -c "import ddddocr" 2>/dev/null; then
        print_warning "ddddocr已安装，跳过安装步骤"
    else
        print_info "从源码安装ddddocr..."
        
        # 安装ddddocr及其依赖
        $PIP_CMD install -e .
        
        if [ $? -eq 0 ]; then
            print_success "ddddocr安装完成"
        else
            print_error "ddddocr安装失败"
            cd "$PROJECT_ROOT"
            exit 1
        fi
    fi
    
    cd "$PROJECT_ROOT"
}

# 创建必要目录
create_directories() {
    print_step "创建必要目录..."
    
    directories=("temp_captcha" "logs" "results")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "创建目录: $dir"
        fi
    done
}

# 测试所有模块导入
test_imports() {
    print_step "测试模块导入..."
    
    print_info "测试基础依赖..."
    $PYTHON_CMD -c "
import sys
print(f'Python版本: {sys.version}')

# 测试基础模块
import pandas as pd
print(f'pandas版本: {pd.__version__}')

import requests
print(f'requests版本: {requests.__version__}')

import numpy as np
print(f'numpy版本: {np.__version__}')

import cv2
print(f'opencv版本: {cv2.__version__}')

from PIL import Image
print('Pillow导入成功')

import openpyxl
print(f'openpyxl版本: {openpyxl.__version__}')

from fake_useragent import UserAgent
print('fake_useragent导入成功')

print('✅ 基础依赖测试通过')
"

    if [ $? -ne 0 ]; then
        print_error "基础依赖测试失败"
        exit 1
    fi
    
    print_info "测试ddddocr..."
    $PYTHON_CMD -c "
import ddddocr
print('ddddocr导入成功')

# 测试OCR功能
ocr = ddddocr.DdddOcr()
print('ddddocr初始化成功')
print('✅ ddddocr测试通过')
"

    if [ $? -ne 0 ]; then
        print_error "ddddocr测试失败"
        exit 1
    fi
    
    print_success "所有模块导入测试通过"
}

# 测试项目功能
test_project_functionality() {
    print_step "测试项目功能..."
    
    # 测试get_captcha.py的导入
    print_info "测试get_captcha.py模块..."
    $PYTHON_CMD -c "
try:
    from get_captcha import get_captcha_and_save, recognize_captcha_with_ocr, batch_query_phones
    print('✅ get_captcha.py模块导入成功')
except Exception as e:
    print(f'❌ get_captcha.py模块导入失败: {e}')
    exit(1)
"

    # 测试phone.py的导入
    print_info "测试phone.py模块..."
    $PYTHON_CMD -c "
try:
    from phone import PhoneNumberMarker
    marker = PhoneNumberMarker()
    print('✅ phone.py模块导入成功')
except Exception as e:
    print(f'❌ phone.py模块导入失败: {e}')
    exit(1)
"

    print_success "项目功能测试通过"
}

# 显示使用说明
show_usage() {
    echo ""
    echo -e "${CYAN}🎯 安装完成！使用说明:${NC}"
    echo "=================================="
    echo ""
    echo -e "${BLUE}📞 验证码查询模式:${NC}"
    echo "   python3 get_captcha.py"
    echo "   - 从dianhua.cn查询电话号码信息"
    echo "   - 自动OCR识别验证码"
    echo "   - 支持Excel批量查询"
    echo ""
    echo -e "${BLUE}🔍 百度搜索查询模式:${NC}"
    echo "   python3 phone.py"
    echo "   - 通过百度搜索获取号码标记"
    echo "   - 支持Excel批量处理"
    echo ""
    echo -e "${BLUE}📁 项目文件说明:${NC}"
    echo "   - 输入文件: 副本123out.xlsx"
    echo "   - 输出文件: 查询结果.xlsx"
    echo "   - 验证码目录: temp_captcha/"
    echo "   - 日志目录: logs/"
    echo ""
    echo -e "${BLUE}🔧 环境信息:${NC}"
    echo "   - Python: $($PYTHON_CMD --version)"
    echo "   - pip: $($PIP_CMD --version | head -n1)"
    echo "   - 项目路径: $PROJECT_ROOT"
    
    if [ -d "phoneNumber_env" ]; then
        echo ""
        echo -e "${YELLOW}⚠️  虚拟环境提醒:${NC}"
        echo "   下次使用前请激活虚拟环境:"
        echo "   source phoneNumber_env/bin/activate"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 环境安装完成，可以开始使用了！${NC}"
}

# 主函数
main() {
    echo -e "${CYAN}开始安装电话号码查询爬虫服务环境...${NC}"
    echo ""
    
    # 环境检查
    check_os
    check_python
    check_pip
    check_files
    
    # 可选创建虚拟环境
    create_virtual_env
    
    # 安装依赖
    install_project_dependencies
    install_ddddocr
    
    # 创建目录
    create_directories
    
    # 测试功能
    test_imports
    test_project_functionality
    
    # 显示使用说明
    show_usage
}

# 错误处理
set -e
trap 'print_error "安装过程中发生错误，请检查上面的错误信息"' ERR

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi