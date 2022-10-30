FROM python:3.10.4

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN pip3 install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app

EXPOSE 8000

RUN chmod +x /app/start-server.sh

CMD ["/app/start-server.sh"]

