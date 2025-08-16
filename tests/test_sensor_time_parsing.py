import sys
import types
import pathlib
from dataclasses import dataclass
from datetime import datetime, timezone

# ---- Begin stubs for homeassistant ----
# Ensure repository root is on sys.path for imports
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

# core module
core = types.ModuleType("homeassistant.core")

class _Loop:
    def call_soon_threadsafe(self, func, *args):
        func(*args)

class HomeAssistant:
    def __init__(self):
        self.data = {}
        self.config = types.SimpleNamespace(time_zone="UTC")
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

# helpers.entity module
entity_helper = types.ModuleType("homeassistant.helpers.entity")

class DeviceInfo:
    def __init__(self, **kwargs):
        pass

entity_helper.DeviceInfo = DeviceInfo
sys.modules["homeassistant.helpers.entity"] = entity_helper

# components.sensor module
components_sensor = types.ModuleType("homeassistant.components.sensor")

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

components_sensor.SensorDeviceClass = SensorDeviceClass
components_sensor.SensorEntity = SensorEntity
sys.modules["homeassistant.components.sensor"] = components_sensor

# helpers.dispatcher module
helpers_dispatcher = types.ModuleType("homeassistant.helpers.dispatcher")

def async_dispatcher_connect(hass, signal, callback):
    def unsub():
        pass
    return unsub

helpers_dispatcher.async_dispatcher_connect = async_dispatcher_connect
sys.modules["homeassistant.helpers.dispatcher"] = helpers_dispatcher

# util.dt module
util_module = types.ModuleType("homeassistant.util")
sys.modules["homeassistant.util"] = util_module

dt_module = types.ModuleType("homeassistant.util.dt")

# Simple parse_datetime: only handles ISO strings with 'T'

def parse_datetime(val: str):
    if "T" in val:
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            return None
    return None


def get_time_zone(name: str):
    class TZ:
        def __init__(self, name):
            self.name = name

        def localize(self, dt):
            if self.name == "America/New_York" and dt == datetime(2023, 3, 12, 2, 30, 0):
                raise ValueError("Non-existent time")
            return dt.replace(tzinfo=timezone.utc)

    return TZ(name)


def as_utc(dt: datetime):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


dt_module.parse_datetime = parse_datetime
dt_module.get_time_zone = get_time_zone
dt_module.as_utc = as_utc
def utcnow():
    return datetime.utcnow()
dt_module.utcnow = utcnow
sys.modules["homeassistant.util.dt"] = dt_module
# ---- End stubs for homeassistant ----

# Now import component modules
from custom_components.ha_mqtt_sensors.sensor import LastSeenSensor
from custom_components.ha_mqtt_sensors.const import TOPIC_TIME


class StubHub:
    def __init__(self):
        self.sensor_id = "abc"
        self.states = {}

    def signal_for(self, suffix):
        return suffix


def _make_sensor(hass, hub):
    entry = ConfigEntry(data={}, options={})
    sensor = LastSeenSensor(hub, entry, DeviceInfo(), "Last Seen")
    sensor.hass = hass
    return sensor


def test_iso_format_parsed():
    hass = HomeAssistant()
    hub = StubHub()
    hub.states[TOPIC_TIME] = "2023-03-10T12:34:56+00:00"
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value == datetime(2023, 3, 10, 12, 34, 56, tzinfo=timezone.utc)


def test_manual_strptime_fallback():
    hass = HomeAssistant()
    hub = StubHub()
    hub.states[TOPIC_TIME] = "2023-03-10 12:34:56"
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value == datetime(2023, 3, 10, 12, 34, 56, tzinfo=timezone.utc)


def test_dst_nonexistent_time_returns_none():
    hass = HomeAssistant()
    hass.config.time_zone = "America/New_York"
    hub = StubHub()
    hub.states[TOPIC_TIME] = "2023-03-12 02:30:00"
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value is None
