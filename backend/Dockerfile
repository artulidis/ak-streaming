FROM python:3.10.7-alpine
# FROM ubuntu
ENV PYTHONUNBUFFERED=1
WORKDIR /backend

RUN apk update && apk add gcc musl-dev postgresql-dev && apk add ffmpeg
# RUN apt-get update && apt-get install -y python3
RUN addgroup root video
# RUN usermod -a -G video root

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
