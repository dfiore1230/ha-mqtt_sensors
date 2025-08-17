import sys
import types
import pathlib
from dataclasses import dataclass
from datetime import datetime, timezone

# Ensure repository root on sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

# Base packages
ha_pkg = types.ModuleType("homeassistant")
sys.modules["homeassistant"] = ha_pkg
helpers_pkg = types.ModuleType("homeassistant.helpers")
sys.modules["homeassistant.helpers"] = helpers_pkg
components_pkg = types.ModuleType("homeassistant.components")
sys.modules["homeassistant.components"] = components_pkg

# core module
core = types.ModuleType("homeassistant.core")

class _Loop:
    def call_soon_threadsafe(self, func, *args):
        func(*args)

class HomeAssistant:
    def __init__(self):
        self.data = {}
        self.loop = _Loop()
        self.config = types.SimpleNamespace(time_zone="UTC")

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

class ConfigFlow:
    def __init_subclass__(cls, **kwargs):
        pass

class OptionsFlow:
    def async_show_form(self, step_id, data_schema):
        return {"type": "form", "step_id": step_id, "data_schema": data_schema}

    def async_create_entry(self, title, data):
        return {"type": "create_entry", "title": title, "data": data}

config_entries.ConfigEntry = ConfigEntry
config_entries.ConfigFlow = ConfigFlow
config_entries.OptionsFlow = OptionsFlow
sys.modules["homeassistant.config_entries"] = config_entries

# voluptuous module (schema validation) stub
vol = types.ModuleType("voluptuous")

class Schema:
    def __init__(self, schema):
        self.schema = schema
    def __call__(self, data):
        return data

def Optional(key, default=None, description=None):
    return key

def Required(key, description=None):
    return key

def In(values):
    def _validator(value):
        return value
    return _validator

def All(*args, **kwargs):
    def _validator(value):
        return value
    return _validator

def Range(min=None, max=None):
    def _validator(value):
        return value
    return _validator

vol.Schema = Schema
vol.Optional = Optional
vol.Required = Required
vol.In = In
vol.All = All
vol.Range = Range
sys.modules["voluptuous"] = vol

# data_entry_flow module
data_entry_flow = types.ModuleType("homeassistant.data_entry_flow")
data_entry_flow.FlowResult = dict
sys.modules["homeassistant.data_entry_flow"] = data_entry_flow

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

# components.mqtt module
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
components_pkg.mqtt = mqtt
sys.modules["homeassistant.components.mqtt"] = mqtt

# util.dt module
util_pkg = types.ModuleType("homeassistant.util")
sys.modules["homeassistant.util"] = util_pkg
dt = types.ModuleType("homeassistant.util.dt")

def utcnow():
    return datetime.utcnow()

def get_time_zone(name):
    class TZ:
        def __init__(self, name):
            self.name = name
        def localize(self, dt_obj):
            if self.name == "America/New_York" and dt_obj == datetime(2023, 3, 12, 2, 30, 0):
                raise ValueError("Non-existent time")
            return dt_obj.replace(tzinfo=timezone.utc)
    return TZ(name)

def parse_datetime(val: str):
    if "T" in val:
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            return None
    return None

def as_utc(dt_obj: datetime):
    if dt_obj.tzinfo is None:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(timezone.utc)

dt.utcnow = utcnow

dt.get_time_zone = get_time_zone

dt.parse_datetime = parse_datetime

dt.as_utc = as_utc
sys.modules["homeassistant.util.dt"] = dt

# pytest fixtures
import pytest

@pytest.fixture
def hass():
    return HomeAssistant()

class StubHub:
    def __init__(self):
        self.sensor_id = "abc"
        self.states = {}
        self.combined_id = self.sensor_id
        self._last_seen_utc = None
    def signal_for(self, suffix):
        return suffix
    @property
    def last_seen_utc(self):
        return self._last_seen_utc

@pytest.fixture
def stub_hub():
    return StubHub()
