import logging
import os
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_MODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, selector

from .const import *

_LOGGER = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    import re, unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace(" ", "_").replace("-", "_")
    text = re.sub(r"[^a-z0-9_]", "", text)
    return text


def _build_schemas(
    hass: HomeAssistant,
    entry_data: Optional[Dict[str, Any]] = None,
    step: str = "user",
    num_speeds: int = 6,
):
    data = entry_data or {}

    if step == "user":
        return vol.Schema({
            vol.Required(CONF_MODE, default=data.get(CONF_MODE, CONF_MODE_REMOTE)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[CONF_MODE_REMOTE, CONF_MODE_DIRECT],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "area":
        return vol.Schema({
            vol.Required(CONF_AREA): selector.AreaSelector(),
            vol.Required(CONF_FAN_NUMBER, default=str(data.get(CONF_FAN_NUMBER, 1))): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(i) for i in range(1, 6)],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "direct_entity":
        return vol.Schema({
            vol.Required(CONF_ENTITY_FAN, default=data.get(CONF_ENTITY_FAN, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch"),
            ),
            vol.Required(CONF_NUM_SPEEDS, default=str(data.get(CONF_NUM_SPEEDS, 1))): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(i) for i in range(MIN_SPEEDS, MAX_SPEEDS + 1)],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "direct_light":
        return vol.Schema({
            vol.Optional(CONF_HAS_LIGHT, default=data.get(CONF_HAS_LIGHT, False)): selector.BooleanSelector(),
        })

    if step == "direct_light_entity":
        return vol.Schema({
            vol.Required(CONF_ENTITY_LIGHT, default=data.get(CONF_ENTITY_LIGHT, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light"),
            ),
        })

    if step == "direct_light_features":
        return vol.Schema({
            vol.Optional(CONF_HAS_LIGHT_TEMPERATURE, default=data.get(CONF_HAS_LIGHT_TEMPERATURE, False)): selector.BooleanSelector(),
            vol.Optional(CONF_HAS_LIGHT_INTENSITY, default=data.get(CONF_HAS_LIGHT_INTENSITY, False)): selector.BooleanSelector(),
        })

    if step == "helpers_speeds":
        return vol.Schema({
            vol.Required(CONF_NUM_SPEEDS, default=str(data.get(CONF_NUM_SPEEDS, 6))): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(i) for i in range(MIN_SPEEDS, MAX_SPEEDS + 1)],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "helpers_light":
        return vol.Schema({
            vol.Optional(CONF_HAS_LIGHT, default=data.get(CONF_HAS_LIGHT, False)): selector.BooleanSelector(),
        })

    if step == "helpers_light_features":
        return vol.Schema({
            vol.Optional(CONF_HAS_LIGHT_TEMPERATURE, default=data.get(CONF_HAS_LIGHT_TEMPERATURE, False)): selector.BooleanSelector(),
            vol.Optional(CONF_HAS_LIGHT_INTENSITY, default=data.get(CONF_HAS_LIGHT_INTENSITY, False)): selector.BooleanSelector(),
        })

    if step == "helpers_timer":
        return vol.Schema({
            vol.Optional(CONF_NUM_TIMERS, default=str(data.get(CONF_NUM_TIMERS, 0))): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(i) for i in range(0, 4)],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "helpers_gateway":
        gateways = _scan_gateways(hass)
        if not gateways:
            gateways = [{"value": "", "label": "No gateways found. Create gateway files in fanpypro_codes/"}]
        default_zone = data.get(CONF_GATEWAY_ZONE, gateways[0]["value"] if gateways else "")
        return vol.Schema({
            vol.Required(CONF_GATEWAY_ZONE, default=default_zone): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=gateways,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    return vol.Schema({})


def _scan_gateways(hass: HomeAssistant) -> list[dict]:
    codes_dir = hass.config.path("custom_components", CODES_DIR)
    if not os.path.isdir(codes_dir):
        return []
    result = []
    for fname in os.listdir(codes_dir):
        if not fname.startswith("gateway_") or not fname.endswith("_codes.yaml"):
            continue
        zone = fname[len("gateway_"):-len("_codes.yaml")]
        label = zone.replace("_", " ").title()
        result.append({"value": zone, "label": label})
    return sorted(result, key=lambda x: x["value"])


class FanpyProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._mode = user_input[CONF_MODE]
            return await self.async_step_area()

        schema = _build_schemas(self.hass, step="user")
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_area(self, user_input=None):
        if user_input is not None:
            area = user_input[CONF_AREA]
            fan_number = int(user_input.get(CONF_FAN_NUMBER, 1))

            self._data = {
                CONF_AREA: area,
                CONF_FAN_NUMBER: fan_number,
                CONF_MODE: self._mode,
            }

            return await self._finalize_area()

        schema = _build_schemas(self.hass, self._data if hasattr(self, '_data') else {}, step="area")
        return self.async_show_form(step_id="area", data_schema=schema)

    async def _finalize_area(self):
        area = self._data[CONF_AREA]
        fan_number = self._data.get(CONF_FAN_NUMBER, 1)

        name = f"Ventilador {area.replace('_', ' ').title()}"
        if fan_number > 1:
            name = f"{name} {fan_number}"

        prefix = _slugify(f"ventilador_{area}")
        if fan_number > 1:
            prefix = _slugify(f"ventilador_{area}_{fan_number}")

        self._data[CONF_NAME] = name
        self._data[CONF_PREFIX] = prefix

        await self.async_set_unique_id(prefix)
        self._abort_if_unique_id_configured()

        if self._mode == CONF_MODE_DIRECT:
            return await self.async_step_direct_entity()
        return await self.async_step_helpers_speeds()

    async def async_step_direct_entity(self, user_input=None):
        if user_input is not None:
            user_input[CONF_NUM_SPEEDS] = int(user_input.get(CONF_NUM_SPEEDS, 1))
            self._data.update(user_input)
            return await self.async_step_direct_light()

        schema = _build_schemas(self.hass, self._data, step="direct_entity")
        return self.async_show_form(step_id="direct_entity", data_schema=schema)

    async def async_step_direct_light(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            if self._data.get(CONF_HAS_LIGHT, False):
                return await self.async_step_direct_light_entity()
            return await self.async_step_helpers_timer()

        schema = _build_schemas(self.hass, self._data, step="direct_light")
        return self.async_show_form(step_id="direct_light", data_schema=schema)

    async def async_step_direct_light_entity(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_direct_light_features()

        schema = _build_schemas(self.hass, self._data, step="direct_light_entity")
        return self.async_show_form(step_id="direct_light_entity", data_schema=schema)

    async def async_step_direct_light_features(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_helpers_timer()

        schema = _build_schemas(self.hass, self._data, step="direct_light_features")
        return self.async_show_form(step_id="direct_light_features", data_schema=schema)

    async def async_step_helpers_speeds(self, user_input=None):
        if user_input is not None:
            user_input[CONF_NUM_SPEEDS] = int(user_input.get(CONF_NUM_SPEEDS, 6))
            self._data.update(user_input)
            return await self.async_step_helpers_light()

        schema = _build_schemas(self.hass, self._data, step="helpers_speeds")
        return self.async_show_form(step_id="helpers_speeds", data_schema=schema)

    async def async_step_helpers_light(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            if self._data.get(CONF_HAS_LIGHT, False):
                return await self.async_step_helpers_light_features()
            return await self.async_step_helpers_timer()

        schema = _build_schemas(self.hass, self._data, step="helpers_light")
        return self.async_show_form(step_id="helpers_light", data_schema=schema)

    async def async_step_helpers_light_features(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_helpers_timer()

        schema = _build_schemas(self.hass, self._data, step="helpers_light_features")
        return self.async_show_form(step_id="helpers_light_features", data_schema=schema)

    async def async_step_helpers_timer(self, user_input=None):
        if user_input is not None:
            user_input[CONF_NUM_TIMERS] = int(user_input.get(CONF_NUM_TIMERS, 0))
            self._data.update(user_input)
            if self._mode == CONF_MODE_DIRECT:
                return self.async_create_entry(
                    title=self._data[CONF_NAME],
                    data=self._data,
                )
            return await self.async_step_helpers_gateway()

        schema = _build_schemas(self.hass, self._data, step="helpers_timer")
        step_id = "helpers_timer_direct" if self._mode == CONF_MODE_DIRECT else "helpers_timer"
        return self.async_show_form(
            step_id=step_id,
            data_schema=schema,
        )

    async def async_step_helpers_timer_direct(self, user_input=None):
        return await self.async_step_helpers_timer(user_input)

    async def async_step_helpers_gateway(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data[CONF_NAME],
                data=self._data,
            )

        schema = _build_schemas(self.hass, self._data, step="helpers_gateway")
        return self.async_show_form(step_id="helpers_gateway", data_schema=schema)


