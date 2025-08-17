import asyncio

from custom_components.ha_mqtt_sensors import config_flow
from custom_components.ha_mqtt_sensors.const import CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE
from homeassistant.config_entries import ConfigEntry


def test_options_flow_changes_device_type():
    entry = ConfigEntry(data={}, options={CONF_DEVICE_TYPE: DEFAULT_DEVICE_TYPE})
    handler = config_flow.OptionsFlowHandler(entry)

    result = asyncio.run(handler.async_step_init())
    assert result["type"] == "form"
    assert CONF_DEVICE_TYPE in result["data_schema"].schema

    result2 = asyncio.run(handler.async_step_init({CONF_DEVICE_TYPE: "door"}))
    assert result2["type"] == "create_entry"
    assert result2["data"][CONF_DEVICE_TYPE] == "door"
