#!/bin/bash
set -v
cd /home/ubuntu/colossus
git fetch origin
git reset --hard origin/master
source venv/bin/activate
pip3 install -r requirements.txt --ignore-installed
python manage.py migrate
sudo systemctl daemon-reload
sudo systemctl restart uwsgi
exit

