#!/bin/bash

ssh -t myue@colossusmskcc.canadacentral.cloudapp.azure.com <<EOF
  cd /home/zeus/colossus
  git pull
  pip install -r requirements.txt
  python manage.py migrate
  cp ../settings.py colossus/settings.py
  python manage.py runserver 0.0.0.0:8000 &
  exit
EOF