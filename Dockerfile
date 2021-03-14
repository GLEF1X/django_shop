FROM python:3.8

ENV WORKDIR /usr/src/app

WORKDIR ${WORKDIR}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .