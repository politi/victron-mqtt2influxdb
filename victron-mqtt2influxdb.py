#!/usr/bin/env python3

# https://gist.github.com/zufardhiyaulhaq/fe322f61b3012114379235341b935539

"""A MQTT to InfluxDB Bridge

This script receives MQTT data and saves those to InfluxDB.

"""

import re
from typing import NamedTuple
import json
import yaml
import os

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from time import time 

# INFLUXDB_ADDRESS = '127.0.0.1'
# INFLUXDB_USER = ''
# INFLUXDB_PASSWORD = ''
# INFLUXDB_DATABASE = 'victron'

# MQTT_ADDRESS = '127.0.0.1'
# MQTT_USER = ''
# MQTT_PASSWORD = ''
# MQTT_TOPIC = 'victron/+/+'  # victron/[DEVICETYPE]/[DEVICENAME]  --> victron/smartsolar/HQ222093NKZ
MQTT_REGEX = 'victron/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'VictronMQTTInfluxDBBridge'

#influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
influxdb_client = None
config = None

# ignores = ['online', 'Identify']
# replaces = {'SmartSolar_': ''}
# lastValuesTS = {'test': 1}

class SensorData(NamedTuple):
	deviceType: str
	deviceName: str
	# measurement: str
	value: object


def on_connect(client, userdata, flags, rc):
	""" The callback for when the client receives a CONNACK response from the server."""
	print('Connected to MQTT broker with result code ' + str(rc))
	client.subscribe(config['mqtt']['topic'])


def on_message(client, userdata, msg):
	"""The callback for when a PUBLISH message is received from the server."""
	# print(msg.topic + ' ' + str(msg.payload))
	# print(msg.topic + ' ' + str(msg.payload.decode('utf-8')))
	sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
	if sensor_data is None:
		return
	# print('sensor_data: ' + str(sensor_data))

	print("Saving to Influx..")
	_send_sensor_data_to_influxdb(sensor_data)
	#if sensor_data is not None:
	#	_send_sensor_data_to_influxdb(sensor_data)


def _parse_mqtt_message(topic, payload):
	match = re.match(MQTT_REGEX, topic)
	if match:
		deviceType = match.group(1)
		deviceName = match.group(2)
		#measurement = match.group(2)
		# if measurement == 'status':
		# 	return None
		return SensorData(deviceType, deviceName, json.loads(payload))
	else:
		return None


def _send_sensor_data_to_influxdb(sensor_data):
	global influxdb_client
	json_body = [
		{
			'measurement': sensor_data.deviceName,
			'tags': {
				'type': sensor_data.deviceType,
				'device': sensor_data.deviceName
			},
			'fields': sensor_data.value
		}
	]
	print (json_body)
	try:
		influxdb_client.write_points(json_body)
	except:
		print("Error saving to Influx") 


def _init_influxdb_database():
	global config
	global influxdb_client
	databases = influxdb_client.get_list_database()
	# if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
	# 	influxdb_client.create_database(INFLUXDB_DATABASE)
	# influxdb_client.switch_database(INFLUXDB_DATABASE)
	if len(list(filter(lambda x: x['name'] == config['influxdb']['database'], databases))) == 0:
		influxdb_client.create_database(config['influxdb']['database'])
	influxdb_client.switch_database(config['influxdb']['database'])


def main():
    global influxdb_client
    global config
    if os.path.exists('config.yml'):
        with open('config.yml', 'r') as ymlfile:
            config = yaml.full_load(ymlfile)
    else:
        print("config.yml missing. Please create one")
        sys.exit(1)


    influxdb_client = InfluxDBClient(config['influxdb']['address'], config['influxdb']['port'], config['influxdb']['username'], config['influxdb']['password'], None)

    _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(config['mqtt']['address'], config['mqtt']['port'])
    mqtt_client.loop_forever()


if __name__ == '__main__':
	print('MQTT to InfluxDB bridge')
	main()

