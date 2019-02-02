# Colossus
# Version 1.0

FROM python:2.7.15

ENV PYTHONUNBUFFERED 1

ENV COLOSSUS_DEBUG true
ENV COLOSSUS_ALLOWED_HOSTS *
ENV COLOSSUS_POSTGRESQL_NAME colossus_dev
ENV COLOSSUS_POSTGRESQL_USER simong
ENV COLOSSUS_POSTGRESQL_PASSWORD pinchpinch
ENV COLOSSUS_POSTGRESQL_HOST db_colossus
ENV COLOSSUS_POSTGRESQL_PORT 5432
ENV COLOSSUS_SECRET_KEY whatever 

RUN mkdir /colossus

WORKDIR /colossus

ADD . /colossus/

RUN pip install --upgrade pip && pip install -r docker-requirements.txt --ignore-installed

EXPOSE 8001
