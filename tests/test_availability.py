from datetime import timedelta

from custom_components.ha_mqtt_sensors.binary_sensor import AvailabilityEntity
from custom_components.ha_mqtt_sensors.const import (
    CONF_AVAIL_MINUTES,
    DEFAULT_AVAIL_MINUTES,
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

    stub_hub._last_seen_utc = dt_util.utcnow() - timedelta(minutes=10)
    assert entity.is_on is False
