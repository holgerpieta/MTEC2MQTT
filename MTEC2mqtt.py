#!/usr/bin/env python3
"""
This tool enables to query MTECapi and can act as demo on how to use the API
(c) 2023 by Christian Rödel 
"""
from config import cfg
import json
import datetime
from dateutil.relativedelta import relativedelta
import MTECapi
from paho.mqtt import client as mqtt_client
import time
import random
import logging

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

DEBUG = True

#-----------------------------
def connect_mqtt():
  broker = cfg["MQTT_BROKER"]
  port = cfg["MQTT_PORT"]
  user = cfg["MQTT_USER"]
  password = cfg["MQTT_PASSWORD"]
  client_id = f'publish-{random.randint(0, 1000)}'
 
  clogger.debug("connecting to broker " + broker + " on port " + str(port) + " with client_id " + client_id)

  topic = cfg["MQTT_BASE_TOPIC"] + "/" + cfg["PV_DEVICE_ID"]

  def on_connect(client, userdata, flags, rc):
    print("fubar")
    if rc == 0:
      clogger.info("Connected to MQTT Broker!")
    else:
      clogger.warn("Failed to connect, return code %d\n", rc)

  def on_disconnect(client, userdata, rc):
    clogger.warn("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
      clogger.info("Reconnecting in %d seconds...", reconnect_delay)
      time.sleep(reconnect_delay)
  
      try:
        client.reconnect()
        clogger.info("Reconnected successfully!")
        return
      except Exception as err:
        clogger.error("%s. Reconnect failed. Retrying...", err)

      reconnect_delay *= RECONNECT_RATE
      reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
      reconnect_count += 1
    clogger.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

  # Set Connecting Client ID
  client = mqtt_client.Client(client_id)

  if user != "" and password != "":
    client.username_pw_set(username, password)

  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  
  client.connect(broker, port, 60)
  return client

#-----------------------------
def show_station_data ( api ):
  stationId = let_user_select_station(api)
  data = api.query_station_data( stationId )
  idx=1
  if data: 
    print( "--------------------------------------------------------" )
    print( "Current data: for station '{}': {}".format( data["stationId"], data["stationName"] ) )
    print( "- Run status:     {}".format( data["stationRunStatus"] ))   # TODO: find out meaning (1=OK)?
    print( "- Run type:       {}".format( data["stationRunType"] ))       # TODO: find out meaning  
    print( "- Lack of master: {}".format( data["lackMaster"] ))     # TODO: find out meaning (grid not available?)  
    print( "PV Energy:" )
    print( "- Today:   {} {}".format( data["todayEnergy"]["value"], data["todayEnergy"]["unit"] ))
    print( "- Month:   {} {}".format( data["monthEnergy"]["value"], data["monthEnergy"]["unit"] ))
    print( "- Year:    {} {}".format( data["yearEnergy"]["value"], data["yearEnergy"]["unit"] ))
    print( "- Total:   {} {}".format( data["totalEnergy"]["value"], data["totalEnergy"]["unit"] ))
    print( "Current stats:" )
    print( "- PV:      {} {}, direction: {} ({})".format( data["PV"]["value"], data["PV"]["unit"], 
          data["PV"]["direction"], api.lookup_direction(data["PV"]["direction"] )))
    print( "- grid:    {} {}, direction: {} ({})".format( data["grid"]["value"], data["grid"]["unit"], 
          data["grid"]["direction"], api.lookup_direction(data["grid"]["direction"])))
    print( "- battery: {} {} , direction: {} ({}), SOC: {}%".format( data["battery"]["value"], data["battery"]["unit"], 
          data["battery"]["direction"], api.lookup_direction(data["battery"]["direction"]), 
          data["battery"]["SOC"]))
    print( "- load:    {} {}, direction: {} ({})".format( data["load"]["value"], data["load"]["unit"], 
          data["load"]["direction"], api.lookup_direction(data["load"]["direction"])))

#-----------------------------
def show_device_data( api ):
  stationId = let_user_select_station( api )
  deviceId = let_user_select_device( api, stationId )
  data = api.query_device_data( deviceId )
  if data: 
    print( "--------------------------------------------------------" )
    print( json.dumps(data, indent=2) )

def post_mqtt_device_data( api, client ):
  data = api.query_device_data( cfg["PV_DEVICE_ID"] )
  #flogger.debug( json.dumps(data, indent=2) )
  #clogger.debug( json.dumps(data, indent=2) )

def configure_logging():
  global flogger
  flogger = logging.getLogger('file_logger')
  flogger.setLevel(getattr(logging,cfg['LOGLEVEL']))

  global clogger
  clogger = logging.getLogger('console_logger')
  clogger.setLevel(getattr(logging,cfg['LOGLEVEL']))

  ch = logging.StreamHandler()
  ch.setLevel(getattr(logging,cfg['LOGLEVEL']))

  fh = logging.FileHandler(cfg['LOGFILE'])
  fh.setLevel(getattr(logging,cfg['LOGLEVEL']))

  formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s:%(message)s',datefmt='%Y%m%d %H:%M:%S')
  
  ch.setFormatter(formatter)
  clogger.addHandler(ch)
   
  fh.setFormatter(formatter)
  flogger.addHandler(fh)

#-------------------------------
def main():
  configure_logging()
  api = MTECapi.MTECapi()
  client = connect_mqtt()

  post_mqtt_device_data( api, client )
  print( "Bye!")

#-------------------------------
if __name__ == '__main__':
  main()
