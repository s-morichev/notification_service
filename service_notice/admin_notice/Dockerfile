# base image
FROM python:3.10

WORKDIR /opt/app
# options
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

RUN chmod a+x ./scripts/run_celery.sh