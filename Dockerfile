FROM python:3.8.2-slim-buster
MAINTAINER Christian Orner <christianorner8@gmail.com>

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

ENV INSTALL_PATH /energyapp
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD gunicorn -c "python:config.gunicorn" "energyapp:create_app()"