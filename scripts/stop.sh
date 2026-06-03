#!/bin/bash
# 停止 waitress 服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/haiku.pid"

# 优先用 PID 文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$PID_FILE"
        echo "服务已停止 (PID: $PID)"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# PID 文件不可用，直接查进程
PID=$(pgrep -f 'uvicorn app:app' 2>/dev/null)
if [ -z "$PID" ]; then
    echo "未找到 uvicorn 进程"
    exit 1
fi

kill "$PID"
echo "已停止 (PID: $PID)"
