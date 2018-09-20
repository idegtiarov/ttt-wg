FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y vim

RUN mkdir /ttt
WORKDIR /ttt
ADD . /ttt/
RUN pip install -r requirements.txt
