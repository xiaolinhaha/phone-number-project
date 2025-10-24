# 电话号码查询爬虫服务

这是一个功能完整的电话号码查询系统，包含两个主要模块：基于验证码的查询服务和基于百度搜索的标记查询服务。

## 项目特性

### 🚀 核心功能
- ✅ 自动验证码获取和OCR识别
- ✅ 批量电话号码查询
- ✅ Excel文件批量处理
- ✅ 多种查询方式支持
- ✅ 自动重试机制
- ✅ 结果导出和保存

### 🛠 技术特性
- ✅ ddddocr验证码识别
- ✅ 百度搜索API集成
- ✅ pandas Excel处理
- ✅ 完整的异常处理
- ✅ 自动图片清理
- ✅ 详细的日志记录

## 项目结构

```
phoneNumber/
├── get_captcha.py          # 主要查询模块（验证码方式）
├── phone.py               # 百度搜索标记查询模块
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
├── start.sh              # 快速启动脚本
├── ddddocr-master/       # OCR识别库
├── temp_captcha/         # 验证码图片临时目录
├── 副本123out.xlsx       # 示例输入文件
├── 查询结果.xlsx          # 查询结果输出文件
└── __pycache__/          # Python缓存目录
```

## 快速开始

### 1. 一键启动
```bash
chmod +x start.sh
./start.sh
```

### 2. 手动安装
```bash
# 安装依赖
pip install -r requirements.txt

# 运行验证码查询模块
python get_captcha.py

# 或运行百度搜索查询模块
python phone.py
```

## 模块说明

### 📞 get_captcha.py - 验证码查询模块

**主要功能：**
- 从dianhua.cn获取电话号码详细信息
- 自动处理验证码识别
- 支持Excel批量查询
- 自动保存查询结果

**核心类和方法：**

#### `get_captcha()` - 验证码获取
```python
def get_captcha():
    """获取验证码图片和UUID"""
    # 自动获取验证码
    # 保存到temp_captcha目录
    # 返回验证码路径和UUID
```

#### `recognize_captcha(image_path)` - OCR识别
```python
def recognize_captcha(image_path):
    """使用ddddocr识别验证码"""
    # 加载验证码图片
    # OCR识别文字
    # 返回识别结果
```

#### `query_phone_number(phone, captcha_code, uuid)` - 查询电话
```python
def query_phone_number(phone, captcha_code, uuid):
    """查询电话号码信息"""
    # 发送查询请求
    # 解析返回结果
    # 返回详细信息字典
```

#### `batch_query_phones(phone_numbers)` - 批量查询
```python
def batch_query_phones(phone_numbers):
    """批量查询电话号码"""
    # 循环处理每个号码
    # 自动重试失败的查询
    # 返回所有查询结果
```

### 🔍 phone.py - 百度搜索查询模块

**主要功能：**
- 通过百度搜索获取电话号码标记信息
- 支持Excel文件批量处理
- 自动提取标记结果
- 智能重试机制

**核心类：**

#### `PhoneNumberMarker` - 电话标记查询类
```python
class PhoneNumberMarker:
    def get_phone_marker(self, phone_number):
        """获取电话号码标记信息"""
        # 构建百度搜索请求
        # 解析HTML响应
        # 提取标记信息
        
    def process_excel_file(self, input_file, output_file):
        """处理Excel文件批量查询"""
        # 读取Excel文件
        # 批量查询电话标记
        # 保存结果到新文件
```

## 使用示例

### 验证码查询方式
```python
from get_captcha import *

# 单个号码查询
phone = "057725859091"
captcha_path, uuid = get_captcha()
captcha_code = recognize_captcha(captcha_path)
result = query_phone_number(phone, captcha_code, uuid)

# 批量查询（从Excel文件）
phone_numbers = load_phone_numbers_from_excel("副本123out.xlsx")
results = batch_query_phones(phone_numbers)
save_results_to_excel(results, "查询结果.xlsx")
```

### 百度搜索查询方式
```python
from phone import PhoneNumberMarker

# 创建查询实例
marker = PhoneNumberMarker()

# 单个号码查询
result = marker.get_phone_marker("057725859091")

# 批量处理Excel文件
marker.process_excel_file("input.xlsx", "output.xlsx")
```

## 配置说明

### 依赖包版本
```
requests==2.31.0          # HTTP请求库
Pillow==10.0.0           # 图像处理
pytesseract==0.3.10      # OCR识别
opencv-python==4.8.1.78  # 计算机视觉
numpy==2.2.6             # 数值计算
loguru==0.7.2            # 日志管理
pandas==2.2.3            # 数据处理
openpyxl==3.1.2          # Excel文件处理
fake-useragent==2.1.0    # 用户代理生成
```

### 请求头配置
- User-Agent: 模拟Chrome浏览器
- 完整的HTTP安全头
- Cookie自动管理
- 防反爬虫机制

## 高级功能

### 🔄 自动重试机制
- 验证码识别失败自动重试
- 网络请求失败自动重试
- 智能延时避免频率限制

### 🧹 自动清理功能
- 查询完成后自动删除验证码图片
- 临时文件自动管理
- 内存使用优化

### 📊 批量处理优化
- Excel文件格式自动检测
- 电话号码格式标准化
- 结果数据结构化保存

## 故障排除

### 常见问题

1. **OCR识别率低**
   ```bash
   # 检查ddddocr安装
   pip install ddddocr
   
   # 验证码图片质量检查
   ls -la temp_captcha/
   ```

2. **Excel文件读取失败**
   ```bash
   # 检查文件格式和权限
   file 副本123out.xlsx
   
   # 确保openpyxl正确安装
   pip install openpyxl
   ```

3. **网络请求失败**
   ```bash
   # 检查网络连接
   ping dianhua.cn
   
   # 检查代理设置
   echo $http_proxy
   ```

4. **依赖包冲突**
   ```bash
   # 重新安装所有依赖
   pip install -r requirements.txt --force-reinstall
   ```

## 性能优化

### 批量查询优化
- 合理的请求间隔（1-2秒）
- 失败重试机制（最多5次）
- 内存使用监控

### 文件处理优化
- 大文件分块处理
- 临时文件及时清理
- 结果实时保存

## 安全注意事项

1. **合规使用**: 仅用于合法的电话号码查询
2. **频率控制**: 避免过于频繁的请求
3. **数据保护**: 查询结果妥善保管
4. **网络安全**: 注意保护个人隐私信息

## 更新日志

### v2.0.0 (当前版本)
- ✅ 新增百度搜索查询模块
- ✅ 完善Excel批量处理功能
- ✅ 优化验证码识别准确率
- ✅ 增加自动图片清理功能
- ✅ 改进错误处理和重试机制

### v1.0.0
- ✅ 基础验证码查询功能
- ✅ OCR验证码识别
- ✅ 基本的批量查询支持

## 许可证

本项目仅供学习和研究使用，请遵守相关网站的使用条款和robots.txt规定。

## 免责声明

使用本工具时请遵守相关法律法规和网站使用条款，开发者不承担因使用本工具而产生的任何法律责任。

---

**开发者**: 融数科技  
**更新时间**: 2025年1月  
**技术支持**: 如有问题请查看故障排除部分或提交Issue