from __future__ import annotations
from datetime import timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, CONF_NAME,
    TOPIC_CONTACT, TOPIC_REED, TOPIC_STATE, TOPIC_TAMPER, TOPIC_BATTOK, TOPIC_ALARM,
    SUFFIX_AVAILABILITY, CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE, CONF_AVAIL_MINUTES, DEFAULT_AVAIL_MINUTES
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

    dtype = entry.options.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE).lower()
    if dtype == "door":
        main_name = f"{base_name} Door"
        main_class = BinarySensorDeviceClass.DOOR
    elif dtype == "leak":
        main_name = f"{base_name} Leak"
        main_class = BinarySensorDeviceClass.MOISTURE
    else:
        main_name = f"{base_name} Window"
        main_class = BinarySensorDeviceClass.WINDOW

    entities = [
        ContactEntity(hub, entry, dev_info, main_name, main_class),
        TamperEntity(hub, entry, dev_info, f"{base_name} Tamper"),
        BatteryLowEntity(hub, entry, dev_info, f"{base_name} Battery"),
        AlarmEntity(hub, entry, dev_info, f"{base_name} Alarm"),
        AvailabilityEntity(hub, entry, dev_info, f"{base_name} Connectivity"),
    ]
    async_add_entities(entities)

class _BaseBin(RestoreEntity, BinarySensorEntity):
    _attr_should_poll = False

    def __init__(self, hub, entry, dev_info: DeviceInfo, name: str, unique_suffix: str):
        self._hub = hub
        self._entry = entry
        self._attr_name = name
        self._attr_unique_id = f"{hub.combined_id}_{unique_suffix}"
        self._attr_device_info = dev_info
        self._removers = []

    async def async_will_remove_from_hass(self) -> None:
        for r in self._removers:
            r()
        self._removers.clear()

class ContactEntity(_BaseBin):
    def __init__(self, hub, entry, dev_info, name, device_class):
        super().__init__(hub, entry, dev_info, name, "contact")
        self._attr_device_class = device_class

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in ("on", "off"):
            self._hub.states[TOPIC_CONTACT] = "1" if last.state == "on" else "0"
        @callback
        def _poke(_payload: str):
            self.async_write_ha_state()
        for suffix in (TOPIC_CONTACT, TOPIC_REED, TOPIC_STATE):
            self._removers.append(async_dispatcher_connect(self.hass, self._hub.signal_for(suffix), _poke))
        self.async_write_ha_state()

    @property
    def is_on(self):
        contact = self._hub.states.get(TOPIC_CONTACT)
        if contact is not None:
            return str(contact) == "1"
        reed = self._hub.states.get(TOPIC_REED)
        if reed is not None:
            return str(reed) == "1"
        state_text = (self._hub.states.get(TOPIC_STATE) or "").lower()
        if state_text in ("open", "opened", "wet", "leak"):
            return True
        if state_text in ("close", "closed", "dry"):
            return False
        return None

class TamperEntity(_BaseBin):
    _attr_device_class = BinarySensorDeviceClass.TAMPER

    def __init__(self, hub, entry, dev_info, name):
        super().__init__(hub, entry, dev_info, name, "tamper")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in ("on", "off"):
            self._hub.states[TOPIC_TAMPER] = "1" if last.state == "on" else "0"
        @callback
        def _on(_payload: str):
            self.async_write_ha_state()
        self._removers.append(async_dispatcher_connect(self.hass, self._hub.signal_for(TOPIC_TAMPER), _on))
        self.async_write_ha_state()

    @property
    def is_on(self):
        v = self._hub.states.get(TOPIC_TAMPER)
        return None if v is None else str(v) == "1"

class BatteryLowEntity(_BaseBin):
    _attr_device_class = BinarySensorDeviceClass.BATTERY

    def __init__(self, hub, entry, dev_info, name):
        super().__init__(hub, entry, dev_info, name, "battery")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in ("on", "off"):
            self._hub.states[TOPIC_BATTOK] = "0" if last.state == "on" else "1"
        @callback
        def _on(_payload: str):
            self.async_write_ha_state()
        self._removers.append(async_dispatcher_connect(self.hass, self._hub.signal_for(TOPIC_BATTOK), _on))
        self.async_write_ha_state()

    @property
    def is_on(self):
        v = self._hub.states.get(TOPIC_BATTOK)
        return None if v is None else str(v) == "0"  # battery_ok == 0 => low

class AlarmEntity(_BaseBin):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, hub, entry, dev_info, name):
        super().__init__(hub, entry, dev_info, name, "alarm")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in ("on", "off"):
            self._hub.states[TOPIC_ALARM] = "1" if last.state == "on" else "0"
        @callback
        def _on(_payload: str):
            self.async_write_ha_state()
        self._removers.append(async_dispatcher_connect(self.hass, self._hub.signal_for(TOPIC_ALARM), _on))
        self.async_write_ha_state()

    @property
    def is_on(self):
        v = self._hub.states.get(TOPIC_ALARM)
        return None if v is None else str(v) == "1"

class AvailabilityEntity(_BaseBin):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub, entry, dev_info, name):
        super().__init__(hub, entry, dev_info, name, "availability")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in ("on", "off"):
            if last.state == "on":
                self._hub._last_seen_utc = dt_util.utcnow()
            else:
                minutes = self._entry.options.get(CONF_AVAIL_MINUTES, DEFAULT_AVAIL_MINUTES)
                self._hub._last_seen_utc = dt_util.utcnow() - timedelta(minutes=minutes * 2)
        @callback
        def _tick(_payload: str):
            self.async_write_ha_state()
        self._removers.append(async_dispatcher_connect(self.hass, self._hub.signal_for(SUFFIX_AVAILABILITY), _tick))
        self.async_write_ha_state()

    @property
    def is_on(self):
        minutes = self._entry.options.get(CONF_AVAIL_MINUTES, DEFAULT_AVAIL_MINUTES)
        last = self._hub.last_seen_utc
        if not last:
            return None
        return (dt_util.utcnow() - last) < timedelta(minutes=minutes)
