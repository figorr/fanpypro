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
    if mode == CONF_MODE_DIRECT:
        return

    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)

    entities = [
        FanpyProFanResyncButton(hass, entry, prefix, name),
    ]
    if entry.data.get(CONF_HAS_LIGHT, False):
        entities.append(FanpyProLuzResyncButton(hass, entry, prefix, name))

    async_add_entities(entities)


class FanpyProFanResyncButton(ButtonEntity):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"FanpyPro {name} Resync Ventilador"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_resync_fan"
        self._attr_icon = "mdi:sync"

    async def async_press(self) -> None:
        fan_entity = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("fan_entity")
        if fan_entity:
            fan_entity._attr_is_on = not fan_entity._attr_is_on
            if fan_entity._attr_is_on:
                if fan_entity._attr_percentage == 0:
                    fan_entity._attr_percentage = fan_entity._last_percentage
                    if not fan_entity._attr_percentage:
                        fan_entity._attr_percentage = fan_entity._percentage_for_level(1)
            else:
                fan_entity._attr_percentage = 0
            fan_entity.async_write_ha_state()
            _LOGGER.info(
                "Ventilador resync button pressed for %s — toggled to %s",
                self._prefix, fan_entity._attr_is_on,
            )


class FanpyProLuzResyncButton(ButtonEntity):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"FanpyPro {name} Resync Luz"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_resync_luz"
        self._attr_icon = "mdi:sync"

    async def async_press(self) -> None:
        light_entity = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("light_entity")
        if light_entity:
            light_entity._attr_is_on = not light_entity._attr_is_on
            light_entity.async_write_ha_state()
            _LOGGER.info(
                "Luz resync button pressed for %s — toggled to %s",
                self._prefix, light_entity._attr_is_on,
            )
