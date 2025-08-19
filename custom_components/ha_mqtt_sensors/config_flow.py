from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_SENSOR_ID,
    CONF_NAME,
    CONF_PREFIX,
    DEFAULT_PREFIX,
    CONF_DEVICE_TYPE,
    DEFAULT_DEVICE_TYPE,
    CONF_AVAIL_MINUTES,
    DEFAULT_AVAIL_MINUTES,
    CONF_AVAIL_TICK,
    DEFAULT_AVAIL_TICK,
    CONF_SENSOR_SOURCE,
    DEFAULT_SENSOR_SOURCE,
    SENSOR_SOURCE_EXTERNAL,
    SENSOR_SOURCE_INTERNAL,
    CONF_USE_EXTERNAL,
    CONF_USE_INTERNAL,
    DEFAULT_USE_EXTERNAL,
    DEFAULT_USE_INTERNAL,
)

DEVICE_CHOICES = ["door", "window", "leak"]

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 3

    async def async_step_user(self, user_input=None) -> FlowResult:
        schema = vol.Schema({
            vol.Required(CONF_SENSOR_ID, description={"suggested_value": "502442"}): str,
            vol.Optional(CONF_NAME): str,
            vol.Optional(CONF_PREFIX, default=DEFAULT_PREFIX): str,
            vol.Optional(CONF_DEVICE_TYPE, default=DEFAULT_DEVICE_TYPE): vol.In(DEVICE_CHOICES),
            vol.Optional(
                CONF_AVAIL_MINUTES, default=DEFAULT_AVAIL_MINUTES
            ): vol.All(int, vol.Range(min=1, max=1440)),
            vol.Optional(
                CONF_AVAIL_TICK, default=DEFAULT_AVAIL_TICK
            ): vol.All(int, vol.Range(min=5, max=3600)),
            vol.Required(CONF_SENSOR_SOURCE): vol.In(
                [SENSOR_SOURCE_EXTERNAL, SENSOR_SOURCE_INTERNAL]
            ),
        })

        if user_input is not None:
            sensor_id = user_input[CONF_SENSOR_ID].strip()
            prefix = user_input.get(CONF_PREFIX, DEFAULT_PREFIX)
            combined_id = f"{prefix}_{sensor_id}"
            await self.async_set_unique_id(combined_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or f"MQTT Sensor {sensor_id}",
                data={
                    CONF_SENSOR_ID: sensor_id,
                    CONF_NAME: user_input.get(CONF_NAME) or f"Sensor {sensor_id}",
                    CONF_PREFIX: prefix,
                },
                options={
                    CONF_PREFIX: user_input.get(CONF_PREFIX, DEFAULT_PREFIX),
                    CONF_DEVICE_TYPE: user_input.get(
                        CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE
                    ),
                    CONF_AVAIL_MINUTES: user_input.get(
                        CONF_AVAIL_MINUTES, DEFAULT_AVAIL_MINUTES
                    ),
                    CONF_AVAIL_TICK: user_input.get(
                        CONF_AVAIL_TICK, DEFAULT_AVAIL_TICK
                    ),
                    CONF_SENSOR_SOURCE: user_input[CONF_SENSOR_SOURCE],
                },
            )

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        current = {**self.entry.data, **self.entry.options}
        schema = vol.Schema({
            vol.Optional(
                CONF_PREFIX, default=current.get(CONF_PREFIX, DEFAULT_PREFIX)
            ): str,
            vol.Optional(
                CONF_DEVICE_TYPE,
                default=current.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE),
            ): vol.In(DEVICE_CHOICES),
            vol.Optional(
                CONF_AVAIL_MINUTES,
                default=current.get(CONF_AVAIL_MINUTES, DEFAULT_AVAIL_MINUTES),
            ): vol.All(int, vol.Range(min=1, max=1440)),
            vol.Optional(
                CONF_AVAIL_TICK,
                default=current.get(CONF_AVAIL_TICK, DEFAULT_AVAIL_TICK),
            ): vol.All(int, vol.Range(min=5, max=3600)),
            vol.Required(CONF_SENSOR_SOURCE): vol.In(
                [SENSOR_SOURCE_EXTERNAL, SENSOR_SOURCE_INTERNAL]
            ),
        })

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=schema)


async def async_migrate_entry(hass, config_entry: config_entries.ConfigEntry) -> bool:
    """Migrate old config entries to the new unique ID format."""
    version = config_entry.version

    if version < 2:
        data = {**config_entry.data}
        prefix = data.get(CONF_PREFIX, DEFAULT_PREFIX)
        sensor_id = data[CONF_SENSOR_ID]
        combined_id = f"{prefix}_{sensor_id}"
        if CONF_PREFIX not in data:
            data[CONF_PREFIX] = prefix
        config_entry.version = 2
        hass.config_entries.async_update_entry(
            config_entry, data=data, unique_id=combined_id
        )

    if version < 3:
        options = {**config_entry.options}
        if CONF_SENSOR_SOURCE not in options:
            if options.get(CONF_USE_EXTERNAL, DEFAULT_USE_EXTERNAL):
                options[CONF_SENSOR_SOURCE] = SENSOR_SOURCE_EXTERNAL
            else:
                options[CONF_SENSOR_SOURCE] = SENSOR_SOURCE_INTERNAL
            options.pop(CONF_USE_EXTERNAL, None)
            options.pop(CONF_USE_INTERNAL, None)
        config_entry.version = 3
        hass.config_entries.async_update_entry(config_entry, options=options)

    return True
