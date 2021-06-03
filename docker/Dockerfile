FROM python:3.9-alpine

# Metadata
LABEL maintainer="Guillem López Garcia (wyl.loga@gmail.com)"
LABEL version="0.1"
LABEL description="Base Image that runs a Scalade Function Instance"

# Dependencies
RUN apk update && \
    apk add curl

# Environment
ENV ROOT_DIR=/root
ENV RABBITMQ_CONNECTION_URI="guest:guest@rabbitmq:5672"
ENV PYTHONPATH="${PYTHONPATH}:$ROOT_DIR"

# Commands
WORKDIR $ROOT_DIR

RUN curl -X GET https://bucket-url/ -O

COPY . $ROOT_DIR

ADD ./docker/start_consumer.sh /opt/

CMD ["/bin/sh", "-c", "scalade", "run", "function.py"]
