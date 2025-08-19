import asyncio
from custom_components.ha_mqtt_sensors import MqttHub
from custom_components.ha_mqtt_sensors.const import (
    CONF_SENSOR_ID,
    CONF_NAME,
    DEFAULT_PREFIX,
    CONF_PREFIX,
)
from custom_components.ha_mqtt_sensors.binary_sensor import ContactEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.mqtt import subscriptions


# Test that event codes override stale state values

def test_event_overrides_state(hass):
    sensor_id = "abc123"
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

    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    # Simulate initial open event with accompanying state text
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/state", "open"))
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/event", "160"))
    assert entity.is_on is True

    # Now send a closed event without changing state text
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/event", "128"))
    assert entity.is_on is False
