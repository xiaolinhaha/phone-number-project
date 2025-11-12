# API定时任务与后台启动说明

## 📋 概览

本项目提供每日自动任务与后台启动脚本，保证在服务器断开连接后仍可持续运行。

### 🎯 每日工作流（11:00）
- 获取号码（调用公共 API，保存到 `files/numberList_YYYY-MM-DD.json`）
- 执行验证码与批量查询（`get_captcha.py`）
- 执行百度标记与公共 API 调用（`phone.py`）

## 📁 相关文件

- `scheduler.py`：定时任务调度器（每日 11:00 运行完整工作流）
- `start.sh`：后台启动/停止/查看状态（使用 `nohup`）
- `api_caller.py`：获取号码的 API 调用器
- `config.json`：API 配置

## 🚀 使用 start.sh（推荐）

### 1) 赋予执行权限
```bash
chmod +x start.sh
```

### 2) 后台启动（nohup）
```bash
./start.sh start
```
- 自动尝试激活虚拟环境（优先顺序：`phoneNumber_env`、`.venv`、`venv`、`env`）
- 使用 `nohup` 后台运行：`python3 scheduler.py --auto`
- 写入日志：`scheduler_nohup.log`
- 写入进程号：`scheduler.pid`

### 3) 查看运行状态与最近日志
```bash
./start.sh status
```

### 4) 停止后台运行
```bash
./start.sh stop
```

## 🛠️ 手动运行（前台）

### 交互模式
```bash
python3 scheduler.py
```
启动后会提示是否开始调度器。

### 非交互模式（直接运行）
```bash
python3 scheduler.py --auto
```

## ⚙️ 配置与执行时间

- `config.json` 中维护 API `api_key`、`base_url`、`response_mode`、`user` 等
- 执行时间：每天 `11:00`（在 `scheduler.py` 中设置）

## 📊 日志说明

- `scheduler.log`：调度器内部日志（由 `scheduler.py` 写入）
- `scheduler_nohup.log`：后台标准输出日志（由 `start.sh` 写入）
- `api_calls.log`：API 调用详细日志（由 `api_caller.py` 写入）

实时查看：
```bash
tail -f scheduler.log
tail -f scheduler_nohup.log
tail -f api_calls.log
```

## 🔍 常见问题与排查

1) 权限问题
```bash
chmod +x start.sh
```

2) 依赖安装
```bash
pip3 install -r requirements.txt
```

3) 无法后台运行
- 检查 `scheduler.pid` 是否存在且对应进程存活
- 查看 `scheduler_nohup.log` 是否有错误输出

4) API 502 或网络问题
- 重试或检查网络
- 查看 `api_calls.log` 获取错误详情

## 🔄 修改与维护

### 修改执行时间
在 `scheduler.py` 中调整：
```python
schedule.every().day.at("11:00").do(self.scheduled_daily_workflow)
```

### 修改 API 参数
在 `config.json` 或 `api_caller.py` 中调整相关字段。

## 📞 技术说明

- `start.sh` 使用 `nohup` 与 PID 文件管理进程，适合服务器部署
- 非交互模式通过 `--auto` 启动，避免 SSH 断连导致任务停止

---

请确保服务器时间准确与依赖安装完整，以保证定时任务按时执行。