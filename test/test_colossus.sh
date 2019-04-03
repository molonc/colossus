#!/bin/bash
set -v
set -e
cd /home/ubuntu/colossus
git fetch origin
git reset --hard origin/master
source venv/bin/activate
/home/ubuntu/colossus/venv/bin/python /home/ubuntu/colossus/backups/get_backups.py
sudo -u postgres psql -c "SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'colossus'"
sudo -u postgres psql -c "DROP database colossus"
sudo -u postgres psql -c "CREATE database colossus"
pg_restore -h localhost -p 5432 -U admin -d colossus -n public < /home/ubuntu/colossus/backups/daily_backup.dump

pip3 install -r requirements.txt --ignore-installed
python3 manage.py migrate
python3 manage.py makemigrations --check

