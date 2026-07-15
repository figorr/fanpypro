import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    mode = entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
    has_light = entry.data.get(CONF_HAS_LIGHT, False)
    if mode == CONF_MODE_DIRECT or not has_light:
        return

    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)

    async_add_entities([
        FanpyProLuzResyncButton(hass, entry, prefix, name),
    ])


class FanpyProLuzResyncButton(ButtonEntity):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy Pro {name} Resync Luz"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_resync_luz"
        self._attr_icon = "mdi:lightbulb-sync"

    async def async_press(self) -> None:
        light_entity = self._hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("light_entity")
        if light_entity:
            await light_entity.async_process_rf_command(["luz_on"])
            _LOGGER.info("Luz resync button pressed for %s", self._prefix)
