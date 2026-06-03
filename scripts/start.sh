#!/bin/bash
# 启动 waitress 服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR=/srv/waitress
PID_FILE="$SCRIPT_DIR/haiku.pid"
ENV_FILE=/home/user/waitress-testing.env

# 检查 env 文件
if [ ! -f "$ENV_FILE" ]; then
    echo "env 文件不存在: $ENV_FILE"
    exit 1
fi

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "服务已在运行中 (PID: $PID)"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

cd "$PROJECT_DIR"

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --env-file "$ENV_FILE" \
    > "$PROJECT_DIR/logs/uvicorn.log" 2>&1 &

echo $! > "$PID_FILE"
echo "服务已启动 (PID: $!)"
