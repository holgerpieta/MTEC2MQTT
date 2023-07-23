#!/bin/bash
cd ../../
sudo docker build -t registry.lan:5000/mtec2mqtt:1.0.0 -f M-TEC-API/docker/Dockerfile .
