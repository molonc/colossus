#!/bin/bash
set -v
set -e
cd /home/ubuntu/colossus
git fetch origin
git reset --hard origin/master
source venv/bin/activate
pip3 install -r requirements.txt --ignore-installed
python3 manage.py migrate
python3 manage.py makemigrations --check
kill $(ps aux | grep '[r]unserver' | awk '{print $2}')
/usr/bin/python3 manage.py runserver 0.0.0.0:8000 log.txt 2>&1 &
