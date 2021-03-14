FROM python:3.8.6 AS base
LABEL maintainer="glebgar567@gmail.com"
ENV WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ="Europe/Moscow"

#FROM base AS production
#
#RUN apk update \
#    && apk add --no-cache tzdata \
#    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
#    && echo $TZ > /etc/timezone \
#    && date \
#    && cat deps.txt | xargs apk add --no-cache \
#    && apk add --no-cache postgresql-libs \
#    && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
#
WORKDIR ${WORKDIR}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .