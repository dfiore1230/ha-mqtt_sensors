from datetime import timedelta
import asyncio
from unittest.mock import patch

from custom_components.ha_mqtt_sensors import MqttHub
from custom_components.ha_mqtt_sensors.binary_sensor import AvailabilityEntity
from custom_components.ha_mqtt_sensors.const import (
    CONF_AVAIL_MINUTES,
    DEFAULT_AVAIL_MINUTES,
    CONF_AVAIL_TICK,
    CONF_SENSOR_ID,
    CONF_NAME,
    CONF_PREFIX,
    DEFAULT_PREFIX,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util


def _make_entity(hass, hub, minutes=DEFAULT_AVAIL_MINUTES):
    entry = ConfigEntry(data={}, options={CONF_AVAIL_MINUTES: minutes})
    entity = AvailabilityEntity(hub, entry, DeviceInfo(), "Connectivity")
    entity.hass = hass
    return entity


def test_availability_based_on_last_seen(hass, stub_hub):
    entity = _make_entity(hass, stub_hub)
    assert entity.is_on is None

    stub_hub._last_seen_utc = dt_util.utcnow()
    assert entity.is_on is True

    stub_hub._last_seen_utc = dt_util.utcnow() - timedelta(
        minutes=DEFAULT_AVAIL_MINUTES * 2
    )
    assert entity.is_on is False


def test_configurable_availability_tick_interval(hass):
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: "abc123", CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={CONF_AVAIL_TICK: 10},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    with patch("custom_components.ha_mqtt_sensors.async_track_time_interval") as mock_track:
        asyncio.run(hub.async_setup())
        assert mock_track.call_args[0][2] == timedelta(seconds=10)
