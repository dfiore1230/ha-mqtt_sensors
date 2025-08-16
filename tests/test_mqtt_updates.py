import sys
import types
import pathlib
import asyncio
from dataclasses import dataclass
from datetime import datetime

# ---- Begin stubs for homeassistant ----
# Ensure the repository root is on sys.path for imports
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
# core module
ha_pkg = types.ModuleType("homeassistant")
sys.modules["homeassistant"] = ha_pkg
helpers_pkg = types.ModuleType("homeassistant.helpers")
sys.modules["homeassistant.helpers"] = helpers_pkg
core = types.ModuleType("homeassistant.core")

class _Loop:
    def call_soon_threadsafe(self, func, *args):
        func(*args)


class HomeAssistant:
    def __init__(self):
        self.data = {}
        self.loop = _Loop()


def callback(func):
    return func

core.HomeAssistant = HomeAssistant
core.callback = callback
sys.modules["homeassistant.core"] = core

# config_entries module
config_entries = types.ModuleType("homeassistant.config_entries")

@dataclass
class ConfigEntry:
    data: dict
    options: dict
    entry_id: str = "1"

config_entries.ConfigEntry = ConfigEntry
sys.modules["homeassistant.config_entries"] = config_entries

# components.mqtt module
components = types.ModuleType("homeassistant.components")
sys.modules["homeassistant.components"] = components
mqtt = types.ModuleType("homeassistant.components.mqtt")
mqtt.subscriptions = {}

async def async_wait_for_mqtt_client(hass):
    return True

async def async_subscribe(hass, topic, callback, qos=0, encoding=None):
    mqtt.subscriptions[topic] = callback
    def unsub():
        mqtt.subscriptions.pop(topic, None)
    return unsub

mqtt.async_wait_for_mqtt_client = async_wait_for_mqtt_client
mqtt.async_subscribe = async_subscribe
sys.modules["homeassistant.components.mqtt"] = mqtt

# helpers.dispatcher module
dispatcher = types.ModuleType("homeassistant.helpers.dispatcher")
dispatcher._signals = {}


def async_dispatcher_send(hass, signal, payload):
    for cb in dispatcher._signals.get(signal, []):
        cb(payload)


def async_dispatcher_connect(hass, signal, callback):
    dispatcher._signals.setdefault(signal, []).append(callback)
    def unsub():
        dispatcher._signals[signal].remove(callback)
    return unsub


dispatcher.async_dispatcher_send = async_dispatcher_send
dispatcher.async_dispatcher_connect = async_dispatcher_connect
sys.modules["homeassistant.helpers.dispatcher"] = dispatcher

# helpers.event module
event = types.ModuleType("homeassistant.helpers.event")

def async_track_time_interval(hass, action, interval):
    def cancel():
        pass
    return cancel

event.async_track_time_interval = async_track_time_interval
sys.modules["homeassistant.helpers.event"] = event

# helpers.entity module
entity_helper = types.ModuleType("homeassistant.helpers.entity")

class DeviceInfo:
    def __init__(self, **kwargs):
        pass

class EntityCategory:
    DIAGNOSTIC = "diagnostic"

entity_helper.DeviceInfo = DeviceInfo
entity_helper.EntityCategory = EntityCategory
sys.modules["homeassistant.helpers.entity"] = entity_helper

# helpers.restore_state module
restore_state = types.ModuleType("homeassistant.helpers.restore_state")

class State:
    def __init__(self, state):
        self.state = state

restore_state.State = State
restore_state.last_states = {}

class RestoreEntity:
    async def async_added_to_hass(self):
        pass

    async def async_get_last_state(self):
        return restore_state.last_states.get(getattr(self, "entity_id", None))

restore_state.RestoreEntity = RestoreEntity
sys.modules["homeassistant.helpers.restore_state"] = restore_state

# components.binary_sensor module
bin_sensor = types.ModuleType("homeassistant.components.binary_sensor")

class BinarySensorDeviceClass:
    DOOR = "door"
    MOISTURE = "moisture"
    WINDOW = "window"
    TAMPER = "tamper"
    BATTERY = "battery"
    PROBLEM = "problem"
    CONNECTIVITY = "connectivity"


class BinarySensorEntity:
    def __init__(self):
        self.hass = None

    async def async_added_to_hass(self):
        pass

    async def async_will_remove_from_hass(self):
        pass

    def async_write_ha_state(self):
        pass


bin_sensor.BinarySensorDeviceClass = BinarySensorDeviceClass
bin_sensor.BinarySensorEntity = BinarySensorEntity
sys.modules["homeassistant.components.binary_sensor"] = bin_sensor

# components.sensor module
sensor_mod = types.ModuleType("homeassistant.components.sensor")

class SensorDeviceClass:
    TIMESTAMP = "timestamp"


class SensorEntity:
    def __init__(self):
        self.hass = None

    async def async_added_to_hass(self):
        pass

    async def async_will_remove_from_hass(self):
        pass

    def async_write_ha_state(self):
        pass


sensor_mod.SensorDeviceClass = SensorDeviceClass
sensor_mod.SensorEntity = SensorEntity
sys.modules["homeassistant.components.sensor"] = sensor_mod

# util.dt module
util = types.ModuleType("homeassistant.util")
sys.modules["homeassistant.util"] = util
dt = types.ModuleType("homeassistant.util.dt")

def utcnow():
    return datetime.utcnow()

dt.utcnow = utcnow
def get_time_zone(_zone):
    class _TZ:
        def localize(self, dt_obj):
            return dt_obj
    return _TZ()

def parse_datetime(val):
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return None

dt.get_time_zone = get_time_zone
dt.parse_datetime = parse_datetime
sys.modules["homeassistant.util.dt"] = dt
# ---- End stubs for homeassistant ----

# Now import the component modules
from custom_components.ha_mqtt_sensors import MqttHub
from custom_components.ha_mqtt_sensors.const import (
    CONF_SENSOR_ID,
    CONF_NAME,
    CONF_PREFIX,
    DEFAULT_PREFIX,
)
from custom_components.ha_mqtt_sensors.binary_sensor import ContactEntity
from custom_components.ha_mqtt_sensors.sensor import IntTopicSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.mqtt import subscriptions
import homeassistant.helpers.restore_state as restore_state

import pytest


def test_contact_entity_state_updates():
    sensor_id = "abc123"
    hass = HomeAssistant()
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Door", BinarySensorDeviceClass.DOOR)
    entity.hass = hass
    asyncio.run(entity.async_added_to_hass())

    assert entity.is_on is None

    topic = f"{DEFAULT_PREFIX}/{sensor_id}/state"
    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(topic, "open"))

    assert entity.is_on is True


def test_contact_entity_restores_state():
    sensor_id = "abc123"
    hass = HomeAssistant()
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Door", BinarySensorDeviceClass.DOOR)
    entity.hass = hass
    entity.entity_id = "binary_sensor.test_door"
    restore_state.last_states[entity.entity_id] = restore_state.State("on")
    asyncio.run(entity.async_added_to_hass())

    assert entity.is_on is True


def test_int_sensor_restores_state():
    sensor_id = "abc123"
    hass = HomeAssistant()
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = IntTopicSensor(hub, entry, DeviceInfo(), "Test Event", "event")
    entity.hass = hass
    entity.entity_id = "sensor.test_event"
    restore_state.last_states[entity.entity_id] = restore_state.State("5")
    asyncio.run(entity.async_added_to_hass())

    assert entity.native_value == 5
