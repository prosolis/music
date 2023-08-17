FROM python:3.11.4

RUN mkdir ./metadata

WORKDIR /app

COPY ./bots/mpd_bot.py ./mpd_bot.py

COPY ./bots/helpers/musicplayer/* ./helpers/musicplayer/

COPY ./bots/helpers/postgres/* ./helpers/postgres/

RUN chmod +x .

RUN apt update & apt upgrade

RUN pip install -U \
    pip \
    setuptools \
    wheel

COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV METADATA_PATH="./metadata"

CMD [ "python","./mpd_bot.py"]
