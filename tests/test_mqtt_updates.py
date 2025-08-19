import asyncio

from custom_components.ha_mqtt_sensors import MqttHub
from custom_components.ha_mqtt_sensors.const import (
    CONF_SENSOR_ID,
    CONF_NAME,
    CONF_PREFIX,
    DEFAULT_PREFIX,
    CONF_SENSOR_SOURCE,
    SENSOR_SOURCE_EXTERNAL,
    SENSOR_SOURCE_INTERNAL,
)
from custom_components.ha_mqtt_sensors.binary_sensor import ContactEntity
from custom_components.ha_mqtt_sensors.sensor import IntTopicSensor, LastSeenSensor, SignalStrengthSensor
from custom_components.ha_mqtt_sensors.util import parse_datetime_utc
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.mqtt import subscriptions
import homeassistant.helpers.restore_state as restore_state


def test_contact_entity_state_updates(hass):
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

    assert entity.is_on is False

    topic = f"{DEFAULT_PREFIX}/{sensor_id}/state"
    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(topic, "open"))
    assert entity.is_on is True


def test_contact_entity_event_updates(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Window", BinarySensorDeviceClass.WINDOW)
    entity.hass = hass
    asyncio.run(entity.async_added_to_hass())

    assert entity.is_on is False

    topic = f"{DEFAULT_PREFIX}/{sensor_id}/event"
    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    for code in (160, 168, 192, 200, 232):
        callback(Msg(topic, str(code)))
        assert entity.is_on is True
    for code in (128, 40, 64, 104):
        callback(Msg(topic, str(code)))
        assert entity.is_on is False


def test_contact_ignores_topics_by_default(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Window", BinarySensorDeviceClass.WINDOW)
    entity.hass = hass
    asyncio.run(entity.async_added_to_hass())

    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/contact_open", "1"))
    assert entity.is_on is False
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/event", "128"))
    assert entity.is_on is False
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/reed_open", "1"))
    assert entity.is_on is False


def test_contact_topic_enabled_option(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={CONF_SENSOR_SOURCE: SENSOR_SOURCE_EXTERNAL},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Window", BinarySensorDeviceClass.WINDOW)
    entity.hass = hass
    asyncio.run(entity.async_added_to_hass())

    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/contact_open", "1"))
    assert entity.is_on is True
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/contact_open", "0"))
    assert entity.is_on is False


def test_reed_topic_enabled_option(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={CONF_SENSOR_SOURCE: SENSOR_SOURCE_INTERNAL},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Window", BinarySensorDeviceClass.WINDOW)
    entity.hass = hass
    asyncio.run(entity.async_added_to_hass())

    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/reed_open", "1"))
    assert entity.is_on is True
    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/reed_open", "0"))
    assert entity.is_on is False

def test_contact_event_updates_after_restore(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Window", BinarySensorDeviceClass.WINDOW)
    entity.hass = hass
    entity.entity_id = "binary_sensor.test_window"
    restore_state.last_states[entity.entity_id] = restore_state.State("off")
    asyncio.run(entity.async_added_to_hass())

    assert entity.is_on is False

    topic = f"{DEFAULT_PREFIX}/{sensor_id}/event"
    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(topic, "160"))
    assert entity.is_on is True


def test_unique_id_includes_prefix(hass):
    sensor_id = "abc123"
    prefix = "testp"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: prefix},
        options={},
        entry_id="entry2",
    )
    hub = MqttHub(hass, entry)
    entity = ContactEntity(hub, entry, DeviceInfo(), "Test Door", BinarySensorDeviceClass.DOOR)
    assert entity._attr_unique_id == f"{prefix}_{sensor_id}_contact"


def test_hub_uses_prefix_from_options(hass):
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: "abc123", CONF_PREFIX: "data_prefix"},
        options={CONF_PREFIX: "opt_prefix"},
        entry_id="entry2",
    )
    hub = MqttHub(hass, entry)
    assert hub.base_topic == "opt_prefix/abc123"


def test_contact_entity_restores_state(hass):
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
    entity.entity_id = "binary_sensor.test_door"
    restore_state.last_states[entity.entity_id] = restore_state.State("on")
    asyncio.run(entity.async_added_to_hass())

    assert entity.is_on is True


def test_int_sensor_restores_state(hass):
    sensor_id = "abc123"
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


def test_last_seen_sensor_restores_state_and_hub(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = LastSeenSensor(hub, entry, DeviceInfo(), "Test Last Seen")
    entity.hass = hass
    entity.entity_id = "sensor.test_last_seen"
    ts = "2024-01-02 03:04:05"
    restore_state.last_states[entity.entity_id] = restore_state.State(ts)
    asyncio.run(entity.async_added_to_hass())

    parsed = parse_datetime_utc(hass, ts)
    assert entity.native_value == parsed
    assert hub.last_seen_utc == parsed


def test_rssi_sensor_updates(hass):
    sensor_id = "abc123"
    entry = ConfigEntry(
        data={CONF_SENSOR_ID: sensor_id, CONF_NAME: "Test", CONF_PREFIX: DEFAULT_PREFIX},
        options={},
        entry_id="entry1",
    )
    hub = MqttHub(hass, entry)
    asyncio.run(hub.async_setup())

    entity = SignalStrengthSensor(hub, entry, DeviceInfo(), "Test RSSI", "rssi")
    entity.hass = hass
    asyncio.run(entity.async_added_to_hass())

    assert entity.native_value is None

    callback = subscriptions[f"{DEFAULT_PREFIX}/{sensor_id}/+"]

    class Msg:
        def __init__(self, topic, payload):
            self.topic = topic
            self.payload = payload

    callback(Msg(f"{DEFAULT_PREFIX}/{sensor_id}/rssi", "-42"))
    assert entity.native_value == -42


