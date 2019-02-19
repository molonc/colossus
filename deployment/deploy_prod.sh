<<EOF
  cd ~/colossus
  git pull
  source bin/activate
  pip install -r requirements.txt
  python manage.py migrate
  sudo supervisorctl restart colossus
  exit
EOF