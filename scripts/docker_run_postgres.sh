
docker rm /colossus_postgres
docker run --name colossus_postgres \
  -e POSTGRES_DB=$COLOSSUS_POSTGRESQL_NAME \
  -e POSTGRES_USER=$COLOSSUS_POSTGRESQL_USER \
  -e POSTGRES_PASSWORD=$COLOSSUS_POSTGRESQL_PASSWORD \
  -p 5432:5432 postgres

