from __future__ import annotations
from datetime import datetime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util
from .const import (
    DOMAIN, CONF_NAME,
    TOPIC_TIME, TOPIC_EVENT, TOPIC_CHANNEL, TOPIC_STATE, TOPIC_MIC, TOPIC_ID
)

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    hub = hass.data[DOMAIN][entry.entry_id]
    base_name = entry.data[CONF_NAME]

    dev_info = DeviceInfo(
        identifiers={(DOMAIN, hub.combined_id)},
        name=base_name,
        manufacturer="345MHz Receiver",
        model="Honeywell/345 Contact",
    )

    entities = [
        LastSeenSensor(hub, entry, dev_info, f"{base_name} Last Seen"),
        IntTopicSensor(hub, entry, dev_info, f"{base_name} Event", "event"),
        IntTopicSensor(hub, entry, dev_info, f"{base_name} Channel", "channel"),
        TextTopicSensor(hub, entry, dev_info, f"{base_name} State Text", "state"),
        TextTopicSensor(hub, entry, dev_info, f"{base_name} MIC", "mic"),
        TextTopicSensor(hub, entry, dev_info, f"{base_name} ID", "id"),
    ]
    async_add_entities(entities)

class _BaseSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, hub, entry, dev_info: DeviceInfo, name: str, unique_suffix: str):
        self._hub = hub
        self._entry = entry
        self._attr_name = name
        self._attr_unique_id = f"{hub.combined_id}_{unique_suffix}"
        self._attr_device_info = dev_info
        self._remove = None

    async def async_will_remove_from_hass(self) -> None:
        if self._remove:
            self._remove()
            self._remove = None

class LastSeenSensor(_BaseSensor):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, hub, entry, dev_info, name):
        super().__init__(hub, entry, dev_info, name, "last_seen")

    async def async_added_to_hass(self) -> None:
        @callback
        def _on(_payload: str):
            self.async_write_ha_state()
        self._remove = async_dispatcher_connect(self.hass, self._hub.signal_for(TOPIC_TIME), _on)
        self.async_write_ha_state()

    @property
    def native_value(self):
        val = self._hub.states.get(TOPIC_TIME)
        if not val:
            return None
        try:
            dt_local = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            tz = dt_util.get_time_zone(self.hass.config.time_zone or "UTC")
            dt_local = tz.localize(dt_local)
            return dt_util.as_utc(dt_local)
        except Exception:
            try:
                return dt_util.as_utc(dt_util.parse_datetime(val))
            except Exception:
                return None

class IntTopicSensor(_BaseSensor):
    def __init__(self, hub, entry, dev_info, name, topic_suffix: str):
        super().__init__(hub, entry, dev_info, name, topic_suffix)
        self._topic_suffix = topic_suffix

    async def async_added_to_hass(self) -> None:
        @callback
        def _on(_payload: str):
            self.async_write_ha_state()
        self._remove = async_dispatcher_connect(self.hass, self._hub.signal_for(self._topic_suffix), _on)
        self.async_write_ha_state()

    @property
    def native_value(self):
        v = self._hub.states.get(self._topic_suffix)
        if v is None:
            return None
        try:
            return int(v)
        except ValueError:
            return None

class TextTopicSensor(_BaseSensor):
    def __init__(self, hub, entry, dev_info, name, topic_suffix: str):
        super().__init__(hub, entry, dev_info, name, topic_suffix)
        self._topic_suffix = topic_suffix

    async def async_added_to_hass(self) -> None:
        @callback
        def _on(_payload: str):
            self.async_write_ha_state()
        self._remove = async_dispatcher_connect(self.hass, self._hub.signal_for(self._topic_suffix), _on)
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._hub.states.get(self._topic_suffix)
