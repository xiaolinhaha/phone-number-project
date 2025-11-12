# 服务器安装与启动指南（非 headless OpenCV）

适用场景：Python 3.11，服务器网络较慢，希望使用非 headless 的 `opencv-python`。

项目路径（服务器）：`/home/rongshu/app/back_end/scheduler/phone-number-project`

## 一次性安装关键依赖

```bash
cd /home/rongshu/app/back_end/scheduler/phone-number-project

# 清理可能的冲突安装
python3 -m pip uninstall -y opencv-python opencv-python-headless || true

# 安装兼容的 numpy、OpenCV 和 onnxruntime（强制用二进制轮子，加镜像、超时与续传）
python3 -m pip install --user \
  numpy==1.26.4 opencv-python==4.8.1.78 onnxruntime \
  --only-binary=opencv-python,numpy,onnxruntime \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --default-timeout 300 --retries 10 --resume-retries 50
```

说明：
- `opencv-python==4.8.1.78` 有 Python 3.11 的预编译轮子，避免源码编译。
- `numpy==1.26.4` 兼容 `pandas 2.2.x`，也满足 `ddddocr` 的 `numpy<2.0.0` 约束。
- 如有本机代理，可在命令前加：
  ```bash
  HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 ALL_PROXY=socks5h://127.0.0.1:7890 \
  python3 -m pip install --user ...
  ```

## 安装项目依赖（两份 requirements）

```bash
# 顶层依赖
python3 -m pip install --user -r requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --default-timeout 300 --retries 10 --resume-retries 50 \
  --only-binary=opencv-python,numpy,onnxruntime

# ddddocr 依赖
python3 -m pip install --user -r ddddocr-master/requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --default-timeout 300 --retries 10 --resume-retries 50 \
  --only-binary=opencv-python,numpy,onnxruntime
```

可选：设置全局镜像（后续命令都不需加 `-i`）：

```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
timeout = 300
EOF
```

## 验证依赖

```bash
python3 -c "import cv2, numpy as np, onnxruntime as ort; print('cv2', cv2.__version__, 'numpy', np.__version__, 'onnxruntime', ort.__version__)"

# 运行验证码脚本（若失败，先根据报错补缺包）
python3 get_captcha.py
```

## 启动与检查

```bash
# 赋权并后台启动
chmod +x start.sh && ./start.sh start

# 查看状态与日志
./start.sh status
tail -n 50 scheduler_nohup.log
tail -n 50 scheduler.log

# 如无法赋权，可用 bash 显式执行
bash start.sh start
```

说明：
- `start.sh` 通过 `nohup` 后台运行 `scheduler.py --auto`，PID 写入 `scheduler.pid`，日志追加到 `scheduler_nohup.log`。
- `scheduler.py` 默认每天 14:00 触发一次完整工作流（获取号码 → 并行执行 `get_captcha.py` 与 `phone.py`）。

## 网络很慢时（离线 wheel 安装）

```bash
mkdir -p ~/wheelhouse
python3 -m pip download numpy==1.26.4 opencv-python==4.8.1.78 onnxruntime \
  -d ~/wheelhouse -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --default-timeout 300 --retries 10 --resume-retries 50 \
  --only-binary=opencv-python,numpy,onnxruntime

python3 -m pip install --user --no-index --find-links ~/wheelhouse \
  numpy==1.26.4 opencv-python==4.8.1.78 onnxruntime
```

## 常见问题排查

- 缺少 `onnxruntime`：安装 `python3 -m pip install --user onnxruntime ...`
- OpenCV 运行时报 `libGL.so.1` 缺失：
  - Debian/Ubuntu：`sudo apt-get install -y libgl1 libglib2.0-0`
  - CentOS/RHEL：`sudo yum install -y mesa-libGL`
  - Fedora：`sudo dnf install -y mesa-libGL`
  - 无 `sudo` 时需联系管理员或使用容器环境。
- `start.sh: Permission denied`：使用 `chmod +x start.sh` 或 `bash start.sh start`。
- 代理示例：
  ```bash
  HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 ALL_PROXY=socks5h://127.0.0.1:7890 \
  python3 -m pip install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout 300
  ```

## 使用安装脚本（已增强慢网支持）

`install_missing.sh` 支持以下环境变量：
- `PIP_INDEX_URL` 镜像地址（例如清华）
- `PIP_TIMEOUT` 超时秒数（默认 300）
- `PIP_RETRIES` 重试次数（默认 10）
- `PIP_RESUME_RETRIES` 断点续传重试（默认 50）

示例：

```bash
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
PIP_TIMEOUT=300 PIP_RETRIES=10 PIP_RESUME_RETRIES=50 \
./install_missing.sh
```

---

复制以上命令到服务器按顺序执行，即可完成安装与运行检查。如遇到具体报错，把终端输出贴给我，我帮你定位并给出快速修复命令。