FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install pyTelegramBotAPI

RUN pip install aiohttp