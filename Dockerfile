# Colossus
# Version 1.0

FROM python:2.7.15

ENV PYTHONUNBUFFERED 1

RUN mkdir /colossus

WORKDIR /colossus

ADD . /colossus/

RUN pip install --upgrade pip && pip install -r docker-requirements.txt --ignore-installed

EXPOSE 8001
