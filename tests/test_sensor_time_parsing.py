from datetime import datetime, timezone, timedelta

from custom_components.ha_mqtt_sensors.sensor import LastSeenSensor
from custom_components.ha_mqtt_sensors.const import TOPIC_TIME
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util


def _make_sensor(hass, hub):
    entry = ConfigEntry(data={}, options={})
    sensor = LastSeenSensor(hub, entry, DeviceInfo(), "Last Seen")
    sensor.hass = hass
    return sensor


def test_iso_format_parsed(hass, stub_hub):
    hub = stub_hub
    hub.states[TOPIC_TIME] = "2023-03-10T12:34:56+00:00"
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value == datetime(2023, 3, 10, 12, 34, 56, tzinfo=timezone.utc)


def test_manual_strptime_fallback(hass, stub_hub):
    hub = stub_hub
    hub.states[TOPIC_TIME] = "2023-03-10 12:34:56"
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value == datetime(2023, 3, 10, 12, 34, 56, tzinfo=timezone.utc)


def test_dst_nonexistent_time_returns_none(hass, stub_hub):
    hass.config.time_zone = "America/New_York"
    hub = stub_hub
    hub.states[TOPIC_TIME] = "2023-03-12 02:30:00"
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value is None


def test_future_timestamp_returns_now(hass, stub_hub):
    hub = stub_hub
    future = dt_util.utcnow() + timedelta(hours=1)
    hub.states[TOPIC_TIME] = future.isoformat()
    sensor = _make_sensor(hass, hub)
    value = sensor.native_value
    assert value <= dt_util.as_utc(dt_util.utcnow())


def test_zoneinfo_timezone_parsed(hass, stub_hub, monkeypatch):
    hub = stub_hub
    hub.states[TOPIC_TIME] = "2023-03-10 12:34:56"
    monkeypatch.setattr(dt_util, "get_time_zone", lambda name: timezone.utc)
    sensor = _make_sensor(hass, hub)
    assert sensor.native_value == datetime(2023, 3, 10, 12, 34, 56, tzinfo=timezone.utc)
