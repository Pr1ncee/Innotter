FROM python:3.10.5-slim AS base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app/microservice

COPY Pipfile* ./

RUN pip3 install pipenv

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app/microservice


FROM base AS main
ENTRYPOINT ["/bin/bash", "/app/microservice/scripts/start-server.sh"]
