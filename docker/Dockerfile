FROM python:slim

RUN apt update && \
    apt install -y python3-pip && \
	apt-get clean
	
RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir python-dateutil paho-mqtt certifi charset-normalizer idna pyYAML requests six urllib3 && \
	pip cache purge

ADD . /M-TEC-API

WORKDIR /M-TEC-API
CMD ["python3", "MTEC2mqtt.py"]
