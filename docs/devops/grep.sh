#!/bin/bash

result=$(ps -ef | grep gunicorn | grep -v grep | grep -v '\.sh')
if [ -z "$result" ]; then
  echo "no gunicorn"
else
  echo "gunicorn list: "
  echo "$result"
fi
