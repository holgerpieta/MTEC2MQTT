FROM python:slim

RUN pip install --no-cache-dir python-dateutil paho-mqtt certifi charset-normalizer idna pyYAML requests six urllib3 && \
    pip cache purge

ADD . /M-TEC-API

WORKDIR /M-TEC-API
CMD ["python3", "MTEC2mqtt.py"]
