FROM python:latest

RUN apt update && \
    apt install -y python3-pip && \
    pip install --upgrade pip && \
    pip install python-dateutil paho-mqtt certifi charset-normalizer idna pyYAML requests six urllib3

RUN mkdir /M-TEC-API

COPY M-TEC-API/ /M-TEC-API

ENTRYPOINT [ "/M-TEC-API/docker/run.sh" ]
