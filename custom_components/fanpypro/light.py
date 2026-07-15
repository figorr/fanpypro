import logging

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    mode = entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
    if mode == CONF_MODE_DIRECT:
        return

    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)

    async_add_entities([
        FanpyProLightEntity(hass, entry, prefix, name),
    ])


class FanpyProLightEntity(LightEntity, RestoreEntity):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy Pro {name} Luz"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_luz"
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._hass.data.setdefault(DOMAIN, {}).setdefault(self._entry.entry_id, {})["light_entity"] = self
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"
        self.async_write_ha_state()

    async def async_process_rf_command(self, matching_commands: list[str]) -> None:
        for c in matching_commands:
            if c.startswith("luz_"):
                self._attr_is_on = not self._attr_is_on
                self.async_write_ha_state()
                _LOGGER.info("Light toggled from RF: is_on=%s", self._attr_is_on)
                return

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_luz_on", {}, blocking=True
        )

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_luz_off", {}, blocking=True
        )
