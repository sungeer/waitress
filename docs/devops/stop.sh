#!/bin/bash
# stop.sh

if [ -f /srv/run/waitress.pid ]; then
    PID=$(cat /srv/run/waitress.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Service stopped (PID: $PID)"
    else
        echo "Process does not exist, clean up PID file"
    fi
    rm -f /srv/run/waitress.pid
else
    echo "PID file does not exist, attempting to force stop..."
    pkill -f "gunicorn.*main:app"
fi