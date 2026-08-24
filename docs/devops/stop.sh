#!/bin/bash

if [ -f /srv/run/waitress.pid ]; then
    kill $(cat /srv/run/waitress.pid)
else
    echo "the PID file /srv/run/waitress.pid does not exist"
fi