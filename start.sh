#!/usr/bin/env bash
set -euo pipefail

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/scheduler_nohup.log"
PID_FILE="${SCRIPT_DIR}/scheduler.pid"

# 选择并激活虚拟环境（如果存在）
activate_venv() {
  local venv_candidates=("phoneNumber_env" ".venv" "venv" "env")
  for venv in "${venv_candidates[@]}"; do
    if [[ -d "${SCRIPT_DIR}/${venv}" && -f "${SCRIPT_DIR}/${venv}/bin/activate" ]]; then
      # shellcheck disable=SC1090
      source "${SCRIPT_DIR}/${venv}/bin/activate"
      echo "✅ 已激活虚拟环境: ${venv}"
      return 0
    fi
  done
  echo "ℹ️ 未发现虚拟环境，使用系统 Python"
}

is_running() {
  if [[ -f "${PID_FILE}" ]]; then
    local pid
    pid="$(cat "${PID_FILE}")"
    if ps -p "${pid}" > /dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

start() {
  if is_running; then
    echo "⚠️ 调度器已在运行 (PID $(cat "${PID_FILE}"))"
    exit 0
  fi

  activate_venv
  cd "${SCRIPT_DIR}"

  # 使用 --auto 非交互启动
  echo "🚀 通过 nohup 启动 scheduler.py (后台运行)..."
  nohup python3 "${SCRIPT_DIR}/scheduler.py" --auto >> "${LOG_FILE}" 2>&1 &
  echo $! > "${PID_FILE}"
  echo "✅ 已启动，PID: $(cat "${PID_FILE}")"
  echo "📝 日志: ${LOG_FILE}"
}

stop() {
  if ! is_running; then
    echo "ℹ️ 未发现运行中的调度器"
    [[ -f "${PID_FILE}" ]] && rm -f "${PID_FILE}"
    exit 0
  fi
  local pid
  pid="$(cat "${PID_FILE}")"
  echo "🛑 正在停止调度器 (PID ${pid})..."
  kill "${pid}" || true
  rm -f "${PID_FILE}"
  echo "✅ 已停止"
}

status() {
  if is_running; then
    echo "✅ 运行中 (PID $(cat "${PID_FILE}"))"
  else
    echo "❌ 未运行"
  fi
  if [[ -f "${LOG_FILE}" ]]; then
    echo "📄 最近日志:"
    tail -n 20 "${LOG_FILE}" || true
  else
    echo "ℹ️ 尚无日志文件"
  fi
}

usage() {
  cat <<EOF
用法: ./start.sh [start|stop|status]

命令:
  start   后台启动调度器 (nohup)，日志写入 ${LOG_FILE}
  stop    停止后台调度器进程
  status  查看运行状态与最近日志
EOF
}

cmd="${1:-}" 
case "${cmd}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  *) usage ;;
esac