FROM python:3.10.5-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app/main

COPY Pipfile* ./

RUN pip3 install pipenv

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app/main

ENTRYPOINT ["/bin/bash", "/app/main/start-server.sh"]
