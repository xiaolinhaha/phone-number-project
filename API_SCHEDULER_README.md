# API定时任务调度器

## 📋 功能说明

这个项目为您的工作流程添加了定时任务功能，可以每天10:00自动调用指定的API接口。

### 🎯 主要功能
- ✅ 每天10:00自动调用API接口
- ✅ 完整的日志记录和错误处理
- ✅ 支持手动测试API调用
- ✅ 优雅的启动和停止机制
- ✅ 多种部署方式（Python调度器 + Cron备选）

## 📁 新增文件说明

### 核心文件
- `api_caller.py` - API调用核心模块
- `scheduler.py` - 定时任务调度器（推荐使用）
- `start_scheduler.sh` - 一键启动脚本

### 配置文件
- `crontab_config.txt` - Cron定时任务配置（备选方案）
- `requirements.txt` - 已更新，添加了schedule库

### 日志文件（运行后自动生成）
- `scheduler.log` - 调度器运行日志
- `api_calls.log` - API调用详细日志
- `cron_api_calls.log` - Cron方式的日志（如使用Cron）

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# 1. 进入项目目录
cd /Users/zjl/develop/xiaolinhaha/new/phone-number-project

# 2. 运行启动脚本
./start_scheduler.sh
```

### 方法二：手动启动

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 启动调度器
python3 scheduler.py
```

### 方法三：后台运行

```bash
# 后台运行调度器
nohup ./start_scheduler.sh > scheduler_output.log 2>&1 &

# 查看后台进程
ps aux | grep scheduler

# 停止后台进程
pkill -f scheduler.py
```

## ⚙️ API配置信息

- **API地址**: `https://malla.leagpoint.com/rssz/v1/workflows/run`
- **API密钥**: `app-4djToLaTnYL1NYdlHv75knvx`
- **执行时间**: 每天 10:00
- **请求方式**: POST
- **响应模式**: streaming

## 🛠️ 使用方式

### 1. 交互式启动
运行 `python3 scheduler.py` 后，程序会询问：
- 是否先测试API调用
- 是否启动定时任务调度器

### 2. 测试API调用
```bash
# 单独测试API调用
python3 api_caller.py
```

### 3. 查看日志
```bash
# 实时查看调度器日志
tail -f scheduler.log

# 实时查看API调用日志
tail -f api_calls.log
```

## 🔧 Cron备选方案

如果您更喜欢使用系统的Cron服务：

### 1. 编辑Cron任务
```bash
crontab -e
```

### 2. 添加定时任务
将以下内容添加到crontab文件中：
```bash
# 每天10:00执行API调用
0 10 * * * cd /Users/zjl/develop/xiaolinhaha/new/phone-number-project && /usr/bin/python3 api_caller.py >> /Users/zjl/develop/xiaolinhaha/new/phone-number-project/cron_api_calls.log 2>&1
```

### 3. 查看Cron任务
```bash
crontab -l
```

## 📊 日志说明

### scheduler.log
记录调度器的运行状态：
- 启动和停止信息
- 任务执行时间
- 错误和异常信息

### api_calls.log
记录API调用的详细信息：
- 请求参数和响应
- 网络连接状态
- 流式响应数据

## 🔍 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   pip3 install --upgrade pip
   pip3 install -r requirements.txt
   ```

2. **权限问题**
   ```bash
   chmod +x start_scheduler.sh
   ```

3. **网络连接问题**
   - 检查网络连接
   - 确认API服务器可访问
   - 查看防火墙设置

4. **API调用失败**
   - 检查API密钥是否正确
   - 确认API接口地址
   - 查看api_calls.log获取详细错误信息

### 调试模式

启用详细日志：
```python
# 在api_caller.py或scheduler.py中修改日志级别
logging.basicConfig(level=logging.DEBUG)
```

## 🛑 停止服务

### 前台运行时
按 `Ctrl+C` 优雅停止

### 后台运行时
```bash
# 查找进程
ps aux | grep scheduler

# 停止进程
pkill -f scheduler.py
# 或者使用进程ID
kill <PID>
```

## 📈 监控和维护

### 1. 日志轮转
建议定期清理日志文件：
```bash
# 备份并清空日志
mv scheduler.log scheduler.log.backup
mv api_calls.log api_calls.log.backup
touch scheduler.log api_calls.log
```

### 2. 系统监控
可以配合系统监控工具使用：
- 监控进程状态
- 监控日志文件大小
- 设置告警机制

## 🔄 更新和维护

### 修改执行时间
编辑 `scheduler.py` 文件中的这一行：
```python
schedule.every().day.at("10:00").do(self.scheduled_api_call)
```

### 修改API参数
编辑 `api_caller.py` 文件中的配置：
```python
self.api_key = "your-new-api-key"
self.base_url = "your-new-api-url"
```

## 📞 技术支持

如有问题，请检查：
1. 日志文件中的错误信息
2. 网络连接状态
3. API服务器状态
4. 系统资源使用情况

---

**注意**: 请确保系统时间准确，以保证定时任务按时执行。