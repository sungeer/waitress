#!/bin/bash

date_str = $(date +%m%d)
mkdir -p /srv/bak
mv /srv/waitress.tar "/srv/bak/${date_str}.tar"

rm -rf /srv/waitress
