#!/bin/bash
# start.sh

cd /srv/waitress

# 启动服务
nohup gunicorn -c gunicorn.conf.py main:app > /dev/null 2>&1 &

# 记录PID
echo $! > /srv/run/waitress.pid

echo "Gunicorn is started，PID: $(cat /srv/run/waitress.pid)"