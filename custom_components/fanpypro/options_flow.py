import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .config_flow import _build_schemas
from .const import *


class FanpyProOptionsFlowHandler(config_entries.OptionsFlow):

    VERSION = 1

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        mode = self._config_entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
        if mode == CONF_MODE_DIRECT:
            return self.async_abort(reason="not_supported")

        if user_input is not None:
            use_broadlink = user_input[CONF_USE_BROADLINK] == "yes"
            new_data = {**self._config_entry.data, CONF_USE_BROADLINK: use_broadlink}
            if use_broadlink:
                self._pending_data = new_data
                return await self.async_step_broadlink_config()
            return await self._finish(new_data)

        current = self._config_entry.data.get(CONF_USE_BROADLINK, False)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_USE_BROADLINK, default="yes" if current else "no"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "no", "label": "No"},
                            {"value": "yes", "label": "Sí"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
        )

    async def async_step_broadlink_config(self, user_input=None):
        if user_input is not None:
            new_data = {**self._pending_data, **user_input}
            return await self._finish(new_data)

        data = self._pending_data
        num_speeds = data.get(CONF_NUM_SPEEDS, 6)
        schema = _build_schemas(self.hass, data, step="helpers_broadlink_config", num_speeds=num_speeds)
        return self.async_show_form(step_id="broadlink_config", data_schema=schema)

    async def _finish(self, new_data):
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            data=new_data,
        )
        from . import _generate_scripts_yaml
        await _generate_scripts_yaml(self.hass)
        return self.async_create_entry(title="", data={})
