#!/bin/bash
# 重启 waitress 服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd")

bash "$SCRIPT_DIR/stop.sh"
sleep 1
bash "$SCRIPT_DIR/start.sh"
