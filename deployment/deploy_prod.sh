#!/bin/bash

ssh zeus@colossusmskcc.canadacentral.cloudapp.azure.com <<EOF
  cd /home/zeus/colossus
  git pull
  source activate colossus
  pip install -r requirements.txt
  python manage.py migrate
  cp ../settings.py colossus/settings.py
  python manage.py runserver 0.0.0.0:8000 &
  exit
EOF