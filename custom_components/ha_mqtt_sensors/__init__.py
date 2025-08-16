from __future__ import annotations
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components import mqtt
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, PLATFORMS, CONF_SENSOR_ID, CONF_PREFIX, DEFAULT_PREFIX, SIG_UPDATE,
    SUFFIX_AVAILABILITY
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hub = MqttHub(hass, entry)
    await hub.async_setup()
    hass.data[DOMAIN][entry.entry_id] = hub
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and entry.entry_id in hass.data.get(DOMAIN, {}):
        await hass.data[DOMAIN][entry.entry_id].async_unload()
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded

class MqttHub:
    """Subscribe to <prefix>/<id>/+ and cache latest values; track availability."""
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.sensor_id: str = entry.data[CONF_SENSOR_ID]
        self.prefix: str = entry.data.get(CONF_PREFIX, DEFAULT_PREFIX)
        self._base = f"{self.prefix}/{self.sensor_id}"
        self.states: dict[str, str | None] = {}
        self._unsub_mqtt = None
        self._unsub_timer = None
        self._last_seen_utc = None  # datetime

    async def async_setup(self) -> None:
        await mqtt.async_wait_for_mqtt_client(self.hass)
        topic = f"{self._base}/+"

        def _cb(msg):
            suffix = msg.topic.split("/")[-1]
            payload = msg.payload if isinstance(msg.payload, str) else msg.payload.decode("utf-8", "ignore")
            payload = payload.strip()
            self.states[suffix] = payload
            self._last_seen_utc = dt_util.utcnow()
            async_dispatcher_send(self.hass, self._signal_name(suffix), payload)
            async_dispatcher_send(self.hass, self._signal_name(SUFFIX_AVAILABILITY), "tick")

        self._unsub_mqtt = mqtt.async_subscribe(self.hass, topic, _cb, qos=0, encoding=None)
        self._unsub_timer = async_track_time_interval(
            self.hass, self._availability_tick, timedelta(seconds=30)
        )

    async def async_unload(self) -> None:
        if self._unsub_mqtt:
            self._unsub_mqtt()
            self._unsub_mqtt = None
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None

    def _availability_tick(self, _now) -> None:
        async_dispatcher_send(self.hass, self._signal_name(SUFFIX_AVAILABILITY), "tick")

    def _signal_name(self, suffix: str) -> str:
        return f"{SIG_UPDATE}_{self.entry.entry_id}_{suffix}"

    def signal_for(self, suffix: str) -> str:
        return self._signal_name(suffix)

    @property
    def base_topic(self) -> str:
        return self._base

    @property
    def last_seen_utc(self) -> datetime | None:
        return self._last_seen_utc
