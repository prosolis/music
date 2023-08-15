FROM python:3.11.4

COPY ./bots/mpd_bot.py /src/mpd_bot.py

COPY ./bots/helpers/musicplayer/* /src/helpers/musicplayer/

COPY ./bots/helpers/postgres/* /src/helpers/postgres/

RUN chmod +x /src

RUN apt update & apt upgrade

RUN pip install -U \
    pip \
    setuptools \
    wheel

COPY requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

WORKDIR /src

RUN mpd_bot.py
