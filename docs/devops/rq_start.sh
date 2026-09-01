#!/bin/bash

cd /srv/waitress
LOG_FILE=/srv/logs/rq.log RQ_LIFECYCLE_LOG=/srv/logs/rq_lifecycle.log nohup /srv/venvs/waitress/bin/python worker.py > /srv/logs/rq.log 2>&1 &
echo $! > /srv/run/waitress_rq.pid
