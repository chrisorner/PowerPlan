FROM python:3.8.2-slim-buster
MAINTAINER Christian Orner <christianorner8@gmail.com>

WORKDIR /app

COPY requirements.txt requirements.txt

ENV BUILD_DEPS="build-essential" \
    APP_DEPS="curl libpq-dev"

RUN apt-get update \
  && apt-get install -y ${BUILD_DEPS} ${APP_DEPS} --no-install-recommends \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc && rm -rf /usr/share/man \
  && apt-get purge -y --auto-remove ${BUILD_DEPS} \
  && apt-get clean

ARG FLASK_ENV="development"
ENV FLASK_ENV="${FLASK_ENV}" \
    FLASK_APP="energyapp" \
    PYTHONUNBUFFERED="true"

COPY . .

CMD gunicorn -c "python:config.gunicorn" "energyapp:create_app()"