#!/bin/bash

if [ -f /srv/run/waitress_rq.pid ]; then
    kill $(cat /srv/run/waitress_rq.pid)
    rm -f /srv/run/waitress_rq.pid
else
    echo "the PID file /srv/run/waitress_rq.pid does not exist"
fi
