#!/bin/bash

ssh ssh -t myue@crcssh.bccrc.ca -t ssh myue@momac31.bccrc.ca <<EOF
  cd ~/Documents/single_cell_lims/
  git pull
  source activate colossus
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver
  exit
EOF