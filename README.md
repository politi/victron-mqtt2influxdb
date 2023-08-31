# Victron MQTT 2 InfluxDB bridge

This software implements a simple MQTT to InfluxDB Bridge specific for the [Victron BLE Monitor](https://github.com/politi/victron-ble-monitor) project.  
It receives messages from Victron devices sent over MQTT by [victron-ble2mqtt](#victron-ble2mqtt) and store them to InfluxDB.

This is based on the script [MQTT-to-influxdb.py](https://gist.github.com/zufardhiyaulhaq/fe322f61b3012114379235341b935539), developed by [zufardhiyaulhaq](https://gist.github.com/zufardhiyaulhaq), so most of the credits goes to him.  
The script has been slightly modified to my specific needs (mainly I changed the message parsing and added a configuration file).

More detail about the global Victron BLE Monitor, its architecture and the hardware and software components, can be found in its GitHub repository: [Victron BLE Monitor](https://github.com/politi/victron-ble-monitor)


## Installation

- Install Python and PIP
```bash
sudo apt update
sudo apt install python3.8
sudo apt install python3-pip
```
- Clone this repo
- install dependencies
```bash
pip install -r requirements.txt
```
- copy files to `/opt` or other choosen directory
```bash
cd /opt
mkdir victron-mqtt2influxdb
cd victron-mqtt2influxdb
unzip victron-mqtt2influxdb.zip
chmod +x victron-mqtt2influxdb.py
```

<br>

## Configuration

To configure the software, you need to edit the config.yml file found in the same directory of the script., to match the connection parameters of MQTT broker and InfluxDB instance


```yaml
influxdb:
    address: 127.0.0.1
    port: 8086
    database: victron
    username:
    password:


## MQTT server
##   host: IP or Hostname
##   port: 1883
##   topic: victron
##   username: MQTT_USER  --> leave blank if empty. Do Not comment
##   password: PASSWORD   --> leave blank if empty. Do Not comment
mqtt:
    address: 127.0.0.1
    port: 1883
    topic: victron/+/+    # --> # victron/[DEVICETYPE]/[DEVICENAME]  --> victron/smartsolar/HQ123456ABC
    username:
    password:
```

## Running

### Manual execution

To manually execute the software (to check if everything is working correctly):
```bash
cd /opt/victron-mqtt2influxdb
./victron-mqtt2influxdb.py
```

To interrupt the executionm, just press `Ctrl+C`

<br>

## Automatic execution (configure as service)

For production you want the program to be automatically executed at startup as a service

```bash
sudo ln -s /opt/victron-mqtt2influxdb/victron-mqtt2influxdb.service /etc/systemd/system/victron-mqtt2influxdb.service

systemctl enable victron-mqtt2influxdb.service

sudo systemctl enable victron-mqtt2influxdb.service

sudo systemctl start victron-mqtt2influxdb.service

systemctl status victron-mqtt2influxdb.service
```
