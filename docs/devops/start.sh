#!/bin/bash

nohup /srv/venvs/waitress/bin/gunicorn -c /srv/waitress/gunicorn.conf.py app:app > /dev/null 2>&1 &
