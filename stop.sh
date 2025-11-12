#!/usr/bin/env bash
set -euo pipefail

# 项目根目录与PID文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/scheduler.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "❌ 未找到PID文件: ${PID_FILE}"
  echo "ℹ️ 请确认已通过 start.sh 启动，或手动检查进程。"
  exit 1
fi

PID="$(cat "${PID_FILE}")"
if [[ -z "${PID}" ]]; then
  echo "❌ PID文件为空或格式错误: ${PID_FILE}"
  exit 1
fi

# 检查进程是否存在
if ! ps -p "${PID}" > /dev/null 2>&1; then
  echo "ℹ️ 进程不在运行 (PID ${PID})，清理PID文件。"
  rm -f "${PID_FILE}"
  exit 0
fi

echo "🛑 正在停止调度器 (PID ${PID})..."
kill "${PID}" || true

# 等待最多5秒，若仍在运行则强制停止
for i in {1..5}; do
  if ! ps -p "${PID}" > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ps -p "${PID}" > /dev/null 2>&1; then
  echo "⚠️ 进程未按预期退出，执行强制停止 (kill -9 ${PID})"
  kill -9 "${PID}" || true
fi

rm -f "${PID_FILE}"
echo "✅ 已停止调度器，并清理PID文件"