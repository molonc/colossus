ssh myue@13.71.161.241 <<EOF
  cd colossus
  git pull
  source bin/activate
  pip install -r requirements.txt
  ./manage.py migrate
  sudo supervisorctl restart colossus
  exit
EOF