# HA MQTT Sensors

Home Assistant custom integration that creates a device with multiple entities from a 345MHz contact’s MQTT topics. Enter a sensor ID (e.g., `702442`) and the integration subscribes to `<prefix>/<id>/+` (default prefix `sensors_345`).

## Features
- Device type selection per sensor: **door**, **window**, **leak**
- Binary sensors: Contact, Tamper, Battery Low, Alarm, Connectivity
- Sensors: Last Seen (timestamp), Event, Channel, Heartbeat, State (text), MIC, ID
- Availability/Connectivity turns **on** when a message was seen within N minutes (default 5)

## Install
- Copy this repo to `config/custom_components/ha_mqtt_sensors`
- Restart Home Assistant

## Add a sensor
- Settings → Devices & services → Add Integration → **HA MQTT Sensors**
- Sensor ID: `702442` (example)
- Topic prefix: `sensors_345` or your bridge topic root
- Device type: door | window | leak
- Availability window: minutes until considered offline

## MQTT topics expected
```
<prefix>/<id>/time          e.g. 2025-08-16 01:10:15
<prefix>/<id>/id            e.g. 702442
<prefix>/<id>/channel       e.g. 10
<prefix>/<id>/event         e.g. 128
<prefix>/<id>/state         e.g. open
<prefix>/<id>/contact_open  e.g. 1
<prefix>/<id>/reed_open     e.g. 0
<prefix>/<id>/alarm         e.g. 0
<prefix>/<id>/tamper        e.g. 0
<prefix>/<id>/battery_ok    e.g. 1
<prefix>/<id>/heartbeat     e.g. 0
<prefix>/<id>/mic           e.g. CRC
```

## Entity mapping
- **Contact**: `contact_open` → 1=open, else fallback `reed_open` → 1=open, else `state` text `open/closed/wet/dry`
- **Battery Low**: `battery_ok` == 0 → **on**
- **Tamper**: `tamper` == 1 → **on**
- **Alarm**: `alarm` == 1 → **on**
- **Connectivity**: last message within N minutes → **on** (configurable)
- **Heartbeat**: `heartbeat` integer (e.g., 0 or 1)

## Mosquitto quick check
```bash
mosquitto_sub -h <BROKER_IP> -t 'sensors_345/+/+' -v
mosquitto_sub -h <BROKER_IP> -t 'sensors_345/702442/#' -v
```

## Options
- Change topic prefix, device type, and availability window from the integration’s **Options**

## Notes
- Requires the **MQTT** integration configured in Home Assistant
- Add more topics (RSSI, supervision, etc.) by extending `const.py` and the platform files
